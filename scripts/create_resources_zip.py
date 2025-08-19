"""Cria resources.zip contendo templates, static, instance e taco_data.py (quando presente).
Uso: rodar da raiz do projeto.
"""
import os
import zipfile

paths = ['templates', 'static', 'instance']
files_to_add = []
for p in paths:
    if os.path.exists(p):
        for root, dirs, files in os.walk(p):
            for f in files:
                files_to_add.append(os.path.join(root, f))

if os.path.exists('taco_data.py'):
    files_to_add.append('taco_data.py')

if not files_to_add:
    print('Nenhum arquivo encontrado para empacotar.')
else:
    with zipfile.ZipFile('resources.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for f in files_to_add:
            z.write(f, arcname=os.path.relpath(f))
    print(f'Criado resources.zip com {len(files_to_add)} arquivos.')
