# Filtra as provas de um determinado ano que possuem itens
import pandas as pd
from pathlib import Path

# Escolha o ano
ano = 2025

"""
Altere para o caminho dos seus dados
Por padrão será na pasta dados/ITENS_PROVAS,
considerando que a pasta dados está uma pasta acima da atual
"""
atual = Path(__file__).resolve()
caminho = atual.parent.parent / 'dados' / 'ITENS_PROVAS' / f"ITENS_PROVA_{ano}.csv"

itens = pd.read_csv(
    caminho,
    sep=';',
    encoding="latin1",
    usecols=['SG_AREA', 'CO_PROVA', 'TX_COR']
)

provas = itens.drop_duplicates(ignore_index=True)

provas.columns = ['area', 'tipo', 'codigo']

provas['ano'] = ano

provas = provas[['ano','area','codigo','tipo']]
provas.to_csv(f"provas_{ano}.csv", index=False)