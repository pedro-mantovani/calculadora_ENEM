# Programa que centraliza os códigos e organiza uma pipeline capaz de processar notas em massa
# Processa todas as provas do arquivo "provas.csv"
# O formato padrão é com as seguintes colunas ano, area, codigo, tipo
# Uma forma de obte-la é usando o código filtrar_provas.py ou o arquivo codigos_provas.csv ou provas_com_participantes.csv
# Ambas estão na pasta dados e o segundo caso exclui as provas que não tiveram participantes divulgados
# Normalmente isso acontece por poucas pessoas terem feito a prova e permitir uma exposição indevida dos participantes

# Valores estimados da transformação linear aplicada por área
transformacao = {
    "LC": (499.977, 108.09),
    "CH": (501.487, 112.315),
    "CN": (501.142, 113.11),
    "MT": (500.016, 129.654),
}

import pandas as pd
import numpy as np
from extracao import extrair_amostra
from proficiencia import processar_thetas
import regressao as rg
from pathlib import Path

def nota_completa(area, prova, lingua, ano, plot=0, regressao = 0):
    """
    Função principal, recebe como parâmetro a área da prova, o código da prova
    A língua estrangeira da prova
    Um booleano indicando se é necessário plotar as figuras referentes às métricas
    Um booleno indicando se é necessário aplicar a regressão linear para estimar os parâmetros da transformação linear
    O padrão é usar os valores fixos.
    """
    # Coleta uma amostra de participantes
    participantes = extrair_amostra(area, prova, ano, lingua)

    if(participantes is None):
        return np.nan, np.nan, {
            "mae": np.nan,
            "rmse": np.nan,
            "erro_max": np.nan,
            "vies": np.nan,
            "correlacao": np.nan,
            "r2": np.nan
        }

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
        usecols=['CO_POSICAO', 'TX_GABARITO', 'TP_LINGUA', 'IN_ITEM_ABAN',
                'NU_PARAM_A', 'NU_PARAM_B', 'NU_PARAM_C', 'CO_PROVA']
    )
    itens = itens[itens['CO_PROVA'] == prova]
    if(area == 'LC'):
       itens = itens[itens['TP_LINGUA'] != int(not lingua)]
    itens = itens.sort_values(by='CO_POSICAO').reset_index(drop=True)

    # Calcula os theta
    thetas = processar_thetas(participantes, itens, area)

    # Calcula o A e B da transformação linear via regressão
    if regressao:
        A, B = rg.ajustar_regressao(thetas['theta_estimado'].values, thetas['nota_oficial'].values)
    else:
        A, B = transformacao[area]


    # Calcula a nota estimada
    nota_estimada = A + thetas['theta_estimado'].values*B
    nota_estimada = np.round(nota_estimada, 1)
    print(f"A estimado {A}")
    print(f"B estimado {B}")

    # Mede a precisão
    metricas = rg.calcular_metricas(thetas['nota_oficial'].values, nota_estimada)

    print("\nMétricas de desempenho:")
    print(f"Erro médio (MAE)  = {metricas['mae']:.4f}")
    print(f"Raiz do Erro Quadrático Médio (RMSE) = {metricas['rmse']:.4f}")
    print(f"Erro máximo = {metricas['erro_max']:.2f}")
    print(f"Viés = {metricas['vies']:.4f}")
    print(f"Correlação = {metricas['correlacao']:.6f}")
    print(f"R² = {metricas['r2']:.6f}")

    # Salva os gráficos de qualidade dos resultados
    if(plot):
        rg.plotar_resultados(thetas['nota_oficial'].values, nota_estimada, prova)
    
    return A, B, metricas

# Função com loop principal para processar várias provas ao mesmo tempo

provas = pd.read_csv(
    "provas.csv",
    sep=',',
    encoding="latin1",
)

lista_A = []
lista_B = []
lista_metricas = []

lingua = 0 # Língua estrangeira

for _, prova in provas.iterrows():

    area = prova['area']
    cod = prova['codigo']
    ano = prova['ano']

    A, B, metricas = nota_completa(area, cod, lingua, ano, plot = 0)

    lista_A.append(A)
    lista_B.append(B)
    lista_metricas.append(metricas)

# adiciona colunas
provas['A'] = lista_A
provas['B'] = lista_B

# expande métricas
metricas_df = pd.DataFrame(lista_metricas)

provas = pd.concat([provas, metricas_df], axis=1)

provas.to_csv(f"estimativas.csv")