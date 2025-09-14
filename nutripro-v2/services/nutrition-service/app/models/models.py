"""
Database models for Nutrition Service
Converted from Flask-SQLAlchemy to modern SQLAlchemy 2.0 style
"""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class Paciente(Base):
    __tablename__ = "paciente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_completo: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    telefone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    data_nascimento: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    peso: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    altura_cm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sexo: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    observacoes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_cadastro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    planos: Mapped[List["PlanoAlimentar"]] = relationship(
        "PlanoAlimentar", back_populates="paciente", cascade="all, delete-orphan"
    )
    consultas: Mapped[List["Consulta"]] = relationship(
        "Consulta", back_populates="paciente", cascade="all, delete-orphan"
    )


class Consulta(Base):
    __tablename__ = "consulta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    tipo_consulta: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Agendada")
    observacoes_nutri: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    link_videochamada: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("paciente.id"), nullable=False)

    # Relationships
    paciente: Mapped["Paciente"] = relationship("Paciente", back_populates="consultas")


class PlanoAlimentar(Base):
    __tablename__ = "plano_alimentar"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("paciente.id"), nullable=False)
    nome_plano: Mapped[str] = mapped_column(String(150), nullable=False, default="Plano Padrão")
    objetivo_calorico_final: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    orientacoes_diabetes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orientacoes_nutricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )
    ativo: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=True)

    # Relationships
    paciente: Mapped["Paciente"] = relationship("Paciente", back_populates="planos")
    refeicoes: Mapped[List["Refeicao"]] = relationship(
        "Refeicao", back_populates="plano", cascade="all, delete-orphan"
    )


class Refeicao(Base):
    __tablename__ = "refeicao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plano_id: Mapped[int] = mapped_column(Integer, ForeignKey("plano_alimentar.id"), nullable=False)
    nome_refeicao: Mapped[str] = mapped_column(String(100), nullable=False)
    horario_sugerido: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    meta_carboidratos_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    meta_proteinas_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    meta_gorduras_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    plano: Mapped["PlanoAlimentar"] = relationship("PlanoAlimentar", back_populates="refeicoes")
    itens: Mapped[List["ItemRefeicao"]] = relationship(
        "ItemRefeicao", back_populates="refeicao", cascade="all, delete-orphan"
    )


class ItemRefeicao(Base):
    __tablename__ = "item_refeicao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    refeicao_id: Mapped[int] = mapped_column(Integer, ForeignKey("refeicao.id"), nullable=False)
    nome_alimento: Mapped[str] = mapped_column(String(200), nullable=False)
    marca_alimento: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    quantidade_g: Mapped[float] = mapped_column(Float, nullable=False)
    medida_caseira: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    substituicoes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    carboidratos_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    proteinas_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    gorduras_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    kcal: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    refeicao: Mapped["Refeicao"] = relationship("Refeicao", back_populates="itens")


class Alimento(Base):
    __tablename__ = "alimento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    marca: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    kcal_100g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    carboidratos_100g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    proteinas_100g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    gorduras_100g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    origem: Mapped[Optional[str]] = mapped_column(String(50), default="manual")
    source_api_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )