import pandas as pd
import logging
import matplotlib.pyplot 
import math

logging.basicConfig(level=logging.INFO, filename="programa_comparador.log", format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("Lendo arquivo de configuração")

arq = open("ComparadorDeResultados/COMPARADOR.CFG")

config = {}
for linha in arq:
    l = linha.split("=")
    config[l[0]] = l[1].rstrip()

logging.info("Configurações lidas.")

def lerArquivo_csv(path):
    return pd.read_csv(path, sep=";")

def salvaArquivo_csv(data, path):
    data.to_csv(path, index=False, header=False, sep=";")

logging.info("Caregando o arquivo: " + config['RESULTADO'])

resultado = lerArquivo_csv(config['RESULTADO'])

logging.info("Arquivo Carregado")

logging.info("Caregando o arquivo: " + config['RESULTADO_ESPERADO'])

resultadoEsperado = lerArquivo_csv(config['RESULTADO_ESPERADO'])

logging.info("Arquivo Carregado")

def findPosicao(vetor,pos):
    for a in range(len(vetor)):
        if(vetor[a][0] == pos):
            return a
    return -1

logging.info("Calculando métricas")
pontos11Point = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9, 1]
resultadoFinalPorConsulta = []
resultado = open(config['RESULTADO'])
f1 = []
p5 = []
p10 = []
R_Precision_histogram = []
R_Precision_histogram.append([])
R_Precision_histogram.append([])
map = []
MRR = []
DCG = []
NDCG = []
numDocDCG = 10
for consulta in resultado:
    consultaResultado = consulta.split(";")
    consultaResultado[1] = eval(consultaResultado[1])
    resultEsperConsult = resultadoEsperado['QueryNumber']==int(consultaResultado[0])
    a = resultadoEsperado[resultEsperConsult]
    NumRecuperados = 0
    TotalRelevantes = len(a)

    if (TotalRelevantes==0):
        continue
    relevantesRecuperados = 0
    revocPrec = []
    revocPrec.append([])
    revocPrec.append([])
    f1tmp=[]
    p5_tmp = 0
    p10_tmp = 0
    map_tmp = []
    primeiro_relevante = True
    DCG_TMP = []
    for i in range(len(consultaResultado[1])):
        pos = findPosicao(consultaResultado[1],i+1)
        NumRecuperados = NumRecuperados+1
        if (a['DocNumber'].isin([int(consultaResultado[1][pos][1])]).any().any()):
            relevantesRecuperados = relevantesRecuperados+1
            map_tmp.append(relevantesRecuperados/NumRecuperados)
            if primeiro_relevante:
                MRR.append(1/(i+1))
                primeiro_relevante = False
            if (i<numDocDCG):
                w = 0
                acc = (int(a[a['DocNumber']==int(consultaResultado[1][pos][1])]['DocVotes']))
                if len(DCG_TMP)!= 0 :
                    w = DCG_TMP[-1]
                    acc = acc/math.log2(i+1)
                DCG_TMP.append(w + acc)
        else:
            if (i<numDocDCG):
                if len(DCG_TMP)== 0 :
                    DCG_TMP.append(0)
                else:
                    DCG_TMP.append(DCG_TMP[-1])    
        revocacao = relevantesRecuperados/TotalRelevantes
        precisao = relevantesRecuperados/NumRecuperados
        revocPrec[0].append(revocacao)
        revocPrec[1].append(precisao)
        try:
            f1tmp.append((2*revocacao*precisao)/(revocacao+precisao))
        except ZeroDivisionError:
            f1tmp.append(0)
        if (i+1 == 5):
            p5_tmp = precisao
        if (i+1 == 10):
            p10_tmp = precisao
        if (i+1 == TotalRelevantes):
            R_Precision_histogram[0].append(int(consultaResultado[0]))
            try:
                R_Precision_histogram[1].append(relevantesRecuperados/TotalRelevantes)
            except ZeroDivisionError:
                R_Precision_histogram[1].append(1)

    rc = [0]*11
    tmp = 0
    for pt in range(len(pontos11Point)):
        for i in range(tmp,len(revocPrec[0])):
            if (revocPrec[0][i]>=pontos11Point[pt]):
                rc[pt] = max(revocPrec[1][i:len(revocPrec[1])])
                tmp = i
                break
    resultadoFinalPorConsulta.append(rc)
    f1.append(f1tmp)
    p5.append(p5_tmp)
    p10.append(p10_tmp)
    map.append(sum(map_tmp)/TotalRelevantes)
    DCG.append(DCG_TMP)

    #criando DCG ideal para calculo do NDCG
    docVotes_sort = list(a.sort_values(by=['DocVotes'], ascending=False)['DocVotes'])
    NDCG_tmp = []
    for i in range(10):
        if (len(docVotes_sort)>=i+1):
            if (i == 0):
                NDCG_tmp.append(docVotes_sort[i])
            else:
                NDCG_tmp.append(NDCG_tmp[-1] + (docVotes_sort[i])/math.log2(i+1))  
        else:
            if (i == 0):
                NDCG_tmp.append(0)
            else:
                NDCG_tmp.append(NDCG_tmp[-1])
        try:  
            NDCG_tmp[i] = DCG_TMP[i]/NDCG_tmp[i]
        except ZeroDivisionError:
            NDCG_tmp[i] = 0
    NDCG.append(NDCG_tmp)

resultadoFinalPorConsulta_df = pd.DataFrame(resultadoFinalPorConsulta)
f1_df = pd.DataFrame(f1)
DCG_DF = pd.DataFrame(DCG)
NDCG_DF = pd.DataFrame(NDCG)

logging.info("Métricas Calculadas")

stemmer_nostemmer = config['RESULTADO'].split('.')[0].split('-')[1]

# matplotlib.pyplot.subplot(2, 4, 1)
matplotlib.pyplot.title("11 pontos de precisão e recall")
matplotlib.pyplot.xlabel('Revocação')
matplotlib.pyplot.ylabel('Precisão')
salvaArquivo_csv(pd.DataFrame([pontos11Point, resultadoFinalPorConsulta_df.mean()]), config['RESULTADOS'] + "11pontos-" + stemmer_nostemmer + ".csv")
matplotlib.pyplot.plot(pontos11Point, resultadoFinalPorConsulta_df.mean())
matplotlib.pyplot.savefig(config['RESULTADOS'] + "11pontos-" + stemmer_nostemmer +".png")
matplotlib.pyplot.clf()
# matplotlib.pyplot.subplot(2, 4, 2)
matplotlib.pyplot.title("F1")
matplotlib.pyplot.xlabel('Documentos Recuperados')
salvaArquivo_csv(pd.DataFrame([f1_df.columns, f1_df.mean()]), config['RESULTADOS'] + "F1-" + stemmer_nostemmer + ".csv")
matplotlib.pyplot.plot(f1_df.columns, f1_df.mean())
matplotlib.pyplot.savefig(config['RESULTADOS'] + "F1-" + stemmer_nostemmer +".png")
matplotlib.pyplot.clf()
# matplotlib.pyplot.subplot(2, 4, 3)
matplotlib.pyplot.title("Histograma de R-Precision")
matplotlib.pyplot.ylabel('R-Precision')
matplotlib.pyplot.xlabel('Numero da Query')
salvaArquivo_csv(pd.DataFrame(R_Precision_histogram), config['RESULTADOS'] + "Precision-Histogram-" + stemmer_nostemmer + ".csv")
matplotlib.pyplot.bar(R_Precision_histogram[0], R_Precision_histogram[1])
matplotlib.pyplot.savefig(config['RESULTADOS'] + "Precision-Histogram-" + stemmer_nostemmer +".png")
matplotlib.pyplot.clf()
# matplotlib.pyplot.subplot(2, 4, 4)
matplotlib.pyplot.title("DCG")
matplotlib.pyplot.xlabel('Documentos Recuperados')
matplotlib.pyplot.ylabel('DCG')
salvaArquivo_csv(pd.DataFrame([DCG_DF.columns, DCG_DF.mean()]), config['RESULTADOS'] + "DCG-" + stemmer_nostemmer + ".csv")
matplotlib.pyplot.plot(DCG_DF.columns, DCG_DF.mean())
matplotlib.pyplot.savefig(config['RESULTADOS'] + "DCG-" + stemmer_nostemmer +".png")
matplotlib.pyplot.clf()
# matplotlib.pyplot.subplot(2, 4, 5)
matplotlib.pyplot.title("NDCG")
matplotlib.pyplot.xlabel('Documentos Recuperados')
matplotlib.pyplot.ylabel('NDCG')
salvaArquivo_csv(pd.DataFrame([NDCG_DF.columns, NDCG_DF.mean()]), config['RESULTADOS'] + "NDCG-" + stemmer_nostemmer + ".csv")
matplotlib.pyplot.plot(NDCG_DF.columns, NDCG_DF.mean())
matplotlib.pyplot.savefig(config['RESULTADOS'] + "NDCG-" + stemmer_nostemmer +".png")
matplotlib.pyplot.clf()
# matplotlib.pyplot.show()

arq = open(config['RESULTADOS'] + "README-" + stemmer_nostemmer+ ".md","w")
arq.write("P@5: " + str(sum(p5)/len(p5)) + '\n')
arq.write("P@10: " + str(sum(p10)/len(p10)) + '\n')
arq.write("MAP: " + str(sum(map)/len(map)) + '\n')
arq.write("MRR: " + str(sum(MRR)/len(MRR)) + '\n')
arq.flush()
arq.close()

print("P@5: " + str(sum(p5)/len(p5)))
print("P@10: " + str(sum(p10)/len(p10)))
print("MAP: " + str(sum(map)/len(map)))
print("MRR: " + str(sum(MRR)/len(MRR)))

print()