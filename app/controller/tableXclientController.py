from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.tablesXclientDto import createTablesXclientDto, updateTablesXclientDto
from app.services.tablesXclientService import tablesXclientService
from typing import List, Optional
import os
import boto3
from botocore.exceptions import ClientError
import anyio

router = APIRouter(prefix="/tablesXclient", tags=["tablesXclient"])

async def get_table_service(db: AsyncSession = Depends(get_db)) -> tablesXclientService:
    return tablesXclientService(db)

@router.post("/", response_model=createTablesXclientDto)
async def create_table(
    table_data: createTablesXclientDto,
    table_service: tablesXclientService = Depends(get_table_service),
) -> Optional[createTablesXclientDto]:
    table = await table_service.create_table(table_data)
    if not table:
        raise HTTPException(status_code=500, detail="Error creating table.")
    return table

@router.get("/{table_id}", response_model=createTablesXclientDto)
async def get_table(
    table_id: int,
    table_service: tablesXclientService = Depends(get_table_service),
) -> Optional[createTablesXclientDto]:
    table = await table_service.get_table_by_id(table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found.")
    return table

@router.get("/", response_model=List[createTablesXclientDto])
async def list_tables(
    skip: int = 0,
    limit: int = 100,
    table_service: tablesXclientService = Depends(get_table_service),
) -> List[createTablesXclientDto]:
    tables = await table_service.get_tables(skip=skip, limit=limit)
    return tables

@router.put("/{table_id}", response_model=createTablesXclientDto)
async def update_table(
    table_id: int,
    table_data: updateTablesXclientDto,
    table_service: tablesXclientService = Depends(get_table_service),
) -> Optional[createTablesXclientDto]:
    table = await table_service.update_table(table_id, table_data)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found or error updating.")
    return table

@router.delete("/{table_id}", response_model=dict)
async def delete_table(
    table_id: int,
    table_service: tablesXclientService = Depends(get_table_service),
) -> dict:
    success = await table_service.delete_table(table_id)
    if not success:
        raise HTTPException(status_code=404, detail="Table not found or error deleting.")
    return {"detail": "Table deleted successfully."}

