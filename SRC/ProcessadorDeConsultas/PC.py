import logging
import pandas as pd 
import unicodedata

from lxml import etree


logging.basicConfig(level=logging.INFO, filename="programa.log", format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("Lendo arquivo de configuração")


arq = open("ProcessadorDeConsultas/PC.CFG")

config = {}
for linha in arq:
    l = linha.split("=")
    config[l[0]] = l[1].rstrip()

logging.info("Configurações lidas.")

logging.info("Caregando e validando o arquivo: " + config['LEIA'])


dtd = etree.DTD(open('CysticFibrosis2-20230404/data/cfcquery-2.dtd'))
parse = etree.XMLParser(dtd_validation=True)
xml = etree.parse( config['LEIA'], parse)

if (dtd.validate(xml)):
    logging.info("Leitura e validação do xml com DTD cfcquery-2.dtd realizada com sucesso")
else :
    logging.error("Falha na validação do arquivo xml " + config['LEIA'])


logging.info("Inicio da criação do arquivo de consultas: " + config['CONSULTAS'] )


QueryNumber = []
QueryText = []
listScore = []

for elem in xml.getroot():
    for subelem in elem:

        if(subelem.tag == 'QueryNumber'): 
            QueryNumber.append(subelem.text)
        else:
            if (subelem.tag == 'QueryText'):
                a = subelem.text.replace("\n","").replace("   ", " ")
                a = unicodedata.normalize("NFD",a)
                a = a.encode("ascii", "ignore")
                a = a.decode("utf-8").upper()
                QueryText.append(a)
            else:
                if (subelem.tag == 'Records'):
                    for item in subelem:
                        if (item.tag == 'Item'):
                            votes =  item.attrib['score']
                            countVotes = len(votes) - votes.count('0')
                            listScore.append([QueryNumber[len(QueryNumber)-1] , item.text, countVotes])

dadosConsulta = {'QueryNumber': QueryNumber,
                 'QueryText': QueryText
                 }


pd.DataFrame(dadosConsulta).to_csv('ProcessadorDeConsultas/'+ config['CONSULTAS'], index=False, sep=";")

logging.info("Arquivo de consultas criado: " + config['CONSULTAS'] )


logging.info("Inicio da criação do arquivo de esperados: " + config['ESPERADOS'] )

resultado_esperado = pd.DataFrame(listScore, columns=['QueryNumber', 'DocNumber', 'DocVotes'])


pd.DataFrame(resultado_esperado).to_csv('ProcessadorDeConsultas/'+ config['ESPERADOS'], index=False, sep=";")

logging.info("Arquivo de esperados criado: " + config['ESPERADOS'] )



