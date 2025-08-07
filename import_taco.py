# import_taco.py (versão final e corrigida)
import csv
from app import app, db, Alimento


def importar_dados_taco():
    """
    Lê o arquivo taco_final.csv com os cabeçalhos corretos e popula a tabela Alimento.
    """
    with app.app_context():
        # Limpa a tabela para garantir uma importação limpa e evitar duplicatas
        try:
            num_rows_deleted = db.session.query(Alimento).delete()
            db.session.commit()
            if num_rows_deleted > 0:
                print(f"Banco de dados limpo. {num_rows_deleted} registros antigos de alimentos foram removidos.")
        except Exception as e:
            db.session.rollback()
            print(f"AVISO: Não foi possível limpar a tabela de alimentos. Erro: {e}")

        print("Iniciando a importação da Tabela TACO final...")

        try:
            with open('taco_alimentos.csv', mode='r', encoding='utf-8') as csv_file:
                # O leitor usará a primeira linha para identificar as chaves do dicionário
                leitor_csv = csv.DictReader(csv_file)

                alimentos_para_adicionar = []
                for linha in leitor_csv:
                    try:
                        # --- MUDANÇA CRÍTICA: Usando os nomes exatos das colunas do seu arquivo ---
                        nome = linha['Descrição dos alimentos'].strip()
                        kcal_str = linha['Energia..kcal.']
                        proteina_str = linha['Proteína..g.']
                        carbo_str = linha['Carboidrato..g.']
                        gordura_str = linha['Lipídeos..g.']

                        # Converte para float, tratando "NA" e outros valores não numéricos
                        kcal = float(kcal_str) if kcal_str and kcal_str != 'NA' else 0.0
                        proteina = float(proteina_str) if proteina_str and proteina_str != 'NA' else 0.0
                        carbo = float(carbo_str) if carbo_str and carbo_str != 'NA' else 0.0
                        gordura = float(gordura_str) if gordura_str and gordura_str != 'NA' else 0.0

                        # Cria o objeto Alimento
                        novo_alimento = Alimento(
                            nome=nome,
                            marca='TACO',
                            kcal_100g=kcal,
                            proteinas_100g=proteina,
                            carboidratos_100g=carbo,
                            gorduras_100g=gordura,
                            origem='TACO'
                        )
                        alimentos_para_adicionar.append(novo_alimento)

                    except (ValueError, TypeError, KeyError):
                        # Pula qualquer linha que ainda possa ter um formato inesperado
                        continue

                if alimentos_para_adicionar:
                    print(f"Leitura bem-sucedida. Preparando para adicionar {len(alimentos_para_adicionar)} alimentos.")
                    db.session.bulk_save_objects(alimentos_para_adicionar)
                    db.session.commit()
                    print(
                        f"Importação concluída com sucesso! {len(alimentos_para_adicionar)} alimentos foram adicionados.")
                else:
                    print("ERRO CRÍTICO: Nenhum alimento foi lido do arquivo. Verifique a primeira linha do seu CSV.")

        except FileNotFoundError:
            print("ERRO CRÍTICO: Arquivo 'taco_final.csv' não encontrado.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            db.session.rollback()


if __name__ == '__main__':
    importar_dados_taco()