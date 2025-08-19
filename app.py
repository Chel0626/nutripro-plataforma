# app.py (Versão 100% Completa, com Banco de Dados Permanente e API de Autocomplete)
import os
import sys
import math
import logging
from datetime import datetime, timezone

# Importa DADOS_TACO se disponível; em falta, usa lista vazia e registra warning.
logger = logging.getLogger(__name__)
try:
    from taco_data import DADOS_TACO
except Exception:
    logger.warning("Arquivo 'taco_data.py' não encontrado — DADOS_TACO vazio. Rode converter_csv.py para gerar os dados.")
    DADOS_TACO = []

from calculadoras import (calcular_necessidade_calorica,
                          distribuir_macros_nas_refeicoes,
                          calcular_macros_por_porcentagem, somar_macros_refeicoes)
from flask import (Flask, flash, jsonify, redirect, render_template,
                   request, url_for, send_from_directory)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import (DateField, FieldList, FloatField, FormField, IntegerField,
                     SelectField, StringField, SubmitField, TextAreaField)
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Email as EmailValidator, NumberRange, Optional

app = Flask(__name__)

# --- CONFIGURAÇÕES GERAIS DO APP ---
# Ler configurações sensíveis de env vars, manter defaults para dev
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma-chave-secreta-muito-segura')

# Banco padrão em ./instance/plataforma_nutri.db, pode ser sobrescrito por APP_DB_URI
project_root = os.path.dirname(os.path.abspath(__file__))
# Quando empacotado pelo PyInstaller, preferir criar/usar a pasta 'instance' no CWD
# para que o banco seja persistente localmente ao lado do executável.
if getattr(sys, '_MEIPASS', False):
    instance_dir = os.path.join(os.getcwd(), 'instance')
else:
    instance_dir = os.path.join(project_root, 'instance')
# Permite sobrescrever via variável de ambiente APP_INSTANCE_DIR
instance_dir = os.environ.get('APP_INSTANCE_DIR', instance_dir)
os.makedirs(instance_dir, exist_ok=True)
default_db_path = os.path.join(instance_dir, 'plataforma_nutri.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('APP_DB_URI', f'sqlite:///{default_db_path}')
logger.info(f"Usando arquivo de banco de dados: {default_db_path}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup básico de logging se não houver handlers
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

db = SQLAlchemy(app)

# Diretório para salvar dados persistentes fora do executável (pasta visível ao usuário)
# Quando empacotado (_MEIPASS), usamos o CWD/data por padrão para que o executável possa
# criar arquivos ao lado dele; em desenvolvimento usamos project_root/data.
if getattr(sys, '_MEIPASS', False):
    default_data_dir = os.path.join(os.getcwd(), 'data')
else:
    default_data_dir = os.path.join(project_root, 'data')
DATA_DIR = os.environ.get('APP_DATA_DIR', default_data_dir)
os.makedirs(DATA_DIR, exist_ok=True)
logger.info(f"Data directory for external saves: {DATA_DIR}")

def _slug(text: str) -> str:
    """Gera slug seguro para nomes de pasta a partir do nome do paciente."""
    if not text:
        return 'sem_nome'
    # mantém apenas caracteres alfanuméricos, hífen e underline
    safe = ''.join(c if c.isalnum() else '_' for c in text.strip())
    return safe[:80]

def save_patient_and_plano_to_disk(paciente: 'Paciente', plano: 'PlanoAlimentar') -> str:
    """Cria pasta do paciente em DATA_DIR e grava arquivos JSON/HTML do plano.

    Retorna o caminho do arquivo HTML gerado do plano.
    """
    try:
        paciente_folder_name = f"paciente_{paciente.id}_{_slug(paciente.nome_completo)}"
        paciente_dir = os.path.join(DATA_DIR, paciente_folder_name)
        os.makedirs(paciente_dir, exist_ok=True)

        # Gravando dados do paciente (parcial)
        paciente_data = {
            'id': paciente.id,
            'nome_completo': paciente.nome_completo,
            'email': paciente.email,
            'telefone': paciente.telefone,
            'data_nascimento': paciente.data_nascimento.isoformat() if paciente.data_nascimento else None,
            'peso': paciente.peso,
            'altura_cm': paciente.altura_cm,
            'sexo': paciente.sexo,
        }
        paciente_json_path = os.path.join(paciente_dir, 'paciente.json')
        with open(paciente_json_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(paciente_data, f, ensure_ascii=False, indent=2)

        # Gravando plano como JSON
        plano_data = {
            'id': plano.id,
            'paciente_id': plano.paciente_id,
            'nome_plano': plano.nome_plano,
            'objetivo_calorico_final': plano.objetivo_calorico_final,
            'orientacoes_diabetes': plano.orientacoes_diabetes,
            'orientacoes_nutricao': plano.orientacoes_nutricao,
            'data_criacao': plano.data_criacao.isoformat() if plano.data_criacao else None,
            'refeicoes': []
        }
        for r in plano.refeicoes:
            itens = []
            for it in r.itens:
                itens.append({
                    'id': it.id,
                    'nome_alimento': it.nome_alimento,
                    'marca_alimento': it.marca_alimento,
                    'quantidade_g': it.quantidade_g,
                    'medida_caseira': it.medida_caseira,
                    'carboidratos_g': it.carboidratos_g,
                    'proteinas_g': it.proteinas_g,
                    'gorduras_g': it.gorduras_g,
                    'kcal': it.kcal
                })
            plano_data['refeicoes'].append({
                'id': r.id,
                'nome_refeicao': r.nome_refeicao,
                'meta_carboidratos_g': r.meta_carboidratos_g,
                'meta_proteinas_g': r.meta_proteinas_g,
                'meta_gorduras_g': r.meta_gorduras_g,
                'itens': itens
            })

        plano_json_path = os.path.join(paciente_dir, f'plano_{plano.id}.json')
        with open(plano_json_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(plano_data, f, ensure_ascii=False, indent=2)

        # Renderiza o template do plano para HTML e grava
        try:
            html = render_template('plano_pdf_template.html', plano=plano, paciente=paciente, data_hoje=datetime.now(timezone.utc).strftime('%d/%m/%Y'))
            plano_html_path = os.path.join(paciente_dir, f'plano_{plano.id}.html')
            with open(plano_html_path, 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            logger.exception('Falha ao renderizar plano para HTML: %s', e)
            plano_html_path = ''

        logger.info('Saved patient and plan to disk: %s', paciente_dir)
        return plano_html_path
    except Exception as e:
        logger.exception('Erro salvando paciente/plano em disco: %s', e)
        return ''

# --- FUNÇÕES DE TEMPLATE E HELPERS (MÉTODO ROBUSTO) ---
@app.context_processor
def utility_processor():
    """Disponibiliza funções úteis para todos os templates."""
    def calculate_age(birth_date):
        if not birth_date:
            return None
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    def cache_buster(filename):
        """Gera um número de versão para arquivos estáticos para evitar cache."""
        try:
            static_folder = getattr(app, 'static_folder', 'static')
            filepath = os.path.join(static_folder, filename)
            if os.path.exists(filepath):
                return int(os.path.getmtime(filepath))
        except Exception:
            return 0
    
    return dict(calculate_age=calculate_age, cache_buster=cache_buster)


# Registra o mesmo cálculo como filtro Jinja para templates que usam '| calculate_age'
@app.template_filter('calculate_age')
def calculate_age_filter(birth_date):
    if not birth_date:
        return None
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def _safe_num(v):
    """Converte para float finito; retorna 0.0 para None/NaN/valores inválidos."""
    try:
        if v is None:
            return 0.0
        f = float(v)
        if math.isfinite(f):
            return f
        return 0.0
    except Exception:
        return 0.0


# Rota para servir arquivos estáticos com versão (usada por templates via url_for('custom_static', ...))
@app.route('/custom_static/<version>/<path:filename>')
def custom_static(version, filename):
    """Serve arquivos estáticos incluindo um segmento de versão para cache busting.

    A URL é construída nas templates via: url_for('custom_static', version=version, filename='js/arquivo.js')
    """
    return send_from_directory(app.static_folder or 'static', filename)

# --- MODELOS DO BANCO DE DADOS ---
class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    peso = db.Column(db.Float, nullable=True)
    altura_cm = db.Column(db.Integer, nullable=True)
    sexo = db.Column(db.String(20), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    planos = db.relationship('PlanoAlimentar', backref='paciente', lazy=True, cascade="all, delete-orphan")
    consultas = db.relationship('Consulta', backref='paciente_consulta', lazy=True, cascade="all, delete-orphan")

class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    tipo_consulta = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='Agendada')
    observacoes_nutri = db.Column(db.Text, nullable=True)
    link_videochamada = db.Column(db.String(255), nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)

class PlanoAlimentar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    nome_plano = db.Column(db.String(150), nullable=False, default='Plano Padrão')
    objetivo_calorico_final = db.Column(db.Integer, nullable=True)
    orientacoes_diabetes = db.Column(db.Text, nullable=True)
    orientacoes_nutricao = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    refeicoes = db.relationship('Refeicao', backref='plano', lazy=True, cascade="all, delete-orphan")

class Refeicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plano_id = db.Column(db.Integer, db.ForeignKey('plano_alimentar.id'), nullable=False)
    nome_refeicao = db.Column(db.String(100), nullable=False)
    meta_carboidratos_g = db.Column(db.Float, nullable=True)
    meta_proteinas_g = db.Column(db.Float, nullable=True)
    meta_gorduras_g = db.Column(db.Float, nullable=True)
    itens = db.relationship('ItemRefeicao', backref='refeicao', lazy=True, cascade="all, delete-orphan")

class ItemRefeicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refeicao_id = db.Column(db.Integer, db.ForeignKey('refeicao.id'), nullable=False)
    nome_alimento = db.Column(db.String(200), nullable=False)
    marca_alimento = db.Column(db.String(150), nullable=True)
    quantidade_g = db.Column(db.Float, nullable=False)
    medida_caseira = db.Column(db.String(100), nullable=True)
    substituicoes = db.Column(db.Text, nullable=True)
    carboidratos_g = db.Column(db.Float, nullable=False, default=0.0)
    proteinas_g = db.Column(db.Float, nullable=False, default=0.0)
    gorduras_g = db.Column(db.Float, nullable=False, default=0.0)
    kcal = db.Column(db.Integer, nullable=False, default=0)

class Alimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False, index=True)
    marca = db.Column(db.String(150), nullable=True)
    kcal_100g = db.Column(db.Float, nullable=False, default=0)
    carboidratos_100g = db.Column(db.Float, nullable=False, default=0)
    proteinas_100g = db.Column(db.Float, nullable=False, default=0)
    gorduras_100g = db.Column(db.Float, nullable=False, default=0)
    origem = db.Column(db.String(50), default='manual')

# --- FORMULÁRIOS (Flask-WTF) ---
class PacienteForm(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), EmailValidator()])
    telefone = StringField('Telefone')
    data_nascimento = DateField('Data de Nascimento (AAAA-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    peso = FloatField('Peso (kg)', validators=[Optional(), NumberRange(min=0)])
    altura_cm = IntegerField('Altura (cm)', validators=[Optional(), NumberRange(min=0)])
    sexo = SelectField('Sexo Biológico', choices=[('', 'Selecione...'), ('masculino', 'Masculino'), ('feminino', 'Feminino')], validators=[Optional()])
    observacoes = TextAreaField('Observações')
    submit = SubmitField('Salvar Paciente')

class ConsultaForm(FlaskForm):
    paciente_id = SelectField('Paciente', coerce=int, validators=[DataRequired()])
    data_hora = DateTimeLocalField('Data e Hora da Consulta', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    tipo_consulta = StringField('Tipo da Consulta', validators=[Optional()])
    status = SelectField('Status da Consulta', choices=[('Agendada', 'Agendada'), ('Realizada', 'Realizada'), ('Cancelada', 'Cancelada')], validators=[DataRequired()])
    observacoes_nutri = TextAreaField('Observações da Nutricionista')
    link_videochamada = StringField('Link da Videochamada', validators=[Optional()])
    submit = SubmitField('Salvar Consulta')

class AlimentoForm(FlaskForm):
    nome = StringField('Nome do Alimento', validators=[DataRequired()])
    marca = StringField('Marca', default='Genérico')
    kcal_100g = FloatField('Calorias (kcal) / 100g', validators=[DataRequired(), NumberRange(min=0)])
    carboidratos_100g = FloatField('Carboidratos (g) / 100g', validators=[DataRequired(), NumberRange(min=0)])
    proteinas_100g = FloatField('Proteínas (g) / 100g', validators=[DataRequired(), NumberRange(min=0)])
    gorduras_100g = FloatField('Gorduras (g) / 100g', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Salvar Alimento')

class NecessidadeCaloricaForm(FlaskForm):
    peso = FloatField('Peso (kg)', validators=[DataRequired(), NumberRange(min=1, max=300)])
    altura = FloatField('Altura (cm)', validators=[DataRequired(), NumberRange(min=50, max=250)])
    idade = IntegerField('Idade (anos)', validators=[DataRequired(), NumberRange(min=1, max=120)])
    sexo = SelectField('Sexo', choices=[('masculino', 'Masculino'), ('feminino', 'Feminino'), ('criança', 'Criança')], validators=[DataRequired()])
    nivel_atividade = SelectField('Nível de Atividade Física', choices=[('sedentario', 'Sedentário'), ('leve', 'Levemente Ativo'), ('moderado', 'Moderadamente Ativo'), ('ativo', 'Muito Ativo'), ('extremo', 'Extremamente Ativo')], validators=[DataRequired()])
    objetivo = SelectField('Objetivo', choices=[('perder', 'Perder Peso'), ('manter', 'Manter Peso'), ('ganhar', 'Ganhar Peso')], validators=[DataRequired()])
    submit = SubmitField('Calcular')

class MacroEntryForm(FlaskForm):
    class Meta:
        csrf = False
    proteina = FloatField('P', validators=[Optional(), NumberRange(min=0)])
    carboidrato = FloatField('C', validators=[Optional(), NumberRange(min=0)])
    gordura = FloatField('G', validators=[Optional(), NumberRange(min=0)])

class DistribuicaoMacrosForm(FlaskForm):
    total_kcal = IntegerField('Calorias Totais (kcal)', validators=[DataRequired(), NumberRange(min=500)])
    perc_carb = FloatField('Carboidratos (%)', default=45.0, validators=[DataRequired(), NumberRange(min=0, max=100)])
    perc_prot = FloatField('Proteínas (%)', default=20.0, validators=[DataRequired(), NumberRange(min=0, max=100)])
    perc_gord = FloatField('Gorduras (%)', default=35.0, validators=[DataRequired(), NumberRange(min=0, max=100)])
    num_refeicoes_grandes = IntegerField('Nº de Refeições Grandes', default=3, validators=[DataRequired(), NumberRange(min=0)])
    num_refeicoes_pequenas = IntegerField('Nº de Refeições Pequenas', default=3, validators=[DataRequired(), NumberRange(min=0)])
    perc_dist_grandes = IntegerField('% Calorias nas Refeições Grandes', default=70, validators=[DataRequired(), NumberRange(min=0, max=100)])
    refeicoes_grandes_ajustadas = FieldList(FormField(MacroEntryForm), min_entries=0)
    refeicoes_pequenas_ajustadas = FieldList(FormField(MacroEntryForm), min_entries=0)
    submit = SubmitField('Calcular Distribuição')

# --- ROTAS DA APLICAÇÃO ---
@app.route('/')
def home():
    total_pacientes = Paciente.query.count()
    return render_template('home_dashboard.html', titulo="Dashboard", total_pacientes=total_pacientes)

@app.route('/pacientes')
def listar_pacientes():
    page = request.args.get('page', 1, type=int)
    pacientes = Paciente.query.order_by(Paciente.nome_completo.asc()).paginate(page=page, per_page=10)
    return render_template('pacientes_listar.html', pacientes=pacientes, titulo="Lista de Pacientes")

@app.route('/paciente/novo', methods=['GET', 'POST'])
def novo_paciente():
    form = PacienteForm()
    if form.validate_on_submit():
        novo_pac = Paciente()
        form.populate_obj(novo_pac)
        db.session.add(novo_pac)
        db.session.commit()
        flash('Paciente cadastrado com sucesso!', 'success')
        return redirect(url_for('detalhe_paciente', paciente_id=novo_pac.id))
    return render_template('paciente_formulario.html', titulo='Novo Paciente', form=form)

@app.route('/paciente/<int:paciente_id>')
def detalhe_paciente(paciente_id):
    paciente_obj = Paciente.query.get_or_404(paciente_id)
    planos_salvos = PlanoAlimentar.query.filter_by(paciente_id=paciente_id).order_by(PlanoAlimentar.data_criacao.desc()).all()
    return render_template('paciente_detalhe.html', titulo=f"Detalhes de {paciente_obj.nome_completo}", paciente=paciente_obj, planos=planos_salvos)

@app.route('/paciente/<int:paciente_id>/editar', methods=['GET', 'POST'])
def editar_paciente(paciente_id):
    paciente_obj = Paciente.query.get_or_404(paciente_id)
    form = PacienteForm(obj=paciente_obj)
    if form.validate_on_submit():
        form.populate_obj(paciente_obj)
        db.session.commit()
        flash('Dados do paciente atualizados com sucesso!', 'success')
        return redirect(url_for('detalhe_paciente', paciente_id=paciente_obj.id))
    return render_template('paciente_formulario.html', titulo=f'Editar Paciente: {paciente_obj.nome_completo}', form=form)

@app.route('/paciente/<int:paciente_id>/excluir', methods=['POST'])
def excluir_paciente(paciente_id):
    paciente_obj = Paciente.query.get_or_404(paciente_id)
    db.session.delete(paciente_obj)
    db.session.commit()
    flash(f'Paciente "{paciente_obj.nome_completo}" excluído com sucesso!', 'success')
    return redirect(url_for('listar_pacientes'))

@app.route('/consultas')
def listar_consultas():
    page = request.args.get('page', 1, type=int)
    consultas_paginadas = Consulta.query.order_by(Consulta.data_hora.desc()).paginate(page=page, per_page=10)
    return render_template('consultas_listar.html', consultas=consultas_paginadas, titulo="Todas as Consultas")

@app.route('/paciente/<int:pid>/consulta/nova', methods=['GET', 'POST'])
def nova_consulta(pid):
    form = ConsultaForm(paciente_id=pid)
    form.paciente_id.choices = [(p.id, p.nome_completo) for p in Paciente.query.order_by(Paciente.nome_completo).all()]
    if form.validate_on_submit():
        nova_cons = Consulta(paciente_id=pid)
        form.populate_obj(nova_cons)
        db.session.add(nova_cons)
        db.session.commit()
        flash(f'Consulta agendada com sucesso!', 'success')
        return redirect(url_for('detalhe_paciente', paciente_id=pid))
    return render_template('consulta_formulario.html', titulo=f'Nova Consulta', form=form, paciente_id=pid)

@app.route('/paciente/<int:paciente_id>/plano/novo', methods=['GET', 'POST'])
def novo_plano(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    return render_template('plano_formulario.html', titulo=f"Novo Plano para {paciente.nome_completo}", paciente=paciente)

@app.route('/plano/<int:plano_id>/visualizar_para_impressao')
def visualizar_plano_para_impressao(plano_id):
    plano = PlanoAlimentar.query.get_or_404(plano_id)
    paciente = plano.paciente
    data_hoje = datetime.now(timezone.utc).strftime('%d/%m/%Y')
    return render_template('plano_pdf_template.html', plano=plano, paciente=paciente, data_hoje=data_hoje)

# Compatibilidade: registra o mesmo view com o endpoint 'gerar_plano_pdf'
# (alguns templates antigos chamam url_for('gerar_plano_pdf', plano_id=...)).
app.add_url_rule('/plano/<int:plano_id>/visualizar_para_impressao', endpoint='gerar_plano_pdf', view_func=visualizar_plano_para_impressao)
# Compatibilidade adicional: alguns templates chamam 'assinar_plano_pdf'
app.add_url_rule('/plano/<int:plano_id>/visualizar_para_impressao', endpoint='assinar_plano_pdf', view_func=visualizar_plano_para_impressao)

@app.route('/meus_alimentos')
def listar_meus_alimentos():
    page = request.args.get('page', 1, type=int)
    termo_busca = request.args.get('busca', '')
    query_base = Alimento.query
    if termo_busca:
        query_base = query_base.filter(Alimento.nome.ilike(f'%{termo_busca}%'))
    alimentos_paginados = query_base.order_by(Alimento.nome.asc()).paginate(page=page, per_page=20)
    return render_template('meus_alimentos.html', titulo="Meu Banco de Alimentos", alimentos=alimentos_paginados, termo_busca=termo_busca)

@app.route('/meus_alimentos/novo', methods=['GET', 'POST'])
def novo_alimento():
    form = AlimentoForm()
    if form.validate_on_submit():
        novo_alimento_obj = Alimento()
        form.populate_obj(novo_alimento_obj)
        db.session.add(novo_alimento_obj)
        db.session.commit()
        flash(f"Alimento '{novo_alimento_obj.nome}' cadastrado com sucesso!", 'success')
        return redirect(url_for('listar_meus_alimentos'))
    return render_template('alimento_formulario.html', titulo="Adicionar Novo Alimento", form=form)

@app.route('/meus_alimentos/<int:alimento_id>/editar', methods=['GET', 'POST'])
def editar_alimento(alimento_id):
    alimento = Alimento.query.get_or_404(alimento_id)
    form = AlimentoForm(obj=alimento)
    if form.validate_on_submit():
        form.populate_obj(alimento)
        db.session.commit()
        flash(f"Alimento '{alimento.nome}' atualizado com sucesso!", 'success')
        return redirect(url_for('listar_meus_alimentos'))
    return render_template('alimento_formulario.html', titulo="Editar Alimento", form=form)

@app.route('/meus_alimentos/<int:alimento_id>/excluir', methods=['POST'])
def excluir_alimento(alimento_id):
    alimento = Alimento.query.get_or_404(alimento_id)
    try:
        db.session.delete(alimento)
        db.session.commit()
        flash(f"Alimento '{alimento.nome}' excluído com sucesso.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir o alimento: {e}", 'danger')
    return redirect(url_for('listar_meus_alimentos'))

@app.route('/ferramentas/calculadora_calorias', methods=['GET', 'POST'])
def calculadora_calorias():
    form = NecessidadeCaloricaForm()
    resultado = None
    if form.validate_on_submit():
        resultado = calcular_necessidade_calorica(
            peso_kg=form.peso.data, altura_cm=form.altura.data, idade_anos=form.idade.data,
            sexo=form.sexo.data, nivel_atividade=form.nivel_atividade.data, objetivo=form.objetivo.data
        )
    return render_template('calculadora_calorias.html', titulo="Calculadora de Necessidade Calórica", form=form, resultado=resultado)

@app.route('/ferramentas/distribuicao_macros', methods=['GET', 'POST'])
def distribuicao_macros():
    form = DistribuicaoMacrosForm(request.form)
    resultado_final = None
    if request.method == 'POST' and form.validate_on_submit() and request.form.get('action') == 'calcular':
        soma_perc = form.perc_carb.data + form.perc_prot.data + form.perc_gord.data
        if round(soma_perc) != 100:
            flash("A soma das porcentagens de macronutrientes deve ser 100%.", "danger")
        else:
            macros_em_gramas = calcular_macros_por_porcentagem(total_kcal=form.total_kcal.data, perc_carb=form.perc_carb.data, perc_prot=form.perc_prot.data, perc_gord=form.perc_gord.data)
            distribuicao_refeicoes = distribuir_macros_nas_refeicoes(macros_em_gramas=macros_em_gramas, num_grandes=form.num_refeicoes_grandes.data, num_pequenas=form.num_refeicoes_pequenas.data, perc_dist_grandes=form.perc_dist_grandes.data)
            resultado_final = {'total_macros': macros_em_gramas, 'distribuicao': distribuicao_refeicoes, 'num_refeicoes_grandes': form.num_refeicoes_grandes.data, 'num_refeicoes_pequenas': form.num_refeicoes_pequenas.data}
            form.refeicoes_grandes_ajustadas.entries = []
            for _ in range(form.num_refeicoes_grandes.data):
                form.refeicoes_grandes_ajustadas.append_entry(data=distribuicao_refeicoes['por_refeicao_grande'])
            form.refeicoes_pequenas_ajustadas.entries = []
            for _ in range(form.num_refeicoes_pequenas.data):
                form.refeicoes_pequenas_ajustadas.append_entry(data=distribuicao_refeicoes['por_refeicao_pequena'])
    elif request.method == 'POST' and request.form.get('action') == 'recalcular':
        soma_ajustada = somar_macros_refeicoes(form.refeicoes_grandes_ajustadas.data + form.refeicoes_pequenas_ajustadas.data)
        flash(f"Soma manual recalculada: Carboidratos: {soma_ajustada['carboidrato']:.1f}g, Proteínas: {soma_ajustada['proteina']:.1f}g, Gorduras: {soma_ajustada['gordura']:.1f}g.", 'info')
        return render_template('distribuicao_macros.html', titulo="Calculadora de Distribuição de Macros", form=form, resultado=None)
    return render_template('distribuicao_macros.html', titulo="Calculadora de Distribuição de Macros", form=form, resultado=resultado_final)

# --- ROTAS DA API ---
@app.route('/api/paciente/<int:paciente_id>/plano/salvar', methods=['POST'])
def api_salvar_plano(paciente_id):
    dados_plano = request.get_json()
    try:
        novo_plano = PlanoAlimentar(
            paciente_id=paciente_id, 
            nome_plano=dados_plano.get('nome_plano'), 
            objetivo_calorico_final=dados_plano.get('objetivo_calorico'),
            orientacoes_diabetes=dados_plano.get('orientacoes_diabetes', None),
            orientacoes_nutricao=dados_plano.get('orientacoes_nutricao', None)
        )
        db.session.add(novo_plano)
        db.session.flush()
        for refeicao_data in dados_plano.get('refeicoes', []):
            nova_refeicao = Refeicao(plano_id=novo_plano.id, nome_refeicao=refeicao_data.get('nome'), meta_carboidratos_g=refeicao_data['metas']['carboidrato'], meta_proteinas_g=refeicao_data['metas']['proteina'], meta_gorduras_g=refeicao_data['metas']['gordura'])
            db.session.add(nova_refeicao)
            db.session.flush()
            for item_data in refeicao_data.get('itens', []):
                novo_item = ItemRefeicao(refeicao_id=nova_refeicao.id, nome_alimento=item_data.get('nome'), marca_alimento=item_data.get('marca'), quantidade_g=item_data.get('quantidade'), medida_caseira=item_data.get('medida_caseira'), substituicoes=item_data.get('substituicoes'), carboidratos_g=item_data['macros']['carboidratos'], proteinas_g=item_data['macros']['proteinas'], gorduras_g=item_data['macros']['gorduras'], kcal=item_data['macros']['kcal'])
                db.session.add(novo_item)
        db.session.commit()
        # Após salvar no DB, também gravar o plano e os dados do paciente em disco para acesso via Explorer
        try:
            paciente_obj = Paciente.query.get(paciente_id)
            plano_obj = novo_plano
            html_path = save_patient_and_plano_to_disk(paciente_obj, plano_obj)
            logger.info('Plano salvo e exportado para: %s', html_path)
        except Exception:
            logger.exception('Erro ao exportar plano para disco')

        return jsonify({'sucesso': True, 'mensagem': 'Plano salvo com sucesso!', 'redirect_url': url_for('detalhe_paciente', paciente_id=paciente_id)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao salvar: {str(e)}'}), 500


# --- ENDPOINTS DE CÁLCULO (API para frontend) ---
@app.route('/api/calcular_calorias', methods=['POST'])
def api_calcular_calorias():
    dados = request.get_json() or {}
    try:
        peso = float(dados.get('peso') or 0)
        altura = float(dados.get('altura') or 0)
        idade = int(float(dados.get('idade') or 0))
        sexo = (dados.get('sexo') or '').strip()
        nivel_atividade = (dados.get('nivel_atividade') or '').strip()
        objetivo = (dados.get('objetivo') or '').strip()

        # Validação mínima
        if peso <= 0 or altura <= 0 or idade <= 0 or not sexo or not nivel_atividade or not objetivo:
            return jsonify({'sucesso': False, 'erro': 'Por favor preencha todos os campos da calculadora corretamente.'}), 400

        resultado = calcular_necessidade_calorica(peso_kg=peso, altura_cm=altura, idade_anos=idade, sexo=sexo, nivel_atividade=nivel_atividade, objetivo=objetivo)
        if resultado is None:
            return jsonify({'sucesso': False, 'erro': 'Dados inválidos para cálculo. Verifique entradas.'}), 400

        return jsonify({'sucesso': True, 'resultado': resultado})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': f'Erro interno: {e}'}), 500


@app.route('/api/calcular_distribuicao', methods=['POST'])
def api_calcular_distribuicao():
    dados = request.get_json() or {}
    try:
        total_kcal = int(float(dados.get('total_kcal') or 0))
        perc_carb = float(dados.get('perc_carb') or 0)
        perc_prot = float(dados.get('perc_prot') or 0)
        perc_gord = float(dados.get('perc_gord') or 0)
        num_grandes = int(float(dados.get('num_refeicoes_grandes') or 0))
        num_pequenas = int(float(dados.get('num_refeicoes_pequenas') or 0))
        perc_dist_grandes = int(float(dados.get('perc_dist_grandes') or 0))

        if total_kcal <= 0 or num_grandes < 0 or num_pequenas < 0:
            return jsonify({'sucesso': False, 'erro': 'Valores inválidos para distribuição.'}), 400

        macros = calcular_macros_por_porcentagem(total_kcal=total_kcal, perc_carb=perc_carb, perc_prot=perc_prot, perc_gord=perc_gord)
        if macros is None:
            return jsonify({'sucesso': False, 'erro': 'Porcentagens inválidas ou não somam 100%.'}), 400

        distribuicao = distribuir_macros_nas_refeicoes(macros_em_gramas=macros, num_grandes=num_grandes, num_pequenas=num_pequenas, perc_dist_grandes=perc_dist_grandes)
        if distribuicao is None:
            return jsonify({'sucesso': False, 'erro': 'Erro ao distribuir macros entre refeições.'}), 500

        resultado = {
            'num_refeicoes_grandes': num_grandes,
            'num_refeicoes_pequenas': num_pequenas,
            'por_refeicao_grande': distribuicao['por_refeicao_grande'],
            'por_refeicao_pequena': distribuicao['por_refeicao_pequena'],
            'macros_gramas': macros
        }
        return jsonify({'sucesso': True, 'resultado': resultado})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': f'Erro interno: {e}'}), 500

# --- ROTA DE API FALTANTE (CORREÇÃO DO ERRO 404) ---
@app.route('/api/alimentos/autocomplete')
def autocomplete_alimentos():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    termo = query.strip()
    alimentos_db = Alimento.query.filter(Alimento.nome.ilike(f'%{termo}%')).order_by(Alimento.nome).limit(10).all()

    resultados = []
    nomes_vistos = set()

    # Primeiro, adiciona resultados do DB (prioritários)
    for al in alimentos_db:
        nomes_vistos.add((al.nome or '').strip().lower())
        resultados.append({
            "id": al.id,
            "nome": al.nome,
            "marca": al.marca or '',
            "kcal_100g": _safe_num(al.kcal_100g),
            "carboidratos_100g": _safe_num(al.carboidratos_100g),
            "proteinas_100g": _safe_num(al.proteinas_100g),
            "gorduras_100g": _safe_num(al.gorduras_100g),
            "origem": getattr(al, 'origem', 'manual') or 'manual',
            "text": al.nome,
            "value": al.nome
        })

    # Se ainda houver espaço, adiciona itens do DADOS_TACO que não estejam no DB
    if len(resultados) < 10 and DADOS_TACO:
        termo_lower = termo.lower()
        for alimento in DADOS_TACO:
            nome = (alimento.get('nome') or '').strip()
            if not nome:
                continue
            if nome.lower() in nomes_vistos:
                continue
            if termo_lower in nome.lower():
                resultados.append({
                    "id": None,
                    "nome": nome,
                    "marca": 'TACO',
                    "kcal_100g": _safe_num(alimento.get('kcal_100g', 0)),
                    "carboidratos_100g": _safe_num(alimento.get('carboidratos_100g', 0)),
                    "proteinas_100g": _safe_num(alimento.get('proteinas_100g', 0)),
                    "gorduras_100g": _safe_num(alimento.get('gorduras_100g', 0)),
                    "origem": 'TACO',
                    "text": nome,
                    "value": nome
                })
            if len(resultados) >= 10:
                break

    return jsonify(resultados)

# --- FUNÇÃO PARA POVOAR O BANCO DE DADOS (VERSÃO FINAL) ---
def seed_taco_data():
    """
    Verifica se a tabela Alimento está vazia e, se estiver, a popula
    usando a lista DADOS_TACO importada do arquivo taco_data.py.
    """
    if Alimento.query.first() is not None:
        print("Banco de dados de alimentos já populado.")
        return

    print("Banco de dados de alimentos vazio. Povoando com dados TACO embutidos...")
    try:
        alimentos_para_adicionar = []
        for dados_alimento in DADOS_TACO:
            novo_alimento = Alimento(
                nome=dados_alimento['nome'],
                marca='TACO',
                kcal_100g=dados_alimento['kcal_100g'],
                proteinas_100g=dados_alimento['proteinas_100g'],
                carboidratos_100g=dados_alimento['carboidratos_100g'],
                gorduras_100g=dados_alimento['gorduras_100g'],
                origem='TACO'
            )
            alimentos_para_adicionar.append(novo_alimento)

        if alimentos_para_adicionar:
            db.session.bulk_save_objects(alimentos_para_adicionar)
            db.session.commit()
            print(f"Importação concluída com sucesso! {len(alimentos_para_adicionar)} alimentos adicionados.")
        
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao importar os dados: {e}")
        db.session.rollback()

# --- Ponto de entrada para desenvolvimento ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_taco_data()
    app.run(debug=True, port=5000)
