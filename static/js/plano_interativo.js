// static/js/plano_interativo.js (Com lógica de Orientações Gerais)
document.addEventListener('DOMContentLoaded', function() {
    // --- SELETORES DOS ELEMENTOS ---
    const formMetas = document.getElementById('form-metas');
    const refeicoesContainer = document.getElementById('refeicoes-container');
    const btnSalvarPlano = document.getElementById('btn-salvar-plano');
    // Novos seletores para a seção de Orientações
    const diabetesCheck = document.getElementById('diabetes-check');
    const diabetesTextareaContainer = document.getElementById('diabetes-textarea-container');
    const nutricaoCheck = document.getElementById('nutricao-check');
    const nutricaoTextareaContainer = document.getElementById('nutricao-textarea-container');

    // --- EVENT LISTENERS ---
    if (formMetas) {
        formMetas.addEventListener('submit', handleDefinirMetas);
    }
    if (btnSalvarPlano) {
        btnSalvarPlano.addEventListener('click', handleSalvarPlano);
    }
    // Novos listeners para os checkboxes
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
                    <div class="d-flex justify-content-between">
                        <h5>${nome}</h5>
                        <small class="text-muted"><strong>Metas:</strong> ${meta.carboidrato.toFixed(1)}g Carb. | ${meta.proteina.toFixed(1)}g Prot. | ${meta.gordura.toFixed(1)}g Gord.</small>
                    </div>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <select id="busca-alimento-${index}" class="form-control" placeholder="Digite para buscar um alimento..."></select>
                    </div>
                    <ul class="list-group list-group-flush food-item-list"></ul>
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
                    .then(json => callback(json))
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
                option: function(data, escape) { return `<div>${escape(data.text)}</div>`; },
                no_results: function(data, escape) { return '<div class="no-results">Nenhum alimento encontrado.</div>'; },
            },
        });
    }

    function adicionarAlimentoNaRefeicao(foodData, mealElement) {
        const itemList = mealElement.querySelector('.food-item-list');
        const li = document.createElement('li');
        li.className = 'list-group-item food-item d-flex align-items-center gap-3 py-3';
        li.dataset.nome = foodData.nome;
        li.dataset.marca = foodData.marca;
        li.dataset.baseCarb = foodData.carboidratos_100g;
        li.dataset.baseProt = foodData.proteinas_100g;
        li.dataset.baseGord = foodData.gorduras_100g;
        li.dataset.baseKcal = foodData.kcal_100g;
        li.innerHTML = `
            <div class="flex-grow-1">
                <strong>${foodData.nome}</strong> <small class="text-muted">(${foodData.marca})</small>
                <div class="row gx-2 mt-2">
                    <div class="col-md-6">
                        <label class="form-label-sm">Medida Caseira</label>
                        <input type="text" class="form-control form-control-sm food-medida" placeholder="Ex: 1 fatia">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label-sm">Substituições</label>
                        <input type="text" class="form-control form-control-sm food-substituicoes" placeholder="Ex: 1 pão francês">
                    </div>
                </div>
            </div>
            <div class="d-flex align-items-center">
                <input type="number" class="form-control form-control-sm food-quantity" value="100" style="width: 80px;" title="Quantidade em Gramas">
                <span class="ms-1">g</span>
            </div>
            <button class="btn btn-sm btn-outline-danger btn-remove-food" title="Remover Alimento">
                <i class="bi bi-x-lg"></i>
            </button>
        `;
        itemList.appendChild(li);
        updateMealTotals(mealElement);
    }

    function updateMealTotals(mealElement) {
        let totalCarb = 0, totalProt = 0, totalGord = 0;
        mealElement.querySelectorAll('.food-item').forEach(item => {
            const quantidade = parseFloat(item.querySelector('.food-quantity').value) || 0;
            const fator = quantidade / 100.0;
            totalCarb += (parseFloat(item.dataset.baseCarb) || 0) * fator;
            totalProt += (parseFloat(item.dataset.baseProt) || 0) * fator;
            totalGord += (parseFloat(item.dataset.baseGord) || 0) * fator;
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
            const nomeRefeicao = bloco.querySelector('h5').textContent;
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
        
        // Coleta dos dados das novas caixas de texto
        if (diabetesCheck.checked && document.getElementById('diabetes-textarea').value.trim() !== '') {
            planoFinal.orientacoes_diabetes = document.getElementById('diabetes-textarea').value;
        }
        if (nutricaoCheck.checked && document.getElementById('nutricao-textarea').value.trim() !== '') {
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
});