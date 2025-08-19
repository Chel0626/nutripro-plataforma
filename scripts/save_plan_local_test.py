from app import app, db, Paciente, PlanoAlimentar
import json
import time

# Testa salvar plano via API e verifica arquivos em DATA_DIR
with app.app_context():
    # cria paciente de teste com email único para evitar constraint de unicidade
    unique_email = f'teste.salvar.local.{int(time.time())}@example.com'
    p = Paciente(nome_completo='Teste Salvar Local', email=unique_email)
    db.session.add(p)
    db.session.commit()
    paciente_id = p.id

    client = app.test_client()
    payload = {
        'nome_plano': 'Plano de Teste Local',
        'objetivo_calorico': 1800,
        'orientacoes_diabetes': 'Nenhuma',
        'orientacoes_nutricao': 'Teste',
        'refeicoes': []
    }
    resp = client.post(f'/api/paciente/{paciente_id}/plano/salvar', json=payload)
    print('status_code', resp.status_code)
    print(resp.get_json())

    # listar arquivos gerados
    import os
    from app import DATA_DIR
    paciente_folder = None
    for name in os.listdir(DATA_DIR):
        if name.startswith(f'paciente_{paciente_id}_'):
            paciente_folder = os.path.join(DATA_DIR, name)
            break
    print('pasta paciente criada:', paciente_folder)
    if paciente_folder:
        files = os.listdir(paciente_folder)
        print('arquivos:', files)
        for f in files:
            print('-', os.path.join(paciente_folder, f))
    else:
        print('pasta não encontrada')
