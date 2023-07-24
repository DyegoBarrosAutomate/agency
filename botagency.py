import botsetup

import  json,  mysql.connector as cnx , os,  socket, time, traceback
from datetime   import datetime
from getmac     import get_mac_address as gma


versao_atual="v1.0.23.07.21"
Log_Agent = f"log_{datetime.now().strftime('%Y-%m-%d')}.log"
mac_address= gma()

# Numero maximo de conexões simultaneas permitida
Max_conection = 15

try: #abre o arquivo de setup
    localSetup = os.path.abspath(os.path.dirname(__file__)) # obtem o local de onde esse codigo esta sendo executado
    setupFile = f"{localSetup}/setup.json"
    print(setupFile)
    if os.path.exists(setupFile):
      print("Carregando o Setup") 
      pJson = open(setupFile, "r")
      parametros = json.load(pJson)
    elif not os.path.exists(setupFile): 
      parametros = [ {"host":"localhost","port":2979,"pacote":2048,"expurgo":90,
                       "dbhost":"localhost","dbuser":"srsuser","database":"SRSCloud",
                       "log_file":"/agency/","job_file":"/agency/","rec_file":"/agency/",
                       "log_trace":1,"log_alert":1,"log_warning":1,"log_danger":1
                       }  ]
      with open(Log_Agent, 'a') as f: f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - log_alert - Setup default\n")
      print("Setup default") 
    
    # Configuração do HOST , Porta do servidor e tamanho do Pacote de rede
    host             = parametros['host']
    Porta_de_rede    = int(parametros['port'])
    tamanho_do_pacote= int(parametros['pacote'])  

    # Diretório para verificação de arquivos JSON
    Pasta_Tarefas   = parametros['job_file']
    Pasta_Registros = parametros['rec_file']
    Log_Agent       = f"{parametros['log_file']}log_{datetime.now().strftime('%Y-%m-%d')}.log"

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
    with open(Log_Agent, 'a') as f: f.write(f"{datetime.now()} - log_danger - Erro: {err}\n")

# escreve o log
def log(nivel,log):
    if int(parametros[nivel]) == 1:
        with open(Log_Agent, 'a') as f: f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {nivel} - {log}\n")

# Conexao com o Base de dados
def conn_mysql():
    return cnx.connect(host=parametros['dbhost'], user=parametros['dbuser'], password='4utOMat3Mysql', database=parametros['database'])

def get_local_ip():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.error as e:
        return f"Erro ao obter o IP: {e}"
    
# Verifica se a Maquina esta ativa no Banco de dados
def maquina_ativa(chave_empresa, codigo_computador):  
    maquina = None
    records = None
    # obtem somente o empresaId dentro da chave_empresa
    empresaid=chave_empresa[19:55] 
    if botsetup.key(empresaid) == chave_empresa:
         sql = f"""select M.empresaid, M.hardwareId, M.nomemaquina AS maquina, M.ativo, null AS socket
                   from maquina M   left join empresa E on (E.empresaId=M.empresaId)
                   where E.ativo=1 and M.ativo=1 and M.hardwareId='{codigo_computador}'
                   and M.empresaId='{empresaid}' 
                 limit 1 ;"""
         cnxn = conn_mysql()   
         cursor = cnxn.cursor(dictionary=True)
         cursor.execute(sql)
         records = cursor.fetchall()
         cursor.close()
         cnxn.close()
         if records :
            for record in records:
                maquina = record["maquina"]
    if maquina is None:
       log('log_trace',f"BotAgent não identificado({codigo_computador}) verifique o cadastro")
    else:
       log('log_trace',f"BotAgent Associado: {maquina}")
    return maquina

def atualiza_maquina_online(codigo_empresa, codigo_computador, conector):
    empresaid = codigo_empresa[19:55]
    conector = str(conector).replace("'", "|")
    if empresaid == codigo_empresa:
        sql = f"""set @minha_maquina := ( SELECT m.maquinaid FROM Maquina AS m WHERE m.empresaId  = "{empresaid}" and m.hardwareId = "{codigo_computador}" limit 1 );   
               update Maquina set conector= '{conector}'  where empresaId='{empresaid}' and maquinaid = @minha_maquina;"""
        cnxn = conn_mysql()
        print(f"UPD: {sql} ")
        cursor = cnxn.cursor(dictionary=True)
        cursor.execute(sql, multi=True)
        cnxn.commit()
        cursor.close()
        cnxn.close()


def obtem_socket_bot(codigo_empresa, codigo_computador):
    conector = None
    empresaid=codigo_empresa[19:55]
    if botsetup.key(empresaid) == codigo_empresa:
         sql = f"""select M.conector from Maquina M   left join empresa E on (E.empresaId=M.empresaId)
                   where E.ativo=1 and M.ativo=1
                   and M.empresaId='{empresaid}' and M.hardwareId='{codigo_computador}'
                 limit 1 ;"""
         cnxn = conn_mysql()
         cursor = cnxn.cursor(dictionary=True)
         cursor.execute(sql)
         records = cursor.fetchall()
         cursor.close()
         cnxn.close()
         if records:
            for record in records:
                conector = record["conector"].replace("|","'")
    log('log_trace',f"conector: {conector}")
    return conector

def get_value(lista, campo_procurado, valor, campo_retorno):
    for dicionario in lista:
        if campo_procurado in dicionario and dicionario[campo_procurado] == valor:
            return dicionario.get(campo_retorno)
    return None


log('log_trace',f"< < < < SRS Server Bot {versao_atual} > > > >")
meuServer= socket.gethostname()
meuIp = get_local_ip()

# Cria o socket do servidor  (socket.AF_INET = familia de IPv4 ; socket.SOCK_STREAM = TCP / socket.SOCK_DGRAM  = UDP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((meuServer, Porta_de_rede))
log('log_trace',f"BotAgency Server: {meuServer} on line IP:{meuIp} : {Porta_de_rede}")

# Aguardar as conexões
server_socket.listen(Max_conection)
conexoes_ativas = []
log('log_trace','SRS Server aguardando conexões...')

print(f"chave {botsetup.key(parametros['empresa'])}")  # use somente para teste **** SEMPRE REMOVA ESSE PRINT ****

while True: 
    # Aceitar uma nova conexãoAssociado
    client_socket, addr = server_socket.accept()
    log('log_trace',f"Obtendo o BotAgent: {addr}")

    # Recebendo  credencial do cliente
    cracha_recebido = client_socket.recv(tamanho_do_pacote).decode()
    credencial = json.loads(cracha_recebido)

    # Valida credencial e consulta se a empresa e a maquina estao ativa
    try:
       cliente = maquina_ativa(credencial['chave'], credencial['hardwareId'])
    except Exception as erro:
       retorno = str(erro) 
       log('log_alert',f"Erro Maquina : {retorno}")
    
    if cliente is not None:

        # Atualizar o status do cliente para "Conexao ativa"  **** substituir por Update no banco de dados  ****
        log('log_alert',f"BotAgent Acoplado.: {addr}")
        botagent = f"{credencial['chave']}|{credencial['hardwareId']}"
        conexoes_ativas.append({'botagent': botagent, 'socket': client_socket})
                
        atualiza_maquina_online(credencial['chave'],credencial['hardwareId'],1)
        log('log_trace',f"BotAgent Disponivel {cliente} ({addr})\n")

        # Enviar confirmação para o cliente
        client_socket.sendall('Conectado'.encode())

        while True:
            # Verificar se existem arquivos JSON na pasta de tarefas
            Tarefa = os.listdir(Pasta_Tarefas)
            log('log_trace',f"Quantidade de JOB: {len(Tarefa)}")
            
            if Tarefa:
                for arquivo in Tarefa:
                    Tarefa_json = os.path.join(Pasta_Tarefas, arquivo)
                    Tarefa = arquivo.replace('.json','')
                    retorno = ""
                    with open(Tarefa_json, 'r') as f:
                        json_Tarefa_dados = json.load(f)
                    log('log_trace',f"Validando Tar.[{json_Tarefa_dados['TipoID']}]: {Tarefa}")
                      
                    # Valida o tipo da tarefa
                    if int(json_Tarefa_dados['TipoID']) not in(1,2,3,4,5,6,11,12,13,20):
                         log('log_alert',f"Não enviei a Tarefa {Tarefa}, TIPO INVALIDO!\n") 
                    else:
                        chave =  json_Tarefa_dados['chave']
                        hardId = json_Tarefa_dados['hardwareId']
                        # Valida a credencial da tarefa e se micro = "Conexao ativa"   **** consulta no banco de dados ****
                        botagent = f"{chave}|{hardId}"
                        cliente = maquina_ativa(chave,hardId)
                        # print(f"Arquivo:<{arquivo}> =>|{chave}|{hardId}|") 
                        if cliente is not None:
                           # Obtem socket do TDE on-line
                           # client_socket =  obtem_socket_bot(chave, hardId)
                           socket_task = get_value(conexoes_ativas,'botagent',botagent,'socket')
                           log('log_alert',f"BotAgent Acoplado.: {socket_task.getpeername()[0]}, {socket_task.getpeername()[1]}")
                           
                           try:
                              if socket_task is not None: 
                                 # Enviar o JSON para o cliente e obter Resposta
                                 socket_task.sendall(json.dumps(json_Tarefa_dados).encode())
                                 log('log_trace',f"Enviando Tarefa[{json_Tarefa_dados['TipoID']}] {Tarefa} ao BotAgent!")
                                 Resposta = socket_task.recv(tamanho_do_pacote).decode()
                              else :
                                 Resposta = f"BotAgent não conectado {hardId}"
                           except Exception as erro1:
                                 retorno = str(erro1) 
                                 Resposta = retorno
                                 log('log_alert',f"Retorno ({retorno}): {Tarefa}")
                           # Se executou move o Json para a pasta de Record
                           if Resposta ==  "Executado": 
                                 log('log_trace',f"Execução Realizada: {Tarefa}")
                                 try:
                                   # remover esse comentario depois dos testes os.rename(Pasta_Tarefas+arquivo, Pasta_Registros+"T_"+arquivo)
                                   # os.remove(Pasta_Tarefas+arquivo)   # Aqui ele apenas deleta o arquivo e não faz uma copia
                                   retorno = f"Tarefa Arquivada..: {Tarefa}\n"
                                 except Exception as erro:
                                   retorno = str(erro) 
                                   log('log_alert',f"Execução da {Tarefa}: {retorno}")
                           else:
                                 retorno = f"Resposta Recebida.: {Resposta}\n"
                           log('log_trace',f"{retorno}")
                        else :
                           log('log_alert',f"Não enviei a Tarefa {Tarefa}, verifique credencial!\n")  
                    print(f"{retorno}")
            # Aguardar 5 minutos antes de verificar novamente
            time.sleep(300)
            
            log('log_trace',f"TDEs Ativos: {len(conexoes_ativas)}\n")
    else:
        log('log_alert',f'Não foi possivel validar a credencial\n')

# Fechar o socket do servidor
server_socket.close()
