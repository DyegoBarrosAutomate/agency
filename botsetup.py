# Ultima atualização em 13/06/2023  Dev: Denilson

# data_atual   =  data corrente
# dia_literal  =  contatena a string "Aut" com o dia literal(um,dois,tres...), para garantir no minimo 5 caracteres
# dia_literal  =  em seguida guardo apenas os ultimos 5 caracteres
# no For ele prepara a variavel "hexadecimal" 
# codigo_hexa = transforma em hexa (dia,mes,dia) da "data_atual" e contatena com o conteudo da variavel "hexadecimal"
# chave = contatena uma sequencia especifica entre a variavel codigo_hexa com o parametro "v"

from datetime  import datetime
from num2words import num2words

def key(v):
  data_atual  = datetime.now().date()
  dia_literal = "Aut"+num2words(int(data_atual.strftime("%d")), lang='pt_BR') 
  dia_literal = dia_literal[-5:] 
  hexadecimal = ""

  for letra in dia_literal:
        valor_decimal = ord(letra)
        valor_hexa    = hex(valor_decimal)
        hexadecimal  += valor_hexa
  
  hexadecimal = hexadecimal.replace("0x","")        
  
  codigo_hexa = hex(int(data_atual.strftime("%d%m%d")))+hexadecimal
  
  chave = f"{codigo_hexa}-b{v}-b{codigo_hexa[::-1]}y-{codigo_hexa[6:4]}f{hexadecimal[::-1]}5e-{codigo_hexa[6:3]}c{hexadecimal}d{codigo_hexa[::-1]}9"
  
  return chave

