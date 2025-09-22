"""
Serviço Híbrido: SQLite Local + Firebase Firestore Cloud
Desenvolvido para NutriPro - Sistema de Gestão Nutricional

Este serviço permite usar SQLite para desenvolvimento local
e Firestore para produção/sincronização na nuvem.
"""

import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Carrega variáveis de ambiente
load_dotenv()

class DatabaseService:
    """Serviço de banco de dados híbrido SQLite + Firestore"""
    
    def __init__(self):
        self.use_firestore = self._should_use_firestore()
        self.firestore_db = None
        
        if self.use_firestore:
            self.firestore_db = self._init_firestore()
            
    def _should_use_firestore(self) -> bool:
        """Determina se deve usar Firestore baseado na configuração"""
        firebase_creds = os.getenv('FIREBASE_CREDENTIALS')
        use_firebase = os.getenv('USE_FIREBASE', 'false').lower() == 'true'
        
        return firebase_creds and use_firebase
    
    def _init_firestore(self):
        """Inicializa Firestore se configurado"""
        try:
            firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS')
            if not firebase_credentials_json:
                return None
            
            cred_dict = json.loads(firebase_credentials_json)
            cred = credentials.Certificate(cred_dict)
            
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            
            return firestore.client()
        except Exception as e:
            print(f"⚠️ Erro ao inicializar Firestore: {e}")
            return None
    
    def get_database_info(self) -> Dict[str, Any]:
        """Retorna informações sobre qual banco está sendo usado"""
        return {
            'using_firestore': self.use_firestore,
            'firestore_available': self.firestore_db is not None,
            'project_id': os.getenv('FIREBASE_PROJECT_ID') if self.use_firestore else None,
            'mode': 'cloud' if self.use_firestore else 'local'
        }
    
    # Métodos para Pacientes
    def get_pacientes_firestore(self) -> List[Dict]:
        """Busca pacientes do Firestore"""
        if not self.firestore_db:
            return []
        
        try:
            docs = self.firestore_db.collection('pacientes').stream()
            pacientes = []
            
            for doc in docs:
                data = doc.to_dict()
                data['firestore_id'] = doc.id
                pacientes.append(data)
            
            return pacientes
        except Exception as e:
            print(f"Erro ao buscar pacientes do Firestore: {e}")
            return []
    
    def create_paciente_firestore(self, paciente_data: Dict) -> Optional[str]:
        """Cria paciente no Firestore"""
        if not self.firestore_db:
            return None
        
        try:
            paciente_data['created_at'] = firestore.SERVER_TIMESTAMP
            paciente_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.firestore_db.collection('pacientes').add(paciente_data)
            return doc_ref[1].id  # Retorna o ID do documento
        except Exception as e:
            print(f"Erro ao criar paciente no Firestore: {e}")
            return None
    
    def update_paciente_firestore(self, firestore_id: str, paciente_data: Dict) -> bool:
        """Atualiza paciente no Firestore"""
        if not self.firestore_db:
            return False
        
        try:
            paciente_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            self.firestore_db.collection('pacientes').document(firestore_id).update(paciente_data)
            return True
        except Exception as e:
            print(f"Erro ao atualizar paciente no Firestore: {e}")
            return False
    
    # Métodos para Consultas
    def get_consultas_firestore(self, paciente_id: Optional[int] = None) -> List[Dict]:
        """Busca consultas do Firestore"""
        if not self.firestore_db:
            return []
        
        try:
            query = self.firestore_db.collection('consultas')
            
            if paciente_id:
                query = query.where('paciente_id', '==', paciente_id)
            
            docs = query.stream()
            consultas = []
            
            for doc in docs:
                data = doc.to_dict()
                data['firestore_id'] = doc.id
                consultas.append(data)
            
            return consultas
        except Exception as e:
            print(f"Erro ao buscar consultas do Firestore: {e}")
            return []
    
    def create_consulta_firestore(self, consulta_data: Dict) -> Optional[str]:
        """Cria consulta no Firestore"""
        if not self.firestore_db:
            return None
        
        try:
            consulta_data['created_at'] = firestore.SERVER_TIMESTAMP
            consulta_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.firestore_db.collection('consultas').add(consulta_data)
            return doc_ref[1].id
        except Exception as e:
            print(f"Erro ao criar consulta no Firestore: {e}")
            return None
    
    # Métodos para Alimentos
    def search_alimentos_firestore(self, termo: str, limit: int = 10) -> List[Dict]:
        """Busca alimentos no Firestore"""
        if not self.firestore_db:
            return []
        
        try:
            # Firestore não tem busca full-text nativa, então fazemos uma busca simples
            docs = (self.firestore_db.collection('alimentos')
                   .limit(limit * 3)  # Busca mais para filtrar depois
                   .stream())
            
            alimentos = []
            termo_lower = termo.lower()
            
            for doc in docs:
                data = doc.to_dict()
                nome = data.get('nome', '').lower()
                
                if termo_lower in nome:
                    data['firestore_id'] = doc.id
                    alimentos.append(data)
                    
                    if len(alimentos) >= limit:
                        break
            
            return alimentos
        except Exception as e:
            print(f"Erro ao buscar alimentos no Firestore: {e}")
            return []
    
    def sync_to_firestore(self):
        """Sincroniza dados do SQLite para Firestore"""
        if not self.firestore_db:
            print("⚠️ Firestore não disponível para sincronização")
            return False
        
        try:
            # Importa modelos SQLite
            from app import app, Paciente, Consulta, Alimento
            
            with app.app_context():
                # Sincroniza pacientes
                pacientes = Paciente.query.all()
                for paciente in pacientes:
                    paciente_data = {
                        'id': paciente.id,
                        'nome_completo': paciente.nome_completo,
                        'email': paciente.email,
                        'telefone': paciente.telefone,
                        'peso': float(paciente.peso) if paciente.peso else None,
                        'altura_cm': paciente.altura_cm,
                        'sexo': paciente.sexo
                    }
                    
                    # Verifica se já existe
                    existing = list(self.firestore_db.collection('pacientes').where('id', '==', paciente.id).limit(1).stream())
                    
                    if not existing:
                        self.create_paciente_firestore(paciente_data)
                
                print("✅ Sincronização concluída")
                return True
                
        except Exception as e:
            print(f"❌ Erro na sincronização: {e}")
            return False

# Instância global do serviço
database_service = DatabaseService()