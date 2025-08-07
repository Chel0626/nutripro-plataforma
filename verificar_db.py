# verificar_db.py
from app import app, Alimento

def verificar_alimentos():
    # Usa o contexto da aplicação Flask para acessar o banco de dados
    with app.app_context():
        print("--- Verificando os 10 primeiros alimentos no banco de dados ---")

        # Busca os 10 primeiros registros na tabela Alimento
        alimentos = Alimento.query.limit(10).all()

        if alimentos:
            for i, alimento in enumerate(alimentos):
                print(f"{i+1}. {alimento.nome} (Kcal: {alimento.kcal_100g})")
        else:
            print("Nenhum alimento encontrado na tabela. A importação pode não ter funcionado.")

        total = Alimento.query.count()
        print(f"\nTotal de alimentos na tabela: {total}")
        print("--- Verificação concluída ---")

if __name__ == '__main__':
    verificar_alimentos()