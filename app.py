# app.py (Versão final com pyhanko - io.BytesIO)
import io # <--- Importação necessária
import os
import tempfile
import traceback
from datetime import datetime, timezone

import requests
from calculadoras import (calcular_necessidade_calorica,
                          distribuir_macros_nas_refeicoes,
                          calcular_macros_por_porcentagem, somar_macros_refeicoes)
from flask import (Flask, Response, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from weasyprint import HTML
from wtforms import (DateField, FieldList, FloatField, FormField, IntegerField,
                     SelectField, StringField, SubmitField, TextAreaField)
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Email as EmailValidator, NumberRange, Optional

# Imports da pyhanko
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigFieldSpec, append_signature_field
from pyhanko.sign.signers import PdfSignatureMetadata, SimpleSigner, sign_pdf

# ... (o resto do seu código, modelos, forms, etc. permanece exatamente igual) ...
app = Flask(__name__)

# --- CONFIGURAÇÕES GERAIS DO APP ---
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plataforma_nutri.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- FUNÇÃO DE CACHE BUSTING ---
@app.context_processor
def utility_processor():
    def cache_buster(filename):
        try:
            filepath = os.path.join(app.static_folder, filename)
            if os.path.exists(filepath):
                return int(os.path.getmtime(filepath))
        except:
            return 0
    return dict(cache_buster=cache_buster)

# --- MODELOS DO BANCO DE DADOS ---
class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    peso = db.Column(db.Float, nullable=True)
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
    nome = db.Column(db.String(200), nullable=False)
    marca = db.Column(db.String(150), nullable=True)
    kcal_100g = db.Column(db.Float, nullable=False, default=0)
    carboidratos_100g = db.Column(db.Float, nullable=False, default=0)
    proteinas_100g = db.Column(db.Float, nullable=False, default=0)
    gorduras_100g = db.Column(db.Float, nullable=False, default=0)
    origem = db.Column(db.String(50), default='manual')
    fatsecret_food_id = db.Column(db.String(50), unique=True, nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

# --- FORMULÁRIOS (Flask-WTF) ---
class PacienteForm(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), EmailValidator()])
    telefone = StringField('Telefone')
    data_nascimento = DateField('Data de Nascimento (AAAA-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    peso = FloatField('Peso (kg)', validators=[Optional(), NumberRange(min=0)])
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

# ... (outras rotas) ...
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

@app.route('/plano/<int:plano_id>/pdf')
def gerar_plano_pdf(plano_id):
    plano = PlanoAlimentar.query.get_or_404(plano_id)
    paciente = plano.paciente
    data_hoje = datetime.now(timezone.utc).strftime('%d/%m/%Y')
    html_renderizado = render_template('plano_pdf_template.html', plano=plano, paciente=paciente, data_hoje=data_hoje)
    pdf = HTML(string=html_renderizado, base_url=request.base_url).write_pdf()
    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition': 'inline; filename=plano_alimentar.pdf'})

@app.route('/plano/<int:plano_id>/assinar', methods=['GET', 'POST'])
def assinar_plano_pdf(plano_id):
    plano = PlanoAlimentar.query.get_or_404(plano_id)
    if request.method == 'POST':
        if 'certificado' not in request.files:
            flash('Nenhum arquivo de certificado enviado.', 'danger')
            return redirect(request.url)
        file = request.files['certificado']
        senha = request.form.get('senha_certificado', '')
        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(request.url)
        if not senha:
            flash('A senha do certificado é obrigatória.', 'danger')
            return redirect(request.url)
        if file and file.filename.endswith(('.p12', '.pfx')):
            temp_cert_path = None
            try:
                paciente = plano.paciente
                data_hoje = datetime.now(timezone.utc).strftime('%d/%m/%Y')
                html_renderizado = render_template('plano_pdf_template.html', plano=plano, paciente=paciente, data_hoje=data_hoje)
                pdf_original_bytes = HTML(string=html_renderizado, base_url=request.base_url).write_pdf()

                certificado_bytes = file.read()
                
                # --- LÓGICA DE ASSINATURA ROBUSTA ---
                # 1. Salva o certificado em um arquivo temporário
                fd, temp_cert_path = tempfile.mkstemp(suffix='.pfx')
                with os.fdopen(fd, 'wb') as temp_file:
                    temp_file.write(certificado_bytes)
                
                # 2. Carrega o assinador a partir do CAMINHO do arquivo
                #    A senha pode ser passada como bytes utf-8, que é mais padrão
                signer = SimpleSigner.load_pkcs12(
                    pfx_file=temp_cert_path, 
                    passphrase=senha.encode('utf-8') 
                )
                
                # 3. Transforma o PDF gerado em um stream em memória para o pyhanko ler
                pdf_stream = io.BytesIO(pdf_original_bytes)
                pdf_writer = IncrementalPdfFileWriter(pdf_stream)
                # --- FIM DA LÓGICA ---

                append_signature_field(pdf_writer, SigFieldSpec(sig_field_name='Signature1'))

                pdf_assinado_bytes = sign_pdf(
                    pdf_writer,
                    PdfSignatureMetadata(field_name='Signature1'),
                    signer=signer,
                )

                return Response(
                    pdf_assinado_bytes,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': f'attachment; filename=plano_assinado_{paciente.nome_completo.split()[0].lower()}.pdf'}
                )
            except Exception as e:
                traceback.print_exc()
                error_string = str(e).upper()
                if 'MAC' in error_string or 'PASSWORD' in error_string or 'DECRYPTION' in error_string:
                     flash('Erro ao decifrar o certificado. A senha está correta?', 'danger')
                else:
                    flash(f'Ocorreu um erro inesperado: {str(e)}', 'danger')
                return redirect(request.url)
            finally:
                # Garante que o arquivo temporário seja sempre apagado
                if temp_cert_path and os.path.exists(temp_cert_path):
                    os.remove(temp_cert_path)
        else:
            flash('Formato de arquivo inválido. Por favor, envie um arquivo .p12 ou .pfx.', 'danger')
            return redirect(request.url)
    return render_template('assinar_plano.html', titulo=f"Assinar Plano de {plano.paciente.nome_completo}", plano=plano)

# ... (resto das rotas da API) ...
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
        novo_alimento = Alimento()
        form.populate_obj(novo_alimento)
        db.session.add(novo_alimento)
        db.session.commit()
        flash(f"Alimento '{novo_alimento.nome}' cadastrado com sucesso!", 'success')
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
        soma_ajustada = somar_macros_refeicoes(form.refeicoes_grandes_ajustadas.data, form.refeicoes_pequenas_ajustadas.data)
        flash(f"Soma manual recalculada: Carboidratos: {soma_ajustada['carboidrato']:.1f}g, Proteínas: {soma_ajustada['proteina']:.1f}g, Gorduras: {soma_ajustada['gordura']:.1f}g.", 'info')
        return render_template('distribuicao_macros.html', titulo="Calculadora de Distribuição de Macros", form=form, resultado=None)
    return render_template('distribuicao_macros.html', titulo="Calculadora de Distribuição de Macros", form=form, resultado=resultado_final)

@app.route('/api/calcular_distribuicao', methods=['POST'])
def api_calcular_distribuicao():
    dados = request.get_json()
    try:
        macros_em_gramas = calcular_macros_por_porcentagem(total_kcal=int(dados['total_kcal']), perc_carb=float(dados['perc_carb']), perc_prot=float(dados['perc_prot']), perc_gord=float(dados['perc_gord']))
        distribuicao_refeicoes = distribuir_macros_nas_refeicoes(macros_em_gramas, int(dados['num_refeicoes_grandes']), int(dados['num_refeicoes_pequenas']), int(dados['perc_dist_grandes']))
        distribuicao_refeicoes['num_refeicoes_grandes'] = int(dados['num_refeicoes_grandes'])
        distribuicao_refeicoes['num_refeicoes_pequenas'] = int(dados['num_refeicoes_pequenas'])
        return jsonify({'sucesso': True, 'resultado': distribuicao_refeicoes})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 400

@app.route('/api/alimentos/autocomplete')
def api_alimentos_autocomplete():
    termo_busca = request.args.get('q', '')
    if len(termo_busca) < 2:
        return jsonify([])
    resultados = []
    alimentos_locais = Alimento.query.filter(Alimento.nome.ilike(f'%{termo_busca}%')).limit(5).all()
    for alimento in alimentos_locais:
        resultados.append({
            'value': f"local-{alimento.id}", 'text': f"{alimento.nome} ({alimento.marca})",
            'dados_completos': { 'id': alimento.id, 'nome': alimento.nome, 'marca': alimento.marca, 'kcal_100g': alimento.kcal_100g, 'carboidratos_100g': alimento.carboidratos_100g, 'proteinas_100g': alimento.proteinas_100g, 'gorduras_100g': alimento.gorduras_100g, 'origem': 'local' }
        })
    try:
        url_api = "https://br.openfoodfacts.org/cgi/search.pl"
        params = {"search_terms": termo_busca, "search_simple": 1, "action": "process", "json": 1, "page_size": 5}
        response = requests.get(url_api, params=params, timeout=5)
        response.raise_for_status()
        dados_api = response.json()
        for produto in dados_api.get("products", []):
            nutrientes = produto.get('nutriments', {})
            nome = produto.get('product_name_pt', produto.get('product_name', 'N/A'))
            marca = produto.get('brands', 'N/A')
            if nome == 'N/A': continue
            kcal = nutrientes.get('energy-kcal_100g', 0) or 0
            carbs = nutrientes.get('carbohydrates_100g', 0) or 0
            prot = nutrientes.get('proteins_100g', 0) or 0
            gord = nutrientes.get('fat_100g', 0) or 0
            resultados.append({
                'value': produto.get('code', ''), 'text': f"{nome} ({marca}) - [Online]",
                'dados_completos': { 'id': produto.get('code', ''), 'nome': nome, 'marca': marca, 'kcal_100g': kcal, 'carboidratos_100g': carbs, 'proteinas_100g': prot, 'gorduras_100g': gord, 'origem': 'online' }
            })
    except requests.exceptions.RequestException:
        pass
    return jsonify(resultados)
    
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
        return jsonify({'sucesso': True, 'mensagem': 'Plano salvo com sucesso!', 'redirect_url': url_for('detalhe_paciente', paciente_id=paciente_id)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao salvar: {str(e)}'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)