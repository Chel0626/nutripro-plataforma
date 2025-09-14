"""
Pydantic schemas for request/response validation
"""
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Base schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Enums
class SexoEnum(str, Enum):
    masculino = "masculino"
    feminino = "feminino"


class StatusConsultaEnum(str, Enum):
    agendada = "Agendada"
    realizada = "Realizada"
    cancelada = "Cancelada"


class NivelAtividadeEnum(str, Enum):
    sedentario = "sedentario"
    leve = "leve"
    moderado = "moderado"
    ativo = "ativo"
    extremo = "extremo"


# Alimento schemas
class AlimentoBase(BaseSchema):
    nome: str = Field(..., min_length=1, max_length=200)
    marca: Optional[str] = Field(None, max_length=150)
    kcal_100g: float = Field(ge=0)
    carboidratos_100g: float = Field(ge=0)
    proteinas_100g: float = Field(ge=0)
    gorduras_100g: float = Field(ge=0)
    origem: Optional[str] = Field(default="manual", max_length=50)


class AlimentoCreate(AlimentoBase):
    pass


class AlimentoUpdate(BaseSchema):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    marca: Optional[str] = Field(None, max_length=150)
    kcal_100g: Optional[float] = Field(None, ge=0)
    carboidratos_100g: Optional[float] = Field(None, ge=0)
    proteinas_100g: Optional[float] = Field(None, ge=0)
    gorduras_100g: Optional[float] = Field(None, ge=0)


class AlimentoResponse(AlimentoBase):
    id: int
    data_criacao: datetime


class AlimentoAutocomplete(BaseSchema):
    id: int
    nome: str
    marca: Optional[str] = None
    kcal_100g: float
    carboidratos_100g: float
    proteinas_100g: float
    gorduras_100g: float


# Paciente schemas
class PacienteBase(BaseSchema):
    nome_completo: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    telefone: Optional[str] = Field(None, max_length=20)
    data_nascimento: Optional[date] = None
    peso: Optional[float] = Field(None, gt=0, le=500)
    altura_cm: Optional[int] = Field(None, gt=0, le=300)
    sexo: Optional[SexoEnum] = None
    observacoes: Optional[str] = None


class PacienteCreate(PacienteBase):
    pass


class PacienteUpdate(BaseSchema):
    nome_completo: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)
    data_nascimento: Optional[date] = None
    peso: Optional[float] = Field(None, gt=0, le=500)
    altura_cm: Optional[int] = Field(None, gt=0, le=300)
    sexo: Optional[SexoEnum] = None
    observacoes: Optional[str] = None


class PacienteResponse(PacienteBase):
    id: int
    data_cadastro: datetime


# Consulta schemas
class ConsultaBase(BaseSchema):
    data_hora: datetime
    tipo_consulta: Optional[str] = Field(None, max_length=100)
    status: StatusConsultaEnum = StatusConsultaEnum.agendada
    observacoes_nutri: Optional[str] = None
    link_videochamada: Optional[str] = Field(None, max_length=255)


class ConsultaCreate(ConsultaBase):
    paciente_id: int


class ConsultaUpdate(BaseSchema):
    data_hora: Optional[datetime] = None
    tipo_consulta: Optional[str] = Field(None, max_length=100)
    status: Optional[StatusConsultaEnum] = None
    observacoes_nutri: Optional[str] = None
    link_videochamada: Optional[str] = Field(None, max_length=255)


class ConsultaResponse(ConsultaBase):
    id: int
    paciente_id: int
    data_criacao: datetime


# Item refeição schemas
class ItemRefeicaoBase(BaseSchema):
    nome_alimento: str = Field(..., min_length=1, max_length=200)
    marca_alimento: Optional[str] = Field(None, max_length=150)
    quantidade_g: float = Field(gt=0)
    medida_caseira: Optional[str] = Field(None, max_length=100)
    substituicoes: Optional[str] = None
    carboidratos_g: float = Field(ge=0)
    proteinas_g: float = Field(ge=0)
    gorduras_g: float = Field(ge=0)
    kcal: int = Field(ge=0)


class ItemRefeicaoCreate(ItemRefeicaoBase):
    pass


class ItemRefeicaoResponse(ItemRefeicaoBase):
    id: int


# Refeição schemas
class RefeicaoBase(BaseSchema):
    nome_refeicao: str = Field(..., min_length=1, max_length=100)
    horario_sugerido: Optional[str] = Field(None, max_length=50)
    meta_carboidratos_g: Optional[float] = Field(None, ge=0)
    meta_proteinas_g: Optional[float] = Field(None, ge=0)
    meta_gorduras_g: Optional[float] = Field(None, ge=0)


class RefeicaoCreate(RefeicaoBase):
    itens: List[ItemRefeicaoCreate] = []


class RefeicaoResponse(RefeicaoBase):
    id: int
    itens: List[ItemRefeicaoResponse] = []


# Plano Alimentar schemas
class PlanoAlimentarBase(BaseSchema):
    nome_plano: str = Field(default="Plano Padrão", max_length=150)
    objetivo_calorico_final: Optional[int] = Field(None, ge=0)
    orientacoes_diabetes: Optional[str] = None
    orientacoes_nutricao: Optional[str] = None


class PlanoAlimentarCreate(PlanoAlimentarBase):
    paciente_id: int
    refeicoes: List[RefeicaoCreate] = []


class PlanoAlimentarUpdate(BaseSchema):
    nome_plano: Optional[str] = Field(None, max_length=150)
    objetivo_calorico_final: Optional[int] = Field(None, ge=0)
    orientacoes_diabetes: Optional[str] = None
    orientacoes_nutricao: Optional[str] = None
    ativo: Optional[bool] = None


class PlanoAlimentarResponse(PlanoAlimentarBase):
    id: int
    paciente_id: int
    data_criacao: datetime
    ativo: Optional[bool] = True
    refeicoes: List[RefeicaoResponse] = []


# Cálculo de calorias schemas
class CalculoCaloriasRequest(BaseSchema):
    peso: float = Field(gt=0, le=500)
    altura: float = Field(gt=0, le=300)
    idade: int = Field(gt=0, le=150)
    sexo: SexoEnum
    nivel_atividade: NivelAtividadeEnum


class CalculoCaloriasResponse(BaseSchema):
    tmb: float
    calorias_objetivo: float
    nivel_atividade: str
    fator_atividade: float


# Distribuição de macros schemas
class DistribuicaoMacrosRequest(BaseSchema):
    total_kcal: int = Field(gt=0)
    perc_carb: float = Field(gt=0, le=100)
    perc_prot: float = Field(gt=0, le=100)
    perc_gord: float = Field(gt=0, le=100)
    num_refeicoes_grandes: int = Field(ge=0, le=10)
    num_refeicoes_pequenas: int = Field(ge=0, le=10)


class MacroRefeicao(BaseSchema):
    nome: str
    tipo: str  # "grande" ou "pequena"
    kcal: int
    carboidratos_g: float
    proteinas_g: float
    gorduras_g: float


class DistribuicaoMacrosResponse(BaseSchema):
    total_kcal: int
    total_carboidratos_g: float
    total_proteinas_g: float
    total_gorduras_g: float
    refeicoes: List[MacroRefeicao]


# Response wrappers
class SuccessResponse(BaseSchema):
    success: bool = True
    message: str = "Operação realizada com sucesso"


class ErrorResponse(BaseSchema):
    success: bool = False
    message: str
    detail: Optional[str] = None


class PaginatedResponse(BaseSchema):
    items: List[BaseSchema]
    total: int
    page: int
    size: int
    pages: int