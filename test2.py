"""
Sistema de Reuniões - Display TFT Touch com Interface de Áudio
Resolução fixa: 320x240 pixels
Interface otimizada para telas touch pequenas com IA conversacional
"""

import customtkinter as ctk
from tkinter import messagebox, Canvas
from datetime import datetime, timedelta
import threading
import time
import os
import math
import random
import numpy as np

class SistemaTFT:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        
        self.cores = {
            "primaria": "#1E88E5",
            "secundaria": "#424242",
            "sucesso": "#43A047",
            "perigo": "#E53935",
            "alerta": "#FB8C00",
            "fundo": "#121212",
            "superficie": "#1E1E1E",
            "texto": "#E0E0E0",
            "texto_secundario": "#9E9E9E",
            "borda": "#2C2C2C",
            "audio_ativo": "#00E676",
            "audio_processando": "#2196F3",
            "audio_inativo": "#616161",
            "glow": "#00BCD4",
            "accent": "#FF4081"
        }
        
        self.janela = ctk.CTk()
        self.janela.overrideredirect(True)
        self.janela.geometry("320x240")
        self.janela.resizable(False, False)
        self.janela.configure(fg_color=self.cores["fundo"])
        
        self.usuario_logado = None
        self.frame_atual = None
        self.gravando = False
        self.timer_ativo = False
        self.contexto_reuniao = None
        
        self.audio_ativo = False
        self.audio_estado = "idle"
        self.animacao_ativa = False
        
        self.centralizar_janela()
        
        self.container_principal = ctk.CTkFrame(self.janela, fg_color=self.cores["fundo"])
        self.container_principal.pack(fill="both", expand=True)
        
        self.mostrar_login()
    
    def centralizar_janela(self):
        self.janela.update_idletasks()
        largura = 320
        altura = 240
        x = (self.janela.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.janela.winfo_screenheight() // 2) - (altura // 2)
        self.janela.geometry(f"{largura}x{altura}+{x}+{y}")
    
    def executar(self):
        self.janela.mainloop()
    
    def transicao_rapida(self, novo_frame_func):
        if self.frame_atual:
            self.frame_atual.destroy()
        novo_frame_func()
    
    # ==================== ASSISTENTE IA ====================
    def mostrar_assistente(self):
        self.transicao_rapida(self._criar_assistente)
    
    def _criar_assistente(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal, fg_color=self.cores["fundo"])
        self.frame_atual.pack(fill="both", expand=True)
        
        self.criar_cabecalho_voltar("🤖 Assistente IA")
        
        self.text_chat = ctk.CTkTextbox(
            self.frame_atual,
            height=120,
            font=ctk.CTkFont(size=11),
            fg_color=self.cores["superficie"]
        )
        self.text_chat.pack(fill="both", expand=True, padx=5, pady=5)
        
        msg_inicial = "🤖 Olá! Como posso ajudá-lo?\n\n"
        if hasattr(self, 'contexto_reuniao') and self.contexto_reuniao:
            msg_inicial += f"📄 Analisando: {self.contexto_reuniao}\n\n"
            msg_inicial += "Posso criar resumo, listar ações ou insights.\n\n"
            self.contexto_reuniao = None
            
        self.text_chat.insert("end", msg_inicial)
        self.text_chat.configure(state="disabled")
        
        frame_entrada = ctk.CTkFrame(self.frame_atual, height=32, fg_color=self.cores["superficie"])
        frame_entrada.pack(fill="x", padx=5, pady=(0, 5))
        frame_entrada.pack_propagate(False)
        
        self.btn_audio = ctk.CTkButton(
            frame_entrada,
            text="🎤",
            width=32,
            height=24,
            font=ctk.CTkFont(size=14),
            fg_color=self.cores["secundaria"],
            hover_color=self.cores["primaria"],
            command=self.abrir_interface_audio
        )
        self.btn_audio.pack(side="left", padx=4)
        
        self.entry_chat = ctk.CTkEntry(
            frame_entrada,
            placeholder_text="Digite ou use o microfone...",
            font=ctk.CTkFont(size=10),
            fg_color=self.cores["fundo"],
            border_color=self.cores["primaria"],
            height=24
        )
        self.entry_chat.pack(side="left", fill="x", expand=True, padx=4, pady=4)
        
        ctk.CTkButton(
            frame_entrada,
            text="➤",
            width=32,
            height=24,
            font=ctk.CTkFont(size=12),
            fg_color=self.cores["primaria"],
            command=self.enviar_mensagem
        ).pack(side="right", padx=4)
        
        self.entry_chat.bind("<Return>", lambda e: self.enviar_mensagem())
        self.entry_chat.focus()
    
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
    
    # ==================== INTERFACE DE ÁUDIO COM PARTÍCULAS AZUIS ====================
    def abrir_interface_audio(self):
        """Abre interface de áudio em tela cheia com animação imediata"""
        # Criar nova tela completa para a animação
        self.frame_audio_full = ctk.CTkFrame(
            self.container_principal,
            fg_color=self.cores["fundo"]
        )
        self.frame_audio_full.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Canvas para partículas em tela cheia
        self.canvas_particulas = Canvas(
            self.frame_audio_full,
            width=320,
            height=240,
            bg=self.cores["fundo"],
            highlightthickness=0
        )
        self.canvas_particulas.pack(fill="both", expand=True)
        
        # Área de controle central
        control_frame = ctk.CTkFrame(
            self.frame_audio_full,
            fg_color="transparent"
        )
        control_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Indicador visual circular (pode arrastar)
        self.indicador = ctk.CTkFrame(
            control_frame,
            width=60,
            height=60,
            corner_radius=30,
            fg_color=self.cores["secundaria"]
        )
        self.indicador.pack()
        
        # Ícone central
        self.label_icone = ctk.CTkLabel(
            self.indicador,
            text="🎤",
            font=ctk.CTkFont(size=24)
        )
        self.label_icone.place(relx=0.5, rely=0.5, anchor="center")
        
        # Instrução
        self.label_instrucao = ctk.CTkLabel(
            control_frame,
            text="Deslize para cima para falar",
            font=ctk.CTkFont(size=11),
            text_color=self.cores["texto_secundario"]
        )
        self.label_instrucao.pack(pady=(5, 0))
        
        # Detectar gestos
        self.indicador.bind("<B1-Motion>", self.detectar_deslize)
        self.indicador.bind("<ButtonRelease-1>", self.finalizar_deslize)
        
        # Botão X minimalista no canto
        self.btn_fechar = ctk.CTkButton(
            self.frame_audio_full,
            text="✕",
            width=40,
            height=40,
            font=ctk.CTkFont(size=18),
            fg_color="transparent",
            text_color=self.cores["texto_secundario"],
            hover_color=self.cores["superficie"],
            corner_radius=20,
            border_width=1,
            border_color=self.cores["borda"],
            command=self.fechar_audio
        )
        self.btn_fechar.place(x=270, y=10)
        
        # Estado
        self.audio_estado = "idle"
        self.animacao_ativa = True
        self.particulas = []
        self.posicao_inicial_y = None
        
        # Iniciar animação
        self.animar_particulas()

    def animar_particulas(self):
        """Animação de partículas flutuantes"""
        if not self.animacao_ativa:
            return
        
        self.canvas_particulas.delete("all")
        
        # Centro da tela
        centro_x = 160
        centro_y = 120
        
        # Adicionar novas partículas
        if self.audio_estado == "recording" and random.random() > 0.7:
            self.particulas.append({
                'x': random.randint(50, 270),
                'y': 200,
                'vy': -random.uniform(1, 3),
                'size': random.uniform(2, 5),
                'life': 1.0
            })
        
        elif self.audio_estado == "processing" and random.random() > 0.5:
            # Partículas circulares ao redor do centro
            angulo = random.uniform(0, 2 * math.pi)
            raio = 40
            self.particulas.append({
                'x': centro_x + math.cos(angulo) * raio,
                'y': centro_y + math.sin(angulo) * raio,
                'vx': -math.cos(angulo) * 0.5,
                'vy': -math.sin(angulo) * 0.5,
                'size': 3,
                'life': 1.0
            })
        
        # Atualizar e desenhar partículas
        particulas_vivas = []
        for p in self.particulas:
            # Movimento
            p['x'] += p.get('vx', 0)
            p['y'] += p.get('vy', 0)
            p['life'] -= 0.02
            
            if p['life'] > 0:
                # Cor baseada no estado
                if self.audio_estado == "recording":
                    cor = self.cores["audio_ativo"]
                elif self.audio_estado == "processing":
                    cor = self.cores["audio_processando"]
                else:
                    cor = self.cores["audio_inativo"]
                
                # Aplicar transparência baseada na vida
                cor_alpha = self._ajustar_cor_alpha(cor, p['life'] * 0.6)
                
                # Desenhar partícula
                size = p['size'] * p['life']
                self.canvas_particulas.create_oval(
                    p['x'] - size, p['y'] - size,
                    p['x'] + size, p['y'] + size,
                    fill=cor_alpha, outline=""
                )
                
                particulas_vivas.append(p)
        
        self.particulas = particulas_vivas
        
        # Efeito glow no centro durante estados ativos
        if self.audio_estado in ["recording", "processing"]:
            for i in range(3):
                raio = 30 - i * 8
                alpha = 0.1 * (1 - i * 0.3)
                cor = self.cores["glow"] if self.audio_estado == "recording" else self.cores["audio_processando"]
                cor_glow = self._ajustar_cor_alpha(cor, alpha)
                
                self.canvas_particulas.create_oval(
                    centro_x - raio, centro_y - raio,
                    centro_x + raio, centro_y + raio,
                    fill=cor_glow, outline=""
                )
        
        self.janela.after(30, self.animar_particulas)

    def _ajustar_cor_alpha(self, cor_hex, alpha):
        """Simula transparência"""
        r = int(cor_hex[1:3], 16)
        g = int(cor_hex[3:5], 16)
        b = int(cor_hex[5:7], 16)
        
        fundo_r = int(self.cores["fundo"][1:3], 16)
        fundo_g = int(self.cores["fundo"][3:5], 16)
        fundo_b = int(self.cores["fundo"][5:7], 16)
        
        r = int(r * alpha + fundo_r * (1 - alpha))
        g = int(g * alpha + fundo_g * (1 - alpha))
        b = int(b * alpha + fundo_b * (1 - alpha))
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def detectar_deslize(self, event):
        """Detecta movimento de deslize"""
        if self.posicao_inicial_y is None:
            self.posicao_inicial_y = event.y_root
        
        # Calcular distância deslizada
        distancia = self.posicao_inicial_y - event.y_root
        
        # Se deslizou para cima o suficiente
        if distancia > 30 and self.audio_estado == "idle":
            self.iniciar_gravacao_deslize()

    def iniciar_gravacao_deslize(self):
        """Inicia gravação por deslize"""
        self.audio_estado = "recording"
        self.indicador.configure(fg_color=self.cores["audio_ativo"])
        self.label_icone.configure(text="🔴")
        self.label_instrucao.configure(text="Gravando... Solte para parar")

    def finalizar_deslize(self, event):
        """Finaliza gesto de deslize"""
        self.posicao_inicial_y = None
        
        if self.audio_estado == "recording":
            # Processar áudio
            self.audio_estado = "processing"
            self.indicador.configure(fg_color=self.cores["audio_processando"])
            self.label_icone.configure(text="⏳")
            self.label_instrucao.configure(text="Processando...")
            
            # Simular processamento
            self.janela.after(1500, self.processar_e_fechar)

    def processar_e_fechar(self):
        """Processa e retorna resultado"""
        # Adicionar resposta
        self.text_chat.configure(state="normal")
        self.text_chat.insert("end", "🎤 [Comando de voz processado]\n")
        self.text_chat.insert("end", "🤖 Aqui está o resumo que você solicitou...\n\n")
        self.text_chat.configure(state="disabled")
        self.text_chat.see("end")
        
        # Fechar interface
        self.fechar_audio()

    def fechar_audio(self):
        """Fecha interface de áudio e volta para assistente"""
        self.animacao_ativa = False
        
        # Destruir frame de áudio
        self.frame_audio_full.destroy()
    
    # ==================== OUTROS MÉTODOS NECESSÁRIOS ====================
    def mostrar_login(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal, fg_color=self.cores["fundo"])
        self.frame_atual.pack(fill="both", expand=True)
        
        frame_central = ctk.CTkFrame(self.frame_atual, width=280, height=170, fg_color=self.cores["superficie"])
        frame_central.place(relx=0.5, rely=0.5, anchor="center")
        frame_central.pack_propagate(False)
        
        ctk.CTkFrame(frame_central, height=10, fg_color=self.cores["superficie"]).pack()
        
        ctk.CTkLabel(
            frame_central, 
            text="Usuário", 
            font=ctk.CTkFont(size=12),
            text_color=self.cores["texto_secundario"]
        ).pack(pady=(0, 2))
        
        self.entry_usuario = ctk.CTkEntry(
            frame_central, 
            width=220, 
            height=30,
            fg_color=self.cores["fundo"],
            border_color=self.cores["primaria"],
            placeholder_text="Digite seu nome"
        )
        self.entry_usuario.pack(pady=(0, 8))
        
        ctk.CTkLabel(
            frame_central, 
            text="Senha", 
            font=ctk.CTkFont(size=12),
            text_color=self.cores["texto_secundario"]
        ).pack(pady=(0, 2))
        
        self.entry_senha = ctk.CTkEntry(
            frame_central, 
            width=220, 
            height=30,
            fg_color=self.cores["fundo"],
            border_color=self.cores["primaria"],
            placeholder_text="Digite sua senha",
            show="●"
        )
        self.entry_senha.pack(pady=(0, 12))
        
        self.btn_login = ctk.CTkButton(
            frame_central,
            text="ENTRAR",
            width=220,
            height=40,
            command=self.fazer_login,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.cores["primaria"],
            hover_color="#1976D2"
        )
        self.btn_login.pack()
        
        self.entry_senha.bind("<Return>", lambda e: self.fazer_login())
        self.entry_usuario.focus()
    
    def fazer_login(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()
        
        if not usuario:
            return
        
        self.usuario_logado = {"usuario": usuario, "area": "geral"}
        self.transicao_rapida(self.mostrar_menu_principal)
    
    def mostrar_menu_principal(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal, fg_color=self.cores["fundo"])
        self.frame_atual.pack(fill="both", expand=True)
        
        frame_header = ctk.CTkFrame(self.frame_atual, height=35, fg_color=self.cores["superficie"])
        frame_header.pack(fill="x")
        frame_header.pack_propagate(False)
        
        ctk.CTkLabel(
            frame_header,
            text="Menu Principal",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores["texto"]
        ).pack(side="left", padx=15, pady=8)
        
        ctk.CTkButton(
            frame_header,
            text="◄",
            width=28,
            height=25,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=self.cores["texto_secundario"],
            hover_color=self.cores["secundaria"],
            command=self.fazer_logout
        ).pack(side="right", padx=8, pady=5)
        
        ctk.CTkLabel(
            frame_header,
            text=self.usuario_logado['usuario'],
            font=ctk.CTkFont(size=10),
            text_color=self.cores["texto_secundario"]
        ).pack(side="right", padx=5)
        
        frame_botoes = ctk.CTkFrame(self.frame_atual, fg_color=self.cores["fundo"])
        frame_botoes.pack(fill="both", expand=True)
        
        botoes = [
            ("HISTÓRICO\nREUNIÕES", self.mostrar_historico, self.cores["secundaria"]),
            ("NOVA\nGRAVAÇÃO", self.mostrar_pre_gravacao, self.cores["sucesso"]),
            ("ASSISTENTE\nINTELIGENTE", self.mostrar_assistente, self.cores["primaria"])
        ]
        
        for i, (texto, comando, cor) in enumerate(botoes):
            btn = ctk.CTkButton(
                frame_botoes,
                text=texto,
                width=320,
                height=68,
                command=comando,
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color=cor,
                hover_color=cor,
                corner_radius=0,
                text_color=self.cores["texto"]
            )
            btn.pack(fill="both", expand=True)
            
            if i < len(botoes) - 1:
                linha = ctk.CTkFrame(frame_botoes, height=1, fg_color=self.cores["fundo"])
                linha.pack(fill="x")
    
    def mostrar_historico(self):
        messagebox.showinfo("Histórico", "Funcionalidade em desenvolvimento")
    
    def mostrar_pre_gravacao(self):
        messagebox.showinfo("Nova Gravação", "Funcionalidade em desenvolvimento")
    
    def criar_cabecalho_voltar(self, titulo):
        frame_header = ctk.CTkFrame(self.frame_atual, height=35, fg_color=self.cores["superficie"])
        frame_header.pack(fill="x")
        frame_header.pack_propagate(False)
        
        ctk.CTkButton(
            frame_header,
            text="◄",
            width=30,
            height=25,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=self.cores["texto"],
            hover_color=self.cores["secundaria"],
            command=lambda: self.transicao_rapida(self.mostrar_menu_principal)
        ).pack(side="left", padx=5, pady=5)
        
        ctk.CTkLabel(
            frame_header,
            text=titulo,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.cores["texto"]
        ).pack(side="left", padx=10, pady=8)
    
    def fazer_logout(self):
        self.usuario_logado = None
        self.transicao_rapida(self.mostrar_login)

# ==================== INICIALIZAÇÃO ====================
if __name__ == "__main__":
    print("🚀 Sistema TFT - Versão com Partículas Azuis")
    print("📱 Interface: 320x240 pixels")
    print("🔵 Animação de processamento com partículas azuis")
    print("⚠️ Use ESC para fechar\n")
    
    app = SistemaTFT()
    app.janela.bind("<Escape>", lambda e: app.janela.destroy())
    app.executar()