"""
Sistema AURALIS - Versão para Display TFT Touch
Otimizado para resolução 320x240 pixels
Interface minimalista para telas pequenas
"""

import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime, timedelta
import threading
import time
import os

class SistemaAuralisTFT:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Janela principal otimizada para TFT
        self.janela = ctk.CTk()
        self.janela.title("AURALIS")
        self.janela.geometry("320x240")
        self.janela.resizable(False, False)
        
        # Estado do sistema
        self.usuario_logado = None
        self.frame_atual = None
        self.gravando = False
        self.timer_ativo = False
        
        # Centralizar janela
        self.centralizar_janela()
        
        # Container principal sem margens
        self.container_principal = ctk.CTkFrame(self.janela)
        self.container_principal.pack(fill="both", expand=True)
        
        # Iniciar com tela de login
        self.mostrar_login()
    
    def centralizar_janela(self):
        self.janela.update_idletasks()
        largura = 320
        altura = 240
        x = (self.janela.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.janela.winfo_screenheight() // 2) - (altura // 2)
        self.janela.geometry(f"{largura}x{altura}+{x}+{y}")
    
    def transicao_rapida(self, novo_frame_func):
        """Transição rápida entre frames"""
        if self.frame_atual:
            self.frame_atual.destroy()
        novo_frame_func()
    
    # ==================== TELA DE LOGIN ====================
    def mostrar_login(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        # Título compacto
        ctk.CTkLabel(
            self.frame_atual,
            text="AURALIS",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(15, 10))
        
        # Frame de login compacto
        frame_login = ctk.CTkFrame(self.frame_atual)
        frame_login.pack(fill="x", padx=20, pady=10)
        
        # Usuário
        ctk.CTkLabel(frame_login, text="Usuário:", font=ctk.CTkFont(size=11)).pack(pady=(10, 2))
        self.entry_usuario = ctk.CTkEntry(frame_login, width=200, height=28, placeholder_text="Nome")
        self.entry_usuario.pack(pady=(0, 8))
        
        # Senha
        ctk.CTkLabel(frame_login, text="Senha:", font=ctk.CTkFont(size=11)).pack(pady=(0, 2))
        self.entry_senha = ctk.CTkEntry(frame_login, width=200, height=28, placeholder_text="****", show="●")
        self.entry_senha.pack(pady=(0, 10))
        
        # Botão entrar
        self.btn_login = ctk.CTkButton(
            frame_login,
            text="ENTRAR",
            width=200,
            height=35,
            command=self.fazer_login,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_login.pack(pady=(5, 10))
        
        self.entry_senha.bind("<Return>", lambda e: self.fazer_login())
        self.entry_usuario.focus()
    
    def fazer_login(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()
        
        if not usuario:
            self.mostrar_popup("Digite o usuário!")
            return
        
        self.usuario_logado = {"usuario": usuario, "area": "geral"}
        self.transicao_rapida(self.mostrar_menu_principal)
    
    # ==================== MENU PRINCIPAL ====================
    def mostrar_menu_principal(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        # Cabeçalho minimalista
        frame_header = ctk.CTkFrame(self.frame_atual, height=35)
        frame_header.pack(fill="x")
        frame_header.pack_propagate(False)
        
        ctk.CTkLabel(
            frame_header,
            text="AURALIS",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=10, pady=8)
        
        # Botão sair pequeno
        ctk.CTkButton(
            frame_header,
            text="↩",
            width=30,
            height=25,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color="gray",
            hover_color=("gray20", "gray20"),
            command=self.fazer_logout
        ).pack(side="right", padx=5, pady=5)
        
        # Usuário
        ctk.CTkLabel(
            frame_header,
            text=f"{self.usuario_logado['usuario']}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(side="right", padx=5)
        
        # Grid de botões 2x2
        frame_botoes = ctk.CTkFrame(self.frame_atual)
        frame_botoes.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar grid
        frame_botoes.grid_rowconfigure(0, weight=1)
        frame_botoes.grid_rowconfigure(1, weight=1)
        frame_botoes.grid_columnconfigure(0, weight=1)
        frame_botoes.grid_columnconfigure(1, weight=1)
        
        # Botões
        botoes = [
            ("📋\nHistórico", self.mostrar_historico, 0, 0),
            ("🎙️\nGravar", self.mostrar_pre_gravacao, 0, 1),
            ("🤖\nAURALIS", self.mostrar_auralis, 1, 0),
            ("ℹ️\nSobre", self.mostrar_sobre, 1, 1)
        ]
        
        for texto, comando, row, col in botoes:
            btn = ctk.CTkButton(
                frame_botoes,
                text=texto,
                width=130,
                height=70,
                command=comando,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
    
    # ==================== HISTÓRICO COMPACTO ====================
    def mostrar_historico(self):
        self.transicao_rapida(self._criar_historico)
    
    def _criar_historico(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        # Cabeçalho com voltar
        self.criar_cabecalho_voltar("📋 Histórico")
        
        # Lista simplificada
        frame_lista = ctk.CTkScrollableFrame(self.frame_atual, height=160)
        frame_lista.pack(fill="both", expand=True, padx=5, pady=5)
        
        reunioes = [
            ("Planejamento", "15/01 14h"),
            ("Daily", "14/01 10h"),
            ("Sprint", "12/01 15h"),
            ("Kickoff", "10/01 09h"),
        ]
        
        for titulo, data in reunioes:
            frame_item = ctk.CTkFrame(frame_lista, height=35)
            frame_item.pack(fill="x", pady=2)
            frame_item.pack_propagate(False)
            
            ctk.CTkLabel(
                frame_item,
                text=f"{titulo} - {data}",
                font=ctk.CTkFont(size=11)
            ).pack(side="left", padx=5, pady=5)
            
            ctk.CTkButton(
                frame_item,
                text="Ver",
                width=40,
                height=25,
                font=ctk.CTkFont(size=10),
                command=lambda t=titulo: self.mostrar_detalhes_compacto(t)
            ).pack(side="right", padx=5, pady=5)
    
    # ==================== PRÉ-GRAVAÇÃO COMPACTA ====================
    def mostrar_pre_gravacao(self):
        self.transicao_rapida(self._criar_pre_gravacao)
    
    def _criar_pre_gravacao(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        self.criar_cabecalho_voltar("🎙️ Nova Gravação")
        
        # Formulário compacto
        frame_form = ctk.CTkFrame(self.frame_atual)
        frame_form.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame_form, text="Título:", font=ctk.CTkFont(size=11)).pack(pady=(10, 2))
        self.entry_titulo = ctk.CTkEntry(frame_form, width=250, height=28, placeholder_text="Nome da reunião")
        self.entry_titulo.pack(pady=(0, 10))
        
        ctk.CTkLabel(frame_form, text="Notas (opcional):", font=ctk.CTkFont(size=11)).pack(pady=(5, 2))
        self.text_obs = ctk.CTkTextbox(frame_form, width=250, height=40, font=ctk.CTkFont(size=10))
        self.text_obs.pack(pady=(0, 15))
        
        # Botões lado a lado
        frame_btns = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_btns.pack()
        
        ctk.CTkButton(
            frame_btns,
            text="Cancelar",
            width=110,
            height=35,
            fg_color="gray",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self.transicao_rapida(self.mostrar_menu_principal)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_btns,
            text="Iniciar",
            width=110,
            height=35,
            fg_color="green",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.iniciar_gravacao
        ).pack(side="left", padx=5)
    
    def iniciar_gravacao(self):
        titulo = self.entry_titulo.get().strip()
        if not titulo:
            self.mostrar_popup("Digite o título!")
            return
        
        self.dados_reuniao = {
            'titulo': titulo,
            'observacoes': self.text_obs.get("1.0", "end-1c")
        }
        
        self.transicao_rapida(self._criar_gravacao)
    
    # ==================== GRAVAÇÃO COMPACTA ====================
    def _criar_gravacao(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        # Título
        ctk.CTkLabel(
            self.frame_atual,
            text=self.dados_reuniao['titulo'][:20] + "...",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5))
        
        # Status
        self.label_rec = ctk.CTkLabel(
            self.frame_atual,
            text="🔴 REC",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="red"
        )
        self.label_rec.pack(pady=10)
        
        # Timer grande
        self.label_timer = ctk.CTkLabel(
            self.frame_atual,
            text="00:00",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.label_timer.pack(pady=5)
        
        # Controles
        frame_controles = ctk.CTkFrame(self.frame_atual)
        frame_controles.pack(pady=15)
        
        self.btn_pausar = ctk.CTkButton(
            frame_controles,
            text="⏸️",
            width=60,
            height=40,
            font=ctk.CTkFont(size=18),
            fg_color="orange",
            command=self.pausar_gravacao
        )
        self.btn_pausar.pack(side="left", padx=3)
        
        ctk.CTkButton(
            frame_controles,
            text="⏹️",
            width=60,
            height=40,
            font=ctk.CTkFont(size=18),
            fg_color="green",
            command=self.parar_gravacao
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            frame_controles,
            text="❌",
            width=60,
            height=40,
            font=ctk.CTkFont(size=18),
            fg_color="red",
            command=self.cancelar_gravacao
        ).pack(side="left", padx=3)
        
        # Iniciar
        self.gravando = True
        self.pausado = False
        self.tempo_inicial = datetime.now()
        self.tempo_pausado = timedelta()
        self.timer_ativo = True
        self.atualizar_timer()
    
    def atualizar_timer(self):
        if self.timer_ativo and self.gravando and not self.pausado:
            tempo_total = datetime.now() - self.tempo_inicial - self.tempo_pausado
            minutos = int(tempo_total.total_seconds() // 60)
            segundos = int(tempo_total.total_seconds() % 60)
            
            self.label_timer.configure(text=f"{minutos:02d}:{segundos:02d}")
            self.janela.after(100, self.atualizar_timer)
    
    def pausar_gravacao(self):
        if not self.pausado:
            self.pausado = True
            self.momento_pausa = datetime.now()
            self.btn_pausar.configure(text="▶️", fg_color="green")
            self.label_rec.configure(text="⏸️ PAUSADO", text_color="orange")
        else:
            self.tempo_pausado += datetime.now() - self.momento_pausa
            self.pausado = False
            self.btn_pausar.configure(text="⏸️", fg_color="orange")
            self.label_rec.configure(text="🔴 REC", text_color="red")
            self.atualizar_timer()
    
    def parar_gravacao(self):
        self.gravando = False
        self.timer_ativo = False
        self.mostrar_popup("Gravação salva!")
        self.transicao_rapida(self.mostrar_menu_principal)
    
    def cancelar_gravacao(self):
        self.gravando = False
        self.timer_ativo = False
        self.transicao_rapida(self.mostrar_menu_principal)
    
    # ==================== AURALIS COMPACTO ====================
    def mostrar_auralis(self):
        self.transicao_rapida(self._criar_auralis)
    
    def _criar_auralis(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        self.criar_cabecalho_voltar("🤖 AURALIS IA")
        
        # Área de chat maximizada
        self.text_chat = ctk.CTkTextbox(
            self.frame_atual,
            height=130,
            font=ctk.CTkFont(size=10)
        )
        self.text_chat.pack(fill="both", expand=True, padx=5, pady=(5, 0))
        
        self.text_chat.insert("end", "🤖 Olá! Como posso ajudar?\n\n")
        self.text_chat.configure(state="disabled")
        
        # Entrada compacta
        frame_entrada = ctk.CTkFrame(self.frame_atual, height=35)
        frame_entrada.pack(fill="x", padx=5, pady=5)
        frame_entrada.pack_propagate(False)
        
        self.entry_chat = ctk.CTkEntry(
            frame_entrada,
            placeholder_text="Digite aqui...",
            font=ctk.CTkFont(size=10)
        )
        self.entry_chat.pack(side="left", fill="x", expand=True, padx=(5, 0), pady=5)
        
        ctk.CTkButton(
            frame_entrada,
            text="→",
            width=35,
            height=25,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.enviar_mensagem
        ).pack(side="right", padx=5)
        
        self.entry_chat.bind("<Return>", lambda e: self.enviar_mensagem())
    
    def enviar_mensagem(self):
        msg = self.entry_chat.get().strip()
        if not msg:
            return
        
        self.text_chat.configure(state="normal")
        self.text_chat.insert("end", f"👤 {msg}\n")
        self.text_chat.insert("end", "🤖 Processando...\n\n")
        self.text_chat.configure(state="disabled")
        self.text_chat.see("end")
        
        self.entry_chat.delete(0, "end")
    
    # ==================== SOBRE ====================
    def mostrar_sobre(self):
        self.transicao_rapida(self._criar_sobre)
    
    def _criar_sobre(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        self.criar_cabecalho_voltar("ℹ️ Sobre")
        
        # Informações
        frame_info = ctk.CTkFrame(self.frame_atual)
        frame_info.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_text = """AURALIS v1.0
        
Sistema de Gestão
de Reuniões com IA

Versão TFT Touch
320x240 pixels

© 2025"""
        
        ctk.CTkLabel(
            frame_info,
            text=info_text,
            font=ctk.CTkFont(size=11),
            justify="center"
        ).pack(expand=True)
    
    # ==================== UTILIDADES ====================
    def criar_cabecalho_voltar(self, titulo):
        """Cria cabeçalho padrão com botão voltar"""
        frame_header = ctk.CTkFrame(self.frame_atual, height=35)
        frame_header.pack(fill="x")
        frame_header.pack_propagate(False)
        
        ctk.CTkButton(
            frame_header,
            text="←",
            width=35,
            height=25,
            font=ctk.CTkFont(size=16),
            command=lambda: self.transicao_rapida(self.mostrar_menu_principal)
        ).pack(side="left", padx=5, pady=5)
        
        ctk.CTkLabel(
            frame_header,
            text=titulo,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10, pady=8)
    
    def mostrar_detalhes_compacto(self, titulo):
        """Mostra detalhes em popup compacto"""
        self.mostrar_popup(f"Detalhes de:\n{titulo}\n\nTranscrição disponível\nno sistema completo")
    
    def mostrar_popup(self, mensagem):
        """Popup customizado para TFT"""
        popup = ctk.CTkToplevel(self.janela)
        popup.title("Info")
        popup.geometry("250x120")
        popup.transient(self.janela)
        popup.grab_set()
        
        # Centralizar popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 125
        y = (popup.winfo_screenheight() // 2) - 60
        popup.geometry(f"250x120+{x}+{y}")
        
        ctk.CTkLabel(
            popup,
            text=mensagem,
            font=ctk.CTkFont(size=12),
            wraplength=220
        ).pack(expand=True, pady=10)
        
        ctk.CTkButton(
            popup,
            text="OK",
            width=80,
            height=30,
            command=popup.destroy
        ).pack(pady=(0, 10))
    
    def fazer_logout(self):
        self.usuario_logado = None
        self.transicao_rapida(self.mostrar_login)
    
    def executar(self):
        self.janela.mainloop()

# ==================== INICIALIZAÇÃO ====================
if __name__ == "__main__":
    print("🚀 Iniciando AURALIS TFT...")
    print("📱 Otimizado para display 320x240 touch")
    
    app = SistemaAuralisTFT()
    app.executar()