import traceback
from app import app

app.testing = True
with app.test_client() as client:
    try:
        resp = client.get('/paciente/1/plano/novo')
        print('Status code:', resp.status_code)
        print(resp.get_data(as_text=True)[:1000])
    except Exception as e:
        print('Exception raised during request:')
        traceback.print_exc()
