import SRSsetup , services 
import asyncio, socket, json, os, pystray, subprocess, traceback, sys
import tkinter as tk
from PIL       import Image
from pystray   import MenuItem as item
from datetime  import datetime
from getmac    import get_mac_address as gma


versao_atual = "v1.0.23.07.13"
Log_Agent = f"log_{datetime.now().strftime('%Y-%m-%d')}.log"
hardwareId = gma()

try: #abre o arquivo de setup e carrega as variaveis de ambiente
    
    localSetup = os.path.abspath(os.path.dirname(__file__)) # obtem o local de onde esse codigo esta sendo executado
    setupFile = f"{localSetup}/setup.json"
    # remover esse comentario antes de compilar o exe pJson = open(setupFile, "r")
    pJson = open("C:\Automate Brasil\SRS_cloud\BOT\setup.json", "r")
    parametros = json.load(pJson)

    # Configuração do HOST , Porta do servidor e tamanho do Pacote de rede
    host             = parametros['host']
    Porta_de_rede    = int(parametros['port'])
    tamanho_do_pacote= int(parametros['pacote'])  

    # Chave do cliente
    chave_empresa = SRSsetup.key(parametros['empresa'])

    # Diretório para verificação de arquivos JSON
    Pasta_Tarefas   = parametros['job_file']
    Pasta_Registros = parametros['rec_file']
    Log_Agent       = f"{parametros['log_file']}bot_{datetime.now().strftime('%Y-%m-%d')}.log"

    #verifica se precisa criar as pastas: 
    if not os.path.exists(os.path.dirname(Pasta_Tarefas)):
           os.makedirs(Pasta_Tarefas)
    if not os.path.exists(os.path.dirname(Pasta_Registros)):
           os.makedirs(Pasta_Registros)
    if not os.path.exists(os.path.dirname(parametros['log_file'])):
           os.makedirs(parametros['log_file'])
           if parametros['log_warning'] == 1: 
              with open(Log_Agent, 'a') as f: f.write(f"{datetime.now().strftime('%Y-%m-%d')} - log_warning - Pasta criada: {parametros['log_file']}\n")
  
except Exception as e: 
    err = traceback.format_exc()
    print(f"Olha isso={err}")
    with open(Log_Agent, 'a') as f: f.write(f"{datetime.now()} - log_danger - Erro: {err}\n")


# escreve o log, respeitando o parametro do nivel
def log(nivel,log):
    if parametros[nivel] == 1:
        with open(Log_Agent, 'a') as f: f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {nivel} - {log}\n")
  
def check_this(entrada):
      if entrada is None:
         return "Executado"
      else:
         log('log_trace',f"{entrada}")
         return "Execução não concluida"

# Processo asincrono para tratar a conexão com o servidor de socket
async def iniciar_conexao():

  # Dados JSON que você deseja enviar
  credencial = {
    'chave': chave_empresa,
    'hardwareId': hardwareId ,
  }
     
  # Serializar o objeto JSON em uma string
  cracha_json = json.dumps(credencial)

  try: 
     print(f"{host}:{Porta_de_rede}\n")
     log('log_trace',f"Localizando servidor: {host}:{Porta_de_rede} ... ")
   # Criar o socket e conectar ao servidor
     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     client_socket.connect((host, Porta_de_rede))

   # Enviar o código do cliente para o servidor
     client_socket.sendall(cracha_json.encode())
     log('log_trace',f"Env.Credencial= {cracha_json[11:17]}... {hardwareId}")
     resposta = client_socket.recv(tamanho_do_pacote).decode()
  except Exception as e:
     # Se ocorrer um erro, envia uma mensagem de erro para o cliente
     resposta = str(e)

  # Receber a confirmação do servidor
  log('log_trace',f'Resposta Recebida= {resposta}')

  if resposta == 'Conectado':
    while True:
        retorno= None
        # Receber o JSON do servidor
        log('log_trace',f"Aguardando Tarefas...\n")
        json_data = client_socket.recv(tamanho_do_pacote).decode()
        log('log_trace',f"Tarefa recebida({len(json_data)}.bts)")
        if len(json_data)>0:
          data = json.loads(json_data)
          tipo_id= int(data['TipoID'])
          log('log_alert',f"Avaliando Tarefa Tipo({tipo_id})")
          # Processar a tarefa recebida do servidor
          retorno = "."
          if os.path.exists(data["App"]):
              log('log_trace',f"Invocando Tarefa Tipo({tipo_id})")
              if tipo_id==1:       # Tipo 01 Plataforma Automate Enterprise
                 retorno = services.invokebot.auto_enterprise(data["App"])
              elif tipo_id==2:     # Tipo 02 Automate Desktop
                 retorno = services.invokebot.auto_desktop(data["App"])

              elif tipo_id==3:     # Tipo 03 Automation Anywhere
                  retorno = services.invokebot.auto_anywhere(data["App"])

              elif tipo_id==4:     # Tipo 04 MS Power Automate
                  retorno = services.invokebot.power_automate(data["App"])

              elif tipo_id==5:     # Tipo 05 UIPATH
                  retorno = services.invokebot.uipath(data["App"])

              elif tipo_id==6:     # Tipo 06 BluePrism
                  retorno = services.invokebot.blueprism(data["App"])

              elif tipo_id==11:    # Tipo 11 Script Python
                  retorno = services.invokebot.python_bot(data["App"])

              elif tipo_id==12:    # Tipo 12 Sistema legado (.NET, Java, C++, Etc)
                  try:
                    retorno = services.invokebot.sistema_legado(data["App"])
                  except Exception as e:
                    # Se ocorrer um erro, envia uma mensagem de erro para o cliente
                    retorno = str(e)
                  break
              elif tipo_id==13:     # Tipo 13 API
                  retorno = services.invokebot.api(data["App"])

              elif tipo_id==20:     # Tipo 20 Outros
                   try:
                   # Executa o programa
                     retorno = subprocess.run(data['App'], shell=True, capture_output=True)
                     check_this(retorno)
                   except Exception as e:
                        # Se ocorrer um erro, envia uma mensagem de erro para o cliente
                        retorno = str(e)
                   break
              else: 
                   retorno= "Tarefa com Tipo invalido"
               # Enviar status de execução
          else:
             retorno= "Não foi possivel invocar o bot"   
        else: 
           retorno = "Tarefa não recebida"
        client_socket.sendall(retorno.encode())
        log('log_trace',f"Status da Tarefa Tipo({tipo_id}): {retorno}")

  if resposta == 'Desconectado': 
    # Fechar o socket
    client_socket.close()
    log('log_trace',f". TDE não identificado, comunicação encerrada!")
  else:
    log('log_trace',f"Falha na conexão !")

# Fechar o socket do cliented
  client_socket.close()

# definição do menu o qual ficara disponivel ao clicar com o botao direito do mouse sobre o Icone deste BotAgent
def criar_menu():
    menu = (item('Conectar', lambda:asyncio.run(iniciar_conexao())),
            item('Sair', lambda: sys.exit())
            )
    return menu


def exibir_programa():
    log('log_trace',f"< < < < SRS BotAgent {versao_atual} > > > >")
    services.startbot.loading("Automate SRS:Iniciando BotAgent...", "C:\Automate Brasil\SRS_cloud\ICO\BOT_agent.png")
    image = Image.open('C:\Automate Brasil\SRS_cloud\ICO\SRSAgent.ico')    
    menu = criar_menu()
    icon = pystray.Icon("Servidor SRS-Agent", image, f"SRS-Agent {versao_atual}", menu)
    icon.run()
    

if __name__ == "__main__":
    exibir_programa()
    sys.exit()