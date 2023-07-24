import subprocess

sucesso = "Executado"
insucesso = "Execução não concluida"

# 01 Plataforma Automate Enterprise
def auto_enterprise(meu_bot):   
        # Tipo 01 Plataforma Automate Enterprise
        process = subprocess.Popen(meu_bot)
        retorno = process.communicate()[0]
        if retorno is None:
           return sucesso
        else:
           return insucesso

# Tipo 02 Automate Desktop
def auto_desktop(meu_bot):
        process = subprocess.Popen(meu_bot)
        retorno = process.communicate()[0]
        if retorno is None:
           return sucesso
        else:
           return insucesso


# Tipo 03 Automation Anywhere
def auto_anywhere(meu_bot):
        process = subprocess.Popen(meu_bot)
        retorno = process.communicate()[0]
        if retorno is None:
           return sucesso
        else:
           return insucesso


# Tipo 04 MS Power Automate
def power_automate(meu_bot):
        process = subprocess.Popen(meu_bot)
        retorno = process.communicate()[0]
        if retorno is None:
           return sucesso
        else:
           return insucesso


# Tipo 05 UIPATH
def uipath(meu_bot):
        process = subprocess.Popen(meu_bot)
        retorno = process.communicate()[0]
        if retorno is None:
           return sucesso
        else:
           return insucesso


# Tipo 06 BluePrism
def blueprism(meu_bot):
        process = subprocess.Popen(meu_bot)
        retorno = process.communicate()[0]
        if retorno is None:
           return sucesso
        else:
           return insucesso

# Tipo 11 Script Python
def python_bot(meu_bot):
        process = subprocess.Popen(meu_bot)
        retorno = process.communicate()[0]
        if retorno is None:
           return sucesso
        else:
           return insucesso

# Tipo 12 Sistema legado (.NET, Java, C++, Etc)
def sistema_legado(meu_bot):
        process = subprocess.Popen(meu_bot)
        retorno = process.communicate()[0]
        if retorno is None:
           return sucesso
        else:
           return insucesso


def api_bot(meu_bot):
        process = subprocess.Popen(meu_bot)
        retorno = process.communicate()[0]
        if retorno is None:
           return sucesso
        else:
           return insucesso
