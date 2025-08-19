from app import app, db, Paciente

with app.app_context():
    p = Paciente(nome_completo='Teste Um', email='teste@example.com')
    db.session.add(p)
    db.session.commit()
    print('Inserted paciente id', p.id)
