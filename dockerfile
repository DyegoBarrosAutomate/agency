FROM python:latest

# Define the diretorio de trabalho dentro do container
WORKDIR /agency


# Copia o arquivo requirements.txt  para o diretorio de trabalho do container

COPY requirements.txt .

# instala todas as bibliotecas requeridas neste projeto do python

RUN pip install --upgrade pip 
RUN pip install -r requirements.txt

RUN apt-get -y update && apt-get -y install vim

COPY . .
CMD [ "python3", "botagency.py" ]

