# google_meet_service.py - Serviço para integração com Google Meet
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
from google_calendar_integration import GoogleCalendarIntegration
from firebase_models import Consulta, Paciente

logger = logging.getLogger(__name__)

class GoogleMeetService:
    """Serviço para gerenciar videoconferências do Google Meet"""
    
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.calendar_integration = GoogleCalendarIntegration()
        
    def create_consultation_with_meet(self, 
                                    paciente_id: str,
                                    data_consulta: datetime,
                                    duracao_minutos: int = 60,
                                    observacoes: str = "") -> Optional[Dict]:
        """
        Cria uma nova consulta com Google Meet automático
        """
        try:
            # Busca dados do paciente
            paciente = Paciente.get_by_id(paciente_id)
            if not paciente:
                logger.error(f"Paciente não encontrado: {paciente_id}")
                return None
            
            if not paciente.email:
                logger.error(f"Paciente sem email: {paciente.nome}")
                return None
            
            # Calcula horário de fim
            end_datetime = data_consulta + timedelta(minutes=duracao_minutos)
            
            # Cria título personalizado
            title = f"Consulta Nutricional - {paciente.nome}"
            
            # Cria descrição
            description = f"""
📋 CONSULTA NUTRICIONAL

👤 Paciente: {paciente.nome}
📧 Email: {paciente.email}
📞 Telefone: {paciente.telefone}
🎯 Objetivo: {paciente.objetivo}

📝 Observações: {observacoes}

---
🥗 Sistema NutriPro
🎥 Videoconferência via Google Meet
            """.strip()
            
            # Autentica no Google Calendar
            if not self.calendar_integration.authenticate():
                logger.error("Falha na autenticação do Google Calendar")
                return None
            
            # Cria evento com Meet no Google Calendar
            calendar_event = self.calendar_integration.create_consultation_with_meet(
                title=title,
                start_datetime=data_consulta,
                end_datetime=end_datetime,
                patient_email=paciente.email,
                patient_name=paciente.nome,
                description=description
            )
            
            if not calendar_event:
                logger.error("Falha ao criar evento no Google Calendar")
                return None
            
            # Cria consulta no Firebase
            consulta = Consulta(
                paciente_id=paciente_id,
                data_consulta=data_consulta,
                observacoes=observacoes,
                status='agendada',
                google_event_id=calendar_event.event_id,
                google_calendar_id=calendar_event.calendar_id,
                origem='sistema',
                email_paciente_gc=paciente.email,
                nome_paciente_gc=paciente.nome,
                telefone_paciente_gc=paciente.telefone,
                meet_link=calendar_event.meet_link,
                meet_criado=True,
                sincronizado_em=datetime.utcnow()
            )
            
            consulta_id = consulta.save()
            
            if consulta_id:
                logger.info(f"✅ Consulta criada com Meet: {calendar_event.meet_link}")
                return {
                    'consulta_id': consulta_id,
                    'calendar_event_id': calendar_event.event_id,
                    'meet_link': calendar_event.meet_link,
                    'paciente_nome': paciente.nome,
                    'paciente_email': paciente.email,
                    'data_consulta': data_consulta,
                    'duracao_minutos': duracao_minutos
                }
            else:
                logger.error("Falha ao salvar consulta no Firebase")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao criar consulta com Meet: {e}")
            return None
    
    def add_meet_to_existing_consultation(self, consulta_id: str) -> bool:
        """
        Adiciona Google Meet a uma consulta existente
        """
        try:
            # Busca consulta
            consulta = Consulta.get_by_id(consulta_id)
            if not consulta:
                logger.error(f"Consulta não encontrada: {consulta_id}")
                return False
            
            # Verifica se já tem Meet
            if consulta.meet_link:
                logger.info(f"Consulta já possui Meet: {consulta.meet_link}")
                return True
            
            # Autentica no Google Calendar
            if not self.calendar_integration.authenticate():
                logger.error("Falha na autenticação do Google Calendar")
                return False
            
            # Se tem evento no Google Calendar, adiciona Meet
            if consulta.google_event_id:
                success = self.calendar_integration.update_event_with_meet(
                    event_id=consulta.google_event_id,
                    calendar_id=consulta.google_calendar_id or 'primary'
                )
                
                if success:
                    # Busca o evento atualizado para pegar o link do Meet
                    events = self.calendar_integration.get_events()
                    for event in events:
                        if event.event_id == consulta.google_event_id:
                            # Atualiza consulta com link do Meet
                            consulta.meet_link = event.meet_link
                            consulta.meet_criado = True
                            consulta.save()
                            
                            logger.info(f"✅ Meet adicionado: {event.meet_link}")
                            return True
                
                return False
            else:
                # Se não tem evento no Calendar, cria um novo
                paciente = Paciente.get_by_id(consulta.paciente_id)
                if not paciente or not paciente.email:
                    logger.error("Paciente sem email para criar evento")
                    return False
                
                # Calcula horários (default 1 hora)
                start_time = consulta.data_consulta
                end_time = start_time + timedelta(hours=1)
                
                calendar_event = self.calendar_integration.create_consultation_with_meet(
                    title=f"Consulta Nutricional - {paciente.nome}",
                    start_datetime=start_time,
                    end_datetime=end_time,
                    patient_email=paciente.email,
                    patient_name=paciente.nome,
                    description=f"Consulta criada pelo sistema NutriPro\nObservações: {consulta.observacoes}"
                )
                
                if calendar_event:
                    # Atualiza consulta
                    consulta.google_event_id = calendar_event.event_id
                    consulta.google_calendar_id = calendar_event.calendar_id
                    consulta.meet_link = calendar_event.meet_link
                    consulta.meet_criado = True
                    consulta.origem = 'sistema'
                    consulta.save()
                    
                    logger.info(f"✅ Evento e Meet criados: {calendar_event.meet_link}")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Erro ao adicionar Meet: {e}")
            return False
    
    def get_upcoming_consultations_with_meet(self, days_ahead: int = 7) -> List[Dict]:
        """
        Busca consultas próximas que possuem Google Meet
        """
        try:
            # Data limite
            limite = datetime.utcnow() + timedelta(days=days_ahead)
            
            # Busca consultas
            consultas = Consulta.get_all(
                where=[
                    ('data_consulta', '>=', datetime.utcnow()),
                    ('data_consulta', '<=', limite),
                    ('meet_link', '!=', '')
                ],
                order_by='data_consulta'
            )
            
            results = []
            for consulta in consultas:
                # Busca dados do paciente
                paciente = Paciente.get_by_id(consulta.paciente_id) if consulta.paciente_id else None
                
                results.append({
                    'consulta_id': consulta.id,
                    'paciente_nome': paciente.nome if paciente else consulta.nome_paciente_gc,
                    'paciente_email': paciente.email if paciente else consulta.email_paciente_gc,
                    'data_consulta': consulta.data_consulta,
                    'meet_link': consulta.meet_link,
                    'status': consulta.status,
                    'observacoes': consulta.observacoes
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao buscar consultas com Meet: {e}")
            return []
    
    def generate_meet_statistics(self) -> Dict:
        """
        Gera estatísticas de uso do Google Meet
        """
        try:
            # Busca todas as consultas
            all_consultas = Consulta.get_all()
            
            total_consultas = len(all_consultas)
            consultas_com_meet = len([c for c in all_consultas if c.meet_link])
            consultas_sem_meet = total_consultas - consultas_com_meet
            
            # Consultas nos próximos 30 dias
            limite = datetime.utcnow() + timedelta(days=30)
            proximas_consultas = [
                c for c in all_consultas 
                if c.data_consulta >= datetime.utcnow() and c.data_consulta <= limite
            ]
            proximas_com_meet = len([c for c in proximas_consultas if c.meet_link])
            
            return {
                'total_consultas': total_consultas,
                'consultas_com_meet': consultas_com_meet,
                'consultas_sem_meet': consultas_sem_meet,
                'percentual_meet': round((consultas_com_meet / total_consultas * 100) if total_consultas > 0 else 0, 1),
                'proximas_30_dias': len(proximas_consultas),
                'proximas_com_meet': proximas_com_meet,
                'meet_coverage_futuro': round((proximas_com_meet / len(proximas_consultas) * 100) if proximas_consultas else 0, 1)
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas: {e}")
            return {}

# Instância global do serviço
meet_service = GoogleMeetService()

def get_meet_service():
    """Retorna a instância do Google Meet Service"""
    return meet_service