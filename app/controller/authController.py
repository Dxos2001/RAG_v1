from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import os, base64, hmac, hashlib, boto3, anyio
from botocore.exceptions import ClientError

router = APIRouter(prefix="/auth", tags=["auth"])

# === Config ===
REGION = os.getenv("COGNITO_REGION")
USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")
CLIENT_SECRET = os.getenv("COGNITO_APP_CLIENT_SECRET")  # si existe -> enviar SECRET_HASH

if not (REGION and USER_POOL_ID and CLIENT_ID):
    raise RuntimeError("Faltan vars de entorno: COGNITO_REGION, COGNITO_USER_POOL_ID, COGNITO_APP_CLIENT_ID.")

cognito = boto3.client("cognito-idp", region_name=REGION)

# === Utils ===
def _secret_hash(username: str) -> str | None:
    if not CLIENT_SECRET:
        return None
    msg = (username + CLIENT_ID).encode("utf-8")
    key = CLIENT_SECRET.encode("utf-8")
    digest = hmac.new(key, msg, hashlib.sha256).digest()
    return base64.b64encode(digest).decode()

def _build_auth_params(username: str, extra: dict) -> dict:
    params = {**extra}
    sh = _secret_hash(username)
    if sh:
        params["SECRET_HASH"] = sh
    return params

# === Schemas ===
class LoginDto(BaseModel):
    email: EmailStr
    password: str

class RefreshDto(BaseModel):
    # IMPORTANTE: incluir username si tu client usa secret
    username: EmailStr | None = None
    refresh_token: str

# === Endpoints ===

@router.post("/login")
async def login(body: LoginDto):
    username = body.email.strip().lower()
    password = body.password

    def _initiate():
        return cognito.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters=_build_auth_params(username, {
                "USERNAME": username,
                "PASSWORD": password,
            }),
        )

    try:
        resp = await anyio.to_thread.run_sync(_initiate)

        # Manejo de challenges comunes
        if "ChallengeName" in resp:
            ch = resp["ChallengeName"]
            # Puedes extender: SMS_MFA, SOFTWARE_TOKEN_MFA, NEW_PASSWORD_REQUIRED, etc.
            return {"challenge": ch, "session": resp.get("Session")}

        auth = resp.get("AuthenticationResult", {})
        return {
            "access_token": auth.get("AccessToken"),
            "id_token": auth.get("IdToken"),
            "refresh_token": auth.get("RefreshToken"),
            "expires_in": auth.get("ExpiresIn"),
            "token_type": auth.get("TokenType"),
        }
    except ClientError as e:
        raise HTTPException(status_code=401, detail=e.response["Error"]["Message"])

@router.post("/refresh")
async def refresh(body: RefreshDto):
    # Si hay client secret, Cognito espera SECRET_HASH calculado con el username.
    username = (body.username or "").strip().lower()
    if CLIENT_SECRET and not username:
        # Forzar a enviar username cuando el client usa secret
        raise HTTPException(status_code=400, detail="username es requerido para REFRESH cuando el client usa secret.")

    def _refresh():
        return cognito.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters=_build_auth_params(username, {
                "REFRESH_TOKEN": body.refresh_token,
            }),
        )

    try:
        resp = await anyio.to_thread.run_sync(_refresh)
        auth = resp.get("AuthenticationResult", {})
        return {
            "access_token": auth.get("AccessToken"),
            "id_token": auth.get("IdToken"),
            "expires_in": auth.get("ExpiresIn"),
            "token_type": auth.get("TokenType"),
        }
    except ClientError as e:
        raise HTTPException(status_code=401, detail=e.response["Error"]["Message"])