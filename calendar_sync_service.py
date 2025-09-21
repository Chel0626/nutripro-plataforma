"""
Serviço de Sincronização com Google Calendar
Integra eventos do Google Calendar com consultas no banco de dados
"""

import re
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from google_calendar_integration import GoogleCalendarIntegration, CalendarEvent

class CalendarSyncService:
    """Serviço para sincronizar eventos do Google Calendar com consultas"""
    
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.calendar_integration = GoogleCalendarIntegration()
        
        # Palavras-chave para identificar consultas de nutrição
        self.nutrition_keywords = [
            'nutrição', 'nutricao', 'consulta', 'atendimento', 'paciente',
            'dieta', 'alimentação', 'alimentacao', 'avaliação', 'avaliacao',
            'retorno', 'acompanhamento', 'orientação', 'orientacao'
        ]
        
        # Padrões regex para extrair informações
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}')
    
    def authenticate_calendar(self) -> bool:
        """Autentica com Google Calendar"""
        return self.calendar_integration.authenticate()
    
    def get_available_calendars(self) -> List[Dict]:
        """Retorna calendários disponíveis"""
        return self.calendar_integration.get_calendars()
    
    def extract_patient_info(self, event: CalendarEvent) -> Dict[str, str]:
        """
        Extrai informações do paciente do evento
        Procura por email, telefone e nome nas descrições e participantes
        """
        info = {
            'email': '',
            'nome': '',
            'telefone': ''
        }
        
        # Busca email nos participantes
        if event.attendees:
            for email in event.attendees:
                if email and '@' in email:
                    info['email'] = email
                    # Tenta extrair nome do email
                    if not info['nome']:
                        name_part = email.split('@')[0]
                        info['nome'] = name_part.replace('.', ' ').replace('_', ' ').title()
                    break
        
        # Busca informações na descrição
        description = event.description or ''
        
        # Busca email na descrição
        if not info['email']:
            emails = self.email_pattern.findall(description)
            if emails:
                info['email'] = emails[0]
        
        # Busca telefone na descrição
        phones = self.phone_pattern.findall(description)
        if phones:
            info['telefone'] = phones[0]
        
        # Se não encontrou nome, usa o título do evento
        if not info['nome']:
            # Remove palavras-chave comuns do título para tentar extrair o nome
            title = event.summary
            for keyword in ['consulta', 'atendimento', 'nutrição', 'nutricao', 'retorno']:
                title = re.sub(f'\\b{keyword}\\b', '', title, flags=re.IGNORECASE)
            
            # Limpa e capitaliza
            title = title.strip(' -')
            if title and len(title) > 2:
                info['nome'] = title.title()
        
        return info
    
    def find_matching_patient(self, patient_info: Dict[str, str]):
        """
        Tenta encontrar um paciente existente baseado nas informações extraídas
        """
        if not self.app:
            return None
            
        with self.app.app_context():
            from app import Paciente
            
            # Busca por email exato
            if patient_info['email']:
                patient = Paciente.query.filter_by(email=patient_info['email']).first()
                if patient:
                    return patient
            
            # Busca por telefone
            if patient_info['telefone']:
                # Remove formatação do telefone para comparação
                clean_phone = re.sub(r'[^\d]', '', patient_info['telefone'])
                patients = Paciente.query.all()
                
                for patient in patients:
                    if patient.telefone:
                        patient_clean_phone = re.sub(r'[^\d]', '', patient.telefone)
                        if clean_phone[-8:] == patient_clean_phone[-8:]:  # Compara últimos 8 dígitos
                            return patient
            
            # Busca por nome similar
            if patient_info['nome'] and len(patient_info['nome']) > 3:
                patients = Paciente.query.filter(
                    Paciente.nome_completo.ilike(f"%{patient_info['nome']}%")
                ).all()
                
                if len(patients) == 1:  # Apenas se encontrar exatamente um
                    return patients[0]
        
        return None
    
    def is_nutrition_appointment(self, event: CalendarEvent) -> bool:
        """Verifica se o evento é uma consulta de nutrição"""
        text_to_search = f"{event.summary} {event.description}".lower()
        return any(keyword.lower() in text_to_search for keyword in self.nutrition_keywords)
    
    def sync_calendar_events(self, calendar_id: str = 'primary', 
                           days_ahead: int = 30, 
                           days_behind: int = 7) -> Dict[str, int]:
        """
        Sincroniza eventos do Google Calendar com consultas no banco
        """
        if not self.app or not self.db:
            raise ValueError("App e DB devem ser configurados")
        
        stats = {
            'total_events': 0,
            'nutrition_events': 0,
            'new_consultations': 0,
            'updated_consultations': 0,
            'matched_patients': 0,
            'unmatched_events': 0
        }
        
        # Busca eventos do Google Calendar
        events = self.calendar_integration.get_events(calendar_id, days_ahead, days_behind)
        stats['total_events'] = len(events)
        
        if not events:
            return stats
        
        with self.app.app_context():
            from app import Consulta, Paciente
            
            for event in events:
                # Verifica se é consulta de nutrição
                if not self.is_nutrition_appointment(event):
                    continue
                
                stats['nutrition_events'] += 1
                
                # Extrai informações do paciente
                patient_info = self.extract_patient_info(event)
                
                # Verifica se já existe consulta para este evento
                existing_consultation = Consulta.query.filter_by(
                    google_event_id=event.event_id
                ).first()
                
                if existing_consultation:
                    # Atualiza consulta existente
                    existing_consultation.data_hora = event.start_time.replace(tzinfo=timezone.utc)
                    existing_consultation.data_fim = event.end_time.replace(tzinfo=timezone.utc)
                    existing_consultation.tipo_consulta = event.summary
                    existing_consultation.localizacao = event.location
                    existing_consultation.sincronizado_em = datetime.now(timezone.utc)
                    existing_consultation.status = 'Confirmada' if event.status == 'confirmed' else 'Agendada'
                    
                    # Atualiza informações do paciente se disponíveis
                    if patient_info['email']:
                        existing_consultation.email_paciente_gc = patient_info['email']
                    if patient_info['nome']:
                        existing_consultation.nome_paciente_gc = patient_info['nome']
                    if patient_info['telefone']:
                        existing_consultation.telefone_paciente_gc = patient_info['telefone']
                    
                    stats['updated_consultations'] += 1
                    
                else:
                    # Tenta encontrar paciente correspondente
                    matched_patient = self.find_matching_patient(patient_info)
                    
                    # Cria nova consulta
                    new_consultation = Consulta(
                        data_hora=event.start_time.replace(tzinfo=timezone.utc),
                        data_fim=event.end_time.replace(tzinfo=timezone.utc),
                        tipo_consulta=event.summary,
                        status='Confirmada' if event.status == 'confirmed' else 'Agendada',
                        localizacao=event.location,
                        google_event_id=event.event_id,
                        google_calendar_id=calendar_id,
                        sincronizado_em=datetime.now(timezone.utc),
                        origem='GoogleCalendar',
                        email_paciente_gc=patient_info['email'],
                        nome_paciente_gc=patient_info['nome'],
                        telefone_paciente_gc=patient_info['telefone'],
                        paciente_id=matched_patient.id if matched_patient else None
                    )
                    
                    self.db.session.add(new_consultation)
                    stats['new_consultations'] += 1
                    
                    if matched_patient:
                        stats['matched_patients'] += 1
                    else:
                        stats['unmatched_events'] += 1
            
            # Salva todas as mudanças
            self.db.session.commit()
        
        return stats
    
    def get_unmatched_consultations(self) -> List:
        """Retorna consultas que não foram associadas a pacientes"""
        if not self.app:
            return []
            
        with self.app.app_context():
            from app import Consulta
            return Consulta.query.filter(
                Consulta.paciente_id.is_(None),
                Consulta.origem == 'GoogleCalendar'
            ).all()
    
    def match_consultation_to_patient(self, consultation_id: int, patient_id: int) -> bool:
        """Associa manualmente uma consulta a um paciente"""
        if not self.app or not self.db:
            return False
            
        with self.app.app_context():
            from app import Consulta, Paciente
            
            consultation = Consulta.query.get(consultation_id)
            patient = Paciente.query.get(patient_id)
            
            if consultation and patient:
                consultation.paciente_id = patient_id
                self.db.session.commit()
                return True
        
        return False
    
    def create_patient_from_consultation(self, consultation_id: int) -> Optional[int]:
        """Cria um novo paciente baseado nas informações da consulta"""
        if not self.app or not self.db:
            return None
            
        with self.app.app_context():
            from app import Consulta, Paciente
            
            consultation = Consulta.query.get(consultation_id)
            if not consultation or not consultation.nome_paciente_gc:
                return None
            
            # Cria novo paciente
            new_patient = Paciente(
                nome_completo=consultation.nome_paciente_gc,
                email=consultation.email_paciente_gc,
                telefone=consultation.telefone_paciente_gc
            )
            
            self.db.session.add(new_patient)
            self.db.session.flush()  # Para obter o ID
            
            # Associa a consulta ao novo paciente
            consultation.paciente_id = new_patient.id
            self.db.session.commit()
            
            return new_patient.id