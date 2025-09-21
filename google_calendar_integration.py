"""
Integração com Google Calendar API para sincronização de consultas
Desenvolvido para NutriPro - Sistema de Gestão Nutricional
"""

import os
import pickle
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Escopos necessários para ler E CRIAR eventos do Google Calendar com Meet
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

@dataclass
class CalendarEvent:
    """Representa um evento do Google Calendar"""
    event_id: str
    summary: str
    description: str
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    location: str
    status: str
    calendar_id: str
    meet_link: str = ""  # Link do Google Meet
    
    def to_dict(self) -> Dict:
        """Converte o evento para dicionário"""
        return {
            'event_id': self.event_id,
            'summary': self.summary,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'attendees': self.attendees,
            'location': self.location,
            'status': self.status,
            'calendar_id': self.calendar_id,
            'meet_link': self.meet_link
        }

class GoogleCalendarIntegration:
    """Classe para integração com Google Calendar"""
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.pickle'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.creds = None
        
    def authenticate(self) -> bool:
        """
        Autentica com Google Calendar API
        Retorna True se autenticação foi bem-sucedida
        """
        try:
            # Verifica se já existem credenciais salvas
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # Se não há credenciais válidas disponíveis, inicia o fluxo OAuth
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        print(f"❌ Arquivo {self.credentials_file} não encontrado!")
                        print("📋 Para configurar a integração:")
                        print("1. Acesse: https://console.cloud.google.com/")
                        print("2. Crie um projeto ou selecione um existente")
                        print("3. Ative a Google Calendar API")
                        print("4. Crie credenciais OAuth 2.0")
                        print("5. Baixe o arquivo JSON e renomeie para 'credentials.json'")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Salva as credenciais para a próxima execução
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            # Constrói o serviço da API
            self.service = build('calendar', 'v3', credentials=self.creds)
            print("✅ Autenticação com Google Calendar realizada com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na autenticação: {str(e)}")
            return False
    
    def get_calendars(self) -> List[Dict]:
        """Retorna lista de calendários disponíveis"""
        if not self.service:
            return []
        
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = []
            
            for calendar in calendar_list.get('items', []):
                calendars.append({
                    'id': calendar['id'],
                    'summary': calendar['summary'],
                    'primary': calendar.get('primary', False),
                    'access_role': calendar.get('accessRole', 'reader')
                })
            
            return calendars
            
        except HttpError as error:
            print(f"❌ Erro ao buscar calendários: {error}")
            return []
    
    def get_events(self, calendar_id: str = 'primary', 
                   days_ahead: int = 30, 
                   days_behind: int = 7) -> List[CalendarEvent]:
        """
        Busca eventos do calendário no período especificado
        """
        if not self.service:
            return []
        
        try:
            # Define o período de busca
            now = datetime.utcnow()
            time_min = (now - timedelta(days=days_behind)).isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            # Busca eventos
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            calendar_events = []
            
            for event in events:
                # Processa horário de início
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Converte para datetime
                if 'T' in start:  # Evento com horário específico
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                else:  # Evento de dia inteiro
                    start_dt = datetime.fromisoformat(start)
                    end_dt = datetime.fromisoformat(end)
                
                # Extrai lista de participantes
                attendees = []
                if 'attendees' in event:
                    attendees = [attendee.get('email', '') for attendee in event['attendees']]
                
                # Extrai link do Google Meet
                meet_link = ""
                if 'conferenceData' in event:
                    conference_data = event['conferenceData']
                    if 'entryPoints' in conference_data:
                        for entry_point in conference_data['entryPoints']:
                            if entry_point.get('entryPointType') == 'video':
                                meet_link = entry_point.get('uri', '')
                                break
                
                # Alternativamente, procura por link Meet na descrição ou location
                if not meet_link:
                    description = event.get('description', '')
                    location = event.get('location', '')
                    
                    # Procura patterns de link Meet
                    import re
                    meet_pattern = r'https://meet\.google\.com/[a-z\-]+'
                    
                    meet_match = re.search(meet_pattern, description + ' ' + location)
                    if meet_match:
                        meet_link = meet_match.group()
                
                calendar_event = CalendarEvent(
                    event_id=event['id'],
                    summary=event.get('summary', 'Sem título'),
                    description=event.get('description', ''),
                    start_time=start_dt,
                    end_time=end_dt,
                    attendees=attendees,
                    location=event.get('location', ''),
                    status=event.get('status', 'confirmed'),
                    calendar_id=calendar_id,
                    meet_link=meet_link
                )
                
                calendar_events.append(calendar_event)
            
            return calendar_events
            
        except HttpError as error:
            print(f"❌ Erro ao buscar eventos: {error}")
            return []
    
    def get_nutrition_appointments(self, calendar_id: str = 'primary', 
                                 keywords: List[str] = None) -> List[CalendarEvent]:
        """
        Busca especificamente por consultas de nutrição baseado em palavras-chave
        """
        if keywords is None:
            keywords = [
                'nutrição', 'nutricao', 'consulta', 'atendimento',
                'dieta', 'alimentação', 'alimentacao', 'paciente',
                'avaliação', 'avaliacao', 'retorno', 'acompanhamento'
            ]
        
        all_events = self.get_events(calendar_id)
        nutrition_events = []
        
        for event in all_events:
            # Verifica se alguma palavra-chave está no título ou descrição
            text_to_search = f"{event.summary} {event.description}".lower()
            
            if any(keyword.lower() in text_to_search for keyword in keywords):
                nutrition_events.append(event)
        
        return nutrition_events
    
    def export_events_to_json(self, events: List[CalendarEvent], filename: str = 'calendar_events.json'):
        """Exporta eventos para arquivo JSON"""
        events_data = [event.to_dict() for event in events]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ {len(events)} eventos exportados para {filename}")

    def create_consultation_with_meet(self, 
                                    title: str,
                                    start_datetime: datetime,
                                    end_datetime: datetime,
                                    patient_email: str,
                                    patient_name: str = "",
                                    description: str = "",
                                    calendar_id: str = 'primary') -> Optional[CalendarEvent]:
        """
        Cria uma nova consulta no Google Calendar com Google Meet automático
        """
        if not self.service:
            print("❌ Serviço Google Calendar não disponível")
            return None
        
        try:
            # Configura o evento
            event_body = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'attendees': [
                    {'email': patient_email, 'displayName': patient_name}
                ],
                # CHAVE: Configuração para criar Google Meet automaticamente
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"meet-{int(datetime.now().timestamp())}",
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 dia antes
                        {'method': 'popup', 'minutes': 30},       # 30 min antes
                    ],
                },
            }
            
            # Cria o evento com conferenceDataVersion=1 para ativar Meet
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_body,
                conferenceDataVersion=1,  # IMPORTANTE: ativa Google Meet
                sendUpdates='all'  # Envia convites por email
            ).execute()
            
            print(f"✅ Consulta criada com sucesso!")
            print(f"📧 Convites enviados para: {patient_email}")
            
            # Extrai informações do evento criado
            meet_link = ""
            if 'conferenceData' in created_event:
                conference_data = created_event['conferenceData']
                if 'entryPoints' in conference_data:
                    for entry_point in conference_data['entryPoints']:
                        if entry_point.get('entryPointType') == 'video':
                            meet_link = entry_point.get('uri', '')
                            break
            
            # Retorna objeto CalendarEvent
            calendar_event = CalendarEvent(
                event_id=created_event['id'],
                summary=created_event.get('summary', ''),
                description=created_event.get('description', ''),
                start_time=start_datetime,
                end_time=end_datetime,
                attendees=[patient_email],
                location=created_event.get('location', ''),
                status=created_event.get('status', 'confirmed'),
                calendar_id=calendar_id,
                meet_link=meet_link
            )
            
            print(f"🎥 Google Meet criado: {meet_link}")
            return calendar_event
            
        except HttpError as error:
            print(f"❌ Erro ao criar consulta: {error}")
            return None
    
    def update_event_with_meet(self, event_id: str, calendar_id: str = 'primary') -> bool:
        """
        Adiciona Google Meet a um evento existente
        """
        if not self.service:
            return False
        
        try:
            # Busca o evento existente
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Adiciona configuração do Meet
            event['conferenceData'] = {
                'createRequest': {
                    'requestId': f"meet-update-{int(datetime.now().timestamp())}",
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            }
            
            # Atualiza o evento
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()
            
            print(f"✅ Google Meet adicionado ao evento existente!")
            return True
            
        except HttpError as error:
            print(f"❌ Erro ao adicionar Meet: {error}")
            return False

def setup_instructions():
    """Imprime instruções de configuração"""
    print("🔧 CONFIGURAÇÃO DA INTEGRAÇÃO COM GOOGLE CALENDAR")
    print("=" * 50)
    print("1. Acesse: https://console.cloud.google.com/")
    print("2. Crie um novo projeto ou selecione um existente")
    print("3. Navegue para 'APIs e Serviços' > 'Biblioteca'")
    print("4. Busque por 'Google Calendar API' e ative")
    print("5. Vá para 'APIs e Serviços' > 'Credenciais'")
    print("6. Clique em 'Criar Credenciais' > 'ID do cliente OAuth'")
    print("7. Escolha 'Aplicativo para desktop'")
    print("8. Baixe o arquivo JSON de credenciais")
    print("9. Renomeie para 'credentials.json' e coloque na pasta do projeto")
    print("10. Execute o script para autorizar o acesso")
    print()
    print("💡 DICA: A API do Google Calendar é GRATUITA para uso pessoal!")
    print("   Limite: 1.000.000 de requisições por dia (mais que suficiente)")

if __name__ == "__main__":
    # Exemplo de uso
    setup_instructions()
    print()
    
    # Testa a integração
    calendar_integration = GoogleCalendarIntegration()
    
    if calendar_integration.authenticate():
        print("\n📅 CALENDÁRIOS DISPONÍVEIS:")
        calendars = calendar_integration.get_calendars()
        
        for i, calendar in enumerate(calendars, 1):
            print(f"{i}. {calendar['summary']} ({'Primário' if calendar.get('primary') else 'Secundário'})")
        
        if calendars:
            print("\n🔍 BUSCANDO CONSULTAS DE NUTRIÇÃO...")
            events = calendar_integration.get_nutrition_appointments()
            
            if events:
                print(f"\n✅ Encontradas {len(events)} consultas:")
                for event in events[:5]:  # Mostra apenas as primeiras 5
                    print(f"- {event.summary} | {event.start_time.strftime('%d/%m/%Y %H:%M')}")
                    if event.attendees:
                        print(f"  Participantes: {', '.join(event.attendees)}")
                
                # Exporta para JSON
                calendar_integration.export_events_to_json(events)
            else:
                print("❌ Nenhuma consulta de nutrição encontrada")
    else:
        print("❌ Falha na autenticação")