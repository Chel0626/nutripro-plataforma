# dashboard_service.py - Serviço para o dashboard renovado centrado no fluxo diário
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class DashboardService:
    """Serviço para o dashboard centrado no fluxo diário da nutricionista"""
    
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
    
    def get_today_overview(self) -> Dict:
        """
        Retorna overview completo do dia atual
        """
        try:
            hoje = datetime.now().date()
            agora = datetime.now()
            
            # Busca consultas de hoje
            consultas_hoje = self._get_consultas_hoje()
            
            # Separa por status
            proximas = []
            em_andamento = []
            finalizadas = []
            atrasadas = []
            
            for consulta in consultas_hoje:
                # Verifica status baseado nos campos do banco e horário
                if consulta.status and consulta.status.lower() in ['finalizada', 'concluida']:
                    finalizadas.append(consulta)
                elif hasattr(consulta, 'data_inicio') and consulta.data_inicio and not (hasattr(consulta, 'data_finalizacao') and consulta.data_finalizacao):
                    # Consulta iniciada mas não finalizada = em andamento
                    em_andamento.append(consulta)
                elif consulta.data_hora <= agora and not (hasattr(consulta, 'data_inicio') and consulta.data_inicio):
                    # Horário passou mas não foi iniciada = atrasada
                    atrasadas.append(consulta)
                else:
                    # Futuras ou presentes não iniciadas = próximas
                    proximas.append(consulta)
            
            # Calcula estatísticas
            total_consultas = len(consultas_hoje)
            com_meet = len([c for c in consultas_hoje if getattr(c, 'link_videochamada', None)])
            receita_estimada = total_consultas * 150  # Valor médio estimado
            
            return {
                'data': hoje,
                'total_consultas': total_consultas,
                'consultas_com_meet': com_meet,
                'receita_estimada': receita_estimada,
                'proximas': self._enrich_consultas(proximas),
                'em_andamento': self._enrich_consultas(em_andamento),
                'finalizadas': self._enrich_consultas(finalizadas),
                'atrasadas': self._enrich_consultas(atrasadas),
                'stats': {
                    'taxa_meet': round((com_meet / total_consultas * 100) if total_consultas > 0 else 0, 1),
                    'taxa_finalizacao': round((len(finalizadas) / total_consultas * 100) if total_consultas > 0 else 0, 1),
                    'consultas_restantes': len(proximas) + len(atrasadas),
                    'tempo_medio_consulta': 60  # minutos
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar overview do dia: {e}")
            return self._get_empty_overview()
    
    def get_proximas_horas_overview(self, horas: int = 3) -> List[Dict]:
        """
        Retorna consultas das próximas N horas com detalhes ricos
        """
        try:
            agora = datetime.now()
            limite = agora + timedelta(hours=horas)
            
            # Importa aqui para evitar dependência circular
            with self.app.app_context():
                from app import Consulta, Paciente
                
                # Busca consultas no período
                consultas = self.db.session.query(Consulta).join(Paciente, Consulta.paciente_id == Paciente.id, isouter=True)\
                    .filter(Consulta.data_hora >= agora)\
                    .filter(Consulta.data_hora <= limite)\
                    .filter(Consulta.status != 'cancelada')\
                    .order_by(Consulta.data_hora)\
                    .all()
            
            return self._enrich_consultas(consultas)
            
        except Exception as e:
            logger.error(f"Erro ao buscar próximas consultas: {e}")
            return []
    
    def get_consultation_room_data(self, consulta_id: str) -> Optional[Dict]:
        """
        Retorna dados completos para a sala de consulta
        """
        try:
            # Importa aqui para evitar dependência circular
            with self.app.app_context():
                from app import Consulta, Paciente
                
                consulta = Consulta.query.get(consulta_id)
                if not consulta:
                    return None
                
                paciente = consulta.paciente_consulta if consulta.paciente_id else None
                
                # Busca histórico de consultas do paciente
                historico = []
                if paciente:
                    historico = self.db.session.query(Consulta)\
                        .filter(Consulta.paciente_id == consulta.paciente_id)\
                        .filter(Consulta.data_hora < consulta.data_hora)\
                        .order_by(Consulta.data_hora.desc())\
                        .limit(5)\
                        .all()
            
            return {
                'consulta': {
                    'id': consulta.id,
                    'data_consulta': consulta.data_hora,
                    'status': consulta.status,
                    'observacoes': consulta.observacoes,
                    'meet_link': consulta.link_videochamada,
                    'duracao_estimada': 60  # minutos
                },
                'paciente': {
                    'id': paciente.id if paciente else None,
                    'nome': paciente.nome_completo if paciente else consulta.nome_paciente_gc,
                    'email': paciente.email if paciente else consulta.email_paciente_gc,
                    'telefone': paciente.telefone if paciente else consulta.telefone_paciente_gc,
                    'idade': self._calcular_idade(paciente.data_nascimento) if paciente and paciente.data_nascimento else None,
                    'objetivo': paciente.objetivo if paciente else 'Não informado',
                    'peso_atual': paciente.peso_atual if paciente else None,
                    'altura': paciente.altura if paciente else None,
                    'imc': self._calcular_imc(paciente) if paciente else None
                },
                'historico': [
                    {
                        'data': h.data_hora,
                        'observacoes': h.observacoes,
                        'status': h.status
                    } for h in historico
                ],
                'tools': {
                    'tem_meet': bool(consulta.link_videochamada),
                    'pode_iniciar': datetime.now() >= consulta.data_hora - timedelta(minutes=15),
                    'em_horario': True  # Lógica para verificar se está no horário
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados da sala de consulta: {e}")
            return None
    
    def update_consultation_status(self, consulta_id: str, novo_status: str, observacoes: str = None) -> bool:
        """
        Atualiza status da consulta
        """
        try:
            # Importa aqui para evitar dependência circular
            with self.app.app_context():
                from app import Consulta
                
                consulta = Consulta.query.get(consulta_id)
                if not consulta:
                    return False
                
                consulta.status = novo_status
                if observacoes:
                    consulta.observacoes = observacoes
                
                self.db.session.commit()
                return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status da consulta: {e}")
            return False
    
    def _get_consultas_hoje(self):
        """Obtém todas as consultas do dia atual"""
        hoje_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        hoje_fim = hoje_inicio + timedelta(days=1)
        
        # Importa aqui para evitar dependência circular
        with self.app.app_context():
            from app import Consulta, Paciente
            
            consultas = self.db.session.query(Consulta).join(Paciente, Consulta.paciente_id == Paciente.id, isouter=True)\
                .filter(Consulta.data_hora >= hoje_inicio)\
                .filter(Consulta.data_hora < hoje_fim)\
                .order_by(Consulta.data_hora)\
                .all()
            
            return consultas
    
    def _enrich_consultas(self, consultas: List) -> List[Dict]:
        """Enriquece dados das consultas com informações do paciente"""
        consultas_enriched = []
        
        for consulta in consultas:
            # Busca dados do paciente através do relacionamento
            paciente = consulta.paciente_consulta if consulta.paciente_id else None
            
            # Calcula tempo restante
            agora = datetime.now()
            tempo_restante = consulta.data_hora - agora
            
            consulta_data = {
                'consulta_id': consulta.id,
                'data_consulta': consulta.data_hora,
                'status': consulta.status,
                'observacoes': consulta.observacoes,
                'meet_link': consulta.link_videochamada,
                'paciente': {
                    'id': paciente.id if paciente else None,
                    'nome': paciente.nome_completo if paciente else consulta.nome_paciente_gc,
                    'email': paciente.email if paciente else consulta.email_paciente_gc,
                    'telefone': paciente.telefone if paciente else consulta.telefone_paciente_gc,
                    'avatar': self._generate_avatar(paciente.nome_completo if paciente else consulta.nome_paciente_gc)
                },
                'timing': {
                    'tempo_restante_minutos': int(tempo_restante.total_seconds() / 60),
                    'em_horario': abs(tempo_restante.total_seconds()) <= 900,  # 15 min tolerância
                    'pode_iniciar': tempo_restante.total_seconds() <= 900,  # Pode iniciar 15 min antes
                    'status_tempo': self._get_status_tempo(tempo_restante)
                },
                'tools': {
                    'tem_meet': bool(consulta.link_videochamada),
                    'precisa_meet': not bool(consulta.link_videochamada),
                    'sala_url': f"/consulta/{consulta.id}/sala"
                }
            }
            
            consultas_enriched.append(consulta_data)
        
        return consultas_enriched
    
    def _calcular_idade(self, data_nascimento: datetime) -> int:
        """Calcula idade a partir da data de nascimento"""
        if not data_nascimento:
            return None
        
        hoje = datetime.now().date()
        if isinstance(data_nascimento, datetime):
            data_nascimento = data_nascimento.date()
        
        return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
    
    def _calcular_imc(self, paciente) -> float:
        """Calcula IMC do paciente"""
        if not paciente or not paciente.peso_atual or not paciente.altura:
            return None
        
        altura_m = paciente.altura / 100  # Converte cm para metros
        imc = paciente.peso_atual / (altura_m ** 2)
        return round(imc, 1)
    
    def _generate_avatar(self, nome: str) -> str:
        """Gera avatar baseado no nome"""
        if not nome:
            return "👤"
        
        # Pega primeira letra de cada palavra
        iniciais = ''.join([palavra[0].upper() for palavra in nome.split() if palavra])
        return iniciais[:2]
    
    def _get_status_tempo(self, tempo_restante: timedelta) -> str:
        """Retorna status baseado no tempo restante"""
        minutos = int(tempo_restante.total_seconds() / 60)
        
        if minutos < -15:
            return "atrasada"
        elif minutos <= 0:
            return "agora"
        elif minutos <= 15:
            return "iminente"
        elif minutos <= 60:
            return "proximo"
        else:
            return "futuro"
    
    def _get_empty_overview(self) -> Dict:
        """Retorna overview vazio em caso de erro"""
        return {
            'data': datetime.now().date(),
            'total_consultas': 0,
            'consultas_com_meet': 0,
            'receita_estimada': 0,
            'proximas': [],
            'em_andamento': [],
            'finalizadas': [],
            'atrasadas': [],
            'stats': {
                'taxa_meet': 0,
                'taxa_finalizacao': 0,
                'consultas_restantes': 0,
                'tempo_medio_consulta': 60
            }
        }

# Instância global do serviço
dashboard_service = DashboardService()

def get_dashboard_service():
    """Retorna a instância do Dashboard Service"""
    return dashboard_service