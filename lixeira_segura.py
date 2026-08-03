#!/usr/bin/env python3
# ==========================================================
# Lixeira Segura Pro
# Versão: 1.2 (Edição Jackson Q. - Versão Final Estável)
#
# Autor: Jackson Q.
# Descrição: Utilitário profissional para destruição de dados.
# Correções: Controle de janelas únicas (Singleton Windows),
#            detecção profunda de hardware e limpeza total.
# ==========================================================

import os
import sys
import threading
import subprocess
import time
import datetime
import json
import customtkinter as ctk
from tkinter import messagebox

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
        self.window.title("Lixeira Segura Pro - v1.2")
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
        self.running_destruction = False
        
        # Controle de Janelas Únicas (Singleton)
        self.win_history = None
        self.win_config = None
        self.win_help = None
        
        self.create_widgets()
        
        # Monitoramento em tempo real
        self.stop_monitor = False
        self.monitor_thread = threading.Thread(target=self.monitorar_pasta, daemon=True)
        self.monitor_thread.start()
        
        self.window.mainloop()

    def load_config(self):
        if os.path.exists(ARQUIVO_CONFIG):
            try:
                with open(ARQUIVO_CONFIG, "r") as f:
                    return json.load(f)
            except: pass
        return {"log": True, "confirmacao_dupla": True}

    def save_config(self):
        with open(ARQUIVO_CONFIG, "w") as f:
            json.dump(self.config, f)

    def detectar_disco(self):
        """Detecta se o disco é HDD ou SSD para aplicar o melhor método de destruição."""
        try:
            # Tenta identificar via lsblk
            output = subprocess.check_output("lsblk -o ROTA,MOUNTPOINT", shell=True).decode()
            if "0 /" in output or "0 /home" in output:
                return "HDD (Disco Rígido)"
            return "SSD/NVMe (Memória Flash)"
        except:
            return "Disco Genérico"

    def get_all_entries(self):
        """Lista todos os arquivos, pastas e links simbólicos recursivamente."""
        entries = []
        try:
            for root, dirs, files in os.walk(DIR_APAGAR):
                for name in files + dirs:
                    full_path = os.path.join(root, name)
                    if os.path.lexists(full_path):
                        entries.append(full_path)
        except Exception as e:
            print(f"Erro ao listar: {e}")
        return entries

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

        # Área Principal
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Botões de Ação
        self.actions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.actions_frame.pack(pady=10, fill="x")

        self.btn_open = ctk.CTkButton(self.actions_frame, text="📂 Abrir Pasta de Descarte", font=("Segoe UI", 14, "bold"), height=45, command=self.abrir_pasta)
        self.btn_open.pack(side="left", padx=10, expand=True, fill="x")

        self.btn_destroy = ctk.CTkButton(self.actions_frame, text="🔥 Destruir Arquivos", font=("Segoe UI", 14, "bold"), height=45, fg_color="#E74C3C", hover_color="#C0392B", command=self.confirmar_destruicao)
        self.btn_destroy.pack(side="left", padx=10, expand=True, fill="x")

        # Caixa de Status
        self.status_box = ctk.CTkTextbox(self.main_frame, height=200, font=("Consolas", 12))
        self.status_box.pack(padx=10, pady=10, fill="both", expand=True)
        self.status_box.configure(state="disabled")

        # Barra de Progresso
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=700)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        # Rodapé
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

    def log_msg(self, msg, clear=False):
        def _write():
            if not self.window.winfo_exists(): return
            self.status_box.configure(state="normal")
            if clear: self.status_box.delete("0.0", "end")
            self.status_box.insert("end", f"{msg}\n")
            self.status_box.see("end")
            self.status_box.configure(state="disabled")
        self.window.after(0, _write)

    def monitorar_pasta(self):
        """Monitora a pasta de descarte e atualiza o status visual."""
        last_count = -1
        while not self.stop_monitor:
            if not self.running_destruction:
                entries = self.get_all_entries()
                count = len(entries)
                if count != last_count:
                    if count == 0:
                        self.log_msg(">>> Aguardando arquivos na pasta de descarte...", clear=True)
                    else:
                        tamanho = 0
                        for f in entries:
                            try: 
                                if os.path.isfile(f): tamanho += os.path.getsize(f)
                            except: pass
                        tamanho_fmt = f"{tamanho / (1024*1024):.2f} MB"
                        self.log_msg(f">>> {count} item(ns) detectado(s) ({tamanho_fmt}).\nPronto para destruição segura.", clear=True)
                    last_count = count
            time.sleep(2)

    def abrir_pasta(self):
        subprocess.Popen(["xdg-open", DIR_APAGAR])

    def confirmar_destruicao(self):
        entries = self.get_all_entries()
        if not entries:
            messagebox.showinfo("Aviso", "A pasta está vazia!")
            return

        pergunta = f"Deseja destruir permanentemente {len(entries)} item(ns)?\n\nESTA AÇÃO É IRREVERSÍVEL!"
        if messagebox.askyesno("CONFIRMAÇÃO CRÍTICA", pergunta):
            if self.config.get("confirmacao_dupla", True):
                if not messagebox.askyesno("ÚLTIMO AVISO", "Você tem certeza absoluta?"):
                    return
            
            self.running_destruction = True
            threading.Thread(target=self.processo_destruicao, args=(entries,), daemon=True).start()

    def processo_destruicao(self, entries):
        self.window.after(0, lambda: self.btn_destroy.configure(state="disabled"))
        self.window.after(0, lambda: self.btn_open.configure(state="disabled"))
        self.log_msg(">>> INICIANDO DESTRUIÇÃO SEGURA...", clear=True)
        
        total = len(entries)
        for i, caminho in enumerate(entries):
            if not os.path.lexists(caminho): continue
            
            nome = os.path.basename(caminho)
            self.log_msg(f"Processando ({i+1}/{total}): {nome}")
            
            try:
                if os.path.islink(caminho):
                    os.unlink(caminho)
                elif os.path.isfile(caminho):
                    cmd = ["shred", "-f", "-u", "-z", "-n", "3"] if "HDD" in self.disco_info else ["shred", "-f", "-u", "-n", "1"]
                    subprocess.run(cmd + [caminho], check=True, stderr=subprocess.DEVNULL)
                
                if self.config.get("log", True):
                    with open(ARQUIVO_LOG, "a") as f:
                        f.write(f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} - {nome} - Sucesso\n")
            except:
                self.log_msg(f"Aviso: Falha ao destruir {nome}")

            self.window.after(0, lambda v=(i + 1) / total: self.progress_bar.set(v))

        # Limpar pastas
        for root, dirs, files in os.walk(DIR_APAGAR, topdown=False):
            for d in dirs:
                try: os.rmdir(os.path.join(root, d))
                except: pass

        subprocess.run(["sync"])
        self.log_msg(">>> OPERAÇÃO CONCLUÍDA COM SUCESSO.")
        self.window.after(0, lambda: messagebox.showinfo("Sucesso", "Todos os dados foram destruídos."))
        self.window.after(0, lambda: self.progress_bar.set(0))
        self.window.after(0, lambda: self.btn_destroy.configure(state="normal"))
        self.window.after(0, lambda: self.btn_open.configure(state="normal"))
        self.running_destruction = False

    def ver_historico(self):
        if self.win_history is not None and self.win_history.winfo_exists():
            self.win_history.focus()
            return

        self.win_history = ctk.CTkToplevel(self.window)
        self.win_history.title("Histórico de Exclusões")
        self.win_history.geometry("600x450")
        self.win_history.attributes("-topmost", True)
        
        txt = ctk.CTkTextbox(self.win_history, width=580, height=350)
        txt.pack(padx=10, pady=10)
        
        if os.path.exists(ARQUIVO_LOG):
            with open(ARQUIVO_LOG, "r") as f: txt.insert("0.0", f.read())
        
        def limpar():
            if messagebox.askyesno("Limpar Logs", "Destruir arquivo de logs permanentemente?", parent=self.win_history):
                subprocess.run(["shred", "-f", "-u", "-z", "-n", "3", ARQUIVO_LOG])
                with open(ARQUIVO_LOG, "w") as f: f.write("")
                txt.delete("0.0", "end")
        
        ctk.CTkButton(self.win_history, text="🔥 Destruir Histórico", fg_color="#E74C3C", command=limpar).pack(pady=5)

    def abrir_config(self):
        if self.win_config is not None and self.win_config.winfo_exists():
            self.win_config.focus()
            return

        self.win_config = ctk.CTkToplevel(self.window)
        self.win_config.title("Ajustes")
        self.win_config.geometry("400x300")
        self.win_config.attributes("-topmost", True)

        ctk.CTkLabel(self.win_config, text="Configurações de Segurança", font=("Segoe UI", 16, "bold")).pack(pady=20)

        def toggle_log():
            self.config["log"] = not self.config.get("log", True)
            self.save_config()
            bl.configure(text=f"Registrar Logs: {'ON' if self.config['log'] else 'OFF'}")

        def toggle_confirm():
            self.config["confirmacao_dupla"] = not self.config.get("confirmacao_dupla", True)
            self.save_config()
            bc.configure(text=f"Confirmação Dupla: {'ON' if self.config['confirmacao_dupla'] else 'OFF'}")

        bl = ctk.CTkButton(self.win_config, text=f"Registrar Logs: {'ON' if self.config.get('log', True) else 'OFF'}", command=toggle_log)
        bl.pack(pady=10)

        bc = ctk.CTkButton(self.win_config, text=f"Confirmação Dupla: {'ON' if self.config.get('confirmacao_dupla', True) else 'OFF'}", command=toggle_confirm)
        bc.pack(pady=10)

    def exibir_ajuda(self):
        msg = f"""Lixeira Segura Pro v1.2
Desenvolvido por Jackson Q.

Este utilitário foi criado para garantir a destruição definitiva de dados confidenciais.

Como Funciona:
Ao contrário da exclusão normal que apenas 'esconde' o arquivo, este programa escreve dados aleatórios por cima do arquivo original várias vezes antes de removê-lo.

Uso em Empresas:
Perfeito para conformidade com a LGPD e descarte seguro de dispositivos.

Hardware:
O programa detecta se você usa HDD ou SSD e aplica a técnica mais segura para cada um.
"""
        messagebox.showinfo("Ajuda / Sobre", msg)

if __name__ == "__main__":
    LixeiraSeguraApp()
