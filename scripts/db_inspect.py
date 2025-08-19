from app import app, db, Alimento

with app.app_context():
    uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    print('DB URI:', uri)
    try:
        total = Alimento.query.count()
    except Exception as e:
        print('Erro ao contar Alimento:', e)
        total = None
    print('Total alimentos na tabela:', total)
    if total and total > 0:
        print('Primeiros 20 alimentos (ordenado por nome):')
        for a in Alimento.query.order_by(Alimento.nome).limit(20).all():
            print('-', a.id, a.nome)

        arroz_qs = Alimento.query.filter(Alimento.nome.ilike('%arroz%')).all()
        print('\nRegistros contendo "arroz":', len(arroz_qs))
        for a in arroz_qs[:20]:
            print('  ->', a.id, a.nome)
