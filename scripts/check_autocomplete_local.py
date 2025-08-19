from app import app

with app.test_client() as client:
    resp = client.get('/api/alimentos/autocomplete?q=arroz')
    print('status', resp.status_code)
    data = resp.get_json()
    print('count', len(data) if isinstance(data, list) else 'not-list')
    if isinstance(data, list):
        for i, item in enumerate(data[:5]):
            print(i+1, item.get('nome'), item.get('kcal_100g'), item.get('carboidratos_100g'))
