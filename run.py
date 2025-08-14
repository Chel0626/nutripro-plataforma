# run.py (Versão limpa e final)

from waitress import serve
from app import app, db
import webbrowser

# --- A MÁGICA ESTÁ AQUI ---
# Esta parte garante que o executável funcione em qualquer computador,
# mesmo que o banco de dados ainda não exista.
with app.app_context():
    db.create_all()

# Função principal que será executada
def main():
    # Define a porta que sabemos que funciona no seu ambiente
    host = '127.0.0.1'
    port = 5000
    
    # Abre o navegador automaticamente na página inicial da aplicação
    # Isso melhora muito a experiência para o usuário final (sua esposa)
    webbrowser.open(f"http://{host}:{port}")

    # Inicia o servidor de produção Waitress
    serve(app, host=host, port=port)

# Ponto de entrada padrão para scripts Python
if __name__ == '__main__':
    main()