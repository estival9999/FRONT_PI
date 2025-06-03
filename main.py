"""
Sistema AURALIS - Interface Fluida e Interativa
Versão com transições suaves e janela única
Tamanho: 480x360 pixels

Requisitos:
- pip install customtkinter
- pip install Pillow (para suporte a logo)
"""

import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime, timedelta
import threading
import time
import os

# Tentar importar PIL/Pillow
try:
    from PIL import Image, ImageTk
    PIL_DISPONIVEL = True
except ImportError:
    PIL_DISPONIVEL = False
    print("⚠️ Pillow não instalado. Logo não será exibida. Instale com: pip install Pillow")

class SistemaAuralis:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Janela única principal
        self.janela = ctk.CTk()
        self.janela.title("AURALIS - Sistema de Gestão de Reuniões")
        self.janela.geometry("320x360")
        self.janela.resizable(False, False)
        
        # Estado do sistema
        self.usuario_logado = None
        self.frame_atual = None
        self.gravando = False
        self.timer_ativo = False
        
        # Logo (placeholder - substitua com o caminho da sua logo)
        self.logo_path = "logo_auralis.png"  # Coloque o arquivo da logo aqui
        self.logo_image = None
        self.carregar_logo()
        
        # Centralizar janela
        self.centralizar_janela()
        
        # Criar container principal
        self.container_principal = ctk.CTkFrame(self.janela)
        self.container_principal.pack(fill="both", expand=True)
        
        # Iniciar com tela de login
        self.mostrar_login()
    
    def carregar_logo(self):
        """Carrega a logo ou usa texto como fallback"""
        if not PIL_DISPONIVEL:
            self.logo_image = None
            return
            
        try:
            if os.path.exists(self.logo_path):
                # Carregar imagem original
                self.pil_image_original = Image.open(self.logo_path)
                
                # Logo grande para tela de login (2.5x maior)
                pil_image_grande = self.pil_image_original.copy()
                pil_image_grande.thumbnail((200, 70), Image.Resampling.LANCZOS)
                self.logo_image = ctk.CTkImage(
                    light_image=pil_image_grande,
                    dark_image=pil_image_grande,
                    size=(pil_image_grande.width, pil_image_grande.height)
                )
                
                # Logo pequena para cabeçalho (mantém proporção)
                pil_image_pequena = self.pil_image_original.copy()
                pil_image_pequena.thumbnail((80, 40), Image.Resampling.LANCZOS)
                self.logo_pequena = ctk.CTkImage(
                    light_image=pil_image_pequena,
                    dark_image=pil_image_pequena,
                    size=(pil_image_pequena.width, pil_image_pequena.height)
                )
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            self.logo_image = None
            self.logo_pequena = None
    
    def centralizar_janela(self):
        self.janela.update_idletasks()
        largura = 480
        altura = 360
        x = (self.janela.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.janela.winfo_screenheight() // 2) - (altura // 2)
        self.janela.geometry(f"{largura}x{altura}+{x}+{y}")
    
    def transicao_suave(self, novo_frame_func):
        """Realiza transição suave entre frames"""
        if self.frame_atual:
            # Fade out
            for i in range(10, 0, -1):
                self.frame_atual.configure(fg_color=(f"gray{i*2}", f"gray{i*2}"))
                self.janela.update()
                time.sleep(0.01)
            self.frame_atual.destroy()
        
        # Criar novo frame
        novo_frame_func()
        
        # Fade in
        if self.frame_atual:
            for i in range(1, 11):
                try:
                    self.frame_atual.configure(fg_color=(f"gray{i*2}", f"gray{20}"))
                    self.janela.update()
                    time.sleep(0.01)
                except:
                    pass
    
    # ==================== TELA DE LOGIN ====================
    def mostrar_login(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        # Logo ou texto
        if self.logo_image:
            label_logo = ctk.CTkLabel(
                self.frame_atual,
                image=self.logo_image,
                text=""
            )
            label_logo.pack(pady=(30, 20))
        else:
            # Logo texto animado como fallback
            self.label_logo = ctk.CTkLabel(
                self.frame_atual,
                text="AURALIS",
                font=ctk.CTkFont(size=36, weight="bold")
            )
            self.label_logo.pack(pady=(30, 10))
            # Animação do logo
            self.animar_logo()
        
        # Campos de login
        frame_login = ctk.CTkFrame(self.frame_atual, width=300, height=200)
        frame_login.pack(pady=20)
        frame_login.pack_propagate(False)
        
        ctk.CTkLabel(frame_login, text="Usuário:", font=ctk.CTkFont(size=12)).pack(pady=(20, 5))
        self.entry_usuario = ctk.CTkEntry(frame_login, width=250, placeholder_text="Digite seu usuário")
        self.entry_usuario.pack(pady=(0, 10))
        
        ctk.CTkLabel(frame_login, text="Senha:", font=ctk.CTkFont(size=12)).pack(pady=(0, 5))
        self.entry_senha = ctk.CTkEntry(frame_login, width=250, placeholder_text="Digite sua senha", show="●")
        self.entry_senha.pack(pady=(0, 20))
        
        # Botão com hover effect
        self.btn_login = ctk.CTkButton(
            frame_login,
            text="Entrar",
            width=250,
            height=35,
            command=self.fazer_login,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_login.pack()
        
        # Bind Enter
        self.entry_senha.bind("<Return>", lambda e: self.fazer_login())
        
        # Status
        self.label_status = ctk.CTkLabel(
            self.frame_atual,
            text="Demo: Use qualquer usuário/senha",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.label_status.pack(pady=10)
        
        self.entry_usuario.focus()
    
    def animar_logo(self):
        """Animação pulsante do logo"""
        def pulsar():
            sizes = [36, 38, 40, 38, 36]
            for size in sizes:
                if hasattr(self, 'label_logo') and self.label_logo:
                    try:
                        self.label_logo.configure(font=ctk.CTkFont(size=size, weight="bold"))
                        self.janela.update()
                        time.sleep(0.1)
                    except:
                        break
        
        threading.Thread(target=pulsar, daemon=True).start()
    
    def fazer_login(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()
        
        if not usuario or not senha:
            self.mostrar_mensagem_temporaria("Preencha todos os campos!", "red")
            return
        
        # Animação de loading
        self.btn_login.configure(state="disabled", text="Entrando...")
        self.label_status.configure(text="Verificando credenciais...", text_color="yellow")
        
        # Simular verificação
        self.janela.after(1000, lambda: self.login_sucesso(usuario))
    
    def login_sucesso(self, usuario):
        self.usuario_logado = {
            "usuario": usuario,
            "area": "administracao"
        }
        
        self.label_status.configure(text="Login realizado! ✓", text_color="green")
        self.janela.after(500, lambda: self.transicao_suave(self.mostrar_menu_principal))
    
    # ==================== MENU PRINCIPAL ====================
    def mostrar_menu_principal(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        # Cabeçalho
        frame_header = ctk.CTkFrame(self.frame_atual, height=60)
        frame_header.pack(fill="x", padx=10, pady=(10, 0))
        frame_header.pack_propagate(False)
        
        # Logo ou texto no cabeçalho
        if hasattr(self, 'logo_pequena') and self.logo_pequena and PIL_DISPONIVEL:
            ctk.CTkLabel(
                frame_header,
                image=self.logo_pequena,
                text=""
            ).pack(side="left", padx=10, pady=10)
        else:
            ctk.CTkLabel(
                frame_header,
                text="AURALIS",
                font=ctk.CTkFont(size=24, weight="bold")
            ).pack(side="left", padx=10, pady=15)
        
        # Usuário e botão sair sutil no canto
        frame_user = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_user.pack(side="right", padx=10, pady=15)
        
        ctk.CTkLabel(
            frame_user,
            text=f"👤 {self.usuario_logado['usuario']}",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 10))
        
        # Botão sair pequeno e sutil
        btn_sair_sutil = ctk.CTkButton(
            frame_user,
            text="sair",
            width=40,
            height=20,
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            text_color="gray",
            hover_color=("gray20", "gray20"),
            command=self.fazer_logout
        )
        btn_sair_sutil.pack(side="left")
        
        # Container de botões principais
        frame_botoes = ctk.CTkFrame(self.frame_atual)
        frame_botoes.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Apenas os 3 botões principais
        botoes = [
            ("📋 Histórico", self.mostrar_historico, "blue"),
            ("🎙️ Nova Gravação", self.mostrar_pre_gravacao, "green"),
            ("🤖 AURALIS IA", self.mostrar_auralis, "purple")
        ]
        
        for i, (texto, comando, cor) in enumerate(botoes):
            btn = ctk.CTkButton(
                frame_botoes,
                text=texto,
                width=220,
                height=55,
                command=comando,
                fg_color=cor if cor != "blue" else None,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            btn.pack(pady=12)
            
            # Efeito hover personalizado
            self.adicionar_efeito_hover(btn, cor)
    
    def adicionar_efeito_hover(self, botao, cor):
        """Adiciona efeito hover animado aos botões"""
        def on_enter(e):
            botao.configure(width=230, height=58)
        
        def on_leave(e):
            botao.configure(width=220, height=55)
        
        botao.bind("<Enter>", on_enter)
        botao.bind("<Leave>", on_leave)
    
    # ==================== HISTÓRICO ====================
    def mostrar_historico(self):
        self.transicao_suave(self._criar_historico)
    
    def _criar_historico(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        # Cabeçalho
        frame_header = ctk.CTkFrame(self.frame_atual, height=50)
        frame_header.pack(fill="x", padx=10, pady=(10, 0))
        frame_header.pack_propagate(False)
        
        ctk.CTkLabel(
            frame_header,
            text="📋 Histórico de Reuniões",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left", padx=10, pady=12)
        
        # Lista scrollável
        frame_scroll = ctk.CTkScrollableFrame(self.frame_atual, height=200)
        frame_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Reuniões exemplo
        reunioes = [
            ("Planejamento Q1", "15/01/2025", "45min"),
            ("Daily Standup", "14/01/2025", "15min"),
            ("Revisão Sprint", "12/01/2025", "1h20min"),
            ("Kickoff Projeto", "10/01/2025", "2h"),
        ]
        
        for i, (titulo, data, duracao) in enumerate(reunioes):
            frame_item = ctk.CTkFrame(frame_scroll, height=50)
            frame_item.pack(fill="x", pady=3)
            frame_item.pack_propagate(False)
            
            ctk.CTkLabel(
                frame_item,
                text=f"{titulo}\n{data} • {duracao}",
                font=ctk.CTkFont(size=11),
                justify="left"
            ).pack(side="left", padx=10, pady=5)
            
            btn_ver = ctk.CTkButton(
                frame_item,
                text="Ver",
                width=50,
                height=30,
                font=ctk.CTkFont(size=11),
                command=lambda t=titulo, d=data, dur=duracao: self.mostrar_detalhes_reuniao(t, d, dur)
            )
            btn_ver.pack(side="right", padx=10, pady=10)
            
            # Adicionar linha separadora (exceto após o último item)
            if i < len(reunioes) - 1:
                separator = ctk.CTkFrame(frame_scroll, height=1, fg_color=("gray70", "gray30"))
                separator.pack(fill="x", padx=20, pady=2)
        
        # Botão voltar
        ctk.CTkButton(
            self.frame_atual,
            text="← Voltar",
            width=100,
            height=30,
            command=lambda: self.transicao_suave(self.mostrar_menu_principal)
        ).pack(pady=10)
    
    def mostrar_detalhes_reuniao(self, titulo, data, duracao):
        """Mostra os detalhes de uma reunião específica"""
        self.transicao_suave(lambda: self._criar_detalhes_reuniao(titulo, data, duracao))
    
    def _criar_detalhes_reuniao(self, titulo, data, duracao):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        # Cabeçalho
        ctk.CTkLabel(
            self.frame_atual,
            text=f"📄 {titulo}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10))
        
        # Informações
        frame_info = ctk.CTkFrame(self.frame_atual)
        frame_info.pack(fill="x", padx=20, pady=10)
        
        info_text = f"📅 Data: {data}\n⏱️ Duração: {duracao}\n👤 Responsável: {self.usuario_logado['usuario']}"
        ctk.CTkLabel(
            frame_info,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(padx=15, pady=10)
        
        # Transcrição simulada
        ctk.CTkLabel(
            self.frame_atual,
            text="Transcrição:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        text_transcricao = ctk.CTkTextbox(
            self.frame_atual,
            height=120,
            font=ctk.CTkFont(size=11)
        )
        text_transcricao.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Texto exemplo
        transcricao_exemplo = f"""Transcrição da reunião: {titulo}

Participantes discutiram os principais pontos do projeto.
- Definição de metas e objetivos
- Distribuição de tarefas
- Prazos estabelecidos
- Próximos passos definidos

Esta é uma transcrição de demonstração."""
        
        text_transcricao.insert("1.0", transcricao_exemplo)
        text_transcricao.configure(state="disabled")
        
        # Botões
        frame_btns = ctk.CTkFrame(self.frame_atual, fg_color="transparent")
        frame_btns.pack(pady=10)
        
        ctk.CTkButton(
            frame_btns,
            text="← Voltar",
            width=100,
            height=30,
            command=lambda: self.transicao_suave(self._criar_historico)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_btns,
            text="🤖 Analisar com IA",
            width=120,
            height=30,
            fg_color="purple",
            command=lambda: messagebox.showinfo("IA", "Análise com IA será implementada em breve!")
        ).pack(side="left", padx=5)
    
    # ==================== PRÉ-GRAVAÇÃO ====================
    def mostrar_pre_gravacao(self):
        self.transicao_suave(self._criar_pre_gravacao)
    
    def _criar_pre_gravacao(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        # Título
        ctk.CTkLabel(
            self.frame_atual,
            text="Nova Gravação",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 10))
        
        # Formulário
        frame_form = ctk.CTkFrame(self.frame_atual)
        frame_form.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(frame_form, text="Título da Reunião:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        self.entry_titulo = ctk.CTkEntry(frame_form, width=300, placeholder_text="Ex: Reunião de Planejamento")
        self.entry_titulo.pack(pady=(0, 10))
        
        # Info automática
        info_text = f"Responsável: {self.usuario_logado['usuario']}\n"
        info_text += f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        ctk.CTkLabel(
            frame_form,
            text=info_text,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(pady=10)
        
        # Observações
        ctk.CTkLabel(frame_form, text="Observações:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        self.text_obs = ctk.CTkTextbox(frame_form, width=300, height=40, font=ctk.CTkFont(size=11))
        self.text_obs.pack(pady=(0, 15))
        
        # Botões maiores e mais espaçados
        frame_btns = ctk.CTkFrame(self.frame_atual, fg_color="transparent", height=60)
        frame_btns.pack(fill="x", pady=(5, 10))
        
        # Frame interno para centralizar botões
        frame_btns_inner = ctk.CTkFrame(frame_btns, fg_color="transparent")
        frame_btns_inner.pack(expand=True)
        
        ctk.CTkButton(
            frame_btns_inner,
            text="Cancelar",
            width=140,
            height=45,
            fg_color="gray",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=lambda: self.transicao_suave(self.mostrar_menu_principal)
        ).pack(side="left", padx=15)
        
        ctk.CTkButton(
            frame_btns_inner,
            text="Iniciar Gravação",
            width=140,
            height=45,
            fg_color="green",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.iniciar_gravacao
        ).pack(side="left", padx=15)
    
    def iniciar_gravacao(self):
        titulo = self.entry_titulo.get().strip()
        if not titulo:
            self.mostrar_mensagem_temporaria("Digite o título da reunião!", "red")
            return
        
        self.dados_reuniao = {
            'titulo': titulo,
            'usuario': self.usuario_logado['usuario'],
            'observacoes': self.text_obs.get("1.0", "end-1c")
        }
        
        self.transicao_suave(self._criar_gravacao)
    
    # ==================== GRAVAÇÃO ====================
    def _criar_gravacao(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        # Título da reunião
        ctk.CTkLabel(
            self.frame_atual,
            text=self.dados_reuniao['titulo'],
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10))
        
        # Indicador de gravação
        self.label_rec = ctk.CTkLabel(
            self.frame_atual,
            text="🔴 GRAVANDO",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="red"
        )
        self.label_rec.pack(pady=20)
        
        # Timer
        self.label_timer = ctk.CTkLabel(
            self.frame_atual,
            text="00:00:00",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        self.label_timer.pack(pady=10)
        
        # Controles
        frame_controles = ctk.CTkFrame(self.frame_atual)
        frame_controles.pack(pady=20)
        
        self.btn_pausar = ctk.CTkButton(
            frame_controles,
            text="⏸️ Pausar",
            width=80,
            height=40,
            fg_color="orange",
            command=self.pausar_gravacao
        )
        self.btn_pausar.pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_controles,
            text="⏹️ Parar",
            width=80,
            height=40,
            fg_color="green",
            command=self.parar_gravacao
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_controles,
            text="❌ Cancelar",
            width=80,
            height=40,
            fg_color="red",
            command=self.cancelar_gravacao
        ).pack(side="left", padx=5)
        
        # Iniciar gravação
        self.gravando = True
        self.pausado = False
        self.tempo_inicial = datetime.now()
        self.tempo_pausado = timedelta()
        self.timer_ativo = True
        self.atualizar_timer()
    
    def atualizar_timer(self):
        if self.timer_ativo and self.gravando and not self.pausado:
            tempo_total = datetime.now() - self.tempo_inicial - self.tempo_pausado
            horas = int(tempo_total.total_seconds() // 3600)
            minutos = int((tempo_total.total_seconds() % 3600) // 60)
            segundos = int(tempo_total.total_seconds() % 60)
            
            self.label_timer.configure(text=f"{horas:02d}:{minutos:02d}:{segundos:02d}")
            self.janela.after(100, self.atualizar_timer)
    
    def pausar_gravacao(self):
        if not self.pausado:
            self.pausado = True
            self.momento_pausa = datetime.now()
            self.btn_pausar.configure(text="▶️ Retomar", fg_color="green")
            self.label_rec.configure(text="⏸️ PAUSADO", text_color="orange")
        else:
            self.tempo_pausado += datetime.now() - self.momento_pausa
            self.pausado = False
            self.btn_pausar.configure(text="⏸️ Pausar", fg_color="orange")
            self.label_rec.configure(text="🔴 GRAVANDO", text_color="red")
            self.atualizar_timer()
    
    def parar_gravacao(self):
        self.gravando = False
        self.timer_ativo = False
        messagebox.showinfo("Sucesso", f"Gravação finalizada!\n\nReunião: {self.dados_reuniao['titulo']}")
        self.transicao_suave(self.mostrar_menu_principal)
    
    def cancelar_gravacao(self):
        if messagebox.askyesno("Cancelar", "Deseja cancelar a gravação?"):
            self.gravando = False
            self.timer_ativo = False
            self.transicao_suave(self.mostrar_menu_principal)
    
    # ==================== AURALIS IA ====================
    def mostrar_auralis(self):
        self.transicao_suave(self._criar_auralis)
    
    def _criar_auralis(self):
        self.frame_atual = ctk.CTkFrame(self.container_principal)
        self.frame_atual.pack(fill="both", expand=True)
        
        # Título
        ctk.CTkLabel(
            self.frame_atual,
            text="🤖 AURALIS IA",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        # Chat
        self.text_chat = ctk.CTkTextbox(
            self.frame_atual,
            height=180,
            font=ctk.CTkFont(size=11)
        )
        self.text_chat.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Mensagem inicial
        self.text_chat.insert("end", "🤖 AURALIS: Olá! Como posso ajudá-lo?\n\n")
        self.text_chat.configure(state="disabled")
        
        # Entrada
        frame_entrada = ctk.CTkFrame(self.frame_atual)
        frame_entrada.pack(fill="x", padx=10, pady=(0, 10))
        
        self.entry_chat = ctk.CTkEntry(
            frame_entrada,
            placeholder_text="Digite sua mensagem...",
            font=ctk.CTkFont(size=11)
        )
        self.entry_chat.pack(side="left", fill="x", expand=True, padx=(5, 0), pady=5)
        
        ctk.CTkButton(
            frame_entrada,
            text="Enviar",
            width=60,
            height=28,
            command=self.enviar_mensagem
        ).pack(side="right", padx=5, pady=5)
        
        # Voltar
        ctk.CTkButton(
            self.frame_atual,
            text="← Voltar",
            width=100,
            height=30,
            command=lambda: self.transicao_suave(self.mostrar_menu_principal)
        ).pack(pady=5)
        
        self.entry_chat.bind("<Return>", lambda e: self.enviar_mensagem())
    
    def enviar_mensagem(self):
        msg = self.entry_chat.get().strip()
        if not msg:
            return
        
        self.text_chat.configure(state="normal")
        self.text_chat.insert("end", f"👤 Você: {msg}\n")
        self.text_chat.insert("end", "🤖 AURALIS: Processando sua solicitação...\n\n")
        self.text_chat.configure(state="disabled")
        self.text_chat.see("end")
        
        self.entry_chat.delete(0, "end")
    
    # ==================== UTILIDADES ====================
    def fazer_logout(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair?"):
            self.usuario_logado = None
            self.transicao_suave(self.mostrar_login)
    
    def mostrar_mensagem_temporaria(self, msg, cor):
        label_temp = ctk.CTkLabel(
            self.frame_atual,
            text=msg,
            text_color=cor,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label_temp.place(relx=0.5, rely=0.9, anchor="center")
        
        self.janela.after(2000, label_temp.destroy)
    
    def executar(self):
        self.janela.mainloop()

# ==================== INICIALIZAÇÃO ====================
if __name__ == "__main__":
    # IMPORTANTE: Para adicionar sua logo:
    # 1. Instale Pillow (opcional): pip install Pillow
    # 2. Salve sua logo como 'logo_auralis.png' na mesma pasta deste script
    # 3. A logo será automaticamente redimensionada mantendo a proporção
    # 4. Se a logo não for encontrada ou Pillow não estiver instalado, 
    #    o sistema usará texto como fallback
    
    print("🚀 Iniciando AURALIS...")
    print("📍 Para adicionar logo: salve como 'logo_auralis.png' nesta pasta")
    
    app = SistemaAuralis()
    app.executar()