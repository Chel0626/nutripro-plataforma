"""
Nutrition calculations routes
"""
from fastapi import APIRouter, HTTPException

from app.schemas.schemas import (
    CalculoCaloriasRequest,
    CalculoCaloriasResponse,
    DistribuicaoMacrosRequest,
    DistribuicaoMacrosResponse,
)
from app.services.calculator import NutritionCalculatorService

router = APIRouter(prefix="/calculos", tags=["calculos"])


@router.post("/calorias", response_model=CalculoCaloriasResponse)
async def calcular_calorias(request: CalculoCaloriasRequest):
    """
    Calcula a necessidade calórica baseada em dados antropométricos e nível de atividade.
    
    Utiliza as equações de Mifflin-St Jeor para adultos e Schofield para crianças.
    """
    result = NutritionCalculatorService.calcular_necessidade_calorica(request)
    
    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Erro no cálculo. Verifique os dados fornecidos."
        )
    
    return result


@router.post("/distribuicao-macros", response_model=DistribuicaoMacrosResponse)
async def calcular_distribuicao_macros(request: DistribuicaoMacrosRequest):
    """
    Calcula a distribuição de macronutrientes entre as refeições.
    
    Distribui automaticamente entre refeições grandes (70%) e pequenas (30%).
    """
    # Validar se as porcentagens somam 100%
    total_percent = request.perc_carb + request.perc_prot + request.perc_gord
    if round(total_percent) != 100:
        raise HTTPException(
            status_code=400,
            detail=f"As porcentagens devem somar 100%. Total atual: {total_percent}%"
        )
    
    result = NutritionCalculatorService.distribuir_macros_nas_refeicoes(request)
    
    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Erro no cálculo. Verifique os dados fornecidos."
        )
    
    return result


@router.get("/tmb")
async def calcular_tmb_simples(
    peso: float,
    altura: float,
    idade: int,
    sexo: str
):
    """
    Endpoint simples para calcular apenas a Taxa Metabólica Basal (TMB).
    """
    from app.schemas.schemas import SexoEnum
    
    try:
        sexo_enum = SexoEnum(sexo.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Sexo deve ser 'masculino' ou 'feminino'"
        )
    
    tmb = NutritionCalculatorService.calcular_tmb(peso, altura, idade, sexo_enum)
    
    if tmb is None:
        raise HTTPException(
            status_code=400,
            detail="Erro no cálculo. Verifique os dados fornecidos."
        )
    
    return {
        "tmb": tmb,
        "unidade": "kcal/dia"
    }