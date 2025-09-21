# firebase_config.py - Configuração e utilitários para Firebase
import os
import json
from typing import Dict, List, Optional, Any
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FirebaseConfig:
    """Configuração e gerenciamento do Firebase Firestore"""
    
    def __init__(self):
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Inicializa a conexão com Firebase"""
        try:
            # Verifica se já foi inicializado
            if firebase_admin._apps:
                self.db = firestore.client()
                return
            
            # Tenta usar credenciais do ambiente (para Vercel)
            firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
            if firebase_creds:
                # Parse das credenciais JSON do ambiente
                cred_dict = json.loads(firebase_creds)
                cred = credentials.Certificate(cred_dict)
            else:
                # Fallback para arquivo local (desenvolvimento)
                cred_path = 'firebase-credentials.json'
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                else:
                    logger.warning("⚠️ Firebase não configurado - usando modo simulação")
                    self.db = None
                    return
            
            # Inicializa Firebase
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            logger.info("✅ Firebase inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Firebase: {e}")
            self.db = None
    
    def is_connected(self) -> bool:
        """Verifica se está conectado ao Firebase"""
        return self.db is not None
    
    # CRUD Operations
    def create_document(self, collection: str, doc_id: str = None, data: Dict = None) -> str:
        """Cria um documento no Firestore"""
        if not self.is_connected():
            logger.warning("Firebase não conectado - operação ignorada")
            return "fake_id"
        
        try:
            if doc_id:
                doc_ref = self.db.collection(collection).document(doc_id)
                doc_ref.set(data)
                return doc_id
            else:
                doc_ref = self.db.collection(collection).add(data)
                return doc_ref[1].id
        except Exception as e:
            logger.error(f"Erro ao criar documento: {e}")
            return None
    
    def get_document(self, collection: str, doc_id: str) -> Optional[Dict]:
        """Recupera um documento do Firestore"""
        if not self.is_connected():
            return None
        
        try:
            doc = self.db.collection(collection).document(doc_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar documento: {e}")
            return None
    
    def update_document(self, collection: str, doc_id: str, data: Dict) -> bool:
        """Atualiza um documento no Firestore"""
        if not self.is_connected():
            return False
        
        try:
            self.db.collection(collection).document(doc_id).update(data)
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar documento: {e}")
            return False
    
    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Deleta um documento do Firestore"""
        if not self.is_connected():
            return False
        
        try:
            self.db.collection(collection).document(doc_id).delete()
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar documento: {e}")
            return False
    
    def get_collection(self, collection: str, where: List = None, order_by: str = None, limit: int = None) -> List[Dict]:
        """Recupera múltiplos documentos de uma coleção"""
        if not self.is_connected():
            return []
        
        try:
            query = self.db.collection(collection)
            
            # Adiciona filtros WHERE
            if where:
                for condition in where:
                    query = query.where(condition[0], condition[1], condition[2])
            
            # Adiciona ordenação
            if order_by:
                query = query.order_by(order_by)
            
            # Adiciona limite
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
        except Exception as e:
            logger.error(f"Erro ao buscar coleção: {e}")
            return []
    
    def search_documents(self, collection: str, field: str, search_term: str) -> List[Dict]:
        """Busca documentos por termo (busca aproximada)"""
        if not self.is_connected():
            return []
        
        try:
            # Firestore não tem busca full-text nativa, então fazemos busca por prefixo
            docs = self.db.collection(collection).where(
                field, '>=', search_term
            ).where(
                field, '<=', search_term + '\uf8ff'
            ).stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []

# Instância global do Firebase
firebase_config = FirebaseConfig()

# Funções de conveniência
def get_firebase_db():
    """Retorna a instância do Firebase"""
    return firebase_config

def add_timestamps(data: Dict) -> Dict:
    """Adiciona timestamps de criação/atualização"""
    now = datetime.utcnow()
    data['created_at'] = now
    data['updated_at'] = now
    return data

def update_timestamp(data: Dict) -> Dict:
    """Atualiza timestamp de modificação"""
    data['updated_at'] = datetime.utcnow()
    return data