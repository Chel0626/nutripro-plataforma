// static/js/distribuicao_macros.js

document.addEventListener('DOMContentLoaded', function() {
    // --- SELETORES DOS ELEMENTOS ---
    const macroInputs = document.querySelectorAll('.macro-input');
    const toggleRedistribuicao = document.getElementById('toggle-redistribuicao');

    // --- ADICIONA OS "OUVINTES" DE EVENTOS ---
    macroInputs.forEach(input => {
        // Guarda o valor antigo quando o campo recebe foco
        input.addEventListener('focus', (event) => {
            event.target.dataset.oldValue = event.target.value;
        });

        // Executa a lógica principal quando o valor do campo muda
        input.addEventListener('change', handleInputChange);
    });

    // --- FUNÇÃO PRINCIPAL ---
    function handleInputChange(event) {
        // Se o botão estiver desligado, apenas recalcula os totais e encerra
        if (!toggleRedistribuicao.checked) {
            recalculateTotalsViaAPI();
            return;
        }

        // --- LÓGICA DE REDISTRIBUIÇÃO AUTOMÁTICA ---
        const changedInput = event.target;
        const oldValue = parseFloat(changedInput.dataset.oldValue) || 0;
        const newValue = parseFloat(changedInput.value) || 0;
        const delta = oldValue - newValue; // Diferença a ser redistribuída

        if (delta === 0) return; // Se nada mudou, não faz nada

        // Encontra todos os campos "pares" (mesmo tipo de refeição e macro)
        const mealType = changedInput.dataset.mealType;
        const macroType = changedInput.dataset.macroType;

        const peerInputs = Array.from(
            document.querySelectorAll(`input[data-meal-type="${mealType}"][data-macro-type="${macroType}"]`)
        ).filter(input => input !== changedInput); // Exclui o próprio campo que foi alterado

        if (peerInputs.length > 0) {
            // Distribui a diferença entre os campos pares
            const baseRedistribution = Math.trunc(delta / peerInputs.length);
            let remainder = delta % peerInputs.length;

            peerInputs.forEach((peer, index) => {
                const currentValue = parseFloat(peer.value) || 0;
                let amountToAdd = baseRedistribution;

                // Distribui o resto da divisão para os primeiros campos
                if (remainder !== 0) {
                    const sign = delta > 0 ? 1 : -1;
                    amountToAdd += sign;
                    remainder -= sign;
                }

                let newPeerValue = currentValue + amountToAdd;
                // Garante que o valor não fique negativo
                peer.value = Math.max(0, Math.round(newPeerValue));
            });
        }

        // Após redistribuir, sempre recalcula os totais via API para garantir a precisão
        recalculateTotalsViaAPI();
    }

    // --- FUNÇÃO DE COMUNICAÇÃO COM O BACKEND ---
    function recalculateTotalsViaAPI() {
        const refeicoesGrandes = getMealData('grande');
        const refeicoesPequenas = getMealData('pequena');
        const pesoPaciente = parseFloat(document.getElementById('peso').value);

        if (!pesoPaciente) {
            console.error('Peso do paciente não encontrado ou inválido!');
            return;
        }

        const payload = {
            refeicoes_grandes: refeicoesGrandes,
            refeicoes_pequenas: refeicoesPequenas,
            peso: pesoPaciente
        };

        fetch('/api/recalcular_macros', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                updateTotalsOnScreen(data);
            } else {
                console.error('Erro no cálculo do servidor:', data.erro);
            }
        })
        .catch(error => console.error('Erro ao chamar a API:', error));
    }

    // --- FUNÇÕES AUXILIARES ---
    function getMealData(mealType) {
        const data = [];
        const inputs = document.querySelectorAll(`input[data-meal-type="${mealType}"]`);

        const meals = {};
        inputs.forEach(input => {
            const idParts = input.id.split('-');
            const index = idParts[1];
            const macro = input.dataset.macroType;

            if (!meals[index]) {
                meals[index] = {};
            }
            meals[index][macro] = parseInt(input.value, 10) || 0;
        });

        return Object.values(meals);
    }

    function updateTotalsOnScreen(data) {
        document.getElementById('total-prot-gramas').textContent = data.macros_totais.proteina;
        document.getElementById('total-prot-gkg').textContent = data.gkg_prot;

        document.getElementById('total-carb-gramas').textContent = data.macros_totais.carboidrato;
        document.getElementById('total-carb-gkg').textContent = data.gkg_carb;

        document.getElementById('total-gord-gramas').textContent = data.macros_totais.gordura;
        document.getElementById('total-gord-gkg').textContent = data.gkg_gord;

        document.getElementById('total-kcal-ajustado').textContent = data.kcal_totais;
    }
});