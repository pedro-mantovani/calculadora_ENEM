# Programa para ajustar A e B via regressão linear e medir o erro das estimativas

import numpy as np
import matplotlib.pyplot as plt

# Ajuste de A e B via regressão linear
def ajustar_regressao(theta, nota):
    B, A = np.polyfit(theta, nota, 1)
    return A, B

# Métricas de erro
def calcular_metricas(nota_real, nota_modelo):

    erro = nota_modelo - nota_real

    mae = np.mean(np.abs(erro))
    rmse = np.sqrt(np.mean(erro**2))
    erro_max = np.max(np.abs(erro))
    vies = np.mean(erro)
    correlacao = np.corrcoef(nota_modelo, nota_real)[0,1]
    r2 = correlacao**2

    return {
        "mae": mae,
        "rmse": rmse,
        "erro_max": erro_max,
        "vies": vies,
        "correlacao": correlacao,
        "r2": r2
    }

# Função para gerar os gráficos de desempenho
def plotar_resultados(nota_real, nota_modelo):

    plt.figure()
    plt.scatter(nota_real, nota_modelo, alpha=0.6)
    plt.plot(
        [min(nota_real), max(nota_real)],
        [min(nota_real), max(nota_real)],
        linestyle='--'
    )
    plt.xlabel("Nota Oficial")
    plt.ylabel("Nota Modelo")
    plt.title("Nota Oficial vs Estimada")
    plt.grid(True)
    plt.savefig("real_modelo.png")

    plt.figure(figsize=(6,5))
    plt.scatter(nota_real, nota_real-nota_modelo, alpha=0.6)
    plt.axhline(0, linestyle='--')
    plt.xlabel("Nota Oficial")
    plt.ylabel("Resíduo (Modelo - Oficial)")
    plt.title("Análise de Resíduos")
    plt.grid(True)
    plt.savefig("residuos.png")