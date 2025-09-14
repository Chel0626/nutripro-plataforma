"""
Nutrition calculation services
Migrated from calculadoras.py with modern typing and error handling
"""
from typing import Dict, List, Optional

from app.schemas.schemas import (
    CalculoCaloriasRequest,
    CalculoCaloriasResponse,
    DistribuicaoMacrosRequest,
    DistribuicaoMacrosResponse,
    MacroRefeicao,
    NivelAtividadeEnum,
    SexoEnum,
)


class NutritionCalculatorService:
    """Service for nutrition calculations"""

    @staticmethod
    def calcular_tmb(peso_kg: float, altura_cm: float, idade_anos: int, sexo: SexoEnum) -> Optional[float]:
        """
        Calcula a Taxa Metabólica Basal (TMB) usando a equação de Mifflin-St Jeor para adultos 
        e Schofield para crianças.
        """
        # Validação dos inputs
        if peso_kg <= 0 or altura_cm <= 0 or idade_anos <= 0:
            return None

        # Para crianças (assumindo que crianças são menores de 18 anos)
        if idade_anos < 18:
            if 0 <= idade_anos <= 3:
                tmb = (59.512 * peso_kg) - 30.4
            elif 3 < idade_anos <= 10:
                tmb = (22.706 * peso_kg) + 504.3
            elif 10 < idade_anos < 18:
                tmb = (17.686 * peso_kg) + 658.2
            else:
                return None
            return round(tmb, 2)

        # Para adultos - Fórmula de Mifflin-St Jeor
        if sexo == SexoEnum.masculino:
            tmb = (10 * peso_kg) + (6.25 * altura_cm) - (5 * idade_anos) + 5
        elif sexo == SexoEnum.feminino:
            tmb = (10 * peso_kg) + (6.25 * altura_cm) - (5 * idade_anos) - 161
        else:
            return None

        return round(tmb, 2)

    @staticmethod
    def calcular_necessidade_calorica(request: CalculoCaloriasRequest) -> Optional[CalculoCaloriasResponse]:
        """
        Calcula a necessidade calórica total com base nos inputs.
        """
        tmb = NutritionCalculatorService.calcular_tmb(
            request.peso, request.altura, request.idade, request.sexo
        )
        if tmb is None:
            return None

        # Fatores de atividade física
        fatores_naf = {
            NivelAtividadeEnum.sedentario: 1.2,
            NivelAtividadeEnum.leve: 1.375,
            NivelAtividadeEnum.moderado: 1.55,
            NivelAtividadeEnum.ativo: 1.725,
            NivelAtividadeEnum.extremo: 1.9,
        }

        fator_atividade = fatores_naf.get(request.nivel_atividade)
        if fator_atividade is None:
            return None

        calorias_objetivo = round(tmb * fator_atividade)

        return CalculoCaloriasResponse(
            tmb=tmb,
            calorias_objetivo=calorias_objetivo,
            nivel_atividade=request.nivel_atividade.value,
            fator_atividade=fator_atividade,
        )

    @staticmethod
    def calcular_macros_por_porcentagem(
        total_kcal: int, perc_carb: float, perc_prot: float, perc_gord: float
    ) -> Optional[Dict[str, float]]:
        """Calcula os gramas de macros com base na distribuição percentual."""
        total_perc = perc_carb + perc_prot + perc_gord
        if round(total_perc) != 100:
            return None

        gramas_carb = round((total_kcal * (perc_carb / 100.0)) / 4, 1)
        gramas_prot = round((total_kcal * (perc_prot / 100.0)) / 4, 1)
        gramas_gord = round((total_kcal * (perc_gord / 100.0)) / 9, 1)

        return {"carboidrato": gramas_carb, "proteina": gramas_prot, "gordura": gramas_gord}

    @staticmethod
    def distribuir_macros_nas_refeicoes(
        request: DistribuicaoMacrosRequest,
    ) -> Optional[DistribuicaoMacrosResponse]:
        """Distribui os macros entre refeições grandes e pequenas."""
        # Calcular macros totais
        macros_em_gramas = NutritionCalculatorService.calcular_macros_por_porcentagem(
            request.total_kcal, request.perc_carb, request.perc_prot, request.perc_gord
        )
        if macros_em_gramas is None:
            return None

        total_refeicoes = request.num_refeicoes_grandes + request.num_refeicoes_pequenas
        if total_refeicoes == 0:
            return None

        # Distribuição: refeições grandes recebem 70% dos macros
        perc_dist_grandes = 70
        perc_dist_pequenas = 30

        # Calcular macros por tipo de refeição
        macros_grandes_total = {
            "carboidrato": macros_em_gramas["carboidrato"] * (perc_dist_grandes / 100.0),
            "proteina": macros_em_gramas["proteina"] * (perc_dist_grandes / 100.0),
            "gordura": macros_em_gramas["gordura"] * (perc_dist_grandes / 100.0),
        }

        macros_pequenas_total = {
            "carboidrato": macros_em_gramas["carboidrato"] * (perc_dist_pequenas / 100.0),
            "proteina": macros_em_gramas["proteina"] * (perc_dist_pequenas / 100.0),
            "gordura": macros_em_gramas["gordura"] * (perc_dist_pequenas / 100.0),
        }

        refeicoes = []

        # Criar refeições grandes
        for i in range(request.num_refeicoes_grandes):
            nome_refeicao = ["Café da Manhã", "Almoço", "Jantar"][i] if i < 3 else f"Refeição Grande {i+1}"
            
            carb_por_refeicao = (
                round(macros_grandes_total["carboidrato"] / request.num_refeicoes_grandes, 1)
                if request.num_refeicoes_grandes > 0
                else 0
            )
            prot_por_refeicao = (
                round(macros_grandes_total["proteina"] / request.num_refeicoes_grandes, 1)
                if request.num_refeicoes_grandes > 0
                else 0
            )
            gord_por_refeicao = (
                round(macros_grandes_total["gordura"] / request.num_refeicoes_grandes, 1)
                if request.num_refeicoes_grandes > 0
                else 0
            )

            kcal_refeicao = round(
                (carb_por_refeicao * 4) + (prot_por_refeicao * 4) + (gord_por_refeicao * 9)
            )

            refeicoes.append(
                MacroRefeicao(
                    nome=nome_refeicao,
                    tipo="grande",
                    kcal=kcal_refeicao,
                    carboidratos_g=carb_por_refeicao,
                    proteinas_g=prot_por_refeicao,
                    gorduras_g=gord_por_refeicao,
                )
            )

        # Criar refeições pequenas
        for i in range(request.num_refeicoes_pequenas):
            nome_refeicao = ["Lanche da Manhã", "Lanche da Tarde", "Ceia"][i] if i < 3 else f"Lanche {i+1}"
            
            carb_por_refeicao = (
                round(macros_pequenas_total["carboidrato"] / request.num_refeicoes_pequenas, 1)
                if request.num_refeicoes_pequenas > 0
                else 0
            )
            prot_por_refeicao = (
                round(macros_pequenas_total["proteina"] / request.num_refeicoes_pequenas, 1)
                if request.num_refeicoes_pequenas > 0
                else 0
            )
            gord_por_refeicao = (
                round(macros_pequenas_total["gordura"] / request.num_refeicoes_pequenas, 1)
                if request.num_refeicoes_pequenas > 0
                else 0
            )

            kcal_refeicao = round(
                (carb_por_refeicao * 4) + (prot_por_refeicao * 4) + (gord_por_refeicao * 9)
            )

            refeicoes.append(
                MacroRefeicao(
                    nome=nome_refeicao,
                    tipo="pequena",
                    kcal=kcal_refeicao,
                    carboidratos_g=carb_por_refeicao,
                    proteinas_g=prot_por_refeicao,
                    gorduras_g=gord_por_refeicao,
                )
            )

        return DistribuicaoMacrosResponse(
            total_kcal=request.total_kcal,
            total_carboidratos_g=macros_em_gramas["carboidrato"],
            total_proteinas_g=macros_em_gramas["proteina"],
            total_gorduras_g=macros_em_gramas["gordura"],
            refeicoes=refeicoes,
        )