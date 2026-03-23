# Programa para plotar a curva característica de um item (CCI)

import numpy as np
import matplotlib.pyplot as plt

# Parâmetros
a = 1.5 #Discriminação
b = 0 #Dificuldade
c = 0.35 #Acerto ao acaso

# Intervalo de proficiência (theta)
theta = np.linspace(-6, 6, 1000)

# Função característica do item (modelo 3PL)
P = c + (1 - c) / (1 + np.exp(-a * (theta - b)))

# Criando o gráfico
plt.figure()
plt.plot(theta, P)

# Eixos centrais
plt.axhline(0)
plt.axvline(0)

# Linha indicando o parâmetro b (dificuldade)
plt.axvline(b, linestyle='--')

# Configurações visuais
plt.ylim(0, 1.05)
plt.xlim(-6, 6)
plt.grid(True)
plt.xlabel("Proficiência (θ)")
plt.ylabel("Probabilidade de Acerto")
plt.title("Curva Característica do Item")

plt.savefig('CCI.png')
