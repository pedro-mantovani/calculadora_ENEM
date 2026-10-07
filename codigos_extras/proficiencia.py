# Programa para determinar a proeficiência de um conjunto volumoso de participantes

import pandas as pd
import numpy as np

# Função para calcular a probabilidade de acerto de um item
def prob_item(theta, a, b, c):
    z = a * (theta - b)
    return c + (1 - c) / (1 + np.exp(-z))

# Função para calcular o logarítmo da função de verossimilhança
def calcular_log_likelihood(theta, resp, itens, base_pos):

    logL = np.zeros_like(theta)

    for _, dados in itens.iterrows():

        if dados['IN_ITEM_ABAN'] == 1:
            continue

        a = dados['NU_PARAM_A']
        b = dados['NU_PARAM_B']
        c = dados['NU_PARAM_C']

        pos = int(dados['CO_POSICAO']) - base_pos

        p = prob_item(theta, a, b, c)
        p = np.clip(p, 1e-9, 1 - 1e-9)

        if dados['TX_GABARITO'] == resp[pos]:
            logL += np.log(p)
        else:
            logL += np.log(1 - p)

    return logL

# Função para estimar o theta
def estimar_theta(resp, itens):

    theta = np.linspace(-4, 4, 400)

    base_pos = itens['CO_POSICAO'].iat[0]

    logL = calcular_log_likelihood(theta, resp, itens, base_pos)

    log_prior = -0.5 * theta**2
    log_post = logL + log_prior

    log_post -= np.max(log_post)

    posterior = np.exp(log_post)
    posterior /= np.trapezoid(posterior, theta)

    theta_eap = np.trapezoid(theta * posterior, theta)

    return theta_eap


def processar_thetas(participantes, itens, area, ano):

    theta_lista = []
    nota_lista = []

    resps = f"TX_RESPOSTAS_{area}"

    notas = f"NU_NOTA_{area}"

    for _, part in participantes.iterrows():

        # Entre 2021 e 2024 as respostas da língua estrangeira incuíam a substring '99999' representando a língua que não foi feita
        if (area == 'LC' and ano <= 2021 and ano >= 2015):
            part[resps] = part[resps].replace('99999', '')

        theta = estimar_theta(
            part[resps],
            itens
        )

        theta_lista.append(theta)
        nota_lista.append(part[notas])

    return pd.DataFrame({
        "nota_oficial": nota_lista,
        "theta_estimado": theta_lista
    })