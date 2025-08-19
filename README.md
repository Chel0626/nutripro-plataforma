# NutriPro - instruções de desenvolvimento

Scripts úteis (PowerShell) — execute a partir da raiz do projeto `C:\dev\nutripro`.

Pré-requisitos
- Ative o venv: `.\.\venv\Scripts\Activate.ps1`
- Instale dependências: `pip install -r requirements.txt`

Mover DB existente (do diretório home para `instance/`)
```powershell
$env:PYTHONPATH='.'; .\venv\Scripts\python.exe .\scripts\move_db_to_instance.py
```

Recriar esquema (drop_all / create_all)
```powershell
$env:PYTHONPATH='.'; .\venv\Scripts\python.exe .\scripts\recreate_db.py
```

Importar TACO (gera 597 alimentos)
```powershell
$env:PYTHONPATH='.'; .\venv\Scripts\python.exe .\import_taco.py
```

Testar autocomplete
```powershell
$env:PYTHONPATH='.'; .\venv\Scripts\python.exe .\scripts\check_autocomplete_no_drop.py
```

Executar o servidor localmente
```powershell
$env:FLASK_APP='app.py'; $env:FLASK_ENV='development'; .\venv\Scripts\flask run
```

Observações
- O caminho padrão do DB agora é `instance/plataforma_nutri.db` — você pode sobrescrever com a variável de ambiente `APP_DB_URI`.
- Se quiser os dados embutidos em `taco_data.py`, rode `converter_csv.py`.
