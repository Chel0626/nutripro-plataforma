import os
import shutil
from pathlib import Path

from app import app

# Caminhos
old_default = os.path.join(os.path.expanduser('~'), 'NutriPro_Data', 'plataforma_nutri.db')
project_root = os.path.dirname(os.path.abspath(__file__))
instance_db = os.path.abspath(os.path.join(project_root, '..', 'instance', 'plataforma_nutri.db'))

print('Old default DB path:', old_default)
print('Target instance DB path:', instance_db)

# Se o DB antigo existir e o instance ainda não tiver, move
if os.path.exists(old_default) and not os.path.exists(instance_db):
    os.makedirs(os.path.dirname(instance_db), exist_ok=True)
    shutil.move(old_default, instance_db)
    print('Movido com sucesso do default para instance.')
elif os.path.exists(instance_db):
    print('Já existe DB em instance. Nenhuma ação necessária.')
else:
    print('Nenhum DB antigo encontrado; nada a mover.')
