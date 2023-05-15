import logging
import pandas as pd 
from lxml import etree
from nltk.tokenize import RegexpTokenizer
import sys
sys.path.append("PorterStemmer")
from PorterStemmer import PorterStemmer


logging.basicConfig(level=logging.INFO, filename="programa.log", format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("Lendo arquivo de configuração")


arq = open("Indexador/GeradorDeListaInvertida/GLI.CFG")

config = {"STEMMER": '',
          "LEIA": [],
          "ESCREVA": ''}
for linha in arq:
    l = linha.split("=")
    if (l[0]=="LEIA"):
        config[l[0]].append(l[1].rstrip()) 
    else:
        config[l[0]] = (l[1].rstrip())   

logging.info("Configurações lidas.")


logging.info("Caregando e validando arquivos.")


dtd = etree.DTD(open('CysticFibrosis2-20230404/data/cfc-2.dtd'))
parse = etree.XMLParser(dtd_validation=True)

xml = []
for arq_name in config['LEIA']:
    logging.info("Caregando e validando o arquivo: " + arq_name)
    tmp_xml = etree.parse(arq_name, parse)
    if (dtd.validate(tmp_xml)):
        logging.info("Leitura e validação do xml com DTD cfcquery-2.dtd realizada com sucesso")
        xml.append(tmp_xml)
    else :
        logging.error("Falha na validação do arquivo xml " + arq_name)


logging.info("Fim da leitura dos arquivos xml")

logging.info("Inicio da criação do arquivo ESCREVA: " + config['ESCREVA'] )

docNum = []
docText = []
tokenizer = RegexpTokenizer(r'[a-zA-Z]{3,}') #\w*
for arq in xml:
    for elem in arq.getroot():
        foundABS = False
        recordnum = []
        abstract = []
        extract = []
        for subelem in elem:
            if (subelem.tag == "RECORDNUM"):
                recordnum.append(subelem.text.strip())
            else:
                if (subelem.tag == "ABSTRACT"):
                    foundABS = True
                    abstract.append(subelem.text)
                else :
                    if (subelem.tag == "EXTRACT"):
                        foundABS = True
                        extract.append(subelem.text)
        # Caso o documento tenha mais de um abstract, será considerado apenas um
        if (len(recordnum) > 0) :
            if (len(abstract) > 0):
                docNum.append(recordnum[0])
                #removendo acentos e colocando em amiusculo

                a = tokenizer.tokenize(abstract[0].lower())

                if (config['STEMMER'] == "STEMMER"):
                    porter = PorterStemmer()
                    for i in range(len(a)):
                        a[i] = (porter.stem(a[i],0,len(a[i])-1).upper())
                else: 
                    if config['STEMMER'] == "NOSTEMMER" :
                        for i in range(len(a)):
                            a[i] = (a[i].upper())
                    else:
                        for i in range(len(a)):
                            a[i] = (a[i].upper())


                #tokenizando o texto
                docText.append(a)
            else:
                if (len(extract)>0):
                    docNum.append(recordnum[0])
                    #removendo acentos e colocando em amiusculo
                    #tokenizando o texto
                    a = tokenizer.tokenize(extract[0].lower())

                    if (config['STEMMER'] == "STEMMER"):
                        porter = PorterStemmer()
                        for i in range(len(a)):
                            a[i] = (porter.stem(a[i],0,len(a[i])-1).upper())
                    else: 
                        if config['STEMMER'] == "NOSTEMMER" :
                            for i in range(len(a)):
                                a[i] = (a[i].upper())
                        else:
                            for i in range(len(a)):
                                a[i] = (a[i].upper())

                    docText.append(a) 

        # print(str(len(recordnum)) + "  " + str(len(abstract)) + "  " + str(len(extract)) )
                        
docList = [docNum,docText]

logging.info("Criando lista de tokens unicos")

list_of_unique_tokens = []

tmp = []
for tk in docList[1]:
    tmp = tmp + tk



list_of_unique_tokens = list(set(tmp))


logging.info("Lista de tokens unicos criada com " + str(len(list_of_unique_tokens)) + " tokens" )
logging.info("Fim da criação de lista de tokens unicos")

logging.info("Criando lista invertida")

countTimes = []
for palavra in list_of_unique_tokens:
    countNum = []
    for i in range(len(docList[1])):
        for k in range(docList[1][i].count(palavra)):
            countNum.append(docList[0][i])
    countTimes.append(countNum)


listaInvertida = {"token": list_of_unique_tokens ,
                  "DocCount": countTimes}

logging.info("Lista invertida criada")

logging.info("Salvando a lista invertida no arquivo " + config['ESCREVA'] + "-" + config['STEMMER'])

pd.DataFrame(listaInvertida).to_csv('Indexador/GeradorDeListaInvertida/'+ config['ESCREVA'] + "-" + config['STEMMER'] + ".csv", index=False, sep=";")



# unique_tokens = set(tmp)
# if (config['STEMMER'] == "STEMMER"):
#     porter = PorterStemmer()
#     for number in unique_tokens:
#         list_of_unique_tokens.append(porter.stem(number,0,len(number)-1).upper())
# else: 
#     if config['STEMMER'] == "NOSTEMMER" :
#         for number in unique_tokens:
#             list_of_unique_tokens.append(number)
#     else:
#         for number in unique_tokens:
#             list_of_unique_tokens.append(number)
