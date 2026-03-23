# Programa qe centraliza os códigos e organiza uma pipeline capaz de processar notas em massa

import pandas as pd
import numpy as np
from extracao import extrair_amostra
from proficiencia import processar_thetas
import regressao as rg

ano = 2022
lingua = 0 # 0 inglês e 1 espanhol

def nota_completa(area, prova, lingua, ano, plot=0):
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

    # Coleta informação dos itens
    caminho = f"ITENS_PROVA_{ano}.csv"
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
    A, B = rg.ajustar_regressao(thetas['theta_estimado'].values, thetas['nota_oficial'].values)

    # Calcula a nota estimada
    nota_estimada = A + thetas['theta_estimado'].values*B
    nota_estimada = np.round(nota_estimada, 2)
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
        rg.plotar_resultados(thetas['nota_oficial'].values, nota_estimada)
    
    return A, B, metricas

# Função com loop principal para processar várias provas ao mesmo tempo

provas = pd.read_csv(
    f"provas_{ano}.csv",
    sep=',',
    encoding="latin1",
)

lista_A = []
lista_B = []
lista_metricas = []

for _, prova in provas.iterrows():

    area = prova['area']
    cod = prova['codigo']
    lingua = int(not lingua) # Alterna entre inglês e espanhol

    A, B, metricas = nota_completa(area, cod, lingua, ano)

    lista_A.append(A)
    lista_B.append(B)
    lista_metricas.append(metricas)

# adiciona colunas
provas['A'] = lista_A
provas['B'] = lista_B

# expande métricas
metricas_df = pd.DataFrame(lista_metricas)

provas = pd.concat([provas, metricas_df], axis=1)

provas.to_csv(f"provas_{ano}.csv")