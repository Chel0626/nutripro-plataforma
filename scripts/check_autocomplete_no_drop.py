from app import app, db
import json
import math

print('Starting autocomplete check (no drop)...')
with app.app_context():
    client = app.test_client()
    resp = client.get('/api/alimentos/autocomplete?q=arroz')
    print('HTTP status:', resp.status_code)
    try:
        data = resp.get_json()
    except Exception as e:
        print('Erro ao decodificar JSON:', e)
        data = None

    if data is None:
        print('Resposta vazia ou inválida')
    else:
        print('Resultados retornados:', len(data))
        problem = False
        for item in data[:50]:
            for key in ('kcal_100g','carboidratos_100g','proteinas_100g','gorduras_100g'):
                val = item.get(key)
                try:
                    f = float(val)
                    if not math.isfinite(f):
                        print('Campo não finito:', item.get('id'), key, val)
                        problem = True
                except Exception:
                    print('Campo inválido:', item.get('id'), key, val)
                    problem = True
        print('Encontrou problema numérico:', problem)
        if len(data) > 0:
            print(json.dumps(data[:5], ensure_ascii=False, indent=2))

print('Check finished.')
