from tkinter import Tk, Label
from PIL import Image, ImageTk

def loading(mensagem, caminho_imagem):
    # Cria uma janela
    janela = Tk()
    janela.title("Iniciando SRS Agent...")

    # Carrega a imagem
    imagem = Image.open(caminho_imagem)
    foto = ImageTk.PhotoImage(imagem)

    # Cria um rótulo para exibir a imagem
    label_imagem = Label(janela, image=foto)
    label_imagem.pack()

    # Cria um rótulo para exibir a mensagem
    label_mensagem = Label(janela, text=mensagem)
    label_mensagem.pack()

    # Define o tamanho e a posição da janela
    largura_janela = imagem.width
    altura_janela = imagem.height   # Altura da imagem + altura do rótulo de mensagem
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    pos_x = (largura_tela - largura_janela) // 2
    pos_y = (altura_tela - altura_janela) // 2
    janela.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

    # Impede que a janela seja redimensionada pelo usuário
    janela.resizable(False, False)
    janela.after(1000,janela.destroy)
    # Executa o loop principal da janela
    janela.mainloop()
