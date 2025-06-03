"""
Sistema de Reuniões - Display TFT Touch
Resolução fixa: 320x240 pixels
Interface otimizada para telas touch pequenas

ESTRUTURA:
- Barra de título customizada: 20px (arrastar janela + fechar)
- Área útil: 320x220 pixels
- Sem decorações de janela do sistema operacional
- Navegação otimizada para toque
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
import threading
import time
import os

class SistemaTFT:
    def __init__(self):
        # Configurar tema escuro com nova paleta
        ctk.set_appearance_mode("dark")
        
        # Paleta de cores personalizada - tons de azul e cinza
        self.cores = {
            "primaria": "#1E88E5",      # Azul principal
            "secundaria": "#424242",     # Cinza escuro
            "sucesso": "#43A047",        # Verde
            "perigo": "#E53935",         # Vermelho
            "alerta": "#FB8C00",         # Laranja
            "fundo": "#121212",          # Preto suave
            "superficie": "#1E1E1E",     # Cinza muito escuro
            "texto": "#E0E0E0",          # Cinza claro
            "texto_secundario": "#9E9E9E" # Cinza médio
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
        
        # Estado do sistema
        self.usuario_logado = None
        self.frame_atual = None
        self.gravando = False
        self.timer_ativo = False
        self.contexto_reuniao = None
        
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
        
        # Container central sem título
        frame_central = ctk.CTkFrame(self.frame_atual, width=280, height=170, fg_color=self.cores["superficie"])
        frame_central.place(relx=0.5, rely=0.5, anchor="center")
        frame_central.pack_propagate(False)
        
        # Espaçamento superior
        ctk.CTkFrame(frame_central, height=15, fg_color=self.cores["superficie"]).pack()
        
        # Campos de login com tamanhos iguais
        # Usuário
        ctk.CTkLabel(
            frame_central, 
            text="Usuário", 
            font=ctk.CTkFont(size=12),
            text_color=self.cores["texto_secundario"]
        ).pack(pady=(0, 3))
        
        self.entry_usuario = ctk.CTkEntry(
            frame_central, 
            width=220, 
            height=30,  # Reduzido levemente
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
        ).pack(pady=(0, 3))
        
        self.entry_senha = ctk.CTkEntry(
            frame_central, 
            width=220, 
            height=30,  # Reduzido levemente
            fg_color=self.cores["fundo"],
            border_color=self.cores["primaria"],
            placeholder_text="Digite sua senha",
            show="●"
        )
        self.entry_senha.pack(pady=(0, 10))
        
        # Botão entrar
        self.btn_login = ctk.CTkButton(
            frame_central,
            text="ENTRAR",
            width=220,
            height=34,  # Levemente menor
            command=self.fazer_login,
            font=ctk.CTkFont(size=13, weight="bold"),
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
        
        # Botões em lista contínua - sem margens laterais
        # Botões direto no frame_atual para tocar as bordas
        
        botoes = [
            ("📋 Histórico", self.mostrar_historico, self.cores["secundaria"]),
            ("🎙️ Nova Gravação", self.mostrar_pre_gravacao, self.cores["sucesso"]),
            ("🤖 Assistente IA", self.mostrar_assistente, self.cores["primaria"])
        ]
        
        for i, (texto, comando, cor) in enumerate(botoes):
            btn = ctk.CTkButton(
                self.frame_atual,  # Direto no frame principal
                text=texto,
                width=320,  # Largura total da janela
                height=58,  # Altura ajustada (160px / 3 botões ≈ 53px + margem)
                command=comando,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=cor,
                hover_color=cor,
                corner_radius=0  # Sem bordas arredondadas
            )
            btn.pack(pady=(0, 1))  # Pequeno espaço entre botões
    
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
            height=150,  # Reduzido para caber no espaço disponível
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
            # Item da reunião
            frame_item = ctk.CTkFrame(
                frame_lista, 
                height=50,  # Aumentado para evitar sobreposição
                fg_color=self.cores["superficie"]
            )
            frame_item.pack(fill="x", padx=10, pady=(5 if i == 0 else 0, 0))
            frame_item.pack_propagate(False)
            
            # Info da reunião
            frame_info = ctk.CTkFrame(frame_item, fg_color="transparent")
            frame_info.pack(side="left", fill="both", expand=True, padx=(10, 0))
            
            ctk.CTkLabel(
                frame_info,
                text=titulo,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.cores["texto"],
                anchor="w"
            ).pack(anchor="w", pady=(8, 2))  # Ajustado espaçamento
            
            ctk.CTkLabel(
                frame_info,
                text=f"{data} • {duracao}",
                font=ctk.CTkFont(size=10),
                text_color=self.cores["texto_secundario"],
                anchor="w"
            ).pack(anchor="w", pady=(0, 8))  # Ajustado espaçamento
            
            # Botão ver
            ctk.CTkButton(
                frame_item,
                text="Ver",
                width=50,
                height=30,
                font=ctk.CTkFont(size=11),
                fg_color=self.cores["primaria"],
                command=lambda t=titulo, d=data, dur=duracao: self.mostrar_detalhes_reuniao(t, d, dur)
            ).pack(side="right", padx=10)
            
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
        
        # Info em uma linha só
        info_text = f"{titulo} • {data} • {duracao}"
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
            height=100,  # Ajustado para o espaço disponível
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
        
        # Botões no topo - altura reduzida
        frame_btns = ctk.CTkFrame(self.frame_atual, height=40, fg_color=self.cores["fundo"])
        frame_btns.pack(fill="x", padx=10, pady=(5, 5))
        frame_btns.pack_propagate(False)
        
        # Container interno para centralizar botões
        inner_btns = ctk.CTkFrame(frame_btns, fg_color=self.cores["fundo"])
        inner_btns.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkButton(
            inner_btns,
            text="Cancelar",
            width=140,
            height=32,  # Menor
            fg_color=self.cores["secundaria"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.transicao_rapida(self.mostrar_menu_principal)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            inner_btns,
            text="Iniciar",
            width=140,
            height=32,  # Menor
            fg_color=self.cores["sucesso"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.iniciar_gravacao
        ).pack(side="left", padx=5)
        
        # Container do formulário com scroll
        frame_scroll = ctk.CTkScrollableFrame(
            self.frame_atual, 
            fg_color=self.cores["superficie"],
            height=140  # Altura reduzida para caber no espaço
        )
        frame_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Título
        ctk.CTkLabel(
            frame_scroll, 
            text="Título da Reunião", 
            font=ctk.CTkFont(size=12),
            text_color=self.cores["texto_secundario"]
        ).pack(pady=(15, 5))
        
        self.entry_titulo = ctk.CTkEntry(
            frame_scroll, 
            width=260, 
            height=35,
            fg_color=self.cores["fundo"],
            border_color=self.cores["primaria"],
            placeholder_text="Ex: Reunião de Planejamento"
        )
        self.entry_titulo.pack(pady=(0, 15))
        
        # Notas - agora visível com scroll
        ctk.CTkLabel(
            frame_scroll, 
            text="Observações (opcional)", 
            font=ctk.CTkFont(size=12),
            text_color=self.cores["texto_secundario"]
        ).pack(pady=(0, 5))
        
        self.text_obs = ctk.CTkTextbox(
            frame_scroll, 
            width=260, 
            height=60,  # Altura adequada
            font=ctk.CTkFont(size=11),
            fg_color=self.cores["fundo"]
        )
        self.text_obs.pack(pady=(0, 20))
    
    def iniciar_gravacao(self):
        titulo = self.entry_titulo.get().strip()
        if not titulo:
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
        frame_central.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
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
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=self.cores["texto"]
        )
        self.label_timer.pack(pady=10)
        
        # Controles
        frame_controles = ctk.CTkFrame(frame_central, fg_color="transparent")
        frame_controles.pack(pady=15)
        
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
            height=130,  # Ajustado para o espaço disponível
            font=ctk.CTkFont(size=11),
            fg_color=self.cores["superficie"]
        )
        self.text_chat.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Mensagem inicial
        msg_inicial = "🤖 Olá! Sou seu assistente. Como posso ajudá-lo?\n\n"
        if hasattr(self, 'contexto_reuniao') and self.contexto_reuniao:
            msg_inicial += f"📄 Vi que você quer analisar: {self.contexto_reuniao}\n\n"
            msg_inicial += "Posso ajudar com:\n• Resumo dos pontos principais\n• Ações pendentes\n• Insights importantes\n\n"
            # Limpar contexto após usar
            self.contexto_reuniao = None
            
        self.text_chat.insert("end", msg_inicial)
        self.text_chat.configure(state="disabled")
        
        # Entrada
        frame_entrada = ctk.CTkFrame(self.frame_atual, height=35, fg_color=self.cores["superficie"])
        frame_entrada.pack(fill="x", padx=5, pady=(0, 5))
        frame_entrada.pack_propagate(False)
        
        self.entry_chat = ctk.CTkEntry(
            frame_entrada,
            placeholder_text="Digite sua mensagem...",
            font=ctk.CTkFont(size=10),
            fg_color=self.cores["fundo"],
            border_color=self.cores["primaria"]
        )
        self.entry_chat.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        ctk.CTkButton(
            frame_entrada,
            text="➤",
            width=35,
            height=25,
            font=ctk.CTkFont(size=14),
            fg_color=self.cores["primaria"],
            command=self.enviar_mensagem
        ).pack(side="right", padx=5)
        
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
    print("🚀 Iniciando Sistema TFT...")
    print("📱 Interface: 320x240 pixels")
    print("🎯 Modo TFT - Janela sem decorações")
    print("🖱️ Arraste pela barra superior para mover")
    print("⚠️ Use o botão ✕ ou ESC para fechar\n")
    
    app = SistemaTFT()
    
    # Bind ESC para fechar
    app.janela.bind("<Escape>", lambda e: app.janela.destroy())
    
    app.executar()