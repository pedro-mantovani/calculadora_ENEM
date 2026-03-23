# Programa para estrair dos resultados uma amostra de participantes

import pandas as pd

def carregar_resultados(ano, area, chunksize=1000):
    
    colunas = {
        "CH": ['CO_PROVA_CH', 'TX_RESPOSTAS_CH', 'NU_NOTA_CH'],
        "CN": ['CO_PROVA_CN', 'TX_RESPOSTAS_CN', 'NU_NOTA_CN'],
        "MT": ['CO_PROVA_MT', 'TX_RESPOSTAS_MT', 'NU_NOTA_MT'],
        "LC": ['CO_PROVA_LC', 'TX_RESPOSTAS_LC', 'NU_NOTA_LC', 'TP_LINGUA']
    }

    caminho = f"MICRODADOS_ENEM_{ano}.csv"

    return pd.read_csv(
        caminho,
        sep=';',
        encoding="latin1",
        usecols=colunas[area],
        chunksize=chunksize
    )


def extrair_amostra(area, cod_prova, ano, lingua, n=800):
    
    print(f"Processando prova {cod_prova}...")
    
    chunks = carregar_resultados(ano, area)

    total = 0
    lista_chunks = []
    col_prova = f"CO_PROVA_{area}"
    col_nota = f"NU_NOTA_{area}"

    for chunk in chunks:
        
        filtrado = chunk[
            (chunk[col_prova] == cod_prova) &
            (chunk[col_nota] > 0)
        ]
        if(area == "LC"):
            filtrado = filtrado[filtrado['TP_LINGUA'] == lingua]

        if not filtrado.empty:
            lista_chunks.append(filtrado)
            total += len(filtrado)
        
        if total >= 800:
            break

    if total == 0:
        print("Nenhum dado encontrado")
        return None

    elif total < 100:
        print(f"Poucos dados: {total}")

    else:
        print(f"OK: {total} participantes")
    
    participantes = pd.concat(lista_chunks, ignore_index=True)
    return participantes