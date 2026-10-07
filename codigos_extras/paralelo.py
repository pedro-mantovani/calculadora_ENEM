# Programa que centraliza os códigos e organiza uma pipeline capaz de processar notas em massa
# Processa todas as provas do arquivo "provas.csv"

import pandas as pd
import numpy as np
from extracao import extrair_amostra
from proficiencia import processar_thetas
import regressao as rg
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

# Valores estimados da transformação linear aplicada por área
transformacao = {
    "LC": (499.977, 108.09),
    "CH": (501.487, 112.315),
    "CN": (501.142, 113.11),
    "MT": (500.016, 129.654),
}

def nota_completa(area, prova, lingua, ano, plot=0, regressao=0):
    """
    Função principal, recebe como parâmetro a área da prova, o código da prova
    A língua estrangeira da prova
    """
    participantes = extrair_amostra(area, prova, ano, lingua)

    if participantes is None:
        return np.nan, np.nan, {
            "mae": np.nan,
            "rmse": np.nan,
            "erro_max": np.nan,
            "vies": np.nan,
            "correlacao": np.nan,
            "r2": np.nan
        }

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
    if area == 'LC':
       itens = itens[itens['TP_LINGUA'] != int(not lingua)]

    itens = itens.sort_values(by='CO_POSICAO').reset_index(drop=True)

    thetas = processar_thetas(participantes, itens, area, ano)

    if regressao:
        A, B = rg.ajustar_regressao(thetas['theta_estimado'].values, thetas['nota_oficial'].values)
    else:
        A, B = transformacao[area]

    nota_estimada = A + thetas['theta_estimado'].values * B
    nota_estimada = np.round(nota_estimada, 1)
    
    print(f"Processado - Prova: {prova} | Ano: {ano} | A: {A:.3f} | B: {B:.3f}")

    metricas = rg.calcular_metricas(thetas['nota_oficial'].values, nota_estimada)

    if plot:
        rg.plotar_resultados(thetas['nota_oficial'].values, nota_estimada, prova)
    
    return A, B, metricas

# Função auxiliar para processar uma única linha do DataFrame em paralelo
def processar_linha(row_idx, row, lingua):
    area = row['area']
    cod = row['codigo']
    ano = row['ano']
    A, B, metricas = nota_completa(area, cod, lingua, ano, plot=0, regressao=0)
    return row_idx, A, B, metricas

if __name__ == '__main__':
    provas = pd.read_csv(
        "provas.csv",
        sep=',',
        encoding="latin1",
    )

    lingua = 0  # Língua estrangeira
    
    # Dicionários ou listas para armazenar os resultados mapeados pelo índice original
    resultados = {}

    # Define o número de núcleos (usa todos os disponíveis ou deixa 1 de folga)
    max_workers = max(1, os.cpu_count() - 1)
    print(f"Iniciando processamento paralelo com {max_workers} núcleos...")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Envia todas as tarefas para o pool de processos
        futures = {
            executor.submit(processar_linha, idx, row, lingua): idx 
            for idx, row in provas.iterrows()
        }

        # Coleta os resultados à medida que vão terminando
        for future in as_completed(futures):
            try:
                idx, A, B, metricas = future.result()
                resultados[idx] = (A, B, metricas)
            except Exception as e:
                idx = futures[future]
                print(f"Erro ao processar a linha {idx}: {e}")
                resultados[idx] = (np.nan, np.nan, {
                    "mae": np.nan, "rmse": np.nan, "erro_max": np.nan, 
                    "vies": np.nan, "correlacao": np.nan, "r2": np.nan
                })

    # Reorganiza os resultados na ordem correta do DataFrame original
    lista_A = [resultados[i][0] for i in range(len(provas))]
    lista_B = [resultados[i][1] for i in range(len(provas))]
    lista_metricas = [resultados[i][2] for i in range(len(provas))]

    # Adiciona colunas ao DataFrame
    provas['A'] = lista_A
    provas['B'] = lista_B

    # Expande métricas
    metricas_df = pd.DataFrame(lista_metricas)
    provas = pd.concat([provas, metricas_df], axis=1)

    provas.to_csv("estimativas.csv", index=False)
    print("Processamento concluído e salvo em 'estimativas.csv'.")