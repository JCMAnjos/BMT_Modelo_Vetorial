import logging
import pandas as pd 
from nltk.tokenize import word_tokenize
from lxml import etree
import numpy as np

logging.basicConfig(level=logging.INFO, filename="programa.log", format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("Lendo arquivo de configuração")


arq = open("Buscador/BUSCA.CFG")

config = {}
for linha in arq:
    l = linha.split("=")
    config[l[0]] = l[1].rstrip()

logging.info("Configurações lidas.")

def lerArquivo_csv(path):
    return pd.read_csv(path, sep=";")


logging.info("Caregando o arquivo: " + config['MODELO'])

modelo = lerArquivo_csv(config['MODELO'])

logging.info("Arquivo Carregado")

logging.info("Caregando o arquivo: " + config['CONSULTAS'])

consultas = lerArquivo_csv(config['CONSULTAS'])

logging.info("Arquivo Carregado")

logging.info("Calculando os pesos dos tokens das consultas")

#gerando lista de pesos das consultas
pesos_consulta = []
for consulta_i in consultas['QueryText']:
    tmp = []
    tk = word_tokenize(consulta_i)
    for t in modelo['token']:
        if t in tk:
            tmp.append(1)
        else:
            tmp.append(0)
    pesos_consulta.append(tmp)

logging.info("Pesos dos tokens das consultas Calculados")

#multiplicando os pesos das consultas pelos pesos dos documentos

logging.info("Multiplicando os pesos das consultas pelos pesos dos documentos")

modelo_sem_tk = modelo.drop(columns=['token'])

#normalizando as matrizes de peso e documento
pesos_consulta_norm = []
for arr in pesos_consulta:
    pesos_consulta_norm.append(arr/np.linalg.norm(arr))

modelo_sem_tk_norm = modelo_sem_tk
for col in modelo_sem_tk_norm.columns:
    modelo_sem_tk_norm[col] = (modelo_sem_tk_norm[col]/np.linalg.norm(modelo_sem_tk_norm[col]))



resultado_consulta = np.dot(pesos_consulta_norm,modelo_sem_tk_norm)

logging.info("Finalizado")

logging.info("Colocando o resultado no formato para ser salvo")
resultado_final = []
for i in range(len(resultado_consulta)):
    #retorna array com o indice dos documentos na ordem decrescente
    indices = sorted(range(len(resultado_consulta[i])), key=lambda j: resultado_consulta[i][j], reverse=True)
    resultado_parcial = []
    for j in range(len(resultado_consulta[i])):
        tmp2 = [indices.index(j)+1,modelo_sem_tk.columns[j], resultado_consulta[i][j] ]
        resultado_parcial.append(tmp2)

    resultado_final.append([i+1,resultado_parcial])


pd.DataFrame(resultado_final).to_csv(config['RESULTADOS'], index=False, header=False, sep=";")

logging.info("Resultado salvo")

