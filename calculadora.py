import pandas as pd
import numpy as np

# Valores estimados da transformação linear aplicada por área
transformacao = {
    "LC": (499.977, 108.091),
    "CH": (501.487, 112.315),
    "CN": (501.141, 113.108),
    "MT": (500.015, 129.654),
}

siglas = {
    "LC": "Linguagens",
    "CH": "Ciências Humanas",
    "CN": "Ciências da Natureza",
    "MT": "Matemática",
}

# Função para calcular a probabilidade de acerto de um item
def prob_item(theta, a, b, c):
    z = a * (theta - b)
    return c + (1 - c) / (1 + np.exp(-z))

# Função para calcular o logarítmo da função de verossimilhança
def calcular_log_likelihood(theta, resp, itens, base_pos):

    logL = np.zeros_like(theta)
    acertos = 0

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
            acertos += 1
        else:
            logL += np.log(1 - p)

    print(f"Acertos: {acertos}")
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

if __name__ == "__main__":
    # Recebe do teclado os dados básicos
    print("Seja bem vindo à calculadora de notas do ENEM!\n")
    print("Para começar digite:")
    ano = input("Ano da prova ")

    caminho = f"ITENS_PROVA_{ano}.csv"

    # Carregando os dados dos itens
    try:
        df = pd.read_csv(
            caminho,
            sep=';',
            encoding="latin1",
            usecols=[
                'CO_POSICAO', 'TX_GABARITO', 'TP_LINGUA',
                'IN_ITEM_ABAN', 'NU_PARAM_A', 'NU_PARAM_B',
                'NU_PARAM_C', 'CO_PROVA', 'SG_AREA'
            ]
        )
    except FileNotFoundError:
        print(f"Arquivo {caminho} não encontrado")
        exit()

    # Encontrando a prova
    itens = df
    area = None
    
    while True:
        prova = int(input("\nCódigo da prova: "))
        itens = df[df['CO_PROVA'] == prova]
        if(len(itens) == 0):
            print("Código de prova não encontrado, tente novamente\n")
        else:
            area = itens['SG_AREA'].iat[0]
            print(f"Prova de {siglas[area]}\n")
            break

    if(area == 'LC'):
        lingua = int(input("Língua estrangeira (0 = inglês, 1 = espanhol): "))
        itens = itens[itens['TP_LINGUA'] != int(not lingua)]

    itens = itens.sort_values(by='CO_POSICAO').reset_index(drop=True)

    print("Agora escreva suas respostas")

    resp = ['0'] * 45
    for item in range(0, 45):
        resp[item] = input(f"{item+1}. ").upper()

    theta = estimar_theta(resp, itens)

    # Cálculo da nota final (transformação linear)
    A, B = transformacao[area]
    nota = A + B*theta

    print("Theta:", theta)
    print(f'Nota: {nota:.2f}')