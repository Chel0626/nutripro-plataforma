// static/js/plano_interativo.js
document.addEventListener('DOMContentLoaded', function() {
    // --- SELETORES DOS ELEMENTOS ---
    const formCalcCalorias = document.getElementById('form-calc-calorias');
    const resultadoCalculadoraDiv = document.getElementById('resultado-calculadora');
    const totalKcalInput = document.getElementById('total_kcal');

    const formMetas = document.getElementById('form-metas');
    const refeicoesContainer = document.getElementById('refeicoes-container');
    const btnSalvarPlano = document.getElementById('btn-salvar-plano');
    const diabetesCheck = document.getElementById('diabetes-check');
    const diabetesTextareaContainer = document.getElementById('diabetes-textarea-container');
    const nutricaoCheck = document.getElementById('nutricao-check');
    const nutricaoTextareaContainer = document.getElementById('nutricao-textarea-container');

    // --- EVENT LISTENERS ---
    if (formCalcCalorias) {
        formCalcCalorias.addEventListener('submit', handleCalcularCalorias);
    }
    if (formMetas) {
        formMetas.addEventListener('submit', handleDefinirMetas);
    }
    if (btnSalvarPlano) {
        btnSalvarPlano.addEventListener('click', handleSalvarPlano);
    }
    if (diabetesCheck) {
        diabetesCheck.addEventListener('change', function() {
            diabetesTextareaContainer.style.display = this.checked ? 'block' : 'none';
        });
    }
    if (nutricaoCheck) {
        nutricaoCheck.addEventListener('change', function() {
            nutricaoTextareaContainer.style.display = this.checked ? 'block' : 'none';
        });
    }
    refeicoesContainer.addEventListener('change', handleMudancaEmRefeicao);
    refeicoesContainer.addEventListener('click', handleRemoverItem);
    
    // --- FUNÇÕES DE LÓGICA DE EVENTOS ---
    function handleCalcularCalorias(event) {
        event.preventDefault();
        const formData = new FormData(formCalcCalorias);
        const dados = Object.fromEntries(formData.entries());
        
        fetch('/api/calcular_calorias', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                const resultado = data.resultado;
                const caloriasFinais = Math.round(resultado.calorias_objetivo);
                
                resultadoCalculadoraDiv.innerHTML = `
                    <div class="alert alert-success mt-3">
                        Necessidade Calórica Estimada: <strong>${caloriasFinais} kcal/dia</strong>.
                        (TMB: ${Math.round(resultado.tmb)} kcal)
                    </div>
                `;
                
                totalKcalInput.value = caloriasFinais;
                
                totalKcalInput.style.transition = 'background-color 0.5s ease';
                totalKcalInput.style.backgroundColor = '#fff3cd';
                setTimeout(() => {
                    totalKcalInput.style.backgroundColor = '';
                }, 1500);

            } else {
                resultadoCalculadoraDiv.innerHTML = `<div class="alert alert-danger mt-3">${data.erro}</div>`;
            }
        });
    }

    function handleDefinirMetas(event) {
        event.preventDefault();
        const formData = new FormData(formMetas);
        const dados = Object.fromEntries(formData.entries());
        fetch('/api/calcular_distribuicao', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        })
        .then(response => response.json())
        .then(data => data.sucesso ? renderizarRefeicoes(data.resultado) : alert('Erro: ' + data.erro));
    }

    function handleMudancaEmRefeicao(event) {
        if (event.target.classList.contains('food-quantity')) {
            updateMealTotals(event.target.closest('.refeicao-bloco'));
        }
    }

    function handleRemoverItem(event) {
        const removeButton = event.target.closest('.btn-remove-food');
        if (removeButton) {
            const mealElement = removeButton.closest('.refeicao-bloco');
            removeButton.closest('.food-item').remove();
            updateMealTotals(mealElement);
        }
    }

    function renderizarRefeicoes(resultados) {
        refeicoesContainer.innerHTML = '';
        const criarRefeicao = (nome, meta, index) => {
            const div = document.createElement('div');
            div.className = 'refeicao-bloco card mb-4';
            div.innerHTML = `
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <input type="text" class="form-control form-control-lg meal-title-input" value="${nome}" placeholder="Nome da Refeição">
                        <small class="text-muted ms-3 text-nowrap"><strong>Metas:</strong> ${meta.carboidrato.toFixed(1)}g Carb. | ${meta.proteina.toFixed(1)}g Prot. | ${meta.gordura.toFixed(1)}g Gord.</small>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-9">
                           <select id="busca-alimento-${index}" placeholder="Digite para buscar um alimento..."></select>
                        </div>
                    </div>
                    <ul class="list-group list-group-flush food-item-list mt-3"></ul>
                </div>
                <div class="card-footer text-end">
                    <strong>Totais:</strong> <span class="total-carb">0.0</span>g Carb. | <span class="total-prot">0.0</span>g Prot. | <span class="total-gord">0.0</span>g Gord.
                </div>
            `;
            refeicoesContainer.appendChild(div);
            inicializarAutocomplete(`#busca-alimento-${index}`, div);
        };
        let mealIndex = 0;
        for (let i = 0; i < resultados.num_refeicoes_grandes; i++) criarRefeicao(`Refeição Grande ${i + 1}`, resultados.por_refeicao_grande, mealIndex++);
        for (let i = 0; i < resultados.num_refeicoes_pequenas; i++) criarRefeicao(`Refeição Pequena ${i + 1}`, resultados.por_refeicao_pequena, mealIndex++);
    }

    function inicializarAutocomplete(selector, mealElement) {
        new TomSelect(selector, {
            valueField: 'value',
            labelField: 'text',
            searchField: 'text',
            load: function(query, callback) {
                if (!query.length || query.length < 2) return callback();
                fetch(`/api/alimentos/autocomplete?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(json => {
                        // Normaliza o formato esperado pelo TomSelect: cada option precisa de value/text
                        // e o código existente espera `dados_completos` dentro da opção.
                        const mapped = (json || []).map(item => ({
                            value: item.value || item.nome,
                            text: item.text || item.nome || item.value,
                            dados_completos: item
                        }));
                        callback(mapped);
                    })
                    .catch(() => callback());
            },
            onChange: function(value) {
                const selectedData = this.options[value];
                if (selectedData) {
                    adicionarAlimentoNaRefeicao(selectedData.dados_completos, mealElement);
                }
                this.clear();
                this.blur();
            },
            render: {
                option: function(data, escape) {
                    const macros = data.dados_completos || data || {};
                    const carb = Number.isFinite(Number(macros.carboidratos_100g)) ? Number(macros.carboidratos_100g) : 0;
                    const prot = Number.isFinite(Number(macros.proteinas_100g)) ? Number(macros.proteinas_100g) : 0;
                    const gord = Number.isFinite(Number(macros.gorduras_100g)) ? Number(macros.gorduras_100g) : 0;
                    return `<div class="d-flex justify-content-between">
                                    <div>${escape(data.text)}</div>
                                    <div class="text-muted small ms-4 text-nowrap">
                                        C: ${carb.toFixed(1)}g | P: ${prot.toFixed(1)}g | G: ${gord.toFixed(1)}g
                                    </div>
                                </div>`;
                },
                no_results: function(data, escape) { return '<div class="no-results">Nenhum alimento encontrado.</div>'; },
            },
        });
    }

    function adicionarAlimentoNaRefeicao(foodData, mealElement) {
        const itemList = mealElement.querySelector('.food-item-list');
        const li = document.createElement('li');
        li.className = 'list-group-item food-item py-3';
        li.dataset.nome = foodData.nome;
        li.dataset.marca = foodData.marca;
        li.dataset.baseCarb = foodData.carboidratos_100g;
        li.dataset.baseProt = foodData.proteinas_100g;
        li.dataset.baseGord = foodData.gorduras_100g;
        li.dataset.baseKcal = foodData.kcal_100g;
        
        li.innerHTML = `
            <div class="w-100">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <strong>${foodData.nome}</strong> 
                        <small class="text-muted">(${foodData.marca})</small>
                    </div>
                    <div class="d-flex align-items-center gap-3">
                        <div class="item-macros-display text-primary fw-bold text-nowrap" style="min-width: 240px;"></div>
                        <div class="d-flex align-items-center">
                            <input type="number" class="form-control form-control-sm food-quantity" value="100" style="width: 75px;" title="Quantidade em Gramas">
                            <span class="ms-1">g</span>
                        </div>
                        <button class="btn btn-sm btn-outline-danger btn-remove-food" title="Remover Alimento">
                            <i class="bi bi-x-lg"></i>
                        </button>
                    </div>
                </div>
                <div class="row gx-2">
                    <div class="col-md-6">
                        <input type="text" class="form-control form-control-sm food-medida" placeholder="Medida Caseira (Ex: 1 unidade)">
                    </div>
                    <div class="col-md-6">
                        <input type="text" class="form-control form-control-sm food-substituicoes" placeholder="Substituições (Ex: 1 pão)">
                    </div>
                </div>
            </div>
        `;
        itemList.appendChild(li);
        updateMealTotals(mealElement);
    }

    function updateMealTotals(mealElement) {
        let totalCarb = 0, totalProt = 0, totalGord = 0;
        const items = mealElement.querySelectorAll('.food-item');
        items.forEach(item => {
            const quantidade = parseFloat(item.querySelector('.food-quantity').value) || 0;
            const fator = quantidade / 100.0;
            const itemCarb = (parseFloat(item.dataset.baseCarb) || 0) * fator;
            const itemProt = (parseFloat(item.dataset.baseProt) || 0) * fator;
            const itemGord = (parseFloat(item.dataset.baseGord) || 0) * fator;
            
            const displayElement = item.querySelector('.item-macros-display');
            if (displayElement) {
                displayElement.innerHTML = `C: ${itemCarb.toFixed(1)}g | P: ${itemProt.toFixed(1)}g | G: ${itemGord.toFixed(1)}g`;
            }
            
            totalCarb += itemCarb;
            totalProt += itemProt;
            totalGord += itemGord;
        });
        mealElement.querySelector('.total-carb').textContent = totalCarb.toFixed(1);
        mealElement.querySelector('.total-prot').textContent = totalProt.toFixed(1);
        mealElement.querySelector('.total-gord').textContent = totalGord.toFixed(1);
    }
    
    function construirObjetoPlano() {
        const refeicoes = [];
        const blocosRefeicao = document.querySelectorAll('.refeicao-bloco');
        if (blocosRefeicao.length === 0) {
            alert('Você precisa primeiro definir as metas para gerar as refeições.');
            return null;
        }
        blocosRefeicao.forEach(bloco => {
            const nomeRefeicao = bloco.querySelector('.meal-title-input').value;
            const metasTexto = bloco.querySelector('small.text-muted').textContent;
            const metas = {
                carboidrato: parseFloat(metasTexto.match(/(\d+\.?\d*)g Carb/)[1]) || 0,
                proteina: parseFloat(metasTexto.match(/(\d+\.?\d*)g Prot/)[1]) || 0,
                gordura: parseFloat(metasTexto.match(/(\d+\.?\d*)g Gord/)[1]) || 0
            };
            const itens = [];
            bloco.querySelectorAll('.food-item').forEach(itemEl => {
                const quantidade = parseFloat(itemEl.querySelector('.food-quantity').value) || 0;
                const fator = quantidade / 100.0;
                const baseCarb = parseFloat(itemEl.dataset.baseCarb) || 0;
                const baseProt = parseFloat(itemEl.dataset.baseProt) || 0;
                const baseGord = parseFloat(itemEl.dataset.baseGord) || 0;
                const baseKcal = parseFloat(itemEl.dataset.baseKcal) || 0;
                itens.push({
                    nome: itemEl.dataset.nome,
                    marca: itemEl.dataset.marca,
                    quantidade: quantidade,
                    medida_caseira: itemEl.querySelector('.food-medida').value,
                    substituicoes: itemEl.querySelector('.food-substituicoes').value,
                    macros: {
                        carboidratos: baseCarb * fator,
                        proteinas: baseProt * fator,
                        gorduras: baseGord * fator,
                        kcal: Math.round(baseKcal * fator)
                    }
                });
            });
            refeicoes.push({ nome: nomeRefeicao, metas: metas, itens: itens });
        });
        const planoFinal = {
            nome_plano: `Plano de ${document.getElementById('total_kcal').value} kcal`,
            objetivo_calorico: parseInt(document.getElementById('total_kcal').value) || 0,
            refeicoes: refeicoes
        };
        if (diabetesCheck && diabetesCheck.checked && document.getElementById('diabetes-textarea').value.trim() !== '') {
            planoFinal.orientacoes_diabetes = document.getElementById('diabetes-textarea').value;
        }
        if (nutricaoCheck && nutricaoCheck.checked && document.getElementById('nutricao-textarea').value.trim() !== '') {
            planoFinal.orientacoes_nutricao = document.getElementById('nutricao-textarea').value;
        }
        return planoFinal;
    }

    function handleSalvarPlano() {
        const planoData = construirObjetoPlano();
        if (!planoData) return;
        const pacienteId = window.location.pathname.split('/')[2];
        btnSalvarPlano.disabled = true;
        btnSalvarPlano.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Salvando...';
        fetch(`/api/paciente/${pacienteId}/plano/salvar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(planoData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                alert(data.mensagem);
                window.location.href = data.redirect_url;
            } else {
                alert('Erro ao salvar o plano: ' + data.erro);
                btnSalvarPlano.disabled = false;
                btnSalvarPlano.innerHTML = '<i class="bi bi-save"></i> Salvar Plano Completo';
            }
        })
        .catch(error => {
            console.error('Erro de comunicação:', error);
            alert('Ocorreu um erro de comunicação. Verifique o console para mais detalhes.');
            btnSalvarPlano.disabled = false;
            btnSalvarPlano.innerHTML = '<i class="bi bi-save"></i> Salvar Plano Completo';
        });
    }

    // Função para calcular a idade a partir da data de nascimento
    function calculateAge(birthDateString) {
        if (!birthDateString) return '';
        const birthDate = new Date(birthDateString);
        const today = new Date();
        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age;
    }

    // Preenche a idade se a data de nascimento estiver disponível
    const idadeInput = document.getElementById('calc-idade');
    const pacienteDataNascimento = '{{ paciente.data_nascimento.strftime("%Y-%m-%d") if paciente.data_nascimento else "" }}';
    if (idadeInput) {
        if (pacienteDataNascimento) {
            const ageVal = calculateAge(pacienteDataNascimento);
            if (Number.isFinite(ageVal)) {
                idadeInput.value = ageVal;
            } else {
                idadeInput.value = '';
            }
        } else {
            idadeInput.value = '';
        }
    }
});