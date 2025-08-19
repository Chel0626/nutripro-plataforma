"""scripts/test_api_calculos.py
Testa os endpoints /api/calcular_calorias e /api/calcular_distribuicao usando o cliente de teste Flask.
"""
from app import app

with app.test_client() as client:
    # Teste calorias
    payload = {
        'peso': 70,
        'altura': 175,
        'idade': 30,
        'sexo': 'masculino',
        'nivel_atividade': 'moderado',
        'objetivo': 'manter'
    }
    resp = client.post('/api/calcular_calorias', json=payload)
    print('calcular_calorias status:', resp.status_code)
    print('body:', resp.get_json())

    # Teste distribuicao
    payload2 = {
        'total_kcal': 2400,
        'perc_carb': 45.0,
        'perc_prot': 20.0,
        'perc_gord': 35.0,
        'num_refeicoes_grandes': 3,
        'num_refeicoes_pequenas': 3,
        'perc_dist_grandes': 70
    }
    resp2 = client.post('/api/calcular_distribuicao', json=payload2)
    print('calcular_distribuicao status:', resp2.status_code)
    print('body:', resp2.get_json())
