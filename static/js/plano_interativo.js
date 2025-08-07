// static/js/plano_interativo.js

document.addEventListener('DOMContentLoaded', function() {
    // --- SELETORES DOS ELEMENTOS ---
    const formMetas = document.getElementById('form-metas');
    const refeicoesContainer = document.getElementById('refeicoes-container');
    const btnSalvarPlano = document.getElementById('btn-salvar-plano');

    // Seletores da Busca Local
    const formBuscaLocal = document.getElementById('form-busca-local');
    const buscaLocalInput = document.getElementById('alimento_busca_local_input');
    const resultadosLocalContainer = document.getElementById('busca-local-resultados-container');

    // Seletores da Busca Online
    const formBuscaOnline = document.getElementById('form-busca-online');
    const buscaOnlineInput = document.getElementById('alimento_busca_online_input');
    const resultadosOnlineContainer = document.getElementById('busca-online-resultados-container');

    // --- EVENT LISTENERS ---

    // Event Listener para o Formulário de Metas
    if (formMetas) {
        formMetas.addEventListener('submit', handleDefinirMetas);
    }

    // Event Listener para o Formulário de Busca Local
    if (formBuscaLocal) {
        formBuscaLocal.addEventListener('submit', handleBuscaLocal);
    }

    // Event Listener para o Formulário de Busca Online
    if (formBuscaOnline) {
        formBuscaOnline.addEventListener('submit', handleBuscaOnline);
    }

    // Delegação de eventos para os botões "Usar" e "Salvar" que são criados dinamicamente
    document.getElementById('buscaTabContent').addEventListener('click', handleActionButtons);

    // Outros listeners (seleção de refeição, salvar plano, etc)
    refeicoesContainer.addEventListener('click', handleSelecaoRefeicao);
    refeicoesContainer.addEventListener('change', handleMudancaQuantidade);
    refeicoesContainer.addEventListener('click', handleRemoverItem);
    if (btnSalvarPlano) {
        btnSalvarPlano.addEventListener('click', handleSalvarPlano);
    }

    // --- FUNÇÕES DE LÓGICA DE EVENTOS ---

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
            .then(data => {
                if (data.sucesso) {
                    renderizarRefeicoes(data.resultado);
                } else {
                    alert('Erro ao calcular metas: ' + data.erro);
                }
            });
    }

    function handleBuscaLocal(event) {
        event.preventDefault();
        const termoBusca = buscaLocalInput.value;
        if (termoBusca.length < 2) {
            alert('Digite pelo menos 2 caracteres para buscar.');
            return;
        }
        resultadosLocalContainer.innerHTML = `<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>`;
        fetch(`/api/meus_alimentos/buscar?q=${encodeURIComponent(termoBusca)}`)
            .then(response => response.json())
            .then(data => {
                if (data.sucesso) {
                    renderizarResultadosBusca(data.resultados, resultadosLocalContainer, false); // false = não é busca online
                } else {
                    resultadosLocalContainer.innerHTML = `<p class="text-danger">Erro: ${data.erro}</p>`;
                }
            });
    }

    function handleBuscaOnline(event) {
        event.preventDefault();
        const termoBusca = buscaOnlineInput.value;
        if (termoBusca.length < 2) {
            alert('Digite pelo menos 2 caracteres para buscar.');
            return;
        }
        resultadosOnlineContainer.innerHTML = `<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>`;
        fetch(`/api/buscar_alimentos?q=${encodeURIComponent(termoBusca)}`)
            .then(response => response.json())
            .then(data => {
                if (data.sucesso) {
                    renderizarResultadosBusca(data.resultados, resultadosOnlineContainer, true); // true = é busca online
                } else {
                    resultadosOnlineContainer.innerHTML = `<p class="text-danger">Erro: ${data.erro}</p>`;
                }
            });
    }

    function handleActionButtons(event) {
        const foodListItem = event.target.closest('.list-group-item');
        if (!foodListItem) return;

        // Lógica para ADICIONAR ao plano
        if (event.target.classList.contains('btn-add-food')) {
            const refeicaoSelecionada = document.querySelector('.refeicao-bloco.selecionada');
            if (!refeicaoSelecionada) {
                alert('Por favor, clique em uma refeição na esquerda para selecioná-la primeiro.');
                return;
            }
            adicionarAlimentoNaRefeicao(foodListItem.dataset, refeicaoSelecionada);
        }

        // Lógica para SALVAR no banco de dados
        if (event.target.classList.contains('btn-save-db')) {
            const btn = event.target;
            const foodData = foodListItem.dataset;

            btn.disabled = true;
            btn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>`;

            fetch('/api/alimentos/salvar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(foodData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.sucesso) {
                        btn.textContent = 'Salvo ✔️';
                        btn.classList.remove('btn-outline-primary');
                        btn.classList.add('btn-success');
                    } else {
                        alert(data.erro);
                        btn.disabled = false;
                        btn.textContent = 'Salvar';
                    }
                });
        }
    }

    function handleSelecaoRefeicao(event) {
        const blocoClicado = event.target.closest('.refeicao-bloco');
        if (blocoClicado) {
            document.querySelectorAll('.refeicao-bloco.selecionada').forEach(el => el.classList.remove('selecionada'));
            blocoClicado.classList.add('selecionada');
        }
    }

    function handleMudancaQuantidade(event) {
        if (event.target.classList.contains('food-quantity')) {
            updateMealTotals(event.target.closest('.refeicao-bloco'));
        }
    }

    function handleRemoverItem(event) {
        if (event.target.classList.contains('btn-remove-food')) {
            const mealElement = event.target.closest('.refeicao-bloco');
            event.target.closest('.food-item').remove();
            updateMealTotals(mealElement);
        }
    }

    function handleSalvarPlano() {
        const planoData = construirObjetoPlano();
        if (!planoData) {
            alert('O plano parece estar vazio ou incompleto. Adicione metas e alimentos antes de salvar.');
            return;
        }

        const pacienteId = window.location.pathname.split('/')[2];

        btnSalvarPlano.disabled = true;
        btnSalvarPlano.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...';

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
                alert('Erro de comunicação ao salvar o plano.');
                console.error('Erro ao salvar:', error);
                btnSalvarPlano.disabled = false;
                btnSalvarPlano.innerHTML = '<i class="bi bi-save"></i> Salvar Plano Completo';
            });
    }

    // --- FUNÇÕES DE RENDERIZAÇÃO E CONSTRUÇÃO DE DADOS ---

    function renderizarRefeicoes(resultados) {
        refeicoesContainer.innerHTML = '<h6 class="text-center text-primary">Clique em uma refeição abaixo para selecioná-la.</h6><hr>';
        const criarRefeicao = (nome, meta) => {
            const div = document.createElement('div');
            div.className = 'refeicao-bloco mb-4';
            div.innerHTML = `
                <div class="p-3 border rounded">
                    <h5>${nome}</h5>
                    <p class="text-muted mb-1"><strong>Metas:</strong> ${meta.carboidrato.toFixed(1)}g C | ${meta.proteina.toFixed(1)}g P | ${meta.gordura.toFixed(1)}g F</p>
                    <p class="mb-2"><strong>Atual:</strong> <span class="total-carb">0.0</span>g C | <span class="total-prot">0.0</span>g P | <span class="total-gord">0.0</span>g F</p>
                    <ul class="list-group list-group-flush food-item-list"></ul>
                </div>`;
            refeicoesContainer.appendChild(div);
        };
        for (let i = 0; i < resultados.num_refeicoes_grandes; i++) criarRefeicao(`Refeição Grande ${i + 1}`, resultados.por_refeicao_grande);
        for (let i = 0; i < resultados.num_refeicoes_pequenas; i++) criarRefeicao(`Refeição Pequena ${i + 1}`, resultados.por_refeicao_pequena);
    }

    function renderizarResultadosBusca(alimentos, container, isOnlineSearch) {
        if (alimentos.length === 0) {
            container.innerHTML = '<p class="text-center text-muted">Nenhum resultado encontrado.</p>';
            return;
        }
        const html = alimentos.map(alimento => `
            <div class="list-group-item"
                 data-fatsecret-food-id="${alimento.id}"
                 data-nome="${alimento.nome}"
                 data-marca="${alimento.marca}"
                 data-kcal-100g="${alimento.kcal_100g}"
                 data-carboidratos-100g="${alimento.carboidratos_100g}"
                 data-proteinas-100g="${alimento.proteinas_100g}"
                 data-gorduras-100g="${alimento.gorduras_100g}">
                <div>
                    <strong>${alimento.nome}</strong> (${alimento.marca})<br>
                    <small class="text-muted">${alimento.descricao || `Macros por 100g: C: ${alimento.carboidratos_100g}g | P: ${alimento.proteinas_100g}g | G: ${alimento.gorduras_100g}g`}</small>
                </div>
                <div class="mt-2 text-end">
                    ${isOnlineSearch ? '<button class="btn btn-sm btn-outline-primary btn-save-db">Salvar</button>' : ''}
                    <button class="btn btn-sm btn-success btn-add-food ms-2">Usar</button>
                </div>
            </div>
        `).join('');
        container.innerHTML = `<div class="list-group list-group-flush">${html}</div>`;
    }

    function adicionarAlimentoNaRefeicao(foodData, mealElement) {
        const itemList = mealElement.querySelector('.food-item-list');
        const li = document.createElement('li');
        li.className = 'list-group-item food-item pt-3';

        li.dataset.nome = foodData.nome;
        li.dataset.marca = foodData.marca;
        li.dataset.baseCarb = foodData.carboidratos100g;
        li.dataset.baseProt = foodData.proteinas100g;
        li.dataset.baseGord = foodData.gorduras100g;
        li.dataset.baseKcal = foodData.kcal100g;

        li.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${foodData.nome}</strong>
                    <small class="text-muted">(${foodData.marca})</small>
                </div>
                <div class="d-flex align-items-center">
                    <input type="number" class="form-control form-control-sm food-quantity" value="100" style="width: 80px;" title="Quantidade em Gramas">
                    <span class="ms-1">g</span>
                    <button class="btn btn-sm btn-outline-danger ms-2 btn-remove-food" title="Remover Alimento">X</button>
                </div>
            </div>
            <div class="row gx-2 mt-2">
                <div class="col-md-6">
                    <label class="form-label-sm">Medida Caseira</label>
                    <input type="text" class="form-control form-control-sm food-medida" placeholder="Ex: 1 unidade pequena">
                </div>
                <div class="col-md-6">
                    <label class="form-label-sm">Substituições</label>
                    <textarea class="form-control form-control-sm food-substituicoes" rows="2" placeholder="Ex: 1 fatia de pão integral..."></textarea>
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
            totalCarb += (parseFloat(item.dataset.baseCarb) || 0) * fator;
            totalProt += (parseFloat(item.dataset.baseProt) || 0) * fator;
            totalGord += (parseFloat(item.dataset.baseGord) || 0) * fator;
        });
        mealElement.querySelector('.total-carb').textContent = totalCarb.toFixed(1);
        mealElement.querySelector('.total-prot').textContent = totalProt.toFixed(1);
        mealElement.querySelector('.total-gord').textContent = totalGord.toFixed(1);
    }

    // Em static/js/plano_interativo.js, SUBSTITUA a função construirObjetoPlano

// Em static/js/plano_interativo.js, SUBSTITUA a função construirObjetoPlano

function construirObjetoPlano() {
    const refeicoes = [];
    const blocosRefeicao = document.querySelectorAll('.refeicao-bloco');

    if (blocosRefeicao.length === 0) return null;

    blocosRefeicao.forEach(bloco => {
        const nomeRefeicao = bloco.querySelector('h5').textContent;
        const metasTexto = bloco.querySelector('p.text-muted').textContent;
        const metas = {
            carboidrato: parseFloat(metasTexto.match(/(\d+\.?\d*)g C/)[1]) || 0,
            proteina: parseFloat(metasTexto.match(/(\d+\.?\d*)g P/)[1]) || 0,
            gordura: parseFloat(metasTexto.match(/(\d+\.?\d*)g F/)[1]) || 0
        };

        const itens = [];
        bloco.querySelectorAll('.food-item').forEach(itemEl => {
            const quantidade = parseFloat(itemEl.querySelector('.food-quantity').value) || 0;
            const fator = quantidade / 100.0;

            // --- CORREÇÃO APLICADA AQUI ---
            // Garante que, mesmo que o data-attribute esteja faltando, enviamos 0 em vez de null.
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

    return {
        nome_plano: `Plano de ${document.getElementById('total_kcal').value} kcal`,
        objetivo_calorico: parseInt(document.getElementById('total_kcal').value) || 0,
        refeicoes: refeicoes
    };
}