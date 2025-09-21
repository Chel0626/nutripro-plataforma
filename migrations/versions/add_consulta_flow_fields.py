"""Adiciona campos de controle de fluxo da consulta

Revision ID: add_consulta_flow_fields
Revises: 
Create Date: 2024-12-19 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_consulta_flow_fields'
down_revision = 'fcb076b0fd98'  # ID da migração anterior
branch_labels = None
depends_on = None


def upgrade():
    # Adiciona novos campos à tabela consulta
    with op.batch_alter_table('consulta', schema=None) as batch_op:
        batch_op.add_column(sa.Column('data_inicio', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('data_finalizacao', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('observacoes', sa.Text(), nullable=True))


def downgrade():
    # Remove os campos adicionados
    with op.batch_alter_table('consulta', schema=None) as batch_op:
        batch_op.drop_column('observacoes')
        batch_op.drop_column('data_finalizacao')
        batch_op.drop_column('data_inicio')