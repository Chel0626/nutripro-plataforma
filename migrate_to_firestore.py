#!/usr/bin/env python3
"""
Script de Migração SQLite → Firebase Firestore
Desenvolvido para NutriPro - Sistema de Gestão Nutricional
"""

import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Carrega variáveis de ambiente
load_dotenv()

# Importa modelos SQLite
from app import app, db, Paciente, Consulta, Alimento, PlanoAlimentar

def init_firebase():
    """Inicializa Firebase Admin SDK"""
    try:
        firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS')
        if not firebase_credentials_json:
            print("❌ FIREBASE_CREDENTIALS não encontrado no .env")
            return None
        
        cred_dict = json.loads(firebase_credentials_json)
        cred = credentials.Certificate(cred_dict)
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    except Exception as e:
        print(f"❌ Erro ao inicializar Firebase: {e}")
        return None

def migrate_pacientes(db_firestore):
    """Migra pacientes do SQLite para Firestore"""
    print("\n👥 Migrando pacientes...")
    
    try:
        pacientes = Paciente.query.all()
        print(f"📊 Encontrados {len(pacientes)} pacientes para migrar")
        
        batch = db_firestore.batch()
        count = 0
        
        for paciente in pacientes:
            doc_ref = db_firestore.collection('pacientes').document(str(paciente.id))
            
            # Converte dados do paciente
            paciente_data = {
                'id': paciente.id,
                'nome_completo': paciente.nome_completo,
                'email': paciente.email,
                'telefone': paciente.telefone,
                'data_nascimento': paciente.data_nascimento.isoformat() if paciente.data_nascimento else None,
                'peso': float(paciente.peso) if paciente.peso else None,
                'altura_cm': paciente.altura_cm,
                'sexo': paciente.sexo,
                'objetivo': getattr(paciente, 'objetivo', None),
                'nivel_atividade': getattr(paciente, 'nivel_atividade', None),
                'restricoes_alimentares': getattr(paciente, 'restricoes_alimentares', None),
                'observacoes': getattr(paciente, 'observacoes', None),
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            batch.set(doc_ref, paciente_data)
            count += 1
            
            # Commit em lotes de 500 (limite do Firestore)
            if count % 500 == 0:
                batch.commit()
                batch = db_firestore.batch()
                print(f"  ✅ {count} pacientes migrados...")
        
        # Commit final
        if count % 500 != 0:
            batch.commit()
        
        print(f"✅ {count} pacientes migrados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração de pacientes: {e}")
        return False

def migrate_consultas(db_firestore):
    """Migra consultas do SQLite para Firestore"""
    print("\n📅 Migrando consultas...")
    
    try:
        consultas = Consulta.query.all()
        print(f"📊 Encontradas {len(consultas)} consultas para migrar")
        
        batch = db_firestore.batch()
        count = 0
        
        for consulta in consultas:
            doc_ref = db_firestore.collection('consultas').document(str(consulta.id))
            
            # Converte dados da consulta
            consulta_data = {
                'id': consulta.id,
                'paciente_id': consulta.paciente_id,
                'data_hora': consulta.data_hora.isoformat() if consulta.data_hora else None,
                'tipo_consulta': consulta.tipo_consulta,
                'status': consulta.status,
                'observacoes_nutri': consulta.observacoes_nutri,
                'link_videochamada': consulta.link_videochamada,
                'localizacao': consulta.localizacao,
                'data_inicio': consulta.data_inicio.isoformat() if hasattr(consulta, 'data_inicio') and consulta.data_inicio else None,
                'data_finalizacao': consulta.data_finalizacao.isoformat() if hasattr(consulta, 'data_finalizacao') and consulta.data_finalizacao else None,
                'observacoes': consulta.observacoes if hasattr(consulta, 'observacoes') else None,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            batch.set(doc_ref, consulta_data)
            count += 1
            
            if count % 500 == 0:
                batch.commit()
                batch = db_firestore.batch()
                print(f"  ✅ {count} consultas migradas...")
        
        if count % 500 != 0:
            batch.commit()
        
        print(f"✅ {count} consultas migradas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração de consultas: {e}")
        return False

def migrate_alimentos(db_firestore):
    """Migra alimentos do SQLite para Firestore"""
    print("\n🍎 Migrando alimentos...")
    
    try:
        alimentos = Alimento.query.all()
        print(f"📊 Encontrados {len(alimentos)} alimentos para migrar")
        
        batch = db_firestore.batch()
        count = 0
        
        for alimento in alimentos:
            doc_ref = db_firestore.collection('alimentos').document(str(alimento.id))
            
            # Converte dados do alimento
            alimento_data = {
                'id': alimento.id,
                'nome': alimento.nome,
                'marca': alimento.marca,
                'kcal_100g': float(alimento.kcal_100g) if alimento.kcal_100g else 0.0,
                'carboidratos_100g': float(alimento.carboidratos_100g) if alimento.carboidratos_100g else 0.0,
                'proteinas_100g': float(alimento.proteinas_100g) if alimento.proteinas_100g else 0.0,
                'gorduras_100g': float(alimento.gorduras_100g) if alimento.gorduras_100g else 0.0,
                'origem': alimento.origem,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            batch.set(doc_ref, alimento_data)
            count += 1
            
            if count % 500 == 0:
                batch.commit()
                batch = db_firestore.batch()
                print(f"  ✅ {count} alimentos migrados...")
        
        if count % 500 != 0:
            batch.commit()
        
        print(f"✅ {count} alimentos migrados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração de alimentos: {e}")
        return False

def migrate_planos(db_firestore):
    """Migra planos alimentares do SQLite para Firestore"""
    print("\n📋 Migrando planos alimentares...")
    
    try:
        planos = PlanoAlimentar.query.all()
        print(f"📊 Encontrados {len(planos)} planos para migrar")
        
        batch = db_firestore.batch()
        count = 0
        
        for plano in planos:
            doc_ref = db_firestore.collection('planos_alimentares').document(str(plano.id))
            
            # Converte dados do plano
            plano_data = {
                'id': plano.id,
                'paciente_id': plano.paciente_id,
                'titulo': plano.titulo,
                'objetivo': plano.objetivo,
                'calorias_totais': float(plano.calorias_totais) if plano.calorias_totais else 0.0,
                'data_criacao': plano.data_criacao.isoformat() if plano.data_criacao else None,
                'ativo': plano.ativo,
                'observacoes': plano.observacoes,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            batch.set(doc_ref, plano_data)
            count += 1
            
            if count % 500 == 0:
                batch.commit()
                batch = db_firestore.batch()
                print(f"  ✅ {count} planos migrados...")
        
        if count % 500 != 0:
            batch.commit()
        
        print(f"✅ {count} planos alimentares migrados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração de planos: {e}")
        return False

def main():
    """Função principal de migração"""
    print("🔄 Iniciando migração SQLite → Firebase Firestore")
    print("=" * 50)
    
    # Inicializa Firebase
    db_firestore = init_firebase()
    if not db_firestore:
        print("❌ Falha ao conectar com Firebase")
        return False
    
    # Inicializa contexto do Flask/SQLite
    with app.app_context():
        try:
            # Executa migrações
            success = True
            
            success &= migrate_pacientes(db_firestore)
            success &= migrate_consultas(db_firestore)
            success &= migrate_alimentos(db_firestore)
            success &= migrate_planos(db_firestore)
            
            if success:
                print("\n🎉 Migração concluída com sucesso!")
                print("✅ Todos os dados foram migrados para o Firestore")
                print(f"🔗 Firebase Project: {os.getenv('FIREBASE_PROJECT_ID')}")
            else:
                print("\n⚠️ Migração concluída com alguns erros")
                
            return success
            
        except Exception as e:
            print(f"❌ Erro geral na migração: {e}")
            return False

if __name__ == "__main__":
    main()