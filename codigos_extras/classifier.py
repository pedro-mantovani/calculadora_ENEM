# Este código visa categorizar todos os tipos de prova de um determinado ano
import pandas as pd

ano = 2021

def categorizar_provas(ano):

    caminho = f"ITENS_PROVA_{ano}.csv"

    df = pd.read_csv(
        caminho,
        sep=';',
        encoding='latin1',
        usecols=['CO_PROVA', 'SG_AREA', 'TX_COR', 'IN_ITEM_ABAN']
    )

    # Itens válidos
    df_validos = df[df['IN_ITEM_ABAN'] != 1]

    n_itens = (
        df_validos
        .groupby('CO_PROVA')
        .size()
        .reset_index(name='n_itens_validos')
    )

    provas_info = (
        df[['CO_PROVA', 'SG_AREA', 'TX_COR']]
        .drop_duplicates()
    )

    provas = provas_info.merge(n_itens, on='CO_PROVA', how='left')

    provas['ano'] = ano

    provas = provas.rename(columns={
        'CO_PROVA': 'codigo',
        'SG_AREA': 'area',
        'TX_COR': 'cor'
    })

    provas = provas.sort_values(by=['area', 'codigo'])
    return provas[['ano', 'codigo', 'area', 'cor', 'n_itens_validos']]

provas = categorizar_provas(ano)

provas.to_csv(f"provas_{ano}.csv", index=False)