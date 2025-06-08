import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk  
import tempfile

# Dicionário de categorias e extensões
categorias = {
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Documentos": [".pdf", ".docx", ".txt", ".xlsx"],
    "Vídeos": [".mp4", ".mkv", ".avi"],
    "Músicas": [".mp3", ".wav", ".aac"],
    "Compactados": [".zip", ".rar", ".7z"],
    "Programas": [".exe", ".msi"],
    "Outros": []
}

class CategoriaConfig:
    def __init__(self, nome):
        self.nome = nome
        self.caminho = ""
        self.tipo = tk.StringVar(value="subpasta")  # "subpasta" ou "nova_pasta"

def escolher_destino(cat_config):
    pasta = filedialog.askdirectory(title=f"Escolha o destino para {cat_config.nome}")
    if pasta:
        cat_config.caminho = pasta
        campos_caminho[cat_config.nome].configure(text=pasta)

def organizar_pasta(pasta_origem, configs):
    arquivos = [f for f in os.listdir(pasta_origem) if os.path.isfile(os.path.join(pasta_origem, f))]
    total = len(arquivos)
    contagem = {cat: 0 for cat in categorias}
    for idx, arquivo in enumerate(arquivos, 1):
        caminho_arquivo = os.path.join(pasta_origem, arquivo)
        _, extensao = os.path.splitext(arquivo)
        categoria = "Outros"
        for cat, extensoes in categorias.items():
            if extensao.lower() in extensoes:
                categoria = cat
                break
        config = configs[categoria]
        if config.tipo.get() == "subpasta":
            destino = os.path.join(config.caminho, categoria)
        else:
            destino = config.caminho
        if not os.path.exists(destino):
            os.makedirs(destino)
        try:
            shutil.move(caminho_arquivo, os.path.join(destino, arquivo))
            contagem[categoria] += 1
        except Exception as e:
            print(f'Erro ao mover {arquivo}: {e}')
        # Atualiza a barra de progresso
        progress = idx / total if total > 0 else 1
        progress_var.set(progress)
        root.update_idletasks()
    progress_var.set(0)
    resumo = "\nResumo da organização:\n"
    for cat, qtd in contagem.items():
        resumo += f"{cat}: {qtd} arquivo(s) movido(s)\n"
    return resumo

def escolher_pasta_origem():
    pasta = filedialog.askdirectory(title="Selecione a pasta para organizar")
    if pasta:
        entrada_origem.set(pasta)

def iniciar_organizacao():
    pasta_origem = entrada_origem.get()
    if not pasta_origem or not os.path.isdir(pasta_origem):
        messagebox.showerror("Erro", "Selecione uma pasta de origem válida.")
        return
    for cat, config in configs.items():
        if not config.caminho:
            messagebox.showerror("Erro", f"Escolha o destino para {cat}.")
            return
    resultado = organizar_pasta(pasta_origem, configs)
    messagebox.showinfo("Organização concluída", resultado)

# Função para limpar arquivos temporários
def limpar_temporarios():
    pastas = [ 
        tempfile.gettempdir(), 
        r"C:\Windows\Temp",
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Temp")
    ]
    arquivos_removidos = 0 
    removidos = []
    # Conta total de arquivos/pastas para a barra de progresso
    total = 0
    for pasta in pastas:
        if not os.path.exists(pasta):
            continue
        total += len(os.listdir(pasta))
    atual = 0
    for pasta in pastas: 
        if not os.path.exists(pasta):
            continue 
        for arquivo in os.listdir(pasta):
            caminho_completo = os.path.join(pasta, arquivo)
            try:
                if os.path.isfile(caminho_completo):
                    os.remove(caminho_completo)
                    arquivos_removidos += 1 
                    removidos.append(arquivo)
                elif os.path.isdir(caminho_completo):
                    shutil.rmtree(caminho_completo)
                    arquivos_removidos += 1     
                    removidos.append(arquivo + "/")
            except Exception as e:
                print(f"Erro ao deletar {caminho_completo}: {e}")
            # Atualiza a barra de progresso
            atual += 1
            progress = atual / total if total > 0 else 1
            progress_var.set(progress)
            root.update_idletasks()
    progress_var.set(0)
    if arquivos_removidos == 0:
        mensagem = "Nenhum arquivo ou pasta temporária foi removido."
    else:
        mensagem = f"Foram removidos {arquivos_removidos} arquivos/pastas temporários:\n\n"
        mensagem += "\n".join(removidos)
    messagebox.showinfo("Limpeza concluída", mensagem)

# Configura o tema do customtkinter
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

# Cria a janela principal
root = ctk.CTk()
root.title("Organizador de Arquivos Avançado")
root.geometry("700x600")

entrada_origem = tk.StringVar()
configs = {cat: CategoriaConfig(cat) for cat in categorias}
campos_caminho = {}

# Mensagem de boas-vindas grande e centralizada
welcome_frame = ctk.CTkFrame(root, fg_color="transparent")
welcome_frame.pack(pady=25)
ctk.CTkLabel(
    welcome_frame,
    text="👋 Bem-vindo ao Organizador de Arquivos!",
    font=("Arial", 28, "bold"),
    text_color="#3370f3"
).pack(pady=10)

ctk.CTkLabel(
    welcome_frame,
    text="Organize seus arquivos facilmente escolhendo onde cada tipo deve ser salvo.",
    font=("Arial", 16),
    text_color="#444"
).pack(pady=2)

# Frame para seleção da pasta de origem
frame_origem = ctk.CTkFrame(root)
frame_origem.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(frame_origem, text="Pasta a organizar:", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
ctk.CTkEntry(frame_origem, textvariable=entrada_origem, width=350, font=("Arial", 13)).pack(side=tk.LEFT, padx=5)
ctk.CTkButton(frame_origem, text="Escolher", command=escolher_pasta_origem).pack(side=tk.LEFT, padx=5)

# Frame para configuração das categorias
frame_categorias = ctk.CTkFrame(root)
frame_categorias.pack(padx=10, pady=10, fill="x")
ctk.CTkLabel(
    frame_categorias,
    text="Configuração dos destinos por categoria",
    font=("Arial", 16, "bold")
).pack(anchor="w", pady=5)

for cat in categorias:
    frame = ctk.CTkFrame(frame_categorias)
    frame.pack(fill="x", pady=4, padx=5)
    ctk.CTkLabel(frame, text=cat, width=90, font=("Arial", 13)).pack(side=tk.LEFT, padx=2)
    campos_caminho[cat] = ctk.CTkLabel(frame, text="(Nenhum destino escolhido)", width=220, anchor="w", font=("Arial", 12))
    campos_caminho[cat].pack(side=tk.LEFT, padx=5)
    ctk.CTkButton(frame, text="Escolher destino", width=120, command=lambda c=configs[cat]: escolher_destino(c)).pack(side=tk.LEFT, padx=5)
    ctk.CTkRadioButton(frame, text="Subpasta", variable=configs[cat].tipo, value="subpasta").pack(side=tk.LEFT, padx=2)
    ctk.CTkRadioButton(frame, text="Nova pasta", variable=configs[cat].tipo, value="nova_pasta").pack(side=tk.LEFT, padx=2)

# Adicione a barra de progresso global
progress_var = tk.DoubleVar(value=0)

progress_bar = ctk.CTkProgressBar(root, variable=progress_var, width=500, height=20)
progress_bar.pack(pady=10)
progress_bar.set(0)

# Botão para iniciar organização
ctk.CTkButton(
    root,
    text="Organizar arquivos",
    command=iniciar_organizacao,
    font=("Arial", 18, "bold"),
    fg_color="#2563eb",
    hover_color="#18e733",
    height=45,
    width=220
).pack(pady=15)

# Botão para limpeza de arquivos temporários
ctk.CTkButton(
    root,
    text="Limpar arquivos temporários",
    command=limpar_temporarios,
    font=("Arial", 15, "bold"),
    fg_color="#eab308",
    hover_color="#ca8a04",
    height=40,
    width=220
).pack(pady=5)

root.mainloop()
