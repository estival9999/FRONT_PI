"""
Sistema de Reuniões - Display TFT Touch com Interface de Áudio
Resolução fixa: 320x240 pixels
Interface otimizada para telas touch pequenas com IA conversacional

ESTRUTURA:
- Barra de título customizada: 20px (arrastar janela + fechar)
- Área útil: 320x220 pixels
- Sem decorações de janela do sistema operacional
- Navegação otimizada para toque
- Interface de áudio inovadora com feedback visual

CORREÇÕES APLICADAS:
1. Login: Campos movidos para cima, botão ENTRAR maior (40px)
2. Histórico: Itens com 55px altura, layout fixo sem sobreposição
3. Pré-gravação: Sem scroll, todo conteúdo visível, formulário compacto
4. Detalhes: Info mínima (30px), transcrição expandida
5. Gravação: Confirmações ao cancelar/finalizar
6. NOVO: Interface de áudio com visualização interativa
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
        # Configurar tema escuro com nova paleta
        ctk.set_appearance_mode("dark")
        
        # Paleta de cores personalizada - tons de azul e cinza
        self.cores = {
            "primaria": "#1E88E5",          # Azul principal
            "secundaria": "#424242",        # Cinza escuro
            "sucesso": "#43A047",           # Verde
            "perigo": "#E53935",            # Vermelho
            "alerta": "#FB8C00",            # Laranja
            "fundo": "#121212",             # Preto suave
            "superficie": "#1E1E1E",        # Cinza muito escuro
            "texto": "#E0E0E0",             # Cinza claro
            "texto_secundario": "#9E9E9E",  # Cinza médio
            "borda": "#2C2C2C",             # Cinza para bordas
            "audio_ativo": "#00E676",       # Verde neon para áudio
            "audio_processando": "#2196F3", # Azul processando
            "audio_inativo": "#616161",     # Cinza inativo
            "glow": "#00BCD4",              # Ciano para efeitos de brilho
            "accent": "#FF4081"             # Rosa accent para detalhes
        }
        
        # Janela principal - sempre modo TFT (sem decorações)
        self.janela = ctk.CTk()
        self.janela.overrideredirect(True)  # Remove barra de título
        self.janela.geometry("320x240")
        self.janela.resizable(False, False)
        self.janela.configure(fg_color=self.cores["fundo"])
        
        # Estado do sistema
        self.usuario_logado = None
        self.frame_atual = None
        self.gravando = False
        self.timer_ativo = False
        self.contexto_reuniao = None
        
        # Estado da interface de áudio
        self.audio_ativo = False
        self.audio_estado = "idle"  # idle, listening, processing, speaking
        self.animacao_ativa = False
        
        # Centralizar janela
        self.centralizar_janela()
        
        # Container principal sem padding
        self.container_principal = ctk.CTkFrame(self.janela, fg_color=self.cores["fundo"])
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
    
    def executar(self):
        self.janela.mainloop()
    
    def transicao_rapida(self, novo_frame_func):
        """Transição rápida entre frames"""
        if self.frame_atual:
            self.frame_atual.destroy()
        novo_frame_func()
    
    # ==================== TELA DE LOGIN ====================
    def mostrar_login(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal, fg_color=self.cores["fundo"])
        self.frame_atual.pack(fill="both", expand=True)
        
        # Container central
        frame_central = ctk.CTkFrame(self.frame_atual, width=280, height=170, fg_color=self.cores["superficie"])
        frame_central.place(relx=0.5, rely=0.5, anchor="center")
        frame_central.pack_propagate(False)
        
        # Espaçamento superior menor - movendo tudo para cima
        ctk.CTkFrame(frame_central, height=10, fg_color=self.cores["superficie"]).pack()
        
        # Campos de login
        # Usuário
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
        
        # Senha
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
        
        # Botão entrar maior
        self.btn_login = ctk.CTkButton(
            frame_central,
            text="ENTRAR",
            width=220,
            height=40,  # Maior
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
    
    # ==================== MENU PRINCIPAL ====================
    def mostrar_menu_principal(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal, fg_color=self.cores["fundo"])
        self.frame_atual.pack(fill="both", expand=True)
        
        # Cabeçalho clean
        frame_header = ctk.CTkFrame(self.frame_atual, height=35, fg_color=self.cores["superficie"])
        frame_header.pack(fill="x")
        frame_header.pack_propagate(False)
        
        ctk.CTkLabel(
            frame_header,
            text="Menu Principal",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores["texto"]
        ).pack(side="left", padx=15, pady=8)
        
        # Logout discreto
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
        
        # Usuário
        ctk.CTkLabel(
            frame_header,
            text=self.usuario_logado['usuario'],
            font=ctk.CTkFont(size=10),
            text_color=self.cores["texto_secundario"]
        ).pack(side="right", padx=5)
        
        # Container para botões preencherem todo espaço disponível
        frame_botoes = ctk.CTkFrame(self.frame_atual, fg_color=self.cores["fundo"])
        frame_botoes.pack(fill="both", expand=True)
        
        # Botões minimalistas com altura igual dividindo o espaço
        # Altura total disponível: 240 - 35 (header) = 205px
        # 3 botões = ~68px cada
        
        botoes = [
            ("HISTÓRICO\nREUNIÕES", self.mostrar_historico, self.cores["secundaria"]),
            ("NOVA\nGRAVAÇÃO", self.mostrar_pre_gravacao, self.cores["sucesso"]),
            ("ASSISTENTE\nINTELIGENTE", self.mostrar_assistente, self.cores["primaria"])
        ]
        
        for i, (texto, comando, cor) in enumerate(botoes):
            btn = ctk.CTkButton(
                frame_botoes,
                text=texto,
                width=320,  # Largura total da janela
                height=68,  # Altura fixa para preencher espaço
                command=comando,
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color=cor,
                hover_color=cor,
                corner_radius=0,  # Sem bordas arredondadas
                text_color=self.cores["texto"]
            )
            btn.pack(fill="both", expand=True)
            
            # Linha divisória sutil entre botões (exceto após o último)
            if i < len(botoes) - 1:
                linha = ctk.CTkFrame(frame_botoes, height=1, fg_color=self.cores["fundo"])
                linha.pack(fill="x")
    
    # ==================== HISTÓRICO ====================
    def mostrar_historico(self):
        self.transicao_rapida(self._criar_historico)
    
    def _criar_historico(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal, fg_color=self.cores["fundo"])
        self.frame_atual.pack(fill="both", expand=True)
        
        self.criar_cabecalho_voltar("📋 Histórico de Reuniões")
        
        # Lista com separadores
        frame_lista = ctk.CTkScrollableFrame(
            self.frame_atual, 
            height=145,  # Ajustado para comportar itens maiores
            fg_color=self.cores["fundo"]
        )
        frame_lista.pack(fill="both", expand=True, padx=0, pady=0)
        
        reunioes = [
            ("Planejamento Q1", "15/01 14:00", "45 min"),
            ("Daily Standup", "14/01 10:00", "15 min"),
            ("Revisão Sprint", "12/01 15:30", "1h 20min"),
            ("Kickoff Projeto", "10/01 09:00", "2h"),
        ]
        
        for i, (titulo, data, duracao) in enumerate(reunioes):
            # Item da reunião com mais altura
            frame_item = ctk.CTkFrame(
                frame_lista, 
                height=55,  # Aumentado ainda mais
                fg_color=self.cores["superficie"]
            )
            frame_item.pack(fill="x", padx=10, pady=(5 if i == 0 else 0, 0))
            frame_item.pack_propagate(False)
            
            # Info da reunião com layout vertical melhor
            frame_info = ctk.CTkFrame(frame_item, fg_color="transparent")
            frame_info.pack(side="left", fill="both", expand=True, padx=(12, 0))
            
            # Título com espaçamento correto
            ctk.CTkLabel(
                frame_info,
                text=titulo,
                font=ctk.CTkFont(size=11, weight="bold"),  
                text_color=self.cores["texto"],
                anchor="w"
            ).place(x=0, y=8)
            
            # Data e duração com posição garantida
            ctk.CTkLabel(
                frame_info,
                text=f"{data} • {duracao}",
                font=ctk.CTkFont(size=9),  # Reduzido de 10
                text_color=self.cores["texto_secundario"],
                anchor="w"
            ).place(x=0, y=28)  # Ajustado
            
            # Botão ver centralizado verticalmente
            btn_ver = ctk.CTkButton(
                frame_item,
                text="Ver",
                width=50,
                height=30,
                font=ctk.CTkFont(size=11),
                fg_color=self.cores["primaria"],
                command=lambda t=titulo, d=data, dur=duracao: self.mostrar_detalhes_reuniao(t, d, dur)
            )
            btn_ver.place(relx=0.85, rely=0.5, anchor="center")  # Posicionamento preciso
            
            # Linha separadora
            if i < len(reunioes) - 1:
                separator = ctk.CTkFrame(
                    frame_lista, 
                    height=1, 
                    fg_color=self.cores["secundaria"]
                )
                separator.pack(fill="x", padx=20, pady=0)
    
    def mostrar_detalhes_reuniao(self, titulo, data, duracao):
        """Mostra detalhes completos da reunião"""
        self.transicao_rapida(lambda: self._criar_detalhes_reuniao(titulo, data, duracao))
    
    def _criar_detalhes_reuniao(self, titulo, data, duracao):
        self.frame_atual = ctk.CTkFrame(self.container_principal, fg_color=self.cores["fundo"])
        self.frame_atual.pack(fill="both", expand=True)
        
        # Cabeçalho com botão voltar
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
            command=lambda: self.transicao_rapida(self._criar_historico)
        ).pack(side="left", padx=5, pady=5)
        
        ctk.CTkLabel(
            frame_header,
            text="📄 Detalhes",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.cores["texto"]
        ).pack(side="left", padx=10, pady=8)
        
        # Botão analisar com IA no topo
        ctk.CTkButton(
            self.frame_atual,
            text="🤖 Analisar com IA",
            width=300,
            height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.cores["primaria"],
            hover_color="#1976D2",
            command=lambda: self.analisar_com_ia(titulo)
        ).pack(padx=10, pady=(5, 5))
        
        # Container de informações - MENOR e SUTIL
        frame_info = ctk.CTkFrame(self.frame_atual, height=30, fg_color=self.cores["superficie"])
        frame_info.pack(fill="x", padx=10, pady=(0, 5))
        frame_info.pack_propagate(False)
        
        # Info em uma linha só - truncar se necessário
        titulo_curto = titulo[:15] + "..." if len(titulo) > 15 else titulo
        info_text = f"{titulo_curto} • {data} • {duracao}"
        ctk.CTkLabel(
            frame_info,
            text=info_text,
            font=ctk.CTkFont(size=9),
            text_color=self.cores["texto_secundario"]
        ).pack(expand=True)
        
        # Transcrição - EXPANDIDA
        ctk.CTkLabel(
            self.frame_atual,
            text="Transcrição:",
            font=ctk.CTkFont(size=11),
            text_color=self.cores["texto"]
        ).pack(anchor="w", padx=10, pady=(0, 2))
        
        # Textbox maior com scroll
        text_transcricao = ctk.CTkTextbox(
            self.frame_atual,
            height=98,  # Ajustado (+3px da redução do info)
            font=ctk.CTkFont(size=10),
            fg_color=self.cores["superficie"],
            wrap="word"
        )
        text_transcricao.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Transcrição com mais conteúdo
        transcricao = f"""Reunião: {titulo}
Data: {data} - Duração: {duracao}

PARTICIPANTES:
• {self.usuario_logado['usuario']} (Organizador)
• João Silva (Desenvolvimento)
• Maria Santos (Design)
• Pedro Costa (Gestão)

PAUTA:
1. Revisão do Sprint anterior
2. Planejamento do próximo ciclo
3. Discussão de impedimentos
4. Definição de prioridades

PONTOS DISCUTIDOS:
• Objetivos do trimestre foram revisados e aprovados
• Alocação de recursos para o novo projeto
• Prazos definidos conforme cronograma
• Métricas de desempenho analisadas
• Feedback da equipe sobre processos

DECISÕES TOMADAS:
• Aprovar novo orçamento de R$ 50.000
• Contratar 2 desenvolvedores até março
• Implementar nova metodologia ágil
• Revisar processos semanalmente

AÇÕES PENDENTES:
• João: Preparar relatório técnico até sexta-feira
• Maria: Agendar reunião com cliente para próxima semana
• Pedro: Revisar documentação do projeto
• Todos: Atualizar status no sistema

PRÓXIMOS PASSOS:
• Reunião de acompanhamento em 15 dias
• Revisão mensal de métricas
• Apresentação para diretoria no fim do mês

OBSERVAÇÕES FINAIS:
A equipe demonstrou comprometimento com as metas estabelecidas. 
Todos os pontos foram discutidos e as dúvidas esclarecidas.
O projeto segue conforme o planejado."""
        
        text_transcricao.insert("1.0", transcricao)
        text_transcricao.configure(state="disabled")
    
    def analisar_com_ia(self, titulo):
        """Abre Assistente com contexto da reunião"""
        self.contexto_reuniao = titulo
        self.transicao_rapida(self._criar_assistente)
    
    # ==================== PRÉ-GRAVAÇÃO ====================
    def mostrar_pre_gravacao(self):
        self.transicao_rapida(self._criar_pre_gravacao)
    
    def _criar_pre_gravacao(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal, fg_color=self.cores["fundo"])
        self.frame_atual.pack(fill="both", expand=True)
        
        self.criar_cabecalho_voltar("🎙️ Nova Gravação")
        
        # Botões no topo - bem próximos ao cabeçalho
        frame_btns = ctk.CTkFrame(self.frame_atual, height=36, fg_color=self.cores["fundo"])
        frame_btns.pack(fill="x", padx=10, pady=(2, 2))
        frame_btns.pack_propagate(False)
        
        # Container interno para centralizar botões
        inner_btns = ctk.CTkFrame(frame_btns, fg_color=self.cores["fundo"])
        inner_btns.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkButton(
            inner_btns,
            text="Cancelar",
            width=140,
            height=30,
            fg_color=self.cores["secundaria"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.transicao_rapida(self.mostrar_menu_principal)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            inner_btns,
            text="Iniciar",
            width=140,
            height=30,
            fg_color=self.cores["sucesso"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.iniciar_gravacao
        ).pack(side="left", padx=5)
        
        # Container do formulário SEM SCROLL
        frame_form = ctk.CTkFrame(self.frame_atual, fg_color=self.cores["superficie"])
        frame_form.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        
        # Título da reunião
        ctk.CTkLabel(
            frame_form, 
            text="Título da Reunião", 
            font=ctk.CTkFont(size=11),
            text_color=self.cores["texto_secundario"]
        ).pack(pady=(8, 2))
        
        self.entry_titulo = ctk.CTkEntry(
            frame_form, 
            width=270,  # Aumentado
            height=30,
            fg_color=self.cores["fundo"],
            border_color=self.cores["primaria"],
            placeholder_text="Ex: Reunião de Planejamento"
        )
        self.entry_titulo.pack(pady=(0, 8))
        
        # Observações - otimizado para caber
        ctk.CTkLabel(
            frame_form, 
            text="Observações (opcional)", 
            font=ctk.CTkFont(size=11),
            text_color=self.cores["texto_secundario"]
        ).pack(pady=(0, 2))
        
        self.text_obs = ctk.CTkTextbox(
            frame_form, 
            width=270,  # Aumentado
            height=40,  # Altura otimizada
            font=ctk.CTkFont(size=10),
            fg_color=self.cores["fundo"]
        )
        self.text_obs.pack(pady=(0, 8))
        
        # Focar no campo título
        self.entry_titulo.focus()
    
    def iniciar_gravacao(self):
        titulo = self.entry_titulo.get().strip()
        if not titulo:
            # Feedback visual no campo
            self.entry_titulo.configure(
                border_color=self.cores["perigo"], 
                border_width=2,
                placeholder_text="⚠️ Campo obrigatório"
            )
            self.entry_titulo.focus()
            self.janela.after(2000, lambda: self.entry_titulo.configure(
                border_color=self.cores["primaria"], 
                border_width=2,
                placeholder_text="Ex: Reunião de Planejamento"
            ))
            return
        
        self.dados_reuniao = {
            'titulo': titulo,
            'observacoes': self.text_obs.get("1.0", "end-1c")
        }
        
        self.transicao_rapida(self._criar_gravacao)
    
    # ==================== GRAVAÇÃO ====================
    def _criar_gravacao(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal, fg_color=self.cores["fundo"])
        self.frame_atual.pack(fill="both", expand=True)
        
        # Container central
        frame_central = ctk.CTkFrame(self.frame_atual, fg_color=self.cores["superficie"])
        frame_central.pack(fill="both", expand=True, padx=10, pady=(5, 8))
        
        # Título
        titulo_curto = self.dados_reuniao['titulo'][:25]
        if len(self.dados_reuniao['titulo']) > 25:
            titulo_curto += "..."
            
        ctk.CTkLabel(
            frame_central,
            text=titulo_curto,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores["texto"]
        ).pack(pady=(15, 10))
        
        # Status
        self.label_rec = ctk.CTkLabel(
            frame_central,
            text="● REC",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.cores["perigo"]
        )
        self.label_rec.pack()
        
        # Timer
        self.label_timer = ctk.CTkLabel(
            frame_central,
            text="00:00",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=self.cores["texto"]
        )
        self.label_timer.pack(pady=8)
        
        # Controles
        frame_controles = ctk.CTkFrame(frame_central, fg_color="transparent")
        frame_controles.pack(pady=12)
        
        self.btn_pausar = ctk.CTkButton(
            frame_controles,
            text="⏸",
            width=70,
            height=45,
            font=ctk.CTkFont(size=20),
            fg_color=self.cores["alerta"],
            command=self.pausar_gravacao
        )
        self.btn_pausar.pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_controles,
            text="⏹",
            width=70,
            height=45,
            font=ctk.CTkFont(size=20),
            fg_color=self.cores["sucesso"],
            command=self.parar_gravacao
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_controles,
            text="✕",
            width=70,
            height=45,
            font=ctk.CTkFont(size=20),
            fg_color=self.cores["perigo"],
            command=self.cancelar_gravacao
        ).pack(side="left", padx=5)
        
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
            self.btn_pausar.configure(text="▶", fg_color=self.cores["sucesso"])
            self.label_rec.configure(text="⏸ PAUSADO", text_color=self.cores["alerta"])
        else:
            self.tempo_pausado += datetime.now() - self.momento_pausa
            self.pausado = False
            self.btn_pausar.configure(text="⏸", fg_color=self.cores["alerta"])
            self.label_rec.configure(text="● REC", text_color=self.cores["perigo"])
            self.atualizar_timer()
    
    def parar_gravacao(self):
        # Confirmação antes de parar
        resposta = messagebox.askyesno(
            "Finalizar Gravação",
            "Deseja finalizar a gravação?\n\nA reunião será salva e processada.",
            parent=self.janela
        )
        
        if resposta:
            self.gravando = False
            self.timer_ativo = False
            
            # Simular processamento
            messagebox.showinfo(
                "Sucesso", 
                "Gravação finalizada com sucesso!\n\nA transcrição está sendo processada.",
                parent=self.janela
            )
            self.transicao_rapida(self.mostrar_menu_principal)
    
    def cancelar_gravacao(self):
        # Confirmação antes de cancelar
        resposta = messagebox.askyesno(
            "Cancelar Gravação",
            "Tem certeza que deseja cancelar?\n\nTodo o conteúdo gravado será perdido!",
            parent=self.janela
        )
        
        if resposta:
            self.gravando = False
            self.timer_ativo = False
            self.transicao_rapida(self.mostrar_menu_principal)
    
    # ==================== ASSISTENTE IA ====================
    def mostrar_assistente(self):
        # Não limpa contexto se vier do histórico
        self.transicao_rapida(self._criar_assistente)
    
    def _criar_assistente(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal, fg_color=self.cores["fundo"])
        self.frame_atual.pack(fill="both", expand=True)
        
        self.criar_cabecalho_voltar("🤖 Assistente IA")
        
        # Chat maximizado
        self.text_chat = ctk.CTkTextbox(
            self.frame_atual,
            height=120,  # Reduzido para acomodar botão de áudio
            font=ctk.CTkFont(size=11),
            fg_color=self.cores["superficie"]
        )
        self.text_chat.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Mensagem inicial
        msg_inicial = "🤖 Olá! Como posso ajudá-lo?\n\n"
        if hasattr(self, 'contexto_reuniao') and self.contexto_reuniao:
            msg_inicial += f"📄 Analisando: {self.contexto_reuniao}\n\n"
            msg_inicial += "Posso criar resumo, listar ações ou insights.\n\n"
            # Limpar contexto após usar
            self.contexto_reuniao = None
            
        self.text_chat.insert("end", msg_inicial)
        self.text_chat.configure(state="disabled")
        
        # Frame de entrada com botão de áudio
        frame_entrada = ctk.CTkFrame(self.frame_atual, height=32, fg_color=self.cores["superficie"])
        frame_entrada.pack(fill="x", padx=5, pady=(0, 5))
        frame_entrada.pack_propagate(False)
        
        # Botão de áudio
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
    
    # ==================== INTERFACE DE ÁUDIO INOVADORA ====================
    def abrir_interface_audio(self):
        """Abre a interface de áudio inovadora"""
        self.transicao_rapida(self._criar_interface_audio)
    
    def _criar_interface_audio(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal, fg_color=self.cores["fundo"])
        self.frame_atual.pack(fill="both", expand=True)
        
        # Canvas em tela cheia
        self.canvas_audio = Canvas(
            self.frame_atual,
            width=320,
            height=240,
            bg=self.cores["fundo"],
            highlightthickness=0
        )
        self.canvas_audio.pack(fill="both", expand=True)
        
        # Botão X minimalista no canto
        btn_fechar = ctk.CTkButton(
            self.frame_atual,
            text="✕",
            width=35,
            height=35,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            text_color=self.cores["texto_secundario"],
            hover_color=self.cores["superficie"],
            corner_radius=17,
            border_width=1,
            border_color=self.cores["borda"],
            command=lambda: self.fechar_interface_audio()
        )
        btn_fechar.place(x=280, y=5)
        
        # Botão de controle circular no rodapé
        self.btn_audio_control = ctk.CTkButton(
            self.frame_atual,
            text="",
            width=64,
            height=64,
            corner_radius=2,
            fg_color=self.cores["superficie"],
            hover_color=self.cores["secundaria"],
            border_width=2,
            border_color=self.cores["borda"],
            font=ctk.CTkFont(size=30),
            command=self.toggle_audio
        )
        self.btn_audio_control.place(x=117, y=188)
        
        # Ícone do botão
        self.update_button_icon()
        
        # Status minimalista
        self.label_status = ctk.CTkLabel(
            self.frame_atual,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=self.cores["texto_secundario"],
            bg_color=self.cores["fundo"]
        )
        self.label_status.place(x=160, y=160, anchor="center")
        
        # Elementos da interface
        self.criar_elementos_audio()
        
        # Iniciar animação idle
        self.audio_estado = "idle"
        self.animacao_ativa = True
        self.entrada_suave = 0  # Para animação de entrada
        self.animar_interface()
        
        # Atualizar interface inicial
        self.atualizar_interface_audio()
    
    def criar_elementos_audio(self):
        """Cria elementos visuais da interface de áudio"""
        # Centro visual perfeitamente equilibrado
        self.centro_x = 255
        self.centro_y = 150  # Centro perfeito considerando botão
        
        # Raio base maior para preencher tela
        self.raio_base = 100
        self.raio_atual = self.raio_base
        
        # Ondas sonoras
        self.ondas = []
        self.particulas = []
        
        # Variáveis de animação
        self.fase = 0
        self.amplitude = 0
        self.cor_atual = self.cores["audio_inativo"]
    
    def update_button_icon(self):
        """Atualiza ícone do botão conforme estado"""
        icons = {
            "idle": "🎙️",
            "listening": "⏹️",
            "processing": "⏳",
            "speaking": "🔊"
        }
        
        if self.audio_estado in icons:
            self.btn_audio_control.configure(text=icons[self.audio_estado])
    
    def animar_interface(self):
        """Loop principal de animação"""
        if not self.animacao_ativa:
            return
        
        # Limpar canvas (preservando widgets)
        for item in self.canvas_audio.find_all():
            if self.canvas_audio.type(item) != "window":
                self.canvas_audio.delete(item)
        
        # Fundo com gradiente radial muito sutil centralizado
        for i in range(3):
            raio = 160 - i * 50
            alpha = 0.015
            cor = self._ajustar_cor_alpha(self.cores["superficie"], alpha)
            self.canvas_audio.create_oval(
                160 - raio, 100 - raio,  # Centro visual equilibrado
                160 + raio, 100 + raio,
                fill=cor, outline=""
            )
        
        # Atualizar estado visual
        if self.audio_estado == "idle":
            self.animar_idle()
        elif self.audio_estado == "listening":
            self.animar_escutando()
        elif self.audio_estado == "processing":
            self.animar_processando()
        elif self.audio_estado == "speaking":
            self.animar_falando()
        
        # Desenhar anel ao redor do botão quando não idle
        if self.audio_estado != "idle":
            # Anel animado ao redor do botão
            btn_centro_x = 160
            btn_centro_y = 187  # Ajustado para nova posição do botão
            pulsacao = abs(math.sin(self.fase * 3)) * 2
            cor_anel = {
                "listening": self.cores["audio_ativo"],
                "processing": self.cores["audio_processando"],
                "speaking": self.cores["primaria"]
            }.get(self.audio_estado, self.cores["borda"])
            
            # Anel único sutil
            cor_anel_alpha = self._ajustar_cor_alpha(cor_anel, 0.5)
            self.canvas_audio.create_oval(
                btn_centro_x - 34 - pulsacao, btn_centro_y - 34 - pulsacao,
                btn_centro_x + 34 + pulsacao, btn_centro_y + 34 + pulsacao,
                fill="", outline=cor_anel_alpha, width=1
            )
        
        # Continuar animação
        self.janela.after(30, self.animar_interface)  # 33fps para suavidade
    
    def animar_idle(self):
        """Animação moderna do estado idle"""
        # Animação de entrada suave
        if hasattr(self, 'entrada_suave') and self.entrada_suave < 1:
            self.entrada_suave = min(1, self.entrada_suave + 0.05)
            
        # Respiração orgânica
        self.fase += 0.03
        
        # Múltiplas camadas para profundidade - maiores
        for i in range(4):
            pulsacao = math.sin(self.fase + i * 0.5) * 4
            r = (self.raio_base + 5 - (i * 18) + pulsacao) * getattr(self, 'entrada_suave', 1)
            alpha = (0.12 - (i * 0.025)) * getattr(self, 'entrada_suave', 1)
            
            if r > 0:
                cor = self._ajustar_cor_alpha(self.cores["audio_inativo"], alpha)
                self.canvas_audio.create_oval(
                    self.centro_x - r, self.centro_y - r,
                    self.centro_x + r, self.centro_y + r,
                    fill=cor, outline=""
                )
        
        # Anel central
        r_anel = 55 * getattr(self, 'entrada_suave', 1)
        self.canvas_audio.create_oval(
            self.centro_x - r_anel, self.centro_y - r_anel,
            self.centro_x + r_anel, self.centro_y + r_anel,
            fill="", outline=self.cores["audio_inativo"], width=1
        )
    
    def animar_escutando(self):
        """Animação moderna do estado escutando"""
        self.fase += 0.12
        
        # Simular entrada de áudio
        self.amplitude = 35 + math.sin(self.fase * 3) * 25 + random.random() * 10
        
        # Efeito glow de fundo
        for i in range(3):
            r = 140 - i * 35
            alpha = 0.05 + (self.amplitude / 100) * 0.15
            cor = self._ajustar_cor_alpha(self.cores["glow"], alpha)
            self.canvas_audio.create_oval(
                self.centro_x - r, self.centro_y - r,
                self.centro_x + r, self.centro_y + r,
                fill=cor, outline=""
            )
        
        # Visualizador circular moderno
        num_barras = 36
        for i in range(num_barras):
            angulo = (2 * math.pi / num_barras) * i
            
            # Altura baseada em "frequência"
            freq_simulada = math.sin(i * 0.3 + self.fase * 2)
            altura = 25 + self.amplitude * abs(freq_simulada) * 0.9
            
            # Posições da barra
            x1 = self.centro_x + math.cos(angulo) * 50
            y1 = self.centro_y + math.sin(angulo) * 50
            x2 = self.centro_x + math.cos(angulo) * (50 + altura)
            y2 = self.centro_y + math.sin(angulo) * (50 + altura)
            
            # Cor com gradiente
            intensidade = abs(freq_simulada)
            cor = self._ajustar_cor_alpha(self.cores["audio_ativo"], 0.3 + intensidade * 0.7)
            
            self.canvas_audio.create_line(
                x1, y1, x2, y2,
                fill=cor, width=3,
                capstyle="round"
            )
        
        # Círculo central pulsante
        vibração = math.sin(self.fase * 5) * 3
        self.canvas_audio.create_oval(
            self.centro_x - 40 - vibração, 
            self.centro_y - 40 - vibração,
            self.centro_x + 40 + vibração, 
            self.centro_y + 40 + vibração,
            fill=self.cores["fundo"], 
            outline=self.cores["audio_ativo"], 
            width=2
        )
    
    def animar_processando(self):
        """Animação moderna do estado processando"""
        self.fase += 0.08
        
        # Efeito de loading líquido
        for ring in range(3):
            num_pontos = 12
            raio_ring = 45 + ring * 25
            
            for i in range(num_pontos):
                angulo = (2 * math.pi / num_pontos) * i
                offset = math.sin(self.fase * 2 + ring) * 0.5
                
                x = self.centro_x + math.cos(angulo + offset) * raio_ring
                y = self.centro_y + math.sin(angulo + offset) * raio_ring
                
                # Tamanho oscilante
                wave = math.sin(self.fase * 3 + i * 0.5 + ring)
                tamanho = 3 + abs(wave) * 4
                
                # Cor pulsante
                alpha = 0.3 + abs(wave) * 0.5
                cor = self._ajustar_cor_alpha(self.cores["audio_processando"], alpha)
                
                self.canvas_audio.create_oval(
                    x - tamanho, y - tamanho,
                    x + tamanho, y + tamanho,
                    fill=cor, outline=""
                )
        
        # Centro brilhante
        brilho = abs(math.sin(self.fase * 2)) * 0.3
        for i in range(3):
            r = 20 - i * 6
            alpha = brilho * (1 - i * 0.3)
            cor = self._ajustar_cor_alpha(self.cores["glow"], alpha)
            self.canvas_audio.create_oval(
                self.centro_x - r, self.centro_y - r,
                self.centro_x + r, self.centro_y + r,
                fill=cor, outline=""
            )
    
    def animar_falando(self):
        """Animação moderna do estado falando"""
        self.fase += 0.06
        
        # Efeito de pulso de voz
        intensidade = abs(math.sin(self.fase * 4)) * 0.3 + 0.2
        for i in range(3):
            r = 110 - i * 30
            cor = self._ajustar_cor_alpha(self.cores["primaria"], intensidade * (0.3 - i * 0.1))
            self.canvas_audio.create_oval(
                self.centro_x - r, self.centro_y - r,
                self.centro_x + r, self.centro_y + r,
                fill=cor, outline=""
            )
        
        # Forma de onda central estilizada
        pontos_centro = []
        amplitude_base = 35
        
        for x in range(-100, 101, 4):
            # Simulação de voz com múltiplas frequências
            voz1 = math.sin(x * 0.08 + self.fase * 3) * amplitude_base
            voz2 = math.sin(x * 0.15 + self.fase * 2) * amplitude_base * 0.5
            voz3 = math.cos(x * 0.05 + self.fase * 4) * amplitude_base * 0.3
            
            # Envelope para dar forma natural
            envelope = 1 - (abs(x) / 100) * 0.5
            y = self.centro_y + (voz1 + voz2 + voz3) * envelope
            
            pontos_centro.extend([self.centro_x + x, y])
        
        # Desenhar onda principal
        if len(pontos_centro) > 4:
            self.canvas_audio.create_line(
                pontos_centro, fill=self.cores["primaria"], 
                width=3, smooth=True, capstyle="round"
            )
            
            # Reflexo sutil
            pontos_reflexo = []
            for i in range(0, len(pontos_centro), 2):
                x = pontos_centro[i]
                y = 2 * self.centro_y - pontos_centro[i + 1]
                pontos_reflexo.extend([x, y])
            
            self.canvas_audio.create_line(
                pontos_reflexo, 
                fill=self._ajustar_cor_alpha(self.cores["primaria"], 0.2), 
                width=2, smooth=True
            )
        
        # Partículas de voz animadas
        if random.random() > 0.6:
            for _ in range(2):
                x = self.centro_x + random.randint(-80, 80)
                y = self.centro_y + random.randint(-30, 30)
                tamanho = random.uniform(1, 3)
                alpha = random.uniform(0.4, 0.7)
                cor = self._ajustar_cor_alpha(self.cores["accent"], alpha)
                
                self.canvas_audio.create_oval(
                    x - tamanho, y - tamanho,
                    x + tamanho, y + tamanho,
                    fill=cor, outline=""
                )
    
    def _ajustar_cor_alpha(self, cor_hex, alpha):
        """Simula transparência ajustando a cor"""
        # Converter hex para RGB
        r = int(cor_hex[1:3], 16)
        g = int(cor_hex[3:5], 16)
        b = int(cor_hex[5:7], 16)
        
        # Ajustar com base no fundo
        fundo_r = int(self.cores["fundo"][1:3], 16)
        fundo_g = int(self.cores["fundo"][3:5], 16)
        fundo_b = int(self.cores["fundo"][5:7], 16)
        
        # Interpolar
        r = int(r * alpha + fundo_r * (1 - alpha))
        g = int(g * alpha + fundo_g * (1 - alpha))
        b = int(b * alpha + fundo_b * (1 - alpha))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def toggle_audio(self):
        """Alterna estado do áudio"""
        if self.audio_estado == "idle":
            self.iniciar_gravacao_audio()
        elif self.audio_estado == "listening":
            self.parar_gravacao_audio()
        elif self.audio_estado == "processing":
            # Não fazer nada durante processamento
            pass
        elif self.audio_estado == "speaking":
            # Parar resposta
            self.audio_estado = "idle"
            self.atualizar_interface_audio()
    
    def iniciar_gravacao_audio(self):
        """Inicia gravação de áudio"""
        self.audio_estado = "listening"
        self.atualizar_interface_audio()
        
        # Simular gravação
        threading.Timer(5.0, self.processar_audio).start()
    
    def parar_gravacao_audio(self):
        """Para gravação e processa"""
        self.audio_estado = "processing"
        self.atualizar_interface_audio()
        
        # Simular processamento
        threading.Timer(2.0, self.responder_audio).start()
    
    def processar_audio(self):
        """Processa o áudio gravado"""
        if self.audio_estado == "listening":
            self.parar_gravacao_audio()
    
    def responder_audio(self):
        """IA responde com áudio"""
        self.audio_estado = "speaking"
        self.atualizar_interface_audio()
        
        # Simular resposta
        threading.Timer(3.0, self.finalizar_resposta).start()
    
    def finalizar_resposta(self):
        """Finaliza resposta e volta ao idle"""
        self.audio_estado = "idle"
        self.atualizar_interface_audio()
    
    def atualizar_interface_audio(self):
        """Atualiza elementos da interface conforme estado"""
        estados = {
            "idle": "",
            "listening": "ouvindo",
            "processing": "analisando",
            "speaking": "respondendo"
        }
        
        cores_botao = {
            "idle": self.cores["superficie"],
            "listening": self.cores["perigo"],
            "processing": self.cores["audio_processando"],
            "speaking": self.cores["primaria"]
        }
        
        if self.audio_estado in estados:
            self.label_status.configure(text=estados[self.audio_estado])
            cor_botao = cores_botao[self.audio_estado]
            # Aplicar transparência quando ativo
            if self.audio_estado != "idle":
                cor_botao = self._ajustar_cor_alpha(cor_botao, 0.9)
            self.btn_audio_control.configure(fg_color=cor_botao)
            self.update_button_icon()
    
    def fechar_interface_audio(self):
        """Fecha interface de áudio e volta ao chat"""
        self.animacao_ativa = False
        self.audio_estado = "idle"
        self.transicao_rapida(self._criar_assistente)
    
    # ==================== UTILIDADES ====================
    def criar_cabecalho_voltar(self, titulo):
        """Cria cabeçalho padrão com botão voltar"""
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
    

    def executar(self):
        self.janela.mainloop()

# ==================== INICIALIZAÇÃO ====================
if __name__ == "__main__":
    print("🚀 Iniciando Sistema TFT com Interface de Áudio...")
    print("📱 Interface: 320x240 pixels")
    print("📐 Área útil: 320x220 pixels (20px barra superior)")
    print("🎯 Modo TFT - Janela sem decorações")
    print("🖱️ Arraste pela barra superior para mover")
    print("🎤 Nova interface de áudio conversacional")
    print("⚠️ Use o botão ✕ ou ESC para fechar\n")
    
    app = SistemaTFT()
    
    # Bind ESC para fechar
    app.janela.bind("<Escape>", lambda e: app.janela.destroy())
    
    app.executar()