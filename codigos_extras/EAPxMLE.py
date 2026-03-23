# Programa para visualizar a proficiencia de um aluno e comparar os métodos EAP e MLE

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

prova = 1408  # Código da prova
# Lingua para ser removida
lingua = 1 # 0 ingles, 1 espanhol

# Carregando os dados dos itens
# Altere para a planilha do seu ano
itens = pd.read_csv(
    "ITENS_PROVA_2024.csv",
    sep=';',
    encoding="latin1",
    usecols=['CO_POSICAO', 'TX_GABARITO', 'TP_LINGUA', 'IN_ITEM_ABAN',
             'NU_PARAM_A', 'NU_PARAM_B', 'NU_PARAM_C', 'CO_PROVA']
)

# Filtra a prova
itens = itens[itens['CO_PROVA'] == prova]
itens = itens[itens['TP_LINGUA'] != lingua]
itens = itens.sort_values(by='CO_POSICAO').reset_index(drop=True)

# Vetor de respostas do aluno
resp = "CECEBEDADCAADECDBBCBBDCCCACABBABBAEDDBEADBBCE"

# Intervalo de proficiência
theta = np.linspace(-5, 5, 600)

# Inicializa a verossimilhança
logL = np.zeros_like(theta)

acertos = 0
# Loop pelos itens
for _, dados in itens.iterrows():

    a = dados['NU_PARAM_A']
    b = dados['NU_PARAM_B']
    c = dados['NU_PARAM_C']

    # Índice da resposta
    pos = int(dados['CO_POSICAO']) - itens['CO_POSICAO'].iat[0]
    
    # Ignora itens anulados
    if dados['IN_ITEM_ABAN'] == 1:
        continue
    
    # Modelo logístico 3PL
    prob_item = c + (1 - c) / (1 + np.exp(-a * (theta - b)))
    
    # Se o aluno acertou ele soma o logarítmo da probabilidade de acerto (Equivalente a multiplicar)
    if dados['TX_GABARITO'] == resp[pos]:
        logL += np.log(prob_item)
        acertos += 1
    # Caso contrario ele soma a probabilidade de erro
    else:
        logL += np.log(1 - prob_item)
    
# Recupera L(theta) para visualização
logL_plot = logL - np.max(logL)
L = np.exp(logL_plot)

# 1. Calcula a prior
log_prior = -0.5*np.log(2*np.pi) - 0.5*theta**2

# 2. Calcula a posterior em log
log_posterior = logL + log_prior

# Volta da escala log
log_posterior -= np.max(log_posterior)
posterior = np.exp(log_posterior)

# Normaliza posterior
posterior /= np.trapezoid(posterior, theta)

# EAP
theta_eap = np.trapezoid(theta * posterior, theta)

print('Acertos:', acertos)
print("Theta EAP:", theta_eap)
theta_mle = theta[np.argmax(L)]
print("Theta MLE:", theta_mle)

# Plot
plt.figure(figsize=(8,5))

plt.plot(theta, L/np.max(L), label="Verossimilhança (MLE)")
plt.plot(theta, posterior/np.max(posterior), label="Posterior (EAP)")

plt.axvline(theta_eap, linestyle='--', label="Theta EAP")

plt.legend()
plt.grid(True)

plt.xlabel("Proficiência (θ)")
plt.ylabel("Densidade relativa")

plt.savefig('EAPxMLE.png')