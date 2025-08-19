"""Converte taco_alimentos.csv em taco_data.py com variável DADOS_TACO simplificada.
Gera apenas os campos necessários: nome, kcal_100g, carboidratos_100g, proteinas_100g, gorduras_100g
"""
import csv
import json

INPUT = 'taco_alimentos.csv'
OUTPUT = 'taco_data.py'

rows = []
with open(INPUT, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        nome = r.get('Descrição dos alimentos') or r.get('Descrição dos Alimentos') or ''
        if not nome:
            continue
        def tof(k):
            v = r.get(k, '')
            try:
                if v is None:
                    return 0.0
                vs = str(v).strip()
                if vs == '' or vs.upper() == 'NA':
                    return 0.0
                return float(vs)
            except Exception:
                return 0.0
        rows.append({
            'nome': nome.strip(),
            'kcal_100g': tof('Energia..kcal.') or tof('Energia (kcal)'),
            'carboidratos_100g': tof('Carboidrato..g.') or tof('Carboidrato..g'),
            'proteinas_100g': tof('Proteína..g.') or tof('Proteína..g'),
            'gorduras_100g': tof('Lipídeos..g.') or tof('Lipídeos..g')
        })

with open(OUTPUT, 'w', encoding='utf-8') as out:
    out.write('# Auto-gerado a partir de taco_alimentos.csv\n')
    out.write('DADOS_TACO = ')
    json.dump(rows, out, ensure_ascii=False, indent=2)
    out.write('\n')
print(f'Gerado {OUTPUT} com {len(rows)} itens.')
