# firebase_models.py - Modelos adaptados para Firebase
from typing import Dict, List, Optional, Any
from datetime import datetime
from firebase_config import get_firebase_db, add_timestamps, update_timestamp
import logging

logger = logging.getLogger(__name__)

class FirebaseModel:
    """Classe base para modelos Firebase"""
    collection_name = None
    
    def __init__(self, **kwargs):
        self.db = get_firebase_db()
        self.id = kwargs.get('id')
        self._data = kwargs
    
    def to_dict(self) -> Dict:
        """Converte o modelo para dicionário"""
        return self._data.copy()
    
    def save(self) -> str:
        """Salva o modelo no Firebase"""
        data = self.to_dict()
        
        if self.id:
            # Atualização
            data = update_timestamp(data)
            data.pop('id', None)  # Remove ID dos dados
            success = self.db.update_document(self.collection_name, self.id, data)
            return self.id if success else None
        else:
            # Criação
            data = add_timestamps(data)
            doc_id = self.db.create_document(self.collection_name, data=data)
            self.id = doc_id
            return doc_id
    
    def delete(self) -> bool:
        """Deleta o modelo do Firebase"""
        if not self.id:
            return False
        return self.db.delete_document(self.collection_name, self.id)
    
    @classmethod
    def get_by_id(cls, doc_id: str):
        """Busca um documento por ID"""
        db = get_firebase_db()
        data = db.get_document(cls.collection_name, doc_id)
        if data:
            return cls(**data)
        return None
    
    @classmethod
    def get_all(cls, where: List = None, order_by: str = None, limit: int = None):
        """Busca múltiplos documentos"""
        db = get_firebase_db()
        docs = db.get_collection(cls.collection_name, where, order_by, limit)
        return [cls(**doc) for doc in docs]
    
    @classmethod
    def search(cls, field: str, search_term: str):
        """Busca documentos por termo"""
        db = get_firebase_db()
        docs = db.search_documents(cls.collection_name, field, search_term)
        return [cls(**doc) for doc in docs]

class Paciente(FirebaseModel):
    """Modelo Paciente para Firebase"""
    collection_name = 'pacientes'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nome = kwargs.get('nome', '')
        self.email = kwargs.get('email', '')
        self.telefone = kwargs.get('telefone', '')
        self.data_nascimento = kwargs.get('data_nascimento')
        self.sexo = kwargs.get('sexo', '')
        self.altura = kwargs.get('altura', 0.0)
        self.peso_atual = kwargs.get('peso_atual', 0.0)
        self.peso_meta = kwargs.get('peso_meta', 0.0)
        self.nivel_atividade = kwargs.get('nivel_atividade', '')
        self.objetivo = kwargs.get('objetivo', '')
        self.observacoes = kwargs.get('observacoes', '')
        self.ativo = kwargs.get('ativo', True)
    
    def to_dict(self) -> Dict:
        return {
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'data_nascimento': self.data_nascimento,
            'sexo': self.sexo,
            'altura': self.altura,
            'peso_atual': self.peso_atual,
            'peso_meta': self.peso_meta,
            'nivel_atividade': self.nivel_atividade,
            'objetivo': self.objetivo,
            'observacoes': self.observacoes,
            'ativo': self.ativo
        }

class Alimento(FirebaseModel):
    """Modelo Alimento para Firebase"""
    collection_name = 'alimentos'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nome = kwargs.get('nome', '')
        self.categoria = kwargs.get('categoria', '')
        self.energia = kwargs.get('energia', 0.0)
        self.proteina = kwargs.get('proteina', 0.0)
        self.lipidios = kwargs.get('lipidios', 0.0)
        self.carboidrato = kwargs.get('carboidrato', 0.0)
        self.fibra = kwargs.get('fibra', 0.0)
        self.origem = kwargs.get('origem', 'TACO')
        self.unidade = kwargs.get('unidade', 'g')
    
    def to_dict(self) -> Dict:
        return {
            'nome': self.nome,
            'categoria': self.categoria,
            'energia': self.energia,
            'proteina': self.proteina,
            'lipidios': self.lipidios,
            'carboidrato': self.carboidrato,
            'fibra': self.fibra,
            'origem': self.origem,
            'unidade': self.unidade
        }

class Consulta(FirebaseModel):
    """Modelo Consulta para Firebase"""
    collection_name = 'consultas'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.paciente_id = kwargs.get('paciente_id', '')
        self.data_consulta = kwargs.get('data_consulta')
        self.peso_atual = kwargs.get('peso_atual', 0.0)
        self.observacoes = kwargs.get('observacoes', '')
        self.status = kwargs.get('status', 'agendada')
        
        # Campos do Google Calendar
        self.google_event_id = kwargs.get('google_event_id', '')
        self.google_calendar_id = kwargs.get('google_calendar_id', '')
        self.sincronizado_em = kwargs.get('sincronizado_em')
        self.origem = kwargs.get('origem', 'manual')
        self.email_paciente_gc = kwargs.get('email_paciente_gc', '')
        self.nome_paciente_gc = kwargs.get('nome_paciente_gc', '')
        self.telefone_paciente_gc = kwargs.get('telefone_paciente_gc', '')
        
        # Campos do Google Meet
        self.meet_link = kwargs.get('meet_link', '')
        self.meet_criado = kwargs.get('meet_criado', False)
    
    def to_dict(self) -> Dict:
        return {
            'paciente_id': self.paciente_id,
            'data_consulta': self.data_consulta,
            'peso_atual': self.peso_atual,
            'observacoes': self.observacoes,
            'status': self.status,
            'google_event_id': self.google_event_id,
            'google_calendar_id': self.google_calendar_id,
            'sincronizado_em': self.sincronizado_em,
            'origem': self.origem,
            'email_paciente_gc': self.email_paciente_gc,
            'nome_paciente_gc': self.nome_paciente_gc,
            'telefone_paciente_gc': self.telefone_paciente_gc,
            'meet_link': self.meet_link,
            'meet_criado': self.meet_criado
        }

class PlanoAlimentar(FirebaseModel):
    """Modelo Plano Alimentar para Firebase"""
    collection_name = 'planos_alimentares'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.paciente_id = kwargs.get('paciente_id', '')
        self.consulta_id = kwargs.get('consulta_id', '')
        self.nome = kwargs.get('nome', '')
        self.descricao = kwargs.get('descricao', '')
        self.calorias_totais = kwargs.get('calorias_totais', 0.0)
        self.proteinas_totais = kwargs.get('proteinas_totais', 0.0)
        self.carboidratos_totais = kwargs.get('carboidratos_totais', 0.0)
        self.gorduras_totais = kwargs.get('gorduras_totais', 0.0)
        self.refeicoes = kwargs.get('refeicoes', [])
        self.ativo = kwargs.get('ativo', True)
        self.data_inicio = kwargs.get('data_inicio')
        self.data_fim = kwargs.get('data_fim')
    
    def to_dict(self) -> Dict:
        return {
            'paciente_id': self.paciente_id,
            'consulta_id': self.consulta_id,
            'nome': self.nome,
            'descricao': self.descricao,
            'calorias_totais': self.calorias_totais,
            'proteinas_totais': self.proteinas_totais,
            'carboidratos_totais': self.carboidratos_totais,
            'gorduras_totais': self.gorduras_totais,
            'refeicoes': self.refeicoes,
            'ativo': self.ativo,
            'data_inicio': self.data_inicio,
            'data_fim': self.data_fim
        }

# Funções de migração e utilidades
def migrate_taco_data_to_firebase():
    """Migra dados TACO para Firebase"""
    try:
        from taco_data import DADOS_TACO
        
        for item in DADOS_TACO:
            alimento = Alimento(
                nome=item.get('nome', ''),
                categoria=item.get('categoria', ''),
                energia=item.get('energia', 0.0),
                proteina=item.get('proteina', 0.0),
                lipidios=item.get('lipidios', 0.0),
                carboidrato=item.get('carboidrato', 0.0),
                fibra=item.get('fibra', 0.0),
                origem='TACO'
            )
            alimento.save()
        
        logger.info(f"✅ Migração TACO concluída: {len(DADOS_TACO)} alimentos")
        
    except Exception as e:
        logger.error(f"❌ Erro na migração TACO: {e}")

def check_firebase_connection():
    """Verifica se Firebase está conectado"""
    db = get_firebase_db()
    if db.is_connected():
        logger.info("✅ Firebase conectado e funcionando")
        return True
    else:
        logger.warning("⚠️ Firebase não conectado - usando modo local")
        return False