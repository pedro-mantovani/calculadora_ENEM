# Calculadora ENEM

## Sumário

* [Sobre o projeto](#sobre-o-projeto)
* [Resultados](#resultados)
* [Estrutura do repositório](#estrutura-do-repositório)
* [Instalação](#instalação)
* [Uso rápido](#uso-rápido)
* [Exemplo de uso](#exemplo-de-uso)
* [Como funciona o cálculo](#como-funciona-o-cálculo)

  * [TRI e modelo 3PL](#1-tri--modelo-3pl)
  * [Estimativa da proficiência (θ)](#2-estimativa-da-proficiência-θ)
  * [Conversão para a escala do ENEM](#3-conversão-para-a-escala-do-enem)
* [Casos atípicos e inconsistências nos microdados](#casos-atípicos-e-inconsistências-nos-microdados)

  * [Provas com inconsistências estruturais](#provas-com-inconsistências-estruturais)
  * [Participantes atípicos](#participantes-atípicos)
* [Dados utilizados](#dados-utilizados)
* [Códigos extras](#códigos-extras)
* [Limitações](#limitações)
* [Reprodutibilidade](#reprodutibilidade)
* [Referências](#referências)
* [Contribuição](#contribuição)

---

# Sobre o projeto

Este projeto implementa uma abordagem reproduzível para estimar notas do ENEM utilizando Python e os microdados públicos disponibilizados pelo INEP.

A metodologia utiliza:

* Teoria de Resposta ao Item (TRI);
* modelo logístico de 3 parâmetros (3PL);
* estimação de proficiência via EAP (*Expected a Posteriori*).

A implementação foi construída a partir dos procedimentos metodológicos divulgados pelo INEP e consegue reproduzir as notas oficiais com alta fidelidade utilizando apenas:

* parâmetros psicométricos dos itens;
* vetor de respostas do participante.

---

# Resultados

Nos experimentos realizados entre 2009 e 2024:

* erro médio absoluto (MAE): ~0,03 pontos;
* mediana do erro: ~0,025 pontos;
* viés próximo de zero;
* alta estabilidade entre anos e áreas.

Isso indica que a metodologia consegue reproduzir o comportamento do sistema oficial com excelente aproximação para fins educacionais e analíticos.

---

# Estrutura do repositório

```text
.
├── calculadora.py
├── dados/
├── imagens/
├── codigos_extras/
├── README.md
```

## Pastas

### `dados/`

Contém:

* parâmetros dos itens;
* códigos de prova;
* métricas de desempenho;
* arquivos auxiliares para reprodução dos experimentos.

### `imagens/`

Gráficos e figuras utilizados na documentação.

### `codigos_extras/`

Scripts auxiliares utilizados nos experimentos e análises.

---

# Instalação

## 1. Clonar o repositório

```bash
git clone https://github.com/pedro-mantovani/calculadora_ENEM
```

## 2. Instalar dependências

```bash
pip install pandas numpy matplotlib
```

---

# Uso rápido

## Executar a calculadora

```bash
python3 calculadora.py
```

Note que para o uso exclusivo de cálculo de nota basta o código calculadora.py e a planilha com os itens das provas na mesma pasta.

O programa solicitará:

* ano da prova;
* código da prova;
* respostas do participante.

O sistema retornará:

* número de acertos;
* proficiência estimada (θ);
* nota final estimada.

---

# Exemplo de uso

## Entrada

```text
Ano: 2024
Código da prova: 1420

1. A
2. B
...
45. A
```

## Saída

```text
Acertos: 35
Theta: 1.1929388941456571
Nota: 654.68
```

---

# Como funciona o cálculo

# 1. TRI — modelo 3PL

Cada questão é representada por três parâmetros:

* **a** → discriminação;
* **b** → dificuldade;
* **c** → acerto ao acaso.

A probabilidade de acerto é dada por:

$$
P(\theta) =
c + \frac{1-c}{1 + e^{-a(\theta-b)}}
$$

## Interpretação intuitiva

* θ maior → maior chance de acerto;
* b alto → questão mais difícil;
* a alto → questão diferencia melhor os participantes;
* c alto → maior chance de acerto por chute.

---

# 2. Estimativa da proficiência (θ)

A proficiência é estimada utilizando o método EAP (*Expected a Posteriori*).

A implementação:

* assume priori normal padrão;
* calcula a distribuição posterior;
* aproxima numericamente as integrais;
* utiliza domínio logarítmico para estabilidade numérica.

## Aproximação numérica

O projeto utiliza:

* intervalo: [-4, 4];
* 400 pontos igualmente espaçados;
* método dos trapézios.

O INEP utiliza quadratura gaussiana, que é mais precisa, porém menos didática e mais complexa de reproduzir.

---

# 3. Conversão para a escala do ENEM

Após a estimação de θ:

$$
\text{Nota} = \mu + \sigma \theta
$$

Os parâmetros foram estimados empiricamente via regressão linear utilizando milhares de participantes reais.

## Valores médios estimados

| Área                 | $\mu$   | $\sigma$|
| -------------------- | ------- | ------- |
| Linguagens           | 499.977 | 108.091 |
| Ciências Humanas     | 501.487 | 112.315 |
| Ciências da Natureza | 501.141 | 113.108 |
| Matemática           | 500.015 | 129.654 |

---

# Casos atípicos e inconsistências nos microdados

Durante os experimentos foram identificadas inconsistências estruturais em subconjuntos específicos dos microdados do ENEM.

Esses casos produzem erros elevados mesmo quando a implementação está correta.

---

## Provas com inconsistências estruturais

Em alguns conjuntos de provas, foi observada uma combinação de forte viés negativo e erro médio na casa das dezenas de pontos, contrastando com o erro médio inferior a 0,03 ponto verificado na maioria dos casos.

A análise detalhada de um desses casos revelou uma despadronização no formato de exibição das respostas, comprometendo a correspondência entre o gabarito e as alternativas indicadas pelo participante.

Um desses casos ocorreu nas provas de Linguagens entre 2015 e 2021. Diferentemente das demais provas, que exibiam apenas as 45 respostas efetivamente respondidas pelo participante, essas provas também apresentavam uma sequência de cinco noves (“99999”) representando a língua estrangeira não escolhida.

Nesse cenário, o código funcionava corretamente, porém a correspondência entre as respostas corretas e as respostas do participante ficava comprometida, tornando os acertos praticamente aleatórios e acarretando a subestimação das notas.

Após a remoção dos “99999” das respostas dos participantes, o erro retornou ao patamar esperado, em torno de 0,03 ponto. Dessa forma, outras provas com tendências semelhantes foram desconsideradas da análise final, por possivelmente conterem inconsistências nos itens ou participantes que não representam adequadamente o método.

Das 571 provas analisadas, 56 foram desconsideradas. Seus resultados estão apresentados em [dados/provas_desconsideradas.csv](dados/provas_desconsideradas.csv).

---

## Participantes atípicos

Também foram identificados participantes com erros elevados, em particular, destaca-se um caso na edição de 2010, no qual um único participante apresentou erro de 279,32 pontos na prova de Ciências Humanas e 171,19 pontos na prova de Ciências da Natureza, enquanto os demais candidatos exibiram erros compatíveis com o padrão observado.

![outlier](imagens/outlier.png)

Observando o padrão de respostas desse participante, há indicios de que o código da prova do participante estão incorretos e as respostas de Humanas e Natureza estão invertidas.

Estimando a nota de Humanas usando as respostas de Natureza e o código de prova 86 (CH- Amarela) o erro cai de 279,32 para 0,03 pontos. Antálogamente, usando as respostas de Humanas com o código 90 (CN - Amarela) o erro cai de 171,19 pontos para 0,04.

Ademais, os códigos originais (101 e 105) são referentes à prova azul de reaplicação, o que não faz sentido visto que sua prova de LC e MT são da primeira aplicação.

Contudo, casos assim são isolados e difíceis de identificar, por isso, eles não foram tratados ou removidos dos dados.

---

# Dados utilizados

Os dados utilizados receberam o seguinte tratamento:

* Exclusão de participantes com nota zero

* Exclusão de colunas desnecessárias (usadas apenas as colunas de nota, respostas, código da prova e língua)

* Formato csv com separador e encoding padrão

* Remoção da substring "99999" das respostas de LC de 2015 a 2021

* Prova de 2009 não abre com a engine padrão do Pandas e não tem língua estrangeira, para resolver esse problema foi adicionado nos itens e na prova original a coluna TP_LINGUA, com valor padrão 0 (equivalente a uma prova de inglês), assim é possível estimar as notas de 2009 sem alterar o código.

Todos os dados padronizados estão disponíveis na plataforma [Zenodo](https://doi.org/10.5281/zenodo.20130840)

---

# Códigos extras

## `cci.py`

Gera gráficos da Curva Característica do Item (CCI).

---

## `EAPxMLE.py`

Compara estimativas EAP e MLE.

---

## `controler.py`

Executa avaliações em massa e calcula métricas de desempenho.

---

## `extracao.py`

Extrai participantes dos microdados.

---

## `proficiencia.py`

Estima proficiências individuais ou em lote.

---

## `regressao.py`

Estima os parâmetros lineares da escala do ENEM e métricas de avaliação.

---

# Limitações

Este projeto não reproduz exatamente o sistema oficial do INEP.

As principais diferenças incluem:

* uso de aproximação numérica simplificada;
* estimação empírica dos parâmetros de escala;
* ausência dos softwares oficiais utilizados pelo INEP;
* possíveis inconsistências presentes nos microdados públicos.

Apesar disso, os resultados obtidos apresentam excelente aproximação prática.

---

# Reprodutibilidade

O projeto disponibiliza:

* código-fonte;
* métricas;
* dados tratados;
* scripts de análise;
* gráficos;
* metodologia completa.

O objetivo é facilitar:

* auditoria;
* replicação;
* estudos sobre TRI;
* desenvolvimento de simuladores educacionais.

---

# Referências

* [*Entenda sua nota do ENEM*](https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_basica/entenda_a_sua_nota_no_enem_guia_do_participante.pdf) 

* [*ENEM: procedimentos de análise*](https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_basica/enem_procedimentos_de_analise.pdf)

* [INEP — Microdados ENEM](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem)

---

# Contribuição

Contribuições são bem-vindas.

Você pode:

* abrir issues;
* sugerir melhorias;
* enviar pull requests;
* reportar inconsistências nos microdados.