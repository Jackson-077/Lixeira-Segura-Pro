#!/usr/bin/env python3
# ==========================================================
# Lixeira Segura Pro
# Versão: 1.0 
#
# Autor: Jackson Q.
# Descrição: Utilitário profissional para destruição de dados.
# Interface moderna utilizando CustomTkinter.
# ==========================================================

import os
import sys
import threading
import subprocess
import shutil
import time
import datetime
import json
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

# -----------------------------
# Configurações de Tema e Estilo
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Variáveis de Ambiente ---
DIR_BASE = os.path.join(os.path.expanduser("~"), "Lixeira_Segura")
DIR_APAGAR = os.path.join(DIR_BASE, "apagar_aqui")
DIR_LOGS = os.path.join(DIR_BASE, "logs")
ARQUIVO_CONFIG = os.path.join(DIR_BASE, "config.json")
ARQUIVO_LOG = os.path.join(DIR_LOGS, "exclusoes.log")

class LixeiraSeguraApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Lixeira Segura Pro")
        self.window.geometry("800x650")
        self.window.resizable(True, True)

        # Garantir estrutura de pastas
        os.makedirs(DIR_APAGAR, exist_ok=True)
        os.makedirs(DIR_LOGS, exist_ok=True)
        if not os.path.exists(ARQUIVO_LOG):
            with open(ARQUIVO_LOG, "w") as f: f.write("")

        # Estado e Configurações
        self.config = self.load_config()
        self.disco_info = self.detectar_disco()
        
        self.create_widgets()
        self.window.mainloop()

    def load_config(self):
        if os.path.exists(ARQUIVO_CONFIG):
            with open(ARQUIVO_CONFIG, "r") as f:
                return json.load(f)
        return {"log": True, "confirmacao_dupla": True}

    def save_config(self):
        with open(ARQUIVO_CONFIG, "w") as f:
            json.dump(self.config, f)

    def detectar_disco(self):
        try:
            # Simplificado para Linux
            output = subprocess.check_output("lsblk -o ROTA,MOUNTPOINT", shell=True).decode()
            if "0 /" in output or "0 /home" in output:
                return "HDD (Disco Rígido)"
            return "SSD/NVMe (Memória Flash)"
        except:
            return "Disco Genérico"

    def create_widgets(self):
        # Título Principal
        self.title_label = ctk.CTkLabel(self.window, text="Lixeira Segura Pro", font=("Segoe UI", 32, "bold"), text_color="#3B8ED0")
        self.title_label.pack(pady=(20, 5))
        
        self.author_label = ctk.CTkLabel(self.window, text="Desenvolvido por Jackson Q.", font=("Segoe UI", 12, "italic"), text_color="gray")
        self.author_label.pack(pady=(0, 20))

        # Painel de Informações do Sistema
        self.info_frame = ctk.CTkFrame(self.window, corner_radius=10)
        self.info_frame.pack(padx=20, pady=10, fill="x")
        
        self.sys_info = ctk.CTkLabel(self.info_frame, text=f"SISTEMA: Linux | HARDWARE: {self.disco_info}", font=("Segoe UI", 13, "bold"))
        self.sys_info.pack(pady=10)

        # Área Principal (Scrollable)
        self.main_frame = ctk.CTkScrollableFrame(self.window, width=750, height=350)
        self.main_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Botões de Ação Rápida
        self.actions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.actions_frame.pack(pady=10, fill="x")

        self.btn_open = ctk.CTkButton(self.actions_frame, text="📂 Abrir Pasta de Descarte", font=("Segoe UI", 14, "bold"), 
                                     height=45, command=self.abrir_pasta)
        self.btn_open.pack(side="left", padx=10, expand=True, fill="x")

        self.btn_destroy = ctk.CTkButton(self.actions_frame, text="🔥 Destruir Arquivos", font=("Segoe UI", 14, "bold"), 
                                        height=45, fg_color="#E74C3C", hover_color="#C0392B", command=self.confirmar_destruicao)
        self.btn_destroy.pack(side="left", padx=10, expand=True, fill="x")

        # Status e Progresso
        self.status_box = ctk.CTkTextbox(self.main_frame, height=150, font=("Consolas", 12))
        self.status_box.pack(padx=10, pady=10, fill="x")
        self.status_box.insert("0.0", ">>> Aguardando arquivos na pasta de descarte...\n")
        self.status_box.configure(state="disabled")

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=700)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        # Rodapé com Configurações e Ajuda
        self.footer_frame = ctk.CTkFrame(self.window, height=60, corner_radius=0, fg_color="transparent")
        self.footer_frame.pack(side="bottom", fill="x", padx=20, pady=10)

        self.btn_history = ctk.CTkButton(self.footer_frame, text="📜 Histórico", width=120, command=self.ver_historico)
        self.btn_history.pack(side="left", padx=5)

        self.btn_config = ctk.CTkButton(self.footer_frame, text="⚙️ Ajustes", width=120, command=self.abrir_config)
        self.btn_config.pack(side="left", padx=5)

        self.btn_help = ctk.CTkButton(self.footer_frame, text="❓ Ajuda", width=120, command=self.exibir_ajuda)
        self.btn_help.pack(side="left", padx=5)

        self.btn_exit = ctk.CTkButton(self.footer_frame, text="Sair", width=100, fg_color="#555", hover_color="#333", command=self.window.quit)
        self.btn_exit.pack(side="right", padx=5)

    # --- Lógica ---

    def log_msg(self, msg):
        self.status_box.configure(state="normal")
        self.status_box.insert("end", f"{msg}\n")
        self.status_box.see("end")
        self.status_box.configure(state="disabled")

    def abrir_pasta(self):
        subprocess.Popen(["xdg-open", DIR_APAGAR])
        self.log_msg(">>> Pasta de descarte aberta.")

    def confirmar_destruicao(self):

        arquivos = []

        # Procurar arquivos dentro de todas as pastas
        for raiz, pastas, arquivos_nome in os.walk(DIR_APAGAR):
            for arquivo in arquivos_nome:
                caminho = os.path.join(raiz, arquivo)
                arquivos.append(caminho)

        if not arquivos:
            messagebox.showinfo(
                "Aviso",
                "A pasta está vazia! Coloque arquivos ou pastas dentro de 'apagar_aqui' primeiro."
            )
            return

        total_tamanho = sum(os.path.getsize(f) for f in arquivos)
        tamanho_formatado = f"{total_tamanho / (1024*1024):.2f} MB"

        lista_nomes = "\n".join(
            [os.path.basename(f) for f in arquivos[:10]]
        )

        if len(arquivos) > 10:
            lista_nomes += "\n... e outros."

        pergunta = (
            f"Deseja destruir permanentemente {len(arquivos)} arquivos "
            f"({tamanho_formatado})?\n\n"
            f"{lista_nomes}\n\n"
            "ESTA AÇÃO NÃO PODE SER DESFEITA!"
        )

        if messagebox.askyesno("CONFIRMAÇÃO CRÍTICA", pergunta):

            if self.config["confirmacao_dupla"]:

                if not messagebox.askyesno(
                    "ÚLTIMO AVISO",
                    "Você tem certeza absoluta?\n\n"
                    "Os dados serão sobrescritos fisicamente."
                ):
                    return

            threading.Thread(
                target=self.processo_destruicao,
                args=(arquivos,),
                daemon=True
            ).start()



    def processo_destruicao(self, arquivos):

            self.btn_destroy.configure(state="disabled")
            self.btn_open.configure(state="disabled")

            self.log_msg(">>> Iniciando destruição segura...")

            total = len(arquivos)

            for i, caminho in enumerate(arquivos):

                nome = os.path.basename(caminho)

                self.log_msg(f"Destruindo: {nome}")

                try:

                    # HDD
                    if "HDD" in self.disco_info:

                        subprocess.run(
                            [
                                "shred",
                                "-f",
                                "-u",
                                "-z",
                                "-n",
                                "3",
                                caminho
                            ],
                            check=True
                        )

                    # SSD / NVMe
                    else:

                        subprocess.run(
                            [
                                "shred",
                                "-f",
                                "-u",
                                "-n",
                                "1",
                                caminho
                            ],
                            check=True
                        )


                    if self.config["log"]:

                        with open(ARQUIVO_LOG, "a") as f:

                            f.write(
                                f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
                                f" - {nome} - Destruído\n"
                            )


                except Exception as e:

                    self.log_msg(
                        f"ERRO em {nome}: {e}"
                    )


                self.progress_bar.set(
                    (i + 1) / total
                )

                self.window.update_idletasks()



            self.log_msg(
                ">>> Removendo pastas vazias..."
            )


            # Remove somente pastas vazias dentro de apagar_aqui
            for raiz, pastas, arquivos in os.walk(
                DIR_APAGAR,
                topdown=False
            ):

                for pasta in pastas:

                    caminho_pasta = os.path.join(
                        raiz,
                        pasta
                    )

                    try:

                        os.rmdir(caminho_pasta)

                        self.log_msg(
                            f"Pasta removida: {pasta}"
                        )

                    except OSError:

                        pass



            self.log_msg(
                ">>> Sincronizando hardware..."
            )

            subprocess.run(
                ["sync"]
            )


            self.log_msg(
                ">>> OPERAÇÃO CONCLUÍDA COM SUCESSO."
            )


            messagebox.showinfo(
                "Sucesso",
                "Todos os arquivos foram destruídos permanentemente."
            )


            self.progress_bar.set(0)

            self.btn_destroy.configure(
                state="normal"
            )

            self.btn_open.configure(
                state="normal"
            )

    def ver_historico(self):
        win = ctk.CTkToplevel(self.window)
        win.title("Histórico de Exclusões")
        win.geometry("600x400")
        
        txt = ctk.CTkTextbox(win, width=580, height=330)
        txt.pack(padx=10, pady=10)
        
        if os.path.exists(ARQUIVO_LOG):
            with open(ARQUIVO_LOG, "r") as f:
                txt.insert("0.0", f.read())
        
        def limpar_log_seguro():
            if messagebox.askyesno("Limpar Logs", "Deseja destruir permanentemente o arquivo de logs?"):
                subprocess.run(["shred", "-f", "-u", "-z", "-n", "3", ARQUIVO_LOG])
                with open(ARQUIVO_LOG, "w") as f: f.write("")
                txt.delete("0.0", "end")
                messagebox.showinfo("Sucesso", "Histórico destruído.")

        ctk.CTkButton(win, text="🔥 Destruir Histórico", fg_color="#E74C3C", command=limpar_log_seguro).pack(pady=5)

    def abrir_config(self):
        win = ctk.CTkToplevel(self.window)
        win.title("Configurações")
        win.geometry("400x300")

        ctk.CTkLabel(win, text="Ajustes de Segurança", font=("Segoe UI", 16, "bold")).pack(pady=20)

        def toggle_log():
            self.config["log"] = not self.config["log"]
            self.save_config()
            btn_l.configure(text=f"Registrar Logs: {'LIGADO' if self.config['log'] else 'DESLIGADO'}")

        def toggle_confirm():
            self.config["confirmacao_dupla"] = not self.config["confirmacao_dupla"]
            self.save_config()
            btn_c.configure(text=f"Confirmação Dupla: {'LIGADO' if self.config['confirmacao_dupla'] else 'DESLIGADO'}")

        btn_l = ctk.CTkButton(win, text=f"Registrar Logs: {'LIGADO' if self.config['log'] else 'DESLIGADO'}", command=toggle_log)
        btn_l.pack(pady=10)

        btn_c = ctk.CTkButton(win, text=f"Confirmação Dupla: {'LIGADO' if self.config['confirmacao_dupla'] else 'DESLIGADO'}", command=toggle_confirm)
        btn_c.pack(pady=10)

    def exibir_ajuda(self):
        msg = f"""Lixeira Segura Pro 

Este programa garante que arquivos sensíveis sejam destruídos fisicamente do disco, tornando a recuperação impossível.

Como usar:
1. Clique em 'Abrir Pasta de Descarte'.
2. Mova os arquivos que deseja apagar para lá.
3. Clique em 'Destruir Arquivos'.

Diferença para a lixeira comum:
A lixeira comum apenas remove o 'nome' do arquivo, mas os dados continuam no disco. Este programa 'esmaga' os dados escrevendo por cima deles várias vezes."""
        messagebox.showinfo("Ajuda / Sobre", msg)

if __name__ == "__main__":
    LixeiraSeguraApp()
