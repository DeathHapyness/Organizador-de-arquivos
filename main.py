import os
import shutil
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import tempfile

# Categorias e extensões
categorias = {
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Documentos": [".pdf", ".docx", ".txt", ".xlsx"],
    "Vídeos": [".mp4", ".mkv", ".avi"],
    "Músicas": [".mp3", ".wav", ".aac"],
    "Compactados": [".zip", ".rar", ".7z"],
    "Programas": [".exe", ".msi"],
    "Outros": []
}

class OrganizadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de Arquivos Automático")
        self.root.geometry("720x700")
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Caminhos fixos: Downloads como origem, subpasta como destino
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        self.pasta_origem = downloads
        self.pasta_destino = os.path.join(downloads, "Organizados")

        self.status_var = tk.StringVar(value="Aguardando ação...")
        self.log_text = None

        self._build_interface()

    def _build_interface(self):
        # Botão organizar
        ctk.CTkButton(
            self.root,
            text="Organizar automaticamente (Downloads)",
            command=self.iniciar_organizacao,
            font=("Arial", 18, "bold"),
            fg_color="#2563eb",
            hover_color="#18e733",
            height=45,
            width=350
        ).pack(pady=15)

        # Status label
        self.status_label = ctk.CTkLabel(self.root, textvariable=self.status_var, font=("Arial", 14, "italic"), text_color="#666")
        self.status_label.pack(pady=5)

        # Campo log (Text widget)
        log_frame = ctk.CTkFrame(self.root)
        log_frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(log_frame, text="Log de Ações:", font=("Arial", 16, "bold")).pack(anchor="w", pady=5)
        self.log_text = tk.Text(log_frame, height=15, state="disabled", font=("Consolas", 11))
        self.log_text.pack(fill="both", expand=True)

        # Botão limpar log
        ctk.CTkButton(self.root, text="Limpar log", command=self.limpar_log, width=120).pack(pady=5)

        # Botão limpar temporários
        ctk.CTkButton(
            self.root,
            text="Limpar arquivos temporários",
            command=self.limpar_temporarios,
            font=("Arial", 15, "bold"),
            fg_color="#eab308",
            hover_color="#ca8a04",
            height=40,
            width=220
        ).pack(pady=5)

    def log(self, texto):
        self.status_var.set(texto)
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, texto + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update_idletasks()

    def organizar_pasta(self):
        origem = self.pasta_origem
        destino_base = self.pasta_destino

        if not os.path.isdir(origem):
            messagebox.showerror("Erro", "A pasta de Downloads não foi encontrada.")
            return

        if not os.path.exists(destino_base):
            os.makedirs(destino_base)

        arquivos = [f for f in os.listdir(origem) if os.path.isfile(os.path.join(origem, f))]
        total = len(arquivos)
        contagem = {cat: 0 for cat in categorias}

        if total == 0:
            self.log("Nenhum arquivo encontrado para organizar.")
            return

        for idx, arquivo in enumerate(arquivos, 1):
            caminho_arquivo = os.path.join(origem, arquivo)
            _, ext = os.path.splitext(arquivo)
            categoria = "Outros"
            for cat, exts in categorias.items():
                if ext.lower() in exts:
                    categoria = cat
                    break
            destino_cat = os.path.join(destino_base, categoria)
            if not os.path.exists(destino_cat):
                os.makedirs(destino_cat)
            try:
                shutil.move(caminho_arquivo, os.path.join(destino_cat, arquivo))
                contagem[categoria] += 1
                self.log(f"[{idx}/{total}] Movido '{arquivo}' para '{destino_cat}'")
            except Exception as e:
                self.log(f"Erro ao mover '{arquivo}': {e}")

        resumo = "Organização concluída:\n"
        for cat, qtd in contagem.items():
            resumo += f"  {cat}: {qtd} arquivo(s) movido(s)\n"
        self.log(resumo)

    def iniciar_organizacao(self):
        self.log("Iniciando organização automática na pasta Downloads...")
        self.organizar_pasta()

    def limpar_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self.status_var.set("Log limpo.")

    def limpar_temporarios(self):
        self.log("Iniciando limpeza de arquivos temporários...")
        pastas = [ 
            tempfile.gettempdir(), 
            r"C:\Windows\Temp",
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Temp")
        ]
        arquivos_removidos = 0
        removidos = []
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
                caminho = os.path.join(pasta, arquivo)
                try:
                    if os.path.isfile(caminho):
                        os.remove(caminho)
                        arquivos_removidos += 1
                        removidos.append(arquivo)
                    elif os.path.isdir(caminho):
                        shutil.rmtree(caminho)
                        arquivos_removidos += 1
                        removidos.append(arquivo + "/")
                except Exception as e:
                    self.log(f"Erro ao deletar {caminho}: {e}")
                atual += 1
                progress = atual / total if total > 0 else 1
                self.status_var.set(f"Limpando temporários... ({atual}/{total})")
                self.root.update_idletasks()
        self.status_var.set("Limpeza concluída.")
        if arquivos_removidos == 0:
            self.log("Nenhum arquivo temporário removido.")
        else:
            self.log(f"Foram removidos {arquivos_removidos} arquivos/pastas temporários:\n" + "\n".join(removidos))

if __name__ == "__main__":
    root = ctk.CTk()
    app = OrganizadorApp(root)
    root.mainloop()
