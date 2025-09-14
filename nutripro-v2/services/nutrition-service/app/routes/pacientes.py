"""
Patients management routes
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models.models import Paciente
from app.schemas.schemas import (
    PacienteCreate,
    PacienteResponse,
    PacienteUpdate,
    SuccessResponse,
)

router = APIRouter(prefix="/pacientes", tags=["pacientes"])


@router.get("/", response_model=List[PacienteResponse])
async def listar_pacientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Buscar por nome ou email"),
    session: AsyncSession = Depends(get_session),
):
    """Lista todos os pacientes com paginação e busca opcional"""
    query = select(Paciente)
    
    if search:
        search_filter = f"%{search.lower()}%"
        query = query.where(
            func.lower(Paciente.nome_completo).contains(search_filter) |
            func.lower(Paciente.email).contains(search_filter)
        )
    
    query = query.offset(skip).limit(limit).order_by(Paciente.nome_completo)
    result = await session.execute(query)
    pacientes = result.scalars().all()
    
    return pacientes


@router.get("/{paciente_id}", response_model=PacienteResponse)
async def obter_paciente(
    paciente_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Obter detalhes de um paciente específico"""
    query = select(Paciente).where(Paciente.id == paciente_id)
    result = await session.execute(query)
    paciente = result.scalar_one_or_none()
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    return paciente


@router.post("/", response_model=PacienteResponse, status_code=201)
async def criar_paciente(
    paciente_data: PacienteCreate,
    session: AsyncSession = Depends(get_session),
):
    """Criar um novo paciente"""
    # Verificar se o email já existe
    query = select(Paciente).where(Paciente.email == paciente_data.email)
    result = await session.execute(query)
    existing_paciente = result.scalar_one_or_none()
    
    if existing_paciente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Criar novo paciente
    paciente = Paciente(**paciente_data.model_dump())
    session.add(paciente)
    await session.commit()
    await session.refresh(paciente)
    
    return paciente


@router.put("/{paciente_id}", response_model=PacienteResponse)
async def atualizar_paciente(
    paciente_id: int,
    paciente_data: PacienteUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Atualizar dados de um paciente"""
    # Buscar paciente
    query = select(Paciente).where(Paciente.id == paciente_id)
    result = await session.execute(query)
    paciente = result.scalar_one_or_none()
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Verificar se o novo email já existe (se fornecido)
    if paciente_data.email and paciente_data.email != paciente.email:
        query = select(Paciente).where(Paciente.email == paciente_data.email)
        result = await session.execute(query)
        existing_paciente = result.scalar_one_or_none()
        
        if existing_paciente:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Atualizar campos fornecidos
    update_data = paciente_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(paciente, field, value)
    
    await session.commit()
    await session.refresh(paciente)
    
    return paciente


@router.delete("/{paciente_id}", response_model=SuccessResponse)
async def excluir_paciente(
    paciente_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Excluir um paciente e todos seus dados relacionados"""
    # Buscar paciente
    query = select(Paciente).where(Paciente.id == paciente_id)
    result = await session.execute(query)
    paciente = result.scalar_one_or_none()
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Excluir paciente (cascade deletará relacionamentos)
    await session.delete(paciente)
    await session.commit()
    
    return SuccessResponse(message=f"Paciente {paciente.nome_completo} excluído com sucesso")


@router.get("/{paciente_id}/planos")
async def listar_planos_paciente(
    paciente_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Listar todos os planos alimentares de um paciente"""
    # Verificar se paciente existe
    query = select(Paciente).where(Paciente.id == paciente_id)
    result = await session.execute(query)
    paciente = result.scalar_one_or_none()
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Buscar planos com relacionamentos
    query = (
        select(Paciente)
        .options(selectinload(Paciente.planos))
        .where(Paciente.id == paciente_id)
    )
    result = await session.execute(query)
    paciente_with_planos = result.scalar_one()
    
    return paciente_with_planos.planos


@router.get("/{paciente_id}/consultas")
async def listar_consultas_paciente(
    paciente_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Listar todas as consultas de um paciente"""
    # Verificar se paciente existe
    query = select(Paciente).where(Paciente.id == paciente_id)
    result = await session.execute(query)
    paciente = result.scalar_one_or_none()
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Buscar consultas com relacionamentos
    query = (
        select(Paciente)
        .options(selectinload(Paciente.consultas))
        .where(Paciente.id == paciente_id)
    )
    result = await session.execute(query)
    paciente_with_consultas = result.scalar_one()
    
    return paciente_with_consultas.consultas