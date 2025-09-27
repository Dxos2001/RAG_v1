from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.usersDto import CreateUsersDto, UpdateUsersDto, UsersDto
from app.services.userServices import UserService
from typing import List
import os
import boto3
from botocore.exceptions import ClientError
import anyio

router = APIRouter(prefix="/users", tags=["users"])

# --- Config Cognito ---
COGNITO_REGION = os.getenv("COGNITO_REGION")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
AWS_ACCESS_KEY_ID = os.getenv("IAM_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("IAM_SECRET_ACCESS_KEY")

if not COGNITO_REGION or not COGNITO_USER_POOL_ID:
    raise RuntimeError("Config Cognito incompleta: COGNITO_REGION y COGNITO_USER_POOL_ID son requeridos.")

# Cliente boto3 (sincrónico; lo usaremos en hilos)
_cognito = boto3.client("cognito-idp", region_name=COGNITO_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

# --- Helpers Cognito en modo async (wrappers) ---

async def cognito_admin_create_user(username: str, email: str, email_verified: bool = True) -> str:
    """
    Crea el usuario en el User Pool y devuelve el 'Username' (normalmente es el sub interno de Cognito
    en formato UUID si no especificas Username distinto).
    """
    def _call():
        attrs = [
            {"Name": "email", "Value": email},
            {"Name": "email_verified", "Value": "true" if email_verified else "false"},
        ]
        # Puedes añadir más atributos, p. ej., phone_number, name, etc.
        return _cognito.admin_create_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=email,  # puedes usar email como username si quieres
            UserAttributes=attrs,
            MessageAction="SUPPRESS",  # no enviar email de invitación
        )

    try:
        resp = await anyio.to_thread.run_sync(_call)
        # El campo resp['User']['Username'] puede ser el mismo que pasaste o uno generado por Cognito
        return resp["User"]["Username"]
    except ClientError as e:
        raise HTTPException(status_code=400, detail=f"Cognito create error: {e.response['Error']['Message']}")

async def cognito_admin_set_permanent_password(username: str, password: str) -> None:
    def _call():
        return _cognito.admin_set_user_password(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,
            Password=password,
            Permanent=True,
        )
    try:
        await anyio.to_thread.run_sync(_call)
    except ClientError as e:
        # Si falla, conviene borrar el usuario que se acabó de crear
        raise HTTPException(status_code=400, detail=f"Cognito set password error: {e.response['Error']['Message']}")

async def cognito_admin_delete_user(username: str) -> None:
    def _call():
        return _cognito.admin_delete_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,
        )
    try:
        await anyio.to_thread.run_sync(_call)
    except ClientError:
        # No levantamos otra excepción aquí para no ocultar el error original.
        pass

# --- Rutas ---

@router.post("/", response_model=UsersDto)
async def create_user(user: CreateUsersDto, service: UserService = Depends(get_user_service)):
    """
    Flujo:
    1) Crear en Cognito (AdminCreateUser + AdminSetUserPassword permanente).
    2) Crear en tu BD con referencia al usuario de Cognito (por ejemplo, guardar cognito_username o cognito_sub).
    3) Si falla la BD, se borra el usuario de Cognito (rollback compensatorio).
    """

    # 1) Crear en Cognito
    # Puedes decidir qué usar como "username" en Cognito: user.username o user.email
    cognito_username = user.username  # o user.email
    created_cognito_username = await cognito_admin_create_user(
        username=cognito_username,
        email=user.email,  # asumiendo que CreateUsersDto tiene email
        email_verified=True,
    )

    # Setear password permanente en Cognito
    await cognito_admin_set_permanent_password(
        username=created_cognito_username,
        password=user.password  # asumiendo que CreateUsersDto tiene password
    )

    # 2) Crear en BD
    # Sugerencia: guarda el "cognito_username" y/o el "sub" (si decides después leerlo del ID Token).
    # Por ahora, guardemos "cognito_username" como referencia:
    try:
        created = await service.create_user(user)  # si tu DTO y modelo ya incluyen campos
        # Si quieres persistir el cognito_username, ajusta tu modelo/DTO:
        # e.g., created = await service.create_user(user, cognito_username=created_cognito_username)
        if not created:
            # rollback cognito
            await cognito_admin_delete_user(created_cognito_username)
            raise HTTPException(status_code=400, detail="User could not be created")
        return created
    except Exception as e:
        # rollback cognito si falla la BD
        await cognito_admin_delete_user(created_cognito_username)
        raise

@router.get("/", response_model=List[UsersDto])
async def get_users(service: UserService = Depends(get_user_service)):
    return await service.get_users()

@router.get("/{user_id}", response_model=UsersDto)
async def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UsersDto)
async def update_user(user_id: int, user_update: UpdateUsersDto, service: UserService = Depends(get_user_service)):
    updated = await service.update_user(user_id, user_update)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{user_id}")
async def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    """
    Opcional: también borrar en Cognito.
    Para eso necesitas tener guardado el 'cognito_username' o 'sub' asociado al registro.
    """
    # 1) Recupera el usuario para conocer su cognito_username (si lo guardaste)
    user_db = await service.get_user(user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    # 2) Borra en Cognito (si tienes el username/sub guardado)
    # if user_db.cognito_username:
    #     await cognito_admin_delete_user(user_db.cognito_username)

    # 3) Borra en BD
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}