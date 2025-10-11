from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.clientsDto import CreateClientsDto, UpdateClientsDto, ClientsDto
from app.services.clientService import clientService
from typing import List, Optional
import os
import boto3
from botocore.exceptions import ClientError
import anyio

router = APIRouter(prefix="/clients", tags=["clients"])

async def get_client_service(db: AsyncSession = Depends(get_db)) -> clientService:
    return clientService(db)

# --- Helpers Cognito en modo async (wrappers) ---
# (los detalles de configuración y funciones son similares a los del userController.py)

@router.post("/", response_model=ClientsDto)
async def create_client(
    client_data: CreateClientsDto,
    client_service: clientService = Depends(get_client_service),
) -> Optional[ClientsDto]:
    existing_client = await client_service.get_client_by_ruc(client_data.ruc)
    if existing_client:
        raise HTTPException(status_code=400, detail="Client with this RUC already exists.")
    
    client = await client_service.create_client(client_data)
    if not client:
        raise HTTPException(status_code=500, detail="Error creating client.")
    
    return client

@router.get("/{client_id}", response_model=ClientsDto)
async def get_client(
    client_id: int,
    client_service: clientService = Depends(get_client_service),
) -> Optional[ClientsDto]:
    client = await client_service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")
    return client

@router.get("/", response_model=List[ClientsDto])
async def list_clients(
    skip: int = 0,
    limit: int = 100,
    client_service: clientService = Depends(get_client_service),
) -> List[ClientsDto]:
    clients = await client_service.get_clients(skip=skip, limit=limit)
    return clients

@router.put("/{client_id}", response_model=ClientsDto)
async def update_client(
    client_id: int,
    client_data: UpdateClientsDto,
    client_service: clientService = Depends(get_client_service),
) -> Optional[ClientsDto]:
    client = await client_service.update_client(client_id, client_data)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found or error updating.")
    return client

@router.delete("/{client_id}", response_model=dict)
async def delete_client(
    client_id: int,
    client_service: clientService = Depends(get_client_service),
) -> dict:
    success = await client_service.delete_client(client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found or error deleting.")
    return {"detail": "Client deleted successfully."}

