# run.py (Versão limpa e final)

from waitress import serve
from app import app, db
import webbrowser
import os
import sys
import zipfile


def extract_resources_if_present():
    """Se existir resources.zip no diretório da aplicação ou no bundle, extrai para o diretório corrente.

    Suporta execução em desenvolvimento e em executável PyInstaller (procura em sys._MEIPASS).
    """
    # localizações a verificar: cwd e packaging temp (sys._MEIPASS)
    candidates = []
    cwd_zip = os.path.join(os.getcwd(), 'resources.zip')
    candidates.append(cwd_zip)
    # quando empacotado com PyInstaller, dados adicionados via --add-data ficam em _MEIPASS
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        candidates.append(os.path.join(meipass, 'resources.zip'))

    for zip_path in candidates:
        try:
            if zip_path and os.path.exists(zip_path):
                print(f"Found resources.zip at {zip_path}, extracting...")
                with zipfile.ZipFile(zip_path, 'r') as z:
                    # extrai apenas se não existir o arquivo/diretório destino
                    for member in z.namelist():
                        dest_path = os.path.join(os.getcwd(), member)
                        if not os.path.exists(dest_path):
                            z.extract(member, os.getcwd())
                print('Extraction complete.')
                return True
        except Exception:
            # falha silenciosa; não queremos quebrar startup por causa da extração
            continue
    return False

# --- A MÁGICA ESTÁ AQUI ---
# Esta parte garante que o executável funcione em qualquer computador,
# mesmo que o banco de dados ainda não exista.
with app.app_context():
    # Se houver um resources.zip fornecido junto ao exe, extraia antes de criar o DB
    extract_resources_if_present()
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