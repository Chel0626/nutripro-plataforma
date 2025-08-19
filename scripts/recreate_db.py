from app import app, db

with app.app_context():
    print('DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])
    db.drop_all()
    db.create_all()
    print('Banco recriado com sucesso.')
