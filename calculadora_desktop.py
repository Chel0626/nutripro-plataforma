import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from functools import partial
from calculadoras import * # Assumindo que este módulo existe e está correto

# --- Variáveis globais para armazenar dados e widgets ---
ultimo_resultado = {}
widgets_refeicoes = {'grandes': [], 'pequenas': []}
entry_old_values = {}


# --- FUNÇÕES DE CÁLCULO E AÇÕES DA INTERFACE ---

def executar_calculo_calorias():
    """Calcula a necessidade calórica e exibe os resultados na primeira aba."""
    global ultimo_resultado
    try:
        peso = float(entry_peso.get())
        altura = float(entry_altura.get())
        idade = int(entry_idade.get())
        sexo = combo_sexo.get().lower()
        map_nivel_atividade = {'Sedentário (pouco ou nenhum exercício)': 'sedentario',
                               'Levemente Ativo (exercício 1-3 dias/semana)': 'leve',
                               'Moderadamente Ativo (exercício 3-5 dias/semana)': 'moderado',
                               'Muito Ativo (exercício 6-7 dias/semana)': 'ativo',
                               'Extremamente Ativo (exercício muito pesado/trabalho físico)': 'extremo'}
        nivel_atividade = map_nivel_atividade.get(combo_nivel_atividade.get())
        map_objetivo = {'Perder Peso': 'perder', 'Manter Peso': 'manter', 'Ganhar Peso': 'ganhar'}
        objetivo = map_objetivo.get(combo_objetivo.get())

        resultado_calorias = calcular_necessidade_calorica(
            peso_kg=peso, altura_cm=altura, idade_anos=idade, sexo=sexo,
            nivel_atividade=nivel_atividade, objetivo=objetivo
        )

        if resultado_calorias:
            ultimo_resultado['resultado_calorias'] = resultado_calorias
            ultimo_resultado['peso'] = peso
            label_resultado_tmb_cal.config(text=f"Taxa Metabólica Basal (TMB): {resultado_calorias['tmb']} kcal/dia")
            label_resultado_fator_cal.config(
                text=f"Fator de Atividade (NAF): x {resultado_calorias['fator_atividade']}")
            label_resultado_manutencao_cal.config(
                text=f"Calorias para Manutenção: {resultado_calorias['calorias_manutencao']} kcal/dia")
            label_resultado_objetivo_cal.config(
                text=f"Meta para Objetivo: {resultado_calorias['calorias_objetivo']} kcal/dia", foreground="blue")
        else:
            messagebox.showerror("Erro",
                                 "Não foi possível calcular. Verifique se todos os campos foram preenchidos corretamente.")

    except (ValueError, TypeError):
        messagebox.showerror("Erro de Entrada",
                             "Por favor, insira valores numéricos válidos para peso, altura e idade.")


def copiar_resultados_calorias():
    """Copia os resultados da primeira aba para a área de transferência."""
    global ultimo_resultado
    if 'resultado_calorias' in ultimo_resultado:
        res = ultimo_resultado['resultado_calorias']
        texto_para_copiar = (
            f"Resultados do Cálculo de Necessidade Calórica:\n"
            f"---------------------------------------------\n"
            f"Taxa Metabólica Basal (TMB): {res['tmb']} kcal/dia\n"
            f"Fator de Atividade (NAF): x {res['fator_atividade']}\n"
            f"Calorias para Manutenção: {res['calorias_manutencao']} kcal/dia\n"
            f"Meta para Objetivo: {res['calorias_objetivo']} kcal/dia\n"
        )
        root.clipboard_clear()
        root.clipboard_append(texto_para_copiar)
        messagebox.showinfo("Copiado!", "Os resultados foram copiados para a área de transferência.")
    else:
        messagebox.showwarning("Aviso", "Calcule a necessidade calórica primeiro antes de copiar.")


def ir_para_distribuicao():
    """Muda para a segunda aba e preenche os campos com os resultados da primeira."""
    global ultimo_resultado
    if 'resultado_calorias' in ultimo_resultado and 'peso' in ultimo_resultado:
        resultado_calorias = ultimo_resultado['resultado_calorias']
        peso = ultimo_resultado['peso']
        entry_total_kcal_macro.delete(0, tk.END)
        entry_total_kcal_macro.insert(0, str(resultado_calorias['calorias_objetivo']))
        entry_peso_paciente_macro.delete(0, tk.END)
        entry_peso_paciente_macro.insert(0, str(peso))
        notebook.select(tab_macros)
    else:
        messagebox.showwarning("Aviso", "Por favor, calcule a necessidade calórica primeiro antes de avançar.")


def executar_calculo_macros(macros_ajustados=None):
    """Calcula a distribuição de macros, usando dados do formulário ou macros ajustados."""
    global ultimo_resultado
    try:
        peso_paciente = float(entry_peso_paciente_macro.get())

        if macros_ajustados is None:
            total_kcal = int(entry_total_kcal_macro.get())
            perc_prot = float(entry_perc_prot.get())
            perc_carb = float(entry_perc_carb.get())
            perc_gord = float(entry_perc_gord.get())
            macros_totais = calcular_macros_por_porcentagem(total_kcal, perc_carb, perc_prot, perc_gord)
            if not macros_totais:
                messagebox.showerror("Erro", "A soma das porcentagens de macronutrientes deve ser 100%.")
                return
        else:
            macros_totais = macros_ajustados

        ultimo_resultado['macros_totais'] = macros_totais
        ultimo_resultado['peso'] = peso_paciente

        atualizar_interface_completa(macros_iniciais=macros_ajustados is None)

    except (ValueError, TypeError):
        messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos para todos os campos.")


def recalcular_totais_manuais():
    """Lê os valores manuais, soma e atualiza a interface."""
    global ultimo_resultado
    try:
        refeicoes_grandes_data = []
        for campos in widgets_refeicoes['grandes']:
            refeicoes_grandes_data.append({
                'proteina': int(campos['prot'].get()),
                'carboidrato': int(campos['carb'].get()),
                'gordura': int(campos['gord'].get())
            })

        refeicoes_pequenas_data = []
        for campos in widgets_refeicoes['pequenas']:
            refeicoes_pequenas_data.append({
                'proteina': int(campos['prot'].get()),
                'carboidrato': int(campos['carb'].get()),
                'gordura': int(campos['gord'].get())
            })

        novos_macros_em_gramas = somar_macros_refeicoes(refeicoes_grandes_data, refeicoes_pequenas_data)

        if novos_macros_em_gramas:
            executar_calculo_macros(macros_ajustados=novos_macros_em_gramas)

    except ValueError:
        messagebox.showerror("Erro", "Valores nas refeições manuais devem ser números inteiros.")


def atualizar_interface_completa(macros_iniciais=False):
    """Atualiza toda a seção de resultados (totais e refeições)."""
    global ultimo_resultado, widgets_refeicoes

    macros_totais = ultimo_resultado.get('macros_totais', {})
    peso_paciente = ultimo_resultado.get('peso')

    if not all([macros_totais, peso_paciente]): return

    prot_gkg = round(macros_totais['proteina'] / peso_paciente, 2)
    carb_gkg = round(macros_totais['carboidrato'] / peso_paciente, 2)
    gord_gkg = round(macros_totais['gordura'] / peso_paciente, 2)

    total_kcal_ajustado = (macros_totais['proteina'] * 4) + (macros_totais['carboidrato'] * 4) + (
            macros_totais['gordura'] * 9)
    label_resultado_prot_total.config(text=f"Proteína: {macros_totais['proteina']} g ({prot_gkg} g/kg)")
    label_resultado_carb_total.config(text=f"Carboidrato: {macros_totais['carboidrato']} g ({carb_gkg} g/kg)")
    label_resultado_gord_total.config(text=f"Gordura: {macros_totais['gordura']} g ({gord_gkg} g/kg)")
    label_kcal_ajustado.config(text=f"Total Ajustado: {total_kcal_ajustado} kcal")

    frame_resultados.grid(column=0, row=13, columnspan=2, sticky='ew', pady=(15, 5))

    if macros_iniciais:
        num_grandes = int(entry_num_grandes.get())
        num_pequenas = int(entry_num_pequenas.get())
        perc_dist_grandes = int(entry_perc_dist_grandes.get())
        distribuicao = distribuir_macros_nas_refeicoes(macros_totais, num_grandes, num_pequenas, perc_dist_grandes)

        for widget in frame_ajuste_manual.winfo_children():
            widget.destroy()
        widgets_refeicoes = {'grandes': [], 'pequenas': []}

        # --- NOVO WIDGET --- Botão para ativar/desativar redistribuição
        check_redistribuicao = ttk.Checkbutton(
            frame_ajuste_manual,
            text="Ativar redistribuição automática de macros",
            variable=redistribuicao_automatica_ativada,
            style="TCheckbutton"
        )
        check_redistribuicao.grid(column=0, row=0, columnspan=4, sticky='w', padx=5, pady=(0, 10))

        # Cria os cabeçalhos para a tabela de ajuste manual
        ttk.Label(frame_ajuste_manual, text="Refeição", style="Bold.TLabel").grid(column=0, row=1, sticky='w', padx=5)
        ttk.Label(frame_ajuste_manual, text="Carboidrato (g)", style="Bold.TLabel").grid(column=1, row=1, padx=5)
        ttk.Label(frame_ajuste_manual, text="Proteína (g)", style="Bold.TLabel").grid(column=2, row=1, padx=5)
        ttk.Label(frame_ajuste_manual, text="Gordura (g)", style="Bold.TLabel").grid(column=3, row=1, padx=5)

        current_row = 2
        if distribuicao and num_grandes > 0:
            ttk.Label(frame_ajuste_manual, text="Refeições Grandes:", style="Bold.TLabel").grid(column=0,
                                                                                                row=current_row,
                                                                                                columnspan=4,
                                                                                                sticky='w',
                                                                                                pady=(10, 2))
            current_row += 1
            for i in range(num_grandes):
                campos = criar_linha_refeicao(frame_ajuste_manual, "Grande", i, current_row,
                                              distribuicao['por_refeicao_grande'])
                widgets_refeicoes['grandes'].append(campos)
                current_row += 1

        if distribuicao and num_pequenas > 0:
            ttk.Label(frame_ajuste_manual, text="Refeições Pequenas:", style="Bold.TLabel").grid(column=0,
                                                                                                 row=current_row,
                                                                                                 columnspan=4,
                                                                                                 sticky='w',
                                                                                                 pady=(10, 2))
            current_row += 1
            for i in range(num_pequenas):
                campos = criar_linha_refeicao(frame_ajuste_manual, "Pequena", i, current_row,
                                              distribuicao['por_refeicao_pequena'])
                widgets_refeicoes['pequenas'].append(campos)
                current_row += 1

        # Botões de ação do ajuste manual
        frame_botoes_ajuste = ttk.Frame(frame_ajuste_manual)
        frame_botoes_ajuste.grid(column=0, row=current_row, pady=10, columnspan=4)
        ttk.Button(frame_botoes_ajuste, text="Recalcular Totais", command=recalcular_totais_manuais).pack(
            side=tk.LEFT,
            padx=5)
        ttk.Button(frame_botoes_ajuste, text="Copiar Plano Completo", command=copiar_plano_completo).pack(
            side=tk.LEFT,
            padx=5)
        ttk.Button(frame_botoes_ajuste, text="Salvar em Arquivo", command=salvar_plano_em_arquivo).pack(
            side=tk.LEFT,
            padx=5)


def gerar_texto_plano_completo():
    """Gera o texto formatado do plano alimentar final."""
    global ultimo_resultado, widgets_refeicoes
    texto = []

    # Seção de Resultados do Cálculo Calórico (se disponível)
    if 'resultado_calorias' in ultimo_resultado:
        res_cal = ultimo_resultado['resultado_calorias']
        texto.append("=== Resultados do Cálculo de Necessidade Calórica ===")
        texto.append(f"TMB: {res_cal['tmb']} kcal/dia")
        texto.append(f"Fator de Atividade (NAF): x {res_cal['fator_atividade']}")
        texto.append(f"Calorias para Manutenção: {res_cal['calorias_manutencao']} kcal/dia")
        texto.append(f"Meta para Objetivo: {res_cal['calorias_objetivo']} kcal/dia")
        texto.append("\n")

    # Seção de Distribuição de Macros
    if 'macros_totais' in ultimo_resultado and 'peso' in ultimo_resultado:
        macros_totais = ultimo_resultado['macros_totais']
        peso_paciente = ultimo_resultado['peso']

        prot_gkg = round(macros_totais['proteina'] / peso_paciente, 2)
        carb_gkg = round(macros_totais['carboidrato'] / peso_paciente, 2)
        gord_gkg = round(macros_totais['gordura'] / peso_paciente, 2)
        total_kcal_ajustado = (macros_totais['proteina'] * 4) + (macros_totais['carboidrato'] * 4) + (
                macros_totais['gordura'] * 9)

        texto.append("=== Distribuição de Macronutrientes ===")
        texto.append(f"Peso do Paciente: {peso_paciente} kg")
        # Ajuste para pegar a meta calórica do resultado de calorias se disponível
        if 'resultado_calorias' in ultimo_resultado:
            texto.append(f"Meta Calórica: {ultimo_resultado['resultado_calorias']['calorias_objetivo']} kcal")
        texto.append(f"Total Ajustado: {total_kcal_ajustado} kcal")
        texto.append(f"Proteína Total: {macros_totais['proteina']} g ({prot_gkg} g/kg)")
        texto.append(f"Carboidrato Total: {macros_totais['carboidrato']} g ({carb_gkg} g/kg)")
        texto.append(f"Gordura Total: {macros_totais['gordura']} g ({gord_gkg} g/kg)")
        texto.append("\n")

        # Detalhes das Refeições
        if widgets_refeicoes['grandes'] or widgets_refeicoes['pequenas']:
            texto.append("=== Detalhamento por Refeição ===")

            if widgets_refeicoes['grandes']:
                texto.append("--- Refeições Grandes ---")
                for i, campos in enumerate(widgets_refeicoes['grandes']):
                    prot = campos['prot'].get()
                    carb = campos['carb'].get()
                    gord = campos['gord'].get()
                    texto.append(f"Refeição Grande {i + 1}: Carb: {carb}g, Prot: {prot}g, Gord: {gord}g")

            if widgets_refeicoes['pequenas']:
                texto.append("\n--- Refeições Pequenas ---")
                for i, campos in enumerate(widgets_refeicoes['pequenas']):
                    prot = campos['prot'].get()
                    carb = campos['carb'].get()
                    gord = campos['gord'].get()
                    texto.append(f"Refeição Pequena {i + 1}: Carb: {carb}g, Prot: {prot}g, Gord: {gord}g")
    else:
        texto.append("Nenhum cálculo de macros realizado ainda.")

    return "\n".join(texto)


def copiar_plano_completo():
    """Copia o plano alimentar final e detalhado para a área de transferência."""
    texto = gerar_texto_plano_completo()
    if texto.strip() and "Nenhum cálculo de macros realizado ainda." not in texto:
        root.clipboard_clear()
        root.clipboard_append(texto)
        messagebox.showinfo("Copiado!", "O plano alimentar completo foi copiado para a área de transferência.")
    else:
        messagebox.showwarning("Aviso", "Não há plano para copiar. Calcule a distribuição primeiro.")


def salvar_plano_em_arquivo():
    """Abre uma janela para salvar o plano em um arquivo de texto."""
    texto = gerar_texto_plano_completo()
    if texto.strip() and "Nenhum cálculo de macros realizado ainda." not in texto:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")],
            title="Salvar Plano Alimentar"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(texto)
                messagebox.showinfo("Salvo!", f"Plano alimentar salvo em: {file_path}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo: {e}")
    else:
        messagebox.showwarning("Aviso", "Não há plano para salvar. Calcule a distribuição primeiro.")


# --- Funções para a Redistribuição Automática ---

def store_old_value(event):
    """Guarda o valor de um campo quando ele ganha foco."""
    global entry_old_values
    widget = event.widget
    try:
        entry_old_values[widget] = int(widget.get())
    except (ValueError, TypeError):
        entry_old_values[widget] = 0


def on_macro_field_change(event, meal_type, changed_index, macro_key):
    """
    Acionado quando um campo de macro perde o foco.
    Calcula a diferença e redistribui entre os outros campos do mesmo tipo.
    --- MODIFICADO: Só executa se o checkbutton estiver ativo. ---
    """
    # Se a redistribuição automática estiver desativada, recalcula os totais e para.
    if not redistribuicao_automatica_ativada.get():
        recalcular_totais_manuais()
        return

    global widgets_refeicoes, entry_old_values
    changed_widget = event.widget

    old_value = entry_old_values.get(changed_widget, 0)

    try:
        new_value = int(changed_widget.get())
    except ValueError:
        changed_widget.delete(0, tk.END)
        changed_widget.insert(0, str(old_value))
        return

    delta = old_value - new_value
    if delta == 0:
        return

    peer_widgets = []
    for i, widget_info in enumerate(widgets_refeicoes[meal_type]):
        if i != changed_index:
            peer_widgets.append(widget_info[macro_key])

    if not peer_widgets:
        recalcular_totais_manuais()
        return

    # Lógica de distribuição melhorada para lidar com restos
    base_redistribution = delta // len(peer_widgets)
    remainder = delta % len(peer_widgets)

    for i, widget in enumerate(peer_widgets):
        try:
            current_peer_value = int(widget.get())
            amount_to_add = base_redistribution
            # Distribui o "resto" da divisão para os primeiros widgets
            if i < remainder:
                amount_to_add += 1

            new_peer_value = current_peer_value + amount_to_add
            widget.delete(0, tk.END)
            widget.insert(0, str(new_peer_value))
        except ValueError:
            continue

    recalcular_totais_manuais()


def criar_linha_refeicao(parent_frame, label_prefix, index_in_type, row_num, data):
    """Cria e retorna uma linha de widgets para uma refeição."""
    ttk.Label(parent_frame, text=f"{label_prefix} {index_in_type + 1}:").grid(column=0, row=row_num, sticky='w')

    meal_type = 'grandes' if 'Grande' in label_prefix else 'pequenas'

    campos = {}
    # Ordem: Carboidrato, Proteína, Gordura
    macro_map = {'carb': 'carboidrato', 'prot': 'proteina', 'gord': 'gordura'}
    col_map = {'carb': 1, 'prot': 2, 'gord': 3}

    for short_name, long_name in macro_map.items():
        entry = ttk.Entry(parent_frame, width=8, justify='center')
        entry.grid(column=col_map[short_name], row=row_num, padx=5)
        entry.insert(0, str(data.get(long_name, 0)))

        entry.bind("<FocusIn>", store_old_value)
        entry.bind("<FocusOut>", partial(on_macro_field_change, meal_type=meal_type, changed_index=index_in_type,
                                         macro_key=short_name))

        campos[short_name] = entry

    return campos


# --- FUNÇÕES DA CALCULADORA DE REGRA DE 3 (NOVA SEÇÃO) ---

def calcular_regra_de_3():
    """Calcula o valor X na regra de três e exibe na interface."""
    try:
        # Pega os valores dos campos, permitindo números decimais (float)
        valor_a = float(entry_r3_a.get())
        valor_b = float(entry_r3_b.get())
        valor_c = float(entry_r3_c.get())

        # Verifica se o valor 'A' é zero para evitar divisão por zero
        if valor_a == 0:
            messagebox.showerror("Erro de Cálculo", "O 'Valor A' não pode ser zero (divisão por zero).")
            return

        # Fórmula da regra de três: X = (B * C) / A
        resultado = (valor_b * valor_c) / valor_a

        # Exibe o resultado formatado no label
        label_r3_resultado_valor.config(text=f"{resultado:.2f}")

    except ValueError:
        # Se a conversão para float falhar
        messagebox.showerror("Erro de Entrada", "Por favor, insira apenas números válidos nos campos.")
    except Exception as e:
        # Captura outros erros inesperados
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")


def limpar_regra_de_3():
    """Limpa todos os campos e o resultado da calculadora de regra de três."""
    entry_r3_a.delete(0, tk.END)
    entry_r3_b.delete(0, tk.END)
    entry_r3_c.delete(0, tk.END)
    label_r3_resultado_valor.config(text="---")


# --- CONFIGURAÇÃO DA JANELA E INTERFACE ---
root = tk.Tk()
root.title("Ferramenta de Planejamento de Dieta")
root.geometry("650x750")

# --- NOVA VARIÁVEL --- Variável para controlar o estado do checkbutton
redistribuicao_automatica_ativada = tk.BooleanVar(value=True)

notebook = ttk.Notebook(root, padding="10")
notebook.pack(expand=True, fill="both")

style = ttk.Style()
style.configure("TNotebook.Tab", font=("Helvetica", "10", "bold"))
style.configure("TButton", padding=6, relief="flat")
style.configure("Result.TLabel", font=("Helvetica", 11))
style.configure("ResultBold.TLabel", font=("Helvetica", 11, "bold"))
style.configure("BigResult.TLabel", font=("Helvetica", 12, "bold"))
style.configure("Bold.TLabel", font=("Helvetica", 10, "bold"))

# Criação dos frames para cada aba
tab_calorias = ttk.Frame(notebook)
tab_macros = ttk.Frame(notebook)
tab_regra3 = ttk.Frame(notebook)

# Adição das abas ao notebook
notebook.add(tab_calorias, text='  1. Necessidade Calórica  ')
notebook.add(tab_macros, text='  2. Distribuição de Dieta  ')
notebook.add(tab_regra3, text='  Calculadora de Regra de 3  ')

# =========================================================
# ===== ABA 1: CALCULADORA DE CALORIAS ====================
# =========================================================
frame_cal = ttk.Frame(tab_calorias, padding="10")
frame_cal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
tab_calorias.columnconfigure(0, weight=1)
frame_cal.columnconfigure(1, weight=1)

ttk.Label(frame_cal, text="Dados do Paciente", font=("Helvetica", 12, "bold")).grid(column=0, row=0, columnspan=2,
                                                                                    pady=10, sticky=tk.W)
ttk.Label(frame_cal, text="Peso (kg):").grid(column=0, row=1, sticky=tk.W, pady=5)
entry_peso = ttk.Entry(frame_cal)
entry_peso.grid(column=1, row=1, sticky=(tk.W, tk.E))
ttk.Label(frame_cal, text="Altura (cm):").grid(column=0, row=2, sticky=tk.W, pady=5)
entry_altura = ttk.Entry(frame_cal)
entry_altura.grid(column=1, row=2, sticky=(tk.W, tk.E))
ttk.Label(frame_cal, text="Idade (anos):").grid(column=0, row=3, sticky=tk.W, pady=5)
entry_idade = ttk.Entry(frame_cal)
entry_idade.grid(column=1, row=3, sticky=(tk.W, tk.E))
ttk.Label(frame_cal, text="Sexo:").grid(column=0, row=4, sticky=tk.W, pady=5)
combo_sexo = ttk.Combobox(frame_cal, values=['Masculino', 'Feminino', 'Criança'], state="readonly")
combo_sexo.grid(column=1, row=4, sticky=(tk.W, tk.E))
combo_sexo.set('Feminino')
ttk.Label(frame_cal, text="Nível de Atividade:").grid(column=0, row=5, sticky=tk.W, pady=5)
combo_nivel_atividade = ttk.Combobox(frame_cal, values=['Sedentário (pouco ou nenhum exercício)',
                                                        'Levemente Ativo (exercício 1-3 dias/semana)',
                                                        'Moderadamente Ativo (exercício 3-5 dias/semana)',
                                                        'Muito Ativo (exercício 6-7 dias/semana)',
                                                        'Extremamente Ativo (exercício muito pesado/trabalho físico)'],
                                     state="readonly")
combo_nivel_atividade.grid(column=1, row=5, sticky=(tk.W, tk.E))
combo_nivel_atividade.set('Levemente Ativo (exercício 1-3 dias/semana)')
ttk.Label(frame_cal, text="Objetivo:").grid(column=0, row=6, sticky=tk.W, pady=5)
combo_objetivo = ttk.Combobox(frame_cal, values=['Perder Peso', 'Manter Peso', 'Ganhar Peso'], state="readonly")
combo_objetivo.grid(column=1, row=6, sticky=(tk.W, tk.E))
combo_objetivo.set('Manter Peso')

frame_botoes_cal = ttk.Frame(frame_cal)
frame_botoes_cal.grid(column=0, row=7, columnspan=2, pady=20)
ttk.Button(frame_botoes_cal, text="Calcular Necessidade", command=executar_calculo_calorias).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_botoes_cal, text="Copiar Resultados", command=copiar_resultados_calorias).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_botoes_cal, text="Avançar para Distribuição →", command=ir_para_distribuicao).pack(side=tk.LEFT,
                                                                                                    padx=5)

ttk.Separator(frame_cal, orient='horizontal').grid(column=0, row=8, columnspan=2, sticky='ew', pady=10)

frame_resultados_cal = ttk.LabelFrame(frame_cal, text="Resultados do Cálculo Calórico", padding=10)
frame_resultados_cal.grid(column=0, row=9, columnspan=2, sticky='ew')
label_resultado_tmb_cal = ttk.Label(frame_resultados_cal, text="Taxa Metabólica Basal (TMB): - kcal/dia",
                                    style="Result.TLabel")
label_resultado_tmb_cal.pack(anchor=tk.W, pady=1)
label_resultado_fator_cal = ttk.Label(frame_resultados_cal, text="Fator de Atividade (NAF): -", style="Result.TLabel")
label_resultado_fator_cal.pack(anchor=tk.W, pady=1)
label_resultado_manutencao_cal = ttk.Label(frame_resultados_cal, text="Calorias para Manutenção: - kcal/dia",
                                           style="Result.TLabel")
label_resultado_manutencao_cal.pack(anchor=tk.W, pady=1)
label_resultado_objetivo_cal = ttk.Label(frame_resultados_cal, text="Meta para Objetivo: - kcal/dia",
                                         style="BigResult.TLabel")
label_resultado_objetivo_cal.pack(anchor=tk.W, pady=(5, 0))

# ==========================================================
# ===== ABA 2: DISTRIBUIÇÃO DE DIETA (COM SCROLLBAR) =======
# ==========================================================

# Crie um Canvas dentro de tab_macros
canvas = tk.Canvas(tab_macros)
scrollbar = ttk.Scrollbar(tab_macros, orient="vertical", command=canvas.yview)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Crie um frame dentro do canvas para o conteúdo rolável
scrollable_frame = ttk.Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# O frame_macro agora é filho do scrollable_frame
frame_macro = ttk.Frame(scrollable_frame, padding="10")
frame_macro.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
# O columnconfigure deve ser do scrollable_frame ou do frame_macro
frame_macro.columnconfigure(0, weight=1) # Permite que o frame_entradas_macro expanda
frame_macro.columnconfigure(1, weight=1) # Permite que o frame_entradas_macro expanda

frame_entradas_macro = ttk.LabelFrame(frame_macro, text="1. Configuração Inicial", padding=10)
frame_entradas_macro.grid(column=0, row=0, columnspan=4, sticky='ew') # Aumentado columnspan para 4
frame_entradas_macro.columnconfigure(1, weight=1) # Para que os entries expandam
frame_entradas_macro.columnconfigure(3, weight=1) # Para que os entries expandam

ttk.Label(frame_entradas_macro, text="Meta Calórica (kcal):").grid(column=0, row=1, sticky=tk.W, pady=2, padx=5)
entry_total_kcal_macro = ttk.Entry(frame_entradas_macro, width=15)
entry_total_kcal_macro.grid(column=1, row=1, sticky=(tk.W, tk.E), padx=5)
ttk.Label(frame_entradas_macro, text="Peso do Paciente (kg):").grid(column=0, row=2, sticky=tk.W, pady=2, padx=5)
entry_peso_paciente_macro = ttk.Entry(frame_entradas_macro, width=15)
entry_peso_paciente_macro.grid(column=1, row=2, sticky=(tk.W, tk.E), padx=5)
ttk.Label(frame_entradas_macro, text="Proteínas (%):").grid(column=0, row=4, sticky=tk.W, pady=2, padx=5)
entry_perc_prot = ttk.Entry(frame_entradas_macro, width=15)
entry_perc_prot.grid(column=1, row=4, sticky=(tk.W, tk.E), padx=5)
entry_perc_prot.insert(0, "20.0")
ttk.Label(frame_entradas_macro, text="Carboidratos (%):").grid(column=0, row=5, sticky=tk.W, pady=2, padx=5)
entry_perc_carb = ttk.Entry(frame_entradas_macro, width=15)
entry_perc_carb.grid(column=1, row=5, sticky=(tk.W, tk.E), padx=5)
entry_perc_carb.insert(0, "45.0")
ttk.Label(frame_entradas_macro, text="Gorduras (%):").grid(column=0, row=6, sticky=tk.W, pady=2, padx=5)
entry_perc_gord = ttk.Entry(frame_entradas_macro, width=15)
entry_perc_gord.grid(column=1, row=6, sticky=(tk.W, tk.E), padx=5)
entry_perc_gord.insert(0, "35.0")
ttk.Label(frame_entradas_macro, text="Nº Refeições Grandes:").grid(column=2, row=1, sticky=tk.W, pady=2, padx=5)
entry_num_grandes = ttk.Entry(frame_entradas_macro, width=15)
entry_num_grandes.grid(column=3, row=1, sticky=(tk.W, tk.E), padx=5)
entry_num_grandes.insert(0, "3")
ttk.Label(frame_entradas_macro, text="Nº Refeições Pequenas:").grid(column=2, row=2, sticky=tk.W, pady=2, padx=5)
entry_num_pequenas = ttk.Entry(frame_entradas_macro, width=15)
entry_num_pequenas.grid(column=3, row=2, sticky=(tk.W, tk.E), padx=5)
entry_num_pequenas.insert(0, "3")
ttk.Label(frame_entradas_macro, text="% Cal. nas Grandes:").grid(column=2, row=4, sticky=tk.W, pady=2, padx=5)
entry_perc_dist_grandes = ttk.Entry(frame_entradas_macro, width=15)
entry_perc_dist_grandes.grid(column=3, row=4, sticky=(tk.W, tk.E), padx=5)
entry_perc_dist_grandes.insert(0, "70")

ttk.Button(frame_macro, text="Calcular Distribuição", command=lambda: executar_calculo_macros()).grid(column=0, row=12,
                                                                                                      columnspan=4, # Aumentado columnspan para 4
                                                                                                      pady=(15, 0))

frame_resultados = ttk.LabelFrame(frame_macro, text="2. Resultados e Ajustes", padding=10)
frame_resultados.grid(column=0, row=13, columnspan=4, sticky='ew', pady=(15, 5)) # Aumentado columnspan para 4
frame_resultados.grid_remove()

# Sub-Frame para Totais
frame_totais = ttk.Frame(frame_resultados)
frame_totais.grid(column=0, row=0, sticky='ew', columnspan=4, pady=5) # Aumentado columnspan para 4
frame_totais.columnconfigure(0, weight=1) # Para que os labels possam expandir, se necessário

ttk.Label(frame_totais, text="Totais Diários:", font=("Helvetica", 10, "bold")).grid(column=0, row=0, sticky=tk.W)
label_resultado_prot_total = ttk.Label(frame_totais, text="Proteína: - g (- g/kg)")
label_resultado_prot_total.grid(column=0, row=1, sticky=tk.W, padx=5)
label_resultado_carb_total = ttk.Label(frame_totais, text="Carboidrato: - g (- g/kg)")
label_resultado_carb_total.grid(column=0, row=2, sticky=tk.W, padx=5)
label_resultado_gord_total = ttk.Label(frame_totais, text="Gordura: - g (- g/kg)")
label_resultado_gord_total.grid(column=0, row=3, sticky=tk.W, padx=5)
label_kcal_ajustado = ttk.Label(frame_totais, text="Total Ajustado: - kcal", font=("Helvetica", 10, "bold"))
label_kcal_ajustado.grid(column=0, row=4, sticky=tk.W, padx=5, pady=(5, 0))

# Sub-Frame para Ajuste Manual das Refeições
frame_ajuste_manual = ttk.LabelFrame(frame_resultados, text="Ajuste Manual por Refeição", padding=10)
frame_ajuste_manual.grid(column=0, row=1, columnspan=4, sticky='ew', pady=(10, 0)) # Aumentado columnspan para 4
# As colunas dentro de frame_ajuste_manual serão configuradas dinamicamente
# O conteúdo aqui (linhas de refeição e botões) é criado dinamicamente pela função atualizar_interface_completa

# =========================================================
# ===== ABA 3: REGRA DE TRÊS ==============================
# =========================================================
frame_r3 = ttk.Frame(tab_regra3, padding="20")
frame_r3.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
tab_regra3.columnconfigure(0, weight=1)

# --- Layout da Calculadora ---
frame_r3_linha1 = ttk.Frame(frame_r3)
frame_r3_linha1.grid(row=0, column=0, columnspan=3, pady=10, sticky='w')

ttk.Label(frame_r3_linha1, text="Valor A:").pack(side=tk.LEFT, padx=5)
entry_r3_a = ttk.Entry(frame_r3_linha1, width=15, justify='center')
entry_r3_a.pack(side=tk.LEFT, padx=5)

ttk.Label(frame_r3_linha1, text="está para").pack(side=tk.LEFT, padx=10)

ttk.Label(frame_r3_linha1, text="Valor B:").pack(side=tk.LEFT, padx=5)
entry_r3_b = ttk.Entry(frame_r3_linha1, width=15, justify='center')
entry_r3_b.pack(side=tk.LEFT, padx=5)

ttk.Label(frame_r3, text="assim como", style="Bold.TLabel").grid(row=1, column=0, columnspan=3, pady=10)

frame_r3_linha2 = ttk.Frame(frame_r3)
frame_r3_linha2.grid(row=2, column=0, columnspan=3, pady=10, sticky='w')

ttk.Label(frame_r3_linha2, text="Valor C:").pack(side=tk.LEFT, padx=5)
entry_r3_c = ttk.Entry(frame_r3_linha2, width=15, justify='center')
entry_r3_c.pack(side=tk.LEFT, padx=5)

ttk.Label(frame_r3_linha2, text="está para").pack(side=tk.LEFT, padx=10)

ttk.Label(frame_r3_linha2, text="Resultado (X):", style="Bold.TLabel").pack(side=tk.LEFT, padx=5)
label_r3_resultado_valor = ttk.Label(frame_r3_linha2, text="---", style="BigResult.TLabel", foreground="blue", width=15,
                                     anchor='center')
label_r3_resultado_valor.pack(side=tk.LEFT, padx=5)

frame_r3_botoes = ttk.Frame(frame_r3)
frame_r3_botoes.grid(row=3, column=0, columnspan=3, pady=25)

ttk.Button(frame_r3_botoes, text="Calcular", command=calcular_regra_de_3).pack(side=tk.LEFT, padx=10)
ttk.Button(frame_r3_botoes, text="Limpar Campos", command=limpar_regra_de_3).pack(side=tk.LEFT, padx=10)

# --- INICIAR O LOOP DA APLICAÇÃO ---
root.mainloop()