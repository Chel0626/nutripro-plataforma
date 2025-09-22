#!/usr/bin/env python3
"""
Teste de conexão Firebase Firestore
Desenvolvido para NutriPro - Sistema de Gestão Nutricional
"""

import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Carrega variáveis de ambiente
load_dotenv()

def test_firebase_connection():
    """Testa conexão com Firebase Firestore"""
    
    try:
        print("🔥 Testando conexão Firebase...")
        
        # Carrega credenciais do .env
        firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS')
        if not firebase_credentials_json:
            print("❌ FIREBASE_CREDENTIALS não encontrado no .env")
            return False
        
        # Parse das credenciais JSON
        cred_dict = json.loads(firebase_credentials_json)
        cred = credentials.Certificate(cred_dict)
        
        # Inicializa Firebase (se já não foi inicializado)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        # Conecta ao Firestore
        db = firestore.client()
        
        # Teste básico: escrever e ler um documento
        print("📝 Testando escrita no Firestore...")
        
        # Cria documento de teste
        test_data = {
            'teste': True,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'message': 'Teste de conexão NutriPro'
        }
        
        # Escreve no Firestore
        doc_ref = db.collection('teste_conexao').document('teste_nutripro')
        doc_ref.set(test_data)
        
        print("✅ Escrita realizada com sucesso!")
        
        # Lê do Firestore
        print("📖 Testando leitura do Firestore...")
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            print("✅ Leitura realizada com sucesso!")
            print(f"📊 Dados lidos: {data}")
        else:
            print("❌ Documento não encontrado")
            return False
        
        # Remove documento de teste
        doc_ref.delete()
        print("🗑️ Documento de teste removido")
        
        print("\n🎉 Firebase Firestore configurado e funcionando perfeitamente!")
        print(f"🔗 Project ID: {cred_dict.get('project_id')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão Firebase: {str(e)}")
        return False

if __name__ == "__main__":
    test_firebase_connection()