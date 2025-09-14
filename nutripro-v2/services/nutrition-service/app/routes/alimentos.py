"""
Food/Alimentos management routes
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.models import Alimento
from app.schemas.schemas import (
    AlimentoAutocomplete,
    AlimentoCreate,
    AlimentoResponse,
    AlimentoUpdate,
    SuccessResponse,
)

router = APIRouter(prefix="/alimentos", tags=["alimentos"])


@router.get("/", response_model=List[AlimentoResponse])
async def listar_alimentos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Buscar por nome do alimento"),
    origem: Optional[str] = Query(None, description="Filtrar por origem (manual, taco, api)"),
    session: AsyncSession = Depends(get_session),
):
    """Lista todos os alimentos com paginação e filtros"""
    query = select(Alimento)
    
    if search:
        search_filter = f"%{search.lower()}%"
        query = query.where(func.lower(Alimento.nome).contains(search_filter))
    
    if origem:
        query = query.where(Alimento.origem == origem)
    
    query = query.offset(skip).limit(limit).order_by(Alimento.nome)
    result = await session.execute(query)
    alimentos = result.scalars().all()
    
    return alimentos


@router.get("/autocomplete", response_model=List[AlimentoAutocomplete])
async def autocomplete_alimentos(
    q: str = Query(..., min_length=2, description="Termo de busca (mínimo 2 caracteres)"),
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    """Endpoint de autocomplete para busca de alimentos"""
    search_filter = f"%{q.lower()}%"
    query = (
        select(Alimento)
        .where(func.lower(Alimento.nome).contains(search_filter))
        .order_by(Alimento.nome)
        .limit(limit)
    )
    
    result = await session.execute(query)
    alimentos = result.scalars().all()
    
    return alimentos


@router.get("/{alimento_id}", response_model=AlimentoResponse)
async def obter_alimento(
    alimento_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Obter detalhes de um alimento específico"""
    query = select(Alimento).where(Alimento.id == alimento_id)
    result = await session.execute(query)
    alimento = result.scalar_one_or_none()
    
    if not alimento:
        raise HTTPException(status_code=404, detail="Alimento não encontrado")
    
    return alimento


@router.post("/", response_model=AlimentoResponse, status_code=201)
async def criar_alimento(
    alimento_data: AlimentoCreate,
    session: AsyncSession = Depends(get_session),
):
    """Criar um novo alimento"""
    alimento = Alimento(**alimento_data.model_dump())
    session.add(alimento)
    await session.commit()
    await session.refresh(alimento)
    
    return alimento


@router.put("/{alimento_id}", response_model=AlimentoResponse)
async def atualizar_alimento(
    alimento_id: int,
    alimento_data: AlimentoUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Atualizar dados de um alimento"""
    # Buscar alimento
    query = select(Alimento).where(Alimento.id == alimento_id)
    result = await session.execute(query)
    alimento = result.scalar_one_or_none()
    
    if not alimento:
        raise HTTPException(status_code=404, detail="Alimento não encontrado")
    
    # Atualizar campos fornecidos
    update_data = alimento_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alimento, field, value)
    
    await session.commit()
    await session.refresh(alimento)
    
    return alimento


@router.delete("/{alimento_id}", response_model=SuccessResponse)
async def excluir_alimento(
    alimento_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Excluir um alimento"""
    # Buscar alimento
    query = select(Alimento).where(Alimento.id == alimento_id)
    result = await session.execute(query)
    alimento = result.scalar_one_or_none()
    
    if not alimento:
        raise HTTPException(status_code=404, detail="Alimento não encontrado")
    
    # Verificar se é um alimento da base TACO (opcional: prevenir exclusão)
    if alimento.origem == "taco":
        raise HTTPException(
            status_code=400, 
            detail="Alimentos da base TACO não podem ser excluídos"
        )
    
    await session.delete(alimento)
    await session.commit()
    
    return SuccessResponse(message=f"Alimento '{alimento.nome}' excluído com sucesso")


@router.post("/bulk-import", response_model=SuccessResponse)
async def importar_alimentos_bulk(
    alimentos_data: List[AlimentoCreate],
    session: AsyncSession = Depends(get_session),
):
    """Importação em lote de alimentos (útil para dados TACO)"""
    if len(alimentos_data) > 1000:
        raise HTTPException(
            status_code=400, 
            detail="Máximo 1000 alimentos por importação"
        )
    
    alimentos = [Alimento(**alimento.model_dump()) for alimento in alimentos_data]
    session.add_all(alimentos)
    await session.commit()
    
    return SuccessResponse(
        message=f"{len(alimentos)} alimentos importados com sucesso"
    )