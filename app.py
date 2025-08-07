from flask import Response
from weasyprint import HTML
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, SelectField, FloatField, FieldList, FormField, \
    IntegerField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Email as EmailValidator, Optional, NumberRange
from datetime import datetime, timezone
from flask_mail import Mail, Message
import os
import json
import re
import requests
from fatsecret import Fatsecret

# Importa todas as funções necessárias do nosso módulo de calculadoras
from calculadoras import calcular_necessidade_calorica, calcular_macros_por_porcentagem, \
    distribuir_macros_nas_refeicoes, somar_macros_refeicoes

app = Flask(__name__)

# --- CONFIGURAÇÕES GERAIS DO APP ---
app.config['SECRET_KEY'] = '9a7ac0c13d69490b8dc92e21075024d1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plataforma_nutri.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- CONFIGURAÇÕES DO FLASK-MAIL ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME_APP', 'SEU_EMAIL_AQUI@example.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD_APP', 'SUA_SENHA_DE_APP_AQUI')
app.config['MAIL_DEFAULT_SENDER'] = ('NutriPlatform', app.config['MAIL_USERNAME'])

# --- CONFIGURAÇÕES DA API FATSECRET ---
FATSECRET_KEY = '9a7ac0c13d69490b8dc92e21075024d1'
FATSECRET_SECRET = 'e5683f5a98b64a19825877370109e15c'

# --- INICIALIZAÇÃO DAS EXTENSÕES ---
db = SQLAlchemy(app)
mail = Mail(app)
fs = Fatsecret(FATSECRET_KEY, FATSECRET_SECRET)


# --- MODELOS DO BANCO DE DADOS ---
class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    consultas = db.relationship('Consulta', backref='paciente_consulta', lazy=True, cascade="all, delete-orphan")
    perfis_diabetes = db.relationship('PerfilDiabetes', backref='paciente_perfil', lazy='dynamic',
                                      cascade="all, delete-orphan")
    planos = db.relationship('PlanoAlimentar', backref='paciente', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Paciente(id={self.id}, nome='{self.nome_completo}')>"


class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    tipo_consulta = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='Agendada')
    observacoes_nutri = db.Column(db.Text, nullable=True)
    link_videochamada = db.Column(db.String(255), nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)

    def __repr__(self):
        return f"<Consulta(id={self.id}, paciente_id={self.paciente_id}, data='{self.data_hora.strftime('%Y-%m-%d')}')>"


class PerfilDiabetes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    nome_perfil = db.Column(db.String(100), nullable=False, default='Padrão')
    data_inicio_validade = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    dia = db.Column(db.Float, nullable=True)
    fuso_horario = db.Column(db.String(50), nullable=True, default='America/Sao_Paulo')
    unidade_glicemia = db.Column(db.String(10), nullable=True, default='mg/dL')
    taxa_absorcao_carb = db.Column(db.Float, nullable=True)
    fsi_valores = db.Column(db.Text, nullable=True)
    rc_valores = db.Column(db.Text, nullable=True)
    basal_valores = db.Column(db.Text, nullable=True)
    metas_valores = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    data_atualizacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                 onupdate=lambda: datetime.now(timezone.utc))

    def _set_json_field(self, field_name, data_list):
        filtered_list = [entry for entry in data_list if (
                    entry.get('hora') and isinstance(entry.get('hora'), str) and entry.get(
                'hora').strip()) or entry.get('valor') is not None or entry.get('valor_baixo') is not None or entry.get(
            'valor_alto') is not None]
        setattr(self, field_name, json.dumps(filtered_list) if filtered_list else None)

    def _get_json_field(self, field_name):
        field_value = getattr(self, field_name)
        return json.loads(field_value) if field_value else []

    def set_fsi(self, data_list): self._set_json_field('fsi_valores', data_list)

    def get_fsi(self): return self._get_json_field('fsi_valores')

    def set_rc(self, data_list): self._set_json_field('rc_valores', data_list)

    def get_rc(self): return self._get_json_field('rc_valores')

    def set_basal(self, data_list): self._set_json_field('basal_valores', data_list)

    def get_basal(self): return self._get_json_field('basal_valores')

    def set_metas(self, data_list): self._set_json_field('metas_valores', data_list)

    def get_metas(self): return self._get_json_field('metas_valores')


class PlanoAlimentar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    nome_plano = db.Column(db.String(150), nullable=False, default='Plano Padrão')
    objetivo_calorico_final = db.Column(db.Integer, nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    ativo = db.Column(db.Boolean, default=True)
    refeicoes = db.relationship('Refeicao', backref='plano', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PlanoAlimentar(id={self.id}, nome='{self.nome_plano}')>"


class Refeicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plano_id = db.Column(db.Integer, db.ForeignKey('plano_alimentar.id'), nullable=False)
    nome_refeicao = db.Column(db.String(100), nullable=False)
    horario_sugerido = db.Column(db.String(50), nullable=True)
    meta_carboidratos_g = db.Column(db.Float, nullable=True)
    meta_proteinas_g = db.Column(db.Float, nullable=True)
    meta_gorduras_g = db.Column(db.Float, nullable=True)
    itens = db.relationship('ItemRefeicao', backref='refeicao', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Refeicao(id={self.id}, nome='{self.nome_refeicao}')>"


class ItemRefeicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refeicao_id = db.Column(db.Integer, db.ForeignKey('refeicao.id'), nullable=False)
    nome_alimento = db.Column(db.String(200), nullable=False)
    marca_alimento = db.Column(db.String(150), nullable=True)
    quantidade_g = db.Column(db.Float, nullable=False)
    medida_caseira = db.Column(db.String(100), nullable=True)
    substituicoes = db.Column(db.Text, nullable=True)
    carboidratos_g = db.Column(db.Float, nullable=False)
    proteinas_g = db.Column(db.Float, nullable=False)
    gorduras_g = db.Column(db.Float, nullable=False)
    kcal = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<ItemRefeicao(id={self.id}, nome='{self.nome_alimento}', qtde={self.quantidade_g}g)>"


# Em app.py, adicione este novo modelo junto com os outros

class Alimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    marca = db.Column(db.String(150), nullable=True)

    # Armazenamos os dados sempre por 100g para manter um padrão
    kcal_100g = db.Column(db.Float, nullable=False, default=0)
    carboidratos_100g = db.Column(db.Float, nullable=False, default=0)
    proteinas_100g = db.Column(db.Float, nullable=False, default=0)
    gorduras_100g = db.Column(db.Float, nullable=False, default=0)

    # Campo para indicar se o alimento foi cadastrado manualmente ou importado da API
    origem = db.Column(db.String(50), default='manual')
    # ID do alimento na API do FatSecret, se aplicável
    fatsecret_food_id = db.Column(db.String(50), unique=True, nullable=True)

    data_criacao = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Alimento(id={self.id}, nome='{self.nome}')>"

# --- FORMULÁRIOS (Flask-WTF) ---
class PacienteForm(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), EmailValidator()])
    telefone = StringField('Telefone')
    data_nascimento = DateField('Data de Nascimento (AAAA-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    observacoes = TextAreaField('Observações')
    submit = SubmitField('Salvar Paciente')


class ConsultaForm(FlaskForm):
    paciente_id = SelectField('Paciente', coerce=int, validators=[DataRequired()])
    data_hora = DateTimeLocalField('Data e Hora da Consulta', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    tipo_consulta = StringField('Tipo da Consulta', validators=[Optional()])
    status = SelectField('Status da Consulta',
                         choices=[('Agendada', 'Agendada'), ('Realizada', 'Realizada'), ('Cancelada', 'Cancelada'),
                                  ('Remarcada', 'Remarcada'), ('Não Compareceu', 'Não Compareceu')],
                         validators=[DataRequired()])
    observacoes_nutri = TextAreaField('Observações da Nutricionista')
    link_videochamada = StringField('Link da Videochamada', validators=[Optional()])
    submit = SubmitField('Salvar Consulta')


class TimeValueEntryForm(FlaskForm):
    class Meta:
        csrf = False

    hora = StringField('Hora (HH:MM)', validators=[Optional()])
    valor = FloatField('Valor', validators=[Optional(), NumberRange()])


class MetaEntryForm(FlaskForm):
    class Meta:
        csrf = False

    hora = StringField('Hora (HH:MM)', validators=[Optional()])
    valor_baixo = FloatField('Valor Baixo', validators=[Optional(), NumberRange()])
    valor_alto = FloatField('Valor Alto', validators=[Optional(), NumberRange()])


class PerfilDiabetesForm(FlaskForm):
    nome_perfil = StringField('Nome do Perfil', default='Padrão', validators=[DataRequired()])
    data_inicio_validade = DateTimeLocalField('Início da Validade', format='%Y-%m-%dT%H:%M',
                                              default=lambda: datetime.now(timezone.utc), validators=[DataRequired()])
    dia = FloatField('DIA (horas)', validators=[Optional(), NumberRange(min=0, max=10)])
    fuso_horario = StringField('Fuso Horário', default='America/Sao_Paulo', validators=[Optional()])
    unidade_glicemia = SelectField('Unidade de Glicemia', choices=[('mg/dL', 'mg/dL'), ('mmol/L', 'mmol/L')],
                                   default='mg/dL', validators=[Optional()])
    taxa_absorcao_carb = FloatField('Taxa de Absorção de Carboidratos (g/hora)',
                                    validators=[Optional(), NumberRange(min=0)])
    fsi_entries = FieldList(FormField(TimeValueEntryForm), label='Fator de Sensibilidade à Insulina (FSI/ISF)',
                            min_entries=0)
    rc_entries = FieldList(FormField(TimeValueEntryForm), label='Relação Insulina/Carboidrato (RC/IC)', min_entries=0)
    basal_entries = FieldList(FormField(TimeValueEntryForm), label='Taxas Basais Programadas (U/hr)', min_entries=0)
    meta_entries = FieldList(FormField(MetaEntryForm), label='Metas Glicêmicas (Hora, Baixo, Alto)', min_entries=0)
    submit = SubmitField('Salvar Perfil')


class NecessidadeCaloricaForm(FlaskForm):
    peso = FloatField('Peso (kg)', validators=[DataRequired(), NumberRange(min=20, max=300)])
    altura = FloatField('Altura (cm)', validators=[DataRequired(), NumberRange(min=100, max=250)])
    idade = IntegerField('Idade (anos)', validators=[DataRequired(), NumberRange(min=1, max=120)])
    sexo = SelectField('Sexo', choices=[('masculino', 'Masculino'), ('feminino', 'Feminino'), ('criança', 'Criança')],
                       validators=[DataRequired()])
    nivel_atividade = SelectField('Nível de Atividade Física', choices=[
        ('sedentario', 'Sedentário'), ('leve', 'Levemente Ativo'), ('moderado', 'Moderadamente Ativo'),
        ('ativo', 'Muito Ativo'), ('extremo', 'Extremamente Ativo')], validators=[DataRequired()])
    objetivo = SelectField('Objetivo',
                           choices=[('perder', 'Perder Peso'), ('manter', 'Manter Peso'), ('ganhar', 'Ganhar Peso')],
                           validators=[DataRequired()])
    submit = SubmitField('Calcular')


class MacroEntryForm(FlaskForm):
    class Meta:
        csrf = False

    proteina = IntegerField('P', validators=[Optional(), NumberRange(min=0)])
    carboidrato = IntegerField('C', validators=[Optional(), NumberRange(min=0)])
    gordura = IntegerField('G', validators=[Optional(), NumberRange(min=0)])


class DistribuicaoMacrosForm(FlaskForm):
    total_kcal = IntegerField('Calorias Totais (kcal)', validators=[DataRequired(), NumberRange(min=500)])
    peso = FloatField('Peso do Paciente (kg)', validators=[DataRequired(), NumberRange(min=20)])
    perc_carb = FloatField('Carboidratos (%)', default=45.0, validators=[DataRequired(), NumberRange(min=0, max=100)])
    perc_prot = FloatField('Proteínas (%)', default=20.0, validators=[DataRequired(), NumberRange(min=0, max=100)])
    perc_gord = FloatField('Gorduras (%)', default=35.0, validators=[DataRequired(), NumberRange(min=0, max=100)])
    num_refeicoes_grandes = IntegerField('Nº de Refeições Grandes', default=3,
                                         validators=[DataRequired(), NumberRange(min=0)])
    num_refeicoes_pequenas = IntegerField('Nº de Refeições Pequenas', default=3,
                                          validators=[DataRequired(), NumberRange(min=0)])
    perc_dist_grandes = IntegerField('% Calorias nas Refeições Grandes', default=70,
                                     validators=[DataRequired(), NumberRange(min=0, max=100)])
    refeicoes_grandes_ajustadas = FieldList(FormField(MacroEntryForm), min_entries=0)
    refeicoes_pequenas_ajustadas = FieldList(FormField(MacroEntryForm), min_entries=0)

# Em app.py, adicione este novo formulário

class AlimentoForm(FlaskForm):
    nome = StringField('Nome do Alimento', validators=[DataRequired()])
    marca = StringField('Marca', default='Genérico')
    kcal_100g = FloatField('Calorias (kcal) / 100g', validators=[DataRequired(), NumberRange(min=0)])
    carboidratos_100g = FloatField('Carboidratos (g) / 100g', validators=[DataRequired(), NumberRange(min=0)])
    proteinas_100g = FloatField('Proteínas (g) / 100g', validators=[DataRequired(), NumberRange(min=0)])
    gorduras_100g = FloatField('Gorduras (g) / 100g', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Salvar Alimento')

# --- PROCESSADOR DE CONTEXTO ---
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now(timezone.utc).year}


# --- FUNÇÕES AUXILIARES ---
def enviar_email_boas_vindas(paciente_obj):
    if not app.config.get('MAIL_USERNAME') or app.config.get('MAIL_USERNAME') == 'SEU_EMAIL_AQUI@example.com':
        return
    try:
        html_corpo_email = render_template('email/boas_vindas_paciente.html', paciente=paciente_obj)
        msg = Message(subject="Seja Bem-vindo(a) à Nossa Plataforma!", recipients=[paciente_obj.email],
                      html=html_corpo_email)
        mail.send(msg)
    except Exception as e:
        flash(f"Erro ao enviar email de boas-vindas: {str(e)}", "warning")


# --- ROTAS DA APLICAÇÃO ---
@app.route('/')
@app.route('/home')
def home():
    total_pacientes = Paciente.query.count()
    return render_template('home_dashboard.html', titulo="Dashboard Nutricionista", request=request,
                           total_pacientes=total_pacientes)


@app.route('/pacientes')
def listar_pacientes():
    page = request.args.get('page', 1, type=int)
    pacientes = Paciente.query.order_by(Paciente.nome_completo.asc()).paginate(page=page, per_page=10)
    return render_template('pacientes_listar.html', pacientes=pacientes, titulo="Lista de Pacientes", request=request)


@app.route('/paciente/novo', methods=['GET', 'POST'])
def novo_paciente():
    form = PacienteForm()
    if form.validate_on_submit():
        novo_pac = Paciente()
        form.populate_obj(novo_pac)
        db.session.add(novo_pac)
        db.session.commit()
        enviar_email_boas_vindas(novo_pac)
        flash('Paciente cadastrado com sucesso!', 'success')
        return redirect(url_for('detalhe_paciente', paciente_id=novo_pac.id))
    elif request.method == 'POST':
        flash('Por favor, corrija os erros no formulário.', 'danger')
    return render_template('paciente_formulario.html', titulo='Novo Paciente', form=form, edit_mode=False)


@app.route('/paciente/<int:paciente_id>')
def detalhe_paciente(paciente_id):
    paciente_obj = Paciente.query.get_or_404(paciente_id)
    planos_salvos = PlanoAlimentar.query.filter_by(paciente_id=paciente_id).order_by(PlanoAlimentar.data_criacao.desc()).all()
    return render_template('paciente_detalhe.html',
                           titulo=f"Detalhes de {paciente_obj.nome_completo}",
                           paciente=paciente_obj,
                           planos=planos_salvos)


@app.route('/paciente/<int:paciente_id>/editar', methods=['GET', 'POST'])
def editar_paciente(paciente_id):
    paciente_obj = Paciente.query.get_or_404(paciente_id)
    form = PacienteForm(obj=paciente_obj)
    if form.validate_on_submit():
        form.populate_obj(paciente_obj)
        db.session.commit()
        flash('Dados do paciente atualizados com sucesso!', 'success')
        return redirect(url_for('detalhe_paciente', paciente_id=paciente_obj.id))
    elif request.method == 'POST':
        flash('Por favor, corrija os erros no formulário.', 'danger')
    return render_template('paciente_formulario.html', titulo=f'Editar Paciente: {paciente_obj.nome_completo}',
                           form=form, edit_mode=True)


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
        nova_cons = Consulta()
        form.populate_obj(nova_cons)
        nova_cons.paciente_id = pid
        db.session.add(nova_cons)
        db.session.commit()
        flash(f'Consulta agendada com sucesso!', 'success')
        return redirect(url_for('detalhe_paciente', paciente_id=pid))
    return render_template('consulta_formulario.html', titulo=f'Nova Consulta', form=form, paciente_id=pid)


@app.route('/paciente/<int:paciente_id>/perfil_diabetes/novo', methods=['GET', 'POST'])
def novo_perfil_diabetes(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    form = PerfilDiabetesForm()
    if request.method == 'POST':
        form.fsi_entries.data = [entry for entry in form.fsi_entries.data if
                                 entry['hora'] or entry['valor'] is not None]
        form.rc_entries.data = [entry for entry in form.rc_entries.data if entry['hora'] or entry['valor'] is not None]
        form.basal_entries.data = [entry for entry in form.basal_entries.data if
                                   entry['hora'] or entry['valor'] is not None]
        form.meta_entries.data = [entry for entry in form.meta_entries.data if
                                  entry['hora'] or entry['valor_baixo'] is not None or entry['valor_alto'] is not None]
    if form.validate_on_submit():
        novo_perfil = PerfilDiabetes(paciente_id=paciente.id)
        novo_perfil.nome_perfil = form.nome_perfil.data
        novo_perfil.data_inicio_validade = form.data_inicio_validade.data
        novo_perfil.dia = form.dia.data
        novo_perfil.fuso_horario = form.fuso_horario.data
        novo_perfil.unidade_glicemia = form.unidade_glicemia.data
        novo_perfil.taxa_absorcao_carb = form.taxa_absorcao_carb.data
        novo_perfil.set_fsi(form.fsi_entries.data)
        novo_perfil.set_rc(form.rc_entries.data)
        novo_perfil.set_basal(form.basal_entries.data)
        novo_perfil.set_metas(form.meta_entries.data)
        db.session.add(novo_perfil)
        db.session.commit()
        flash('Novo perfil de diabetes criado com sucesso!', 'success')
        return redirect(url_for('detalhe_paciente', paciente_id=paciente.id))
    elif request.method == 'POST' and form.errors:
        flash('Por favor, corrija os erros no formulário.', 'danger')
    return render_template('perfil_diabetes_formulario.html',
                           titulo=f"Novo Perfil de Diabetes para {paciente.nome_completo}",
                           form=form,
                           paciente=paciente)


@app.route('/ferramentas/calculadora_calorias', methods=['GET', 'POST'])
def calculadora_calorias():
    form = NecessidadeCaloricaForm()
    resultado = None
    if form.validate_on_submit():
        resultado = calcular_necessidade_calorica(
            peso_kg=form.peso.data, altura_cm=form.altura.data, idade_anos=form.idade.data,
            sexo=form.sexo.data, nivel_atividade=form.nivel_atividade.data, objetivo=form.objetivo.data
        )
        if resultado is None:
            flash("Ocorreu um erro no cálculo. Verifique os dados inseridos.", "danger")
    return render_template('calculadora_calorias.html',
                           titulo="Calculadora de Necessidade Calórica",
                           form=form,
                           resultado=resultado)


@app.route('/ferramentas/distribuicao_macros', methods=['GET', 'POST'])
def distribuicao_macros():
    form = DistribuicaoMacrosForm(request.form)
    resultado_final = None
    if request.method == 'POST' and form.validate_on_submit() and request.form.get('action') == 'calcular':
        soma_perc = form.perc_carb.data + form.perc_prot.data + form.perc_gord.data
        if round(soma_perc) != 100:
            flash("A soma das porcentagens de macronutrientes deve ser 100%.", "danger")
        else:
            macros_em_gramas = calcular_macros_por_porcentagem(
                total_kcal=form.total_kcal.data, perc_carb=form.perc_carb.data,
                perc_prot=form.perc_prot.data, perc_gord=form.perc_gord.data
            )
            if macros_em_gramas:
                peso_kg = form.peso.data
                macros_em_gramas['gkg_prot'] = round(macros_em_gramas['proteina'] / peso_kg, 2)
                macros_em_gramas['gkg_carb'] = round(macros_em_gramas['carboidrato'] / peso_kg, 2)
                macros_em_gramas['gkg_gord'] = round(macros_em_gramas['gordura'] / peso_kg, 2)
                distribuicao_refeicoes = distribuir_macros_nas_refeicoes(
                    macros_em_gramas=macros_em_gramas, num_grandes=form.num_refeicoes_grandes.data,
                    num_pequenas=form.num_refeicoes_pequenas.data, perc_dist_grandes=form.perc_dist_grandes.data
                )
                resultado_final = {
                    'total_macros': macros_em_gramas, 'distribuicao': distribuicao_refeicoes,
                    'num_refeicoes_grandes': form.num_refeicoes_grandes.data,
                    'num_refeicoes_pequenas': form.num_refeicoes_pequenas.data
                }
                form.refeicoes_grandes_ajustadas.entries = []
                for _ in range(form.num_refeicoes_grandes.data):
                    form.refeicoes_grandes_ajustadas.append_entry(distribuicao_refeicoes['por_refeicao_grande'])
                form.refeicoes_pequenas_ajustadas.entries = []
                for _ in range(form.num_refeicoes_pequenas.data):
                    form.refeicoes_pequenas_ajustadas.append_entry(distribuicao_refeicoes['por_refeicao_pequena'])
    elif request.method == 'POST' and not form.validate():
        flash("Por favor, corrija os erros no formulário.", "danger")
    return render_template('distribuicao_macros.html',
                           titulo="Calculadora de Distribuição de Macros",
                           form=form,
                           resultado=resultado_final)


@app.route('/paciente/<int:paciente_id>/plano/novo', methods=['GET', 'POST'])
def novo_plano(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    dist_form = DistribuicaoMacrosForm(request.form)
    resultados_distribuicao = None
    resultados_busca = []
    termo_busca = ""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'calcular_macros' and dist_form.validate():
            macros_em_gramas = calcular_macros_por_porcentagem(
                total_kcal=dist_form.total_kcal.data,
                perc_carb=dist_form.perc_carb.data,
                perc_prot=dist_form.perc_prot.data,
                perc_gord=dist_form.perc_gord.data
            )
            if macros_em_gramas:
                distribuicao_refeicoes = distribuir_macros_nas_refeicoes(
                    macros_em_gramas,
                    dist_form.num_refeicoes_grandes.data,
                    dist_form.num_refeicoes_pequenas.data,
                    dist_form.perc_dist_grandes.data
                )
                resultados_distribuicao = {
                    'total_macros': macros_em_gramas,
                    'distribuicao': distribuicao_refeicoes
                }
        elif action == 'buscar_alimentos':
            termo_busca = request.form.get('alimento_busca', '')
            if termo_busca:
                try:
                    alimentos_encontrados = fs.foods_search(termo_busca)
                    for alimento in alimentos_encontrados:
                        descricao = alimento['food_description']
                        kcal = re.search(r'Calories: (\d+kcal)', descricao)
                        gorduras = re.search(r'Fat: ([\d.]+)g', descricao)
                        carboidratos = re.search(r'Carbs: ([\d.]+)g', descricao)
                        proteinas = re.search(r'Protein: ([\d.]+)g', descricao)
                        resultados_busca.append({
                            'nome': alimento['food_name'],
                            'marca': alimento.get('brand_name', 'Genérico'),
                            'descricao_completa': descricao,
                            'kcal': int(kcal.group(1).replace('kcal', '')) if kcal else 0
                        })
                except Exception as e:
                    flash(f"Ocorreu um erro ao buscar os alimentos: {e}", "danger")
    return render_template('plano_formulario.html',
                           titulo=f"Novo Plano para {paciente.nome_completo}",
                           paciente=paciente,
                           dist_form=dist_form,
                           resultados_distribuicao=resultados_distribuicao,
                           resultados_busca=resultados_busca,
                           termo_busca=termo_busca)


@app.route('/sobre')
def sobre():
    return render_template('sobre.html', titulo="Sobre a Plataforma")


@app.route('/api/calcular_distribuicao', methods=['POST'])
def api_calcular_distribuicao():
    dados = request.get_json()
    if not dados:
        return jsonify({'sucesso': False, 'erro': 'Dados não recebidos'}), 400
    try:
        macros_em_gramas = calcular_macros_por_porcentagem(
            total_kcal=int(dados['total_kcal']),
            perc_carb=float(dados['perc_carb']),
            perc_prot=float(dados['perc_prot']),
            perc_gord=float(dados['perc_gord'])
        )
        if not macros_em_gramas:
            return jsonify({'sucesso': False, 'erro': 'Erro no cálculo de macros.'}), 400
        distribuicao_refeicoes = distribuir_macros_nas_refeicoes(
            macros_em_gramas,
            int(dados['num_refeicoes_grandes']),
            int(dados['num_refeicoes_pequenas']),
            int(dados['perc_dist_grandes'])
        )
        if not distribuicao_refeicoes:
            return jsonify({'sucesso': False, 'erro': 'Erro na distribuição de refeições.'}), 400
        distribuicao_refeicoes['total_macros'] = macros_em_gramas
        distribuicao_refeicoes['num_refeicoes_grandes'] = int(dados['num_refeicoes_grandes'])
        distribuicao_refeicoes['num_refeicoes_pequenas'] = int(dados['num_refeicoes_pequenas'])
        return jsonify({'sucesso': True, 'resultado': distribuicao_refeicoes})
    except (ValueError, TypeError) as e:
        return jsonify({'sucesso': False, 'erro': f'Erro de tipo ou valor nos dados: {e}'}), 400


# Em app.py, SUBSTITUA a rota /api/buscar_alimentos inteira por esta nova versão:

@app.route('/api/buscar_alimentos', methods=['GET'])
def api_buscar_alimentos():
    termo_busca = request.args.get('q', '')
    if not termo_busca:
        return jsonify({'sucesso': False, 'erro': 'Nenhum termo de busca fornecido.'}), 400

    # URL da API do Open Food Facts para o Brasil
    url_api = "https://br.openfoodfacts.org/cgi/search.pl"

    params = {
        "search_terms": termo_busca,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 20
    }

    try:
        response = requests.get(url_api, params=params)
        response.raise_for_status()
        dados_api = response.json()

        resultados = []
        for produto in dados_api.get("products", []):
            nutrientes = produto.get('nutriments', {})

            # Pega o nome em português, se não existir, pega o nome genérico
            nome = produto.get('product_name_pt', produto.get('product_name', 'Nome não disponível'))

            # Pega os valores nutricionais, usando 0 como padrão se não existir
            kcal = nutriente = nutrientes.get('energy-kcal_100g', 0)
            carboidratos = nutrientes.get('carbohydrates_100g', 0)
            proteinas = nutrientes.get('proteins_100g', 0)
            gorduras = nutrientes.get('fat_100g', 0)

            # Para manter a consistência com o formato do FatSecret, criamos uma descrição
            descricao = f"Por 100g - Calorias: {kcal}kcal | Carb: {carboidratos}g | Prot: {proteinas}g | Gord: {gorduras}g"

            # Adicionamos o alimento à lista de resultados
            resultados.append({
                'id': produto.get('code', ''),  # Usamos o código de barras como ID
                'nome': nome,
                'marca': produto.get('brands', 'Marca não informada'),
                'descricao': descricao,
                'kcal_100g': kcal,
                'gorduras_100g': gorduras,
                'carboidratos_100g': carboidratos,
                'proteinas_100g': proteinas
            })

        return jsonify({'sucesso': True, 'resultados': resultados})

    except requests.exceptions.RequestException as e:
        return jsonify({'sucesso': False, 'erro': f'Ocorreu um erro de comunicação com a API: {e}'}), 500
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': f'Ocorreu um erro inesperado ao processar os dados: {e}'}), 500

@app.route('/api/paciente/<int:paciente_id>/plano/salvar', methods=['POST'])
def api_salvar_plano(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    dados_plano = request.get_json()
    if not dados_plano:
        return jsonify({'sucesso': False, 'erro': 'Nenhum dado recebido.'}), 400
    try:
        novo_plano = PlanoAlimentar(
            paciente_id=paciente.id,
            nome_plano=dados_plano.get('nome_plano', 'Plano Padrão'),
            objetivo_calorico_final=dados_plano.get('objetivo_calorico')
        )
        db.session.add(novo_plano)
        db.session.flush()
        for refeicao_data in dados_plano.get('refeicoes', []):
            nova_refeicao = Refeicao(
                plano_id=novo_plano.id,
                nome_refeicao=refeicao_data.get('nome'),
                meta_carboidratos_g=refeicao_data['metas']['carboidrato'],
                meta_proteinas_g=refeicao_data['metas']['proteina'],
                meta_gorduras_g=refeicao_data['metas']['gordura']
            )
            db.session.add(nova_refeicao)
            db.session.flush()
            for item_data in refeicao_data.get('itens', []):
                novo_item = ItemRefeicao(
                    refeicao_id=nova_refeicao.id,
                    nome_alimento=item_data.get('nome'),
                    marca_alimento=item_data.get('marca'),
                    quantidade_g=item_data.get('quantidade'),
                    medida_caseira=item_data.get('medida_caseira'),
                    substituicoes=item_data.get('substituicoes'),
                    carboidratos_g=item_data['macros']['carboidratos'],
                    proteinas_g=item_data['macros']['proteinas'],
                    gorduras_g=item_data['macros']['gorduras'],
                    kcal=item_data['macros']['kcal']
                )
                db.session.add(novo_item)
        db.session.commit()
        return jsonify({
            'sucesso': True,
            'mensagem': 'Plano alimentar salvo com sucesso!',
            'redirect_url': url_for('detalhe_paciente', paciente_id=paciente.id)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao salvar no banco de dados: {str(e)}'}), 500

@app.route('/plano/<int:plano_id>/pdf')
def gerar_plano_pdf(plano_id):
    plano = PlanoAlimentar.query.get_or_404(plano_id)
    paciente = plano.paciente
    data_hoje = datetime.now(timezone.utc).strftime('%d/%m/%Y')

    html_renderizado = render_template('plano_pdf_template.html',
                                     plano=plano,
                                     paciente=paciente,
                                     data_hoje=data_hoje)

    pdf = HTML(string=html_renderizado).write_pdf()

    return Response(pdf,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': 'inline; filename=plano_alimentar.pdf'})


# Em app.py, adicione esta nova rota de API

@app.route('/api/alimentos/salvar', methods=['POST'])
def api_salvar_alimento():
    dados_alimento = request.get_json()

    # Validação básica dos dados recebidos
    if not dados_alimento or not dados_alimento.get('fatsecret_food_id'):
        return jsonify({'sucesso': False, 'erro': 'Dados do alimento inválidos.'}), 400

    # Verifica se o alimento já foi salvo para evitar duplicatas
    id_fatsecret = dados_alimento.get('fatsecret_food_id')
    alimento_existente = Alimento.query.filter_by(fatsecret_food_id=id_fatsecret).first()

    if alimento_existente:
        return jsonify(
            {'sucesso': False, 'erro': 'Este alimento já está salvo em "Meus Alimentos".'}), 409  # 409 Conflict

    try:
        # Cria um novo objeto Alimento com os dados recebidos
        novo_alimento = Alimento(
            nome=dados_alimento.get('nome'),
            marca=dados_alimento.get('marca'),
            kcal_100g=dados_alimento.get('kcal_100g'),
            carboidratos_100g=dados_alimento.get('carboidratos_100g'),
            proteinas_100g=dados_alimento.get('proteinas_100g'),
            gorduras_100g=dados_alimento.get('gorduras_100g'),
            origem='FatSecret',
            fatsecret_food_id=id_fatsecret
        )
        db.session.add(novo_alimento)
        db.session.commit()

        return jsonify({'sucesso': True, 'mensagem': f"'{novo_alimento.nome}' salvo com sucesso!"})

    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao salvar no banco de dados: {str(e)}'}), 500

# Em app.py, adicione esta nova rota

@app.route('/meus_alimentos')
def listar_meus_alimentos():
    page = request.args.get('page', 1, type=int)
    termo_busca = request.args.get('busca', '')

    query_base = Alimento.query

    if termo_busca:
        # Filtra por nome do alimento, ignorando maiúsculas/minúsculas
        query_base = query_base.filter(Alimento.nome.ilike(f'%{termo_busca}%'))

    alimentos_paginados = query_base.order_by(Alimento.nome.asc()).paginate(page=page, per_page=20)

    return render_template('meus_alimentos.html',
                           titulo="Meu Banco de Alimentos",
                           alimentos=alimentos_paginados,
                           termo_busca=termo_busca)

# Em app.py, adicione estas novas rotas

@app.route('/meus_alimentos/novo', methods=['GET', 'POST'])
def novo_alimento():
    form = AlimentoForm()
    if form.validate_on_submit():
        novo_alimento = Alimento()
        form.populate_obj(novo_alimento)
        db.session.add(novo_alimento)
        db.session.commit()
        flash(f"Alimento '{novo_alimento.nome}' cadastrado com sucesso!", 'success')
        return redirect(url_for('listar_meus_alimentos'))
    return render_template('alimento_formulario.html',
                           titulo="Adicionar Novo Alimento",
                           form=form)

@app.route('/meus_alimentos/<int:alimento_id>/editar', methods=['GET', 'POST'])
def editar_alimento(alimento_id):
    alimento = Alimento.query.get_or_404(alimento_id)
    form = AlimentoForm(obj=alimento)
    if form.validate_on_submit():
        form.populate_obj(alimento)
        db.session.commit()
        flash(f"Alimento '{alimento.nome}' atualizado com sucesso!", 'success')
        return redirect(url_for('listar_meus_alimentos'))
    return render_template('alimento_formulario.html',
                           titulo="Editar Alimento",
                           form=form)

# Em app.py, adicione esta rota para excluir

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


# Em app.py, adicione esta nova rota de API

@app.route('/api/meus_alimentos/buscar')
def api_buscar_meus_alimentos():
    termo_busca = request.args.get('q', '')
    if not termo_busca:
        return jsonify({'sucesso': False, 'erro': 'Termo de busca vazio.'}), 400

    # Busca no nosso banco de dados local
    alimentos_encontrados = Alimento.query.filter(Alimento.nome.ilike(f'%{termo_busca}%')).limit(20).all()

    # Formata os resultados para enviar como JSON
    resultados = []
    for alimento in alimentos_encontrados:
        resultados.append({
            'id': alimento.id,  # ID do nosso banco local
            'nome': alimento.nome,
            'marca': alimento.marca,
            'kcal_100g': alimento.kcal_100g,
            'carboidratos_100g': alimento.carboidratos_100g,
            'proteinas_100g': alimento.proteinas_100g,
            'gorduras_100g': alimento.gorduras_100g,
            'origem': 'local'  # Identifica que veio do nosso banco
        })

    return jsonify({'sucesso': True, 'resultados': resultados})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)