import logging
import pandas as pd 
import math



logging.basicConfig(level=logging.INFO, filename="programa.log", format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("Lendo arquivo de configuração")


arq = open("Indexador/INDEX.CFG")

config = {}
for linha in arq:
    l = linha.split("=")
    config[l[0]] = l[1].rstrip()  

logging.info("Configurações lidas.")

logging.info("Lendo Lista Invertida")

lista_invertida = pd.read_csv(config["LEIA"], sep=";")

logging.info("Lista Invertida carregada")

logging.info("Calculando numero de documentos na lista invertida")

lista_documentos = set()
for key in list(lista_invertida['DocCount'].to_list()):
    lista_documentos.update(eval(key))

logging.info("Numero de documentos na lista invertida: " + str(len(lista_documentos)))

#Lista de documentos criada, agora tem que fazer a matriz termo documento
doc_ls = list(lista_documentos)

logging.info("Gerando matriz termo documento e calculando TF-IDF")
vec = []
pattern = "^[A-Z]"
for index in range(len(lista_invertida['token'])):
    if ( len(str(lista_invertida['token'][index])) < 2) : 
        continue
    tmp = []
    tmp.append(lista_invertida['token'][index]) 
    for doc_index in doc_ls:
        vet = eval(lista_invertida["DocCount"][index])
        tmp.append(vet.count(doc_index)) 
    
    vec.append(tmp)

#calculando TF-IDF
vecDF = pd.DataFrame(vec)
for j in range(len(vec[0])):
    if j != 0:
        for i in range(len(vec)):
            if vec[i][j] != 0:
                posTk = lista_invertida["token"].tolist().index(vec[i][0])
                vet = list(eval(lista_invertida["DocCount"][posTk]))
                tij = vet.count(doc_ls[j-1])
                #maior frequencia entre os termos do documento
                maxtij = max(vecDF[j])
                N = len(doc_ls)
                nj = len(set(vet))

                vec[i][j] = (tij/maxtij)*math.log10(N/nj)
               # vec[i][j] = tij*math.log10(N/nj)

logging.info("Matriz Termo documento gerada")

logging.info("Salvando Modelo")
df = pd.DataFrame(vec)
doc_ls.insert(0,"token")
df.columns = doc_ls
df.to_csv(config['ESCREVA'], index=False, sep=";")

logging.info("Modelo salvo")



