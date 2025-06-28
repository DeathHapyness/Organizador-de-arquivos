import os
import shutil
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import tempfile
import threading
import time
import json
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        self.root.geometry("900x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.config_file = os.path.join(os.path.expanduser("~"), ".organizador_config.json")
        self.pasta_origem = self.carregar_preferencias().get("pasta_origem", os.path.join(os.path.expanduser("~"), "Downloads"))
        self.pasta_destino = os.path.join(self.pasta_origem, "Organizados")
        self.status_var = tk.StringVar(value="Bem-vindo! Pronto para organizar seus arquivos.")
        self.log_text = None
        self.log_file = os.path.join(self.pasta_destino, "log_organizacao.txt")
        self.log_visible = False
        self._build_interface()
        self.root.after(1000, self.iniciar_organizacao)
        self._agendar_organizacao_periodica()

    def carregar_preferencias(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def salvar_preferencias(self):
        prefs = {"pasta_origem": self.pasta_origem}
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(prefs, f)
        except Exception:
            pass

    def escolher_pasta(self):
        pasta = filedialog.askdirectory(title="Escolha a pasta para organizar")
        if pasta:
            self.pasta_origem = pasta
            self.pasta_destino = os.path.join(pasta, "Organizados")
            self.salvar_preferencias()
            self.status_var.set(f"Nova pasta selecionada: {pasta}")

    def mostrar_grafico(self):
        contagem = self.contagem_arquivos_por_categoria()
        fig, ax = plt.subplots(figsize=(5, 4))
        categorias_labels = list(contagem.keys())
        valores = list(contagem.values())
        ax.pie(valores, labels=categorias_labels, autopct='%1.1f%%', startangle=140)
        ax.set_title('Distribuição dos Arquivos Organizados')
        win = tk.Toplevel(self.root)
        win.title("Relatório Visual")
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def contagem_arquivos_por_categoria(self):
        resultado = {cat: 0 for cat in categorias}
        if not os.path.exists(self.pasta_destino):
            return resultado
        for cat in categorias:
            pasta_cat = os.path.join(self.pasta_destino, cat)
            if os.path.exists(pasta_cat):
                resultado[cat] = len([f for f in os.listdir(pasta_cat) if os.path.isfile(os.path.join(pasta_cat, f))])
        return resultado

    def mostrar_ajuda(self):
        msg = ("Bem-vindo ao Organizador de Arquivos!\n\n" 
               "- Clique em 'Escolher Pasta' para selecionar qualquer pasta para organizar.\n"
               "- Use 'Relatório Visual' para ver um gráfico dos arquivos organizados.\n"
               "- O log mostra tudo que acontece, clique em 'Ver Log'.\n"
               "- Limpe cache e temporários com os botões apropriados.\n"
               "- Suas preferências são salvas automaticamente.\n\n"
               "Dúvidas? Entre em contato!")
        messagebox.showinfo("Ajuda", msg)

    def _agendar_organizacao_periodica(self):
        def agendar():
            while True:
                time.sleep(600)  
                self.root.after(0, self.iniciar_organizacao)
        t = threading.Thread(target=agendar, daemon=True)
        t.start()

    def _build_interface(self):
        # Título estilizado
        ctk.CTkLabel(self.root, text="Organizador de Arquivos", font=("Arial Black", 28, "bold"), text_color="#22d3ee").pack(pady=10)

        # Botão escolher pasta
        ctk.CTkButton(
            self.root,
            text="Escolher Pasta",
            command=self.escolher_pasta,
            font=("Arial", 15, "bold"),
            fg_color="#a3e635",
            hover_color="#65a30d",
            height=40,
            width=220
        ).pack(pady=5)

        # Botão organizar
        ctk.CTkButton(
            self.root,
            text="Organizar automaticamente (Downloads)",
            command=self.iniciar_organizacao,
            font=("Arial", 18, "bold"),
            fg_color="#2563eb",
            hover_color="#18e733",
            height=45,
            width=400
        ).pack(pady=10)

        # Botão relatório visual
        ctk.CTkButton(
            self.root,
            text="Relatório Visual",
            command=self.mostrar_grafico,
            font=("Arial", 15, "bold"),
            fg_color="#fbbf24",
            hover_color="#f59e42",
            height=40,
            width=220
        ).pack(pady=5)

        # Botão ajuda
        ctk.CTkButton(
            self.root,
            text="Ajuda",
            command=self.mostrar_ajuda,
            font=("Arial", 15, "bold"),
            fg_color="#38bdf8",
            hover_color="#0ea5e9",
            height=40,
            width=220
        ).pack(pady=5)

        # Botão limpar cache
        ctk.CTkButton(
            self.root,
            text="Limpar Cache",
            command=self.limpar_cache,
            font=("Arial", 15, "bold"),
            fg_color="#f472b6",
            hover_color="#be185d",
            height=40,
            width=220
        ).pack(pady=5)

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

        # Botão mostrar/ocultar log
        ctk.CTkButton(
            self.root,
            text="Ver Log",
            command=self.toggle_log,
            font=("Arial", 15, "bold"),
            fg_color="#22d3ee",
            hover_color="#0ea5e9",
            height=40,
            width=220
        ).pack(pady=5)

        # Status label
        self.status_label = ctk.CTkLabel(self.root, textvariable=self.status_var, font=("Arial", 16, "italic"), text_color="#a3e635")
        self.status_label.pack(pady=10)

        # Frame do log (inicialmente oculto)
        self.log_frame = ctk.CTkFrame(self.root)
        ctk.CTkLabel(self.log_frame, text="Log de Ações:", font=("Arial", 16, "bold"), text_color="#fbbf24").pack(anchor="w", pady=5)
        self.log_text = tk.Text(self.log_frame, height=15, state="disabled", font=("Consolas", 11), bg="#18181b", fg="#fbbf24")
        self.log_text.pack(fill="both", expand=True)
        ctk.CTkButton(self.log_frame, text="Limpar log", command=self.limpar_log, width=120, fg_color="#ef4444", hover_color="#b91c1c").pack(pady=5)

    def toggle_log(self):
        if self.log_visible:
            self.log_frame.pack_forget()
            self.log_visible = False
        else:
            self.log_frame.pack(pady=10, padx=10, fill="both", expand=True)
            self.log_visible = True

    def limpar_cache(self):
        self.log("Limpando cache do sistema...")
        pastas_cache = [
            os.path.expandvars(r"%USERPROFILE%\\AppData\\Local\\Microsoft\\Windows\\INetCache"),
            os.path.expandvars(r"%USERPROFILE%\\AppData\\Local\\Temp\\Cache"),
        ]
        removidos = 0
        for pasta in pastas_cache:
            if os.path.exists(pasta):
                for arquivo in os.listdir(pasta):
                    caminho = os.path.join(pasta, arquivo)
                    try:
                        if os.path.isfile(caminho):
                            os.remove(caminho)
                            removidos += 1
                        elif os.path.isdir(caminho):
                            shutil.rmtree(caminho)
                            removidos += 1
                    except Exception as e:
                        self.log(f"Erro ao deletar {caminho}: {e}")
        if removidos == 0:
            self.log("Nenhum arquivo de cache removido.")
        else:
            self.log(f"Cache limpo: {removidos} arquivos/pastas removidos.")

    def log(self, texto):
        self.status_var.set(texto)
        if self.log_visible:
            self.log_text.config(state="normal")
            self.log_text.insert(tk.END, texto + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state="disabled")
        self.root.update_idletasks()
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(texto + "\n")
        except Exception:
            pass

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
