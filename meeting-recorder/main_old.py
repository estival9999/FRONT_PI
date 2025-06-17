#!/usr/bin/env python3
"""
Aplicativo de Gravação de Reuniões
Resolução: 320x240 pixels
Design minimalista e profissional
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import re
import threading
import time
import json
import difflib

# Carrega variáveis de ambiente
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")

# Print temporário para verificar se a API key foi carregada
print(f"API Key carregada com sucesso! Primeiros 10 caracteres: {OPENAI_API_KEY[:10]}...")

# Importa a classe AudioRecorder
try:
    from audio_recorder_standalone import AudioRecorder
    print("AudioRecorder importado com sucesso!")
except ImportError as e:
    print(f"Erro ao importar AudioRecorder: {e}")
    AudioRecorder = None

# Funções de validação de nomes
def load_funcionarios():
    """Carrega a lista de funcionários do arquivo JSON"""
    try:
        with open('data/funcionarios.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar funcionários: {e}")
        return {"funcionarios": []}

def validate_names(transcribed_names):
    """
    Valida e corrige nomes transcritos usando correspondência fuzzy.
    
    Args:
        transcribed_names: Lista de nomes transcritos
        
    Returns:
        Lista de dicionários com informações sobre cada nome validado
    """
    funcionarios = load_funcionarios()
    nomes_funcionarios = [f['nome'] for f in funcionarios['funcionarios']]
    
    validated = []
    for name in transcribed_names:
        # Remove espaços extras e normaliza
        name = ' '.join(name.strip().split())
        
        # Busca correspondência mais próxima
        matches = difflib.get_close_matches(name, nomes_funcionarios, n=1, cutoff=0.6)
        
        if matches:
            correto = matches[0]
            # Calcula a similaridade
            ratio = difflib.SequenceMatcher(None, name.lower(), correto.lower()).ratio()
            
            validated.append({
                'original': name,
                'correto': correto,
                'corrigido': name.lower() != correto.lower(),
                'similaridade': ratio
            })
        else:
            # Nome não encontrado - mantém original
            validated.append({
                'original': name,
                'correto': name,
                'corrigido': False,
                'similaridade': 1.0
            })
    
    return validated

# Adiciona o diretório atual ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa a classe AudioRecorder
try:
    from audio_recorder_standalone import AudioRecorder
    print("AudioRecorder importado com sucesso!")
except ImportError as e:
    print(f"Erro ao importar AudioRecorder: {e}")
    AudioRecorder = None

# Cores da aplicação
COLORS = {
    'bg': '#1a1a1a',        # Fundo principal
    'fg': '#f0f0f0',        # Texto principal
    'primary': '#4a90e2',   # Cor de destaque
    'secondary': '#2a2a2a', # Fundo secundário
    'danger': '#e74c3c',    # Vermelho para ações perigosas
    'success': '#27ae60',   # Verde para sucesso
    'warning': '#f39c12',   # Amarelo para avisos
    'muted': '#7f8c8d'      # Cinza para texto secundário
}

class StartScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        
        # Container principal
        container = tk.Frame(self, bg=COLORS['bg'])
        container.pack(expand=True)
        
        # Título
        title = tk.Label(
            container,
            text="Gravador de Reuniões",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS['bg'],
            fg=COLORS['fg']
        )
        title.pack(pady=(0, 30))
        
        # Botão circular grande
        self.canvas = tk.Canvas(
            container,
            width=100,
            height=100,
            bg=COLORS['bg'],
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Desenha o botão circular
        self.button = self.canvas.create_oval(
            5, 5, 95, 95,
            fill=COLORS['primary'],
            outline=COLORS['primary']
        )
        
        # Texto do botão
        self.canvas.create_text(
            50, 50,
            text="INICIAR",
            font=("Segoe UI", 14, "bold"),
            fill="white"
        )
        
        # Bind do clique
        self.canvas.tag_bind(self.button, "<Button-1>", self.on_click)
        self.canvas.bind("<Button-1>", self.on_click)
        
        # Botão Ver Reuniões - verificar se há reuniões
        meeting_count = 0
        if os.path.exists('reunioes'):
            files = [f for f in os.listdir('reunioes') if f.endswith('.txt')]
            meeting_count = len(files)
        
        if meeting_count > 0:
            self.view_meetings_btn = tk.Button(
                container,
                text=f"Ver Reuniões ({meeting_count})",
                font=("Segoe UI", 11, "bold"),  # Fonte maior e bold
                bg=COLORS['primary'],  # Cor primária azul vibrante
                fg="white",  # Texto branco para contraste
                bd=1,  # Borda para destaque
                relief="solid",
                padx=15,
                pady=8,
                command=lambda: controller.show_frame("ViewMeetingsScreen"),
                cursor="hand2",
                activebackground="#5ba0f2",  # Cor mais clara ao clicar
                activeforeground="white"
            )
            self.view_meetings_btn.pack(pady=(15, 0))  # Menos espaço vertical
        else:
            # Botão desabilitado quando não há reuniões
            self.view_meetings_btn = tk.Button(
                container,
                text="Ver Reuniões",
                font=("Segoe UI", 10),
                bg=COLORS['secondary'],
                fg=COLORS['muted'],
                state="disabled",
                cursor="arrow"
            )
            self.view_meetings_btn.pack(pady=(15, 0))
        
        # Versão
        version = tk.Label(
            self,
            text="v1.0.0",
            font=("Segoe UI", 8),
            bg=COLORS['bg'],
            fg=COLORS['muted']
        )
        version.pack(side="bottom", pady=5)
    
    def on_click(self, event):
        self.controller.show_frame("ResponsibleScreen")
    
    def reset(self):
        # Atualiza o botão Ver Reuniões com o número de reuniões
        meeting_count = 0
        if os.path.exists('reunioes'):
            files = [f for f in os.listdir('reunioes') if f.endswith('.txt')]
            meeting_count = len(files)
        
        if meeting_count > 0:
            self.view_meetings_btn.config(
                text=f"Ver Reuniões ({meeting_count})",
                font=("Segoe UI", 11, "bold"),
                bg=COLORS['primary'],
                fg="white",
                state="normal",
                cursor="hand2",
                activebackground="#5ba0f2",
                activeforeground="white"
            )
        else:
            self.view_meetings_btn.config(
                text="Ver Reuniões",
                font=("Segoe UI", 10),
                bg=COLORS['secondary'],
                fg=COLORS['muted'],
                state="disabled",
                cursor="arrow"
            )

class ResponsibleScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        
        # Container principal
        container = tk.Frame(self, bg=COLORS['bg'])
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        title = tk.Label(
            container,
            text="Responsável pela Reunião",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS['bg'],
            fg=COLORS['fg']
        )
        title.pack(pady=(0, 20))
        
        # Campo de entrada
        self.entry = tk.Entry(
            container,
            font=("Segoe UI", 12),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            insertbackground=COLORS['fg'],
            width=25
        )
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", lambda e: self.next_screen())
        
        # Frame para botões
        button_frame = tk.Frame(container, bg=COLORS['bg'])
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Botão Voltar
        back_btn = tk.Button(
            button_frame,
            text="← Voltar",
            font=("Segoe UI", 10),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            command=lambda: controller.show_frame("StartScreen"),
            cursor="hand2"
        )
        back_btn.pack(side="left")
        
        # Botão Próximo
        next_btn = tk.Button(
            button_frame,
            text="Próximo →",
            font=("Segoe UI", 10),
            bg=COLORS['primary'],
            fg="white",
            command=self.next_screen,
            cursor="hand2"
        )
        next_btn.pack(side="right")
    
    def next_screen(self):
        name = self.entry.get().strip()
        if not name:
            messagebox.showwarning("Aviso", "Por favor, informe o nome do responsável.")
            return
        self.controller.shared_data['responsible'] = name
        self.controller.show_frame("ObjectiveScreen")
    
    def reset(self):
        self.entry.delete(0, tk.END)

class ObjectiveScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        
        # Container principal
        container = tk.Frame(self, bg=COLORS['bg'])
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        title = tk.Label(
            container,
            text="Objetivo da Reunião",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS['bg'],
            fg=COLORS['fg']
        )
        title.pack(pady=(0, 10))
        
        # Text area
        self.text = tk.Text(
            container,
            font=("Segoe UI", 10),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            insertbackground=COLORS['fg'],
            width=35,
            height=4,
            wrap=tk.WORD
        )
        self.text.pack(pady=5)
        self.text.bind("<KeyRelease>", self.update_counter)
        
        # Contador de caracteres
        self.counter = tk.Label(
            container,
            text="0/200",
            font=("Segoe UI", 8),
            bg=COLORS['bg'],
            fg=COLORS['muted']
        )
        self.counter.pack()
        
        # Frame para botões
        button_frame = tk.Frame(container, bg=COLORS['bg'])
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Botão Voltar
        back_btn = tk.Button(
            button_frame,
            text="← Voltar",
            font=("Segoe UI", 10),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            command=lambda: controller.show_frame("ResponsibleScreen"),
            cursor="hand2"
        )
        back_btn.pack(side="left")
        
        # Botão Próximo
        next_btn = tk.Button(
            button_frame,
            text="Próximo →",
            font=("Segoe UI", 10),
            bg=COLORS['primary'],
            fg="white",
            command=self.next_screen,
            cursor="hand2"
        )
        next_btn.pack(side="right")
    
    def update_counter(self, event=None):
        text = self.text.get(1.0, "end-1c")
        length = len(text)
        if length > 200:
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", text[:200])
            length = 200
        
        self.counter.config(text=f"{length}/200")
        if length > 180:
            self.counter.config(fg=COLORS['danger'])
        else:
            self.counter.config(fg=COLORS['muted'])
    
    def next_screen(self):
        objective = self.text.get(1.0, "end-1c").strip()
        if not objective:
            messagebox.showwarning("Aviso", "Por favor, informe o objetivo da reunião.")
            return
        self.controller.shared_data['objective'] = objective
        self.controller.shared_data['start_time'] = datetime.now()
        self.controller.show_frame("RecordingScreen")
    
    def reset(self):
        self.text.delete(1.0, tk.END)
        self.update_counter()

class RecordingScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        self.is_recording = True
        self.is_paused = False
        self.start_time = None
        self.audio_recorder = None  # Será criado no reset()
        
        # Container principal
        container = tk.Frame(self, bg=COLORS['bg'])
        container.pack(expand=True, fill="both")
        
        # Indicador de status
        self.status_frame = tk.Frame(container, bg=COLORS['bg'])
        self.status_frame.pack(pady=(10, 5))
        
        self.status_dot = tk.Canvas(
            self.status_frame,
            width=10,
            height=10,
            bg=COLORS['bg'],
            highlightthickness=0
        )
        self.status_dot.pack(side="left", padx=(0, 5))
        self.status_dot.create_oval(2, 2, 8, 8, fill=COLORS['danger'], outline="")
        
        self.status_label = tk.Label(
            self.status_frame,
            text="GRAVANDO",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['bg'],
            fg=COLORS['danger']
        )
        self.status_label.pack(side="left")
        
        # Timer
        self.timer_label = tk.Label(
            container,
            text="00:00:00",
            font=("Segoe UI Bold", 24),
            bg=COLORS['bg'],
            fg=COLORS['fg']
        )
        self.timer_label.pack(pady=(5, 10))
        
        # Visualizador de áudio (simulado)
        self.audio_canvas = tk.Canvas(
            container,
            width=280,
            height=60,
            bg=COLORS['secondary'],
            highlightthickness=0
        )
        self.audio_canvas.pack(pady=5)
        
        # Desenha barras de áudio
        self.audio_bars = []
        for i in range(50):
            x = i * 6
            bar = self.audio_canvas.create_rectangle(
                x, 30, x + 4, 30,
                fill=COLORS['primary'],
                outline=""
            )
            self.audio_bars.append(bar)
        
        # Frame para controles
        controls_frame = tk.Frame(container, bg=COLORS['bg'])
        controls_frame.pack(pady=(10, 0))
        
        # Botão Pause/Resume
        self.pause_btn = tk.Button(
            controls_frame,
            text="⏸",
            font=("Segoe UI", 16),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            width=3,
            command=self.toggle_pause,
            cursor="hand2"
        )
        self.pause_btn.pack(side="left", padx=5)
        
        # Botão Finalizar
        finish_btn = tk.Button(
            controls_frame,
            text="Finalizar",
            font=("Segoe UI", 10),
            bg=COLORS['danger'],
            fg="white",
            command=self.finish_recording,
            cursor="hand2"
        )
        finish_btn.pack(side="left", padx=5)
        
        # Inicia o timer e animação
        self.update_timer()
        self.animate_audio()
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="▶")
            self.status_label.config(text="PAUSADO", fg=COLORS['warning'])
            if self.audio_recorder:
                self.audio_recorder.pause_recording()
        else:
            self.pause_btn.config(text="⏸")
            self.status_label.config(text="GRAVANDO", fg=COLORS['danger'])
            if self.audio_recorder:
                self.audio_recorder.resume_recording()
    
    def update_timer(self):
        if self.is_recording and not self.is_paused:
            if self.start_time is None:
                self.start_time = datetime.now()
            
            elapsed = datetime.now() - self.start_time
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            seconds = int(elapsed.total_seconds() % 60)
            
            self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        if self.is_recording:
            self.after(1000, self.update_timer)
    
    def animate_audio(self):
        if self.is_recording and not self.is_paused:
            # Usa níveis de áudio reais se disponíveis
            if self.audio_recorder:
                audio_levels = self.audio_recorder.get_audio_levels()
                if audio_levels:
                    # Normaliza os níveis para a altura das barras
                    max_level = max(audio_levels) if max(audio_levels) > 0 else 1
                    for i, bar in enumerate(self.audio_bars):
                        if i < len(audio_levels):
                            level = audio_levels[-(i+1)]  # Pega do final para o início
                            height = int((level / max_level) * 35) + 5
                        else:
                            height = 5
                        self.audio_canvas.coords(bar, i * 6, 60 - height, i * 6 + 4, 60)
                else:
                    # Fallback para animação aleatória
                    import random
                    for i, bar in enumerate(self.audio_bars):
                        height = random.randint(5, 40)
                        self.audio_canvas.coords(bar, i * 6, 60 - height, i * 6 + 4, 60)
            else:
                # Fallback para animação aleatória
                import random
                for i, bar in enumerate(self.audio_bars):
                    height = random.randint(5, 40)
                    self.audio_canvas.coords(bar, i * 6, 60 - height, i * 6 + 4, 60)
        
        if self.is_recording:
            self.after(100, self.animate_audio)
    
    def finish_recording(self):
        self.is_recording = False
        if self.start_time:
            self.controller.shared_data['duration'] = (datetime.now() - self.start_time).total_seconds()
        
        # Para a gravação e salva o arquivo
        if self.audio_recorder:
            print("Finalizando gravação...")
            audio_path = self.audio_recorder.stop_recording()
            if audio_path and os.path.exists(audio_path):
                self.controller.shared_data['audio_path'] = audio_path
                # Verifica tamanho do arquivo
                file_size = os.path.getsize(audio_path)
                print(f"Áudio salvo em: {audio_path}")
                print(f"Tamanho do arquivo: {file_size} bytes")
            else:
                print("Erro ao salvar áudio ou arquivo não encontrado")
                self.controller.shared_data['audio_path'] = None
        else:
            print("AudioRecorder não inicializado")
            self.controller.shared_data['audio_path'] = None
            
        self.controller.show_frame("ParticipantsScreen")
    
    def reset(self):
        self.is_recording = True
        self.is_paused = False
        self.start_time = datetime.now()
        self.pause_btn.config(text="⏸")
        self.status_label.config(text="GRAVANDO", fg=COLORS['danger'])
        
        # Cria nova instância do AudioRecorder e inicia gravação
        if AudioRecorder:
            try:
                self.audio_recorder = AudioRecorder()
                self.audio_recorder.start_recording()
                print("Gravação de áudio iniciada com sucesso")
            except Exception as e:
                print(f"Erro ao iniciar gravação: {e}")
                self.audio_recorder = None
                messagebox.showwarning("Aviso", "Não foi possível iniciar a gravação de áudio.\nContinuando sem gravação.")
        else:
            print("AudioRecorder não disponível")
            self.audio_recorder = None
        
        self.update_timer()
        self.animate_audio()

class ParticipantsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        self.is_recording = False
        self.audio_recorder = None
        self.transcription_text = ""
        self.audio_level_job = None
        self.progress_animation_job = None
        self.progress_dots = 0
        
        # Container principal
        container = tk.Frame(self, bg=COLORS['bg'])
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        title = tk.Label(
            container,
            text="Informe os Participantes",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS['bg'],
            fg=COLORS['fg']
        )
        title.pack(pady=(0, 10))
        
        # Microfone
        self.mic_canvas = tk.Canvas(
            container,
            width=80,
            height=80,
            bg=COLORS['bg'],
            highlightthickness=0
        )
        self.mic_canvas.pack(pady=10)
        
        # Desenha o microfone
        self.mic_canvas.create_oval(25, 10, 55, 50, fill=COLORS['secondary'], outline=COLORS['fg'], width=2)
        self.mic_canvas.create_rectangle(35, 45, 45, 60, fill=COLORS['secondary'], outline=COLORS['fg'], width=2)
        self.mic_canvas.create_arc(20, 40, 60, 65, start=0, extent=-180, style="arc", outline=COLORS['fg'], width=2)
        
        # Frame para instrução com fundo
        self.instruction_frame = tk.Frame(container, bg=COLORS['bg'])
        self.instruction_frame.pack(pady=5, fill="x")
        
        # Instrução
        self.instruction = tk.Label(
            self.instruction_frame,
            text="Fale os nomes dos participantes",
            font=("Segoe UI", 10),
            bg=COLORS['bg'],
            fg=COLORS['muted'],
            padx=10,
            pady=5
        )
        self.instruction.pack()
        
        # Botão de gravação
        self.record_btn = tk.Button(
            container,
            text="Iniciar Gravação",
            font=("Segoe UI", 12, "bold"),  # Fonte maior e bold
            bg=COLORS['primary'],            # Cor primária azul
            fg="white",                      # Texto branco
            bd=2,                            # Borda maior
            relief="raised",                 # Relevo para destaque
            padx=20,                         # Mais padding horizontal
            pady=10,                         # Mais padding vertical
            command=self.toggle_recording,
            cursor="hand2"
        )
        self.record_btn.pack(pady=10)
        
        # Botão de cancelar (inicialmente oculto)
        self.cancel_btn = tk.Button(
            container,
            text="Cancelar",
            font=("Segoe UI", 10),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            command=self.cancel_processing,
            cursor="hand2"
        )
        # Não empacota inicialmente
    
    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.audio_recorder = AudioRecorder()
            self.audio_recorder.start_recording()
            self.record_btn.config(text="Parar", bg=COLORS['danger'])
            self.instruction.config(text="Gravando... Fale os nomes dos participantes", bg=COLORS['danger'], fg="white")
            # Adiciona indicador visual de gravação
            self.animate_recording()
        else:
            self.stop_recording()
    
    def stop_recording(self):
        self.is_recording = False
        self.record_btn.config(text="Processando...", bg=COLORS['warning'], state="disabled")
        self.instruction.config(text="🔄 Transcrevendo áudio...", bg=COLORS['warning'], fg=COLORS['bg'])
        
        # Para o indicador visual
        if self.audio_level_job:
            self.after_cancel(self.audio_level_job)
            self.audio_level_job = None
        
        # Inicia animação de progresso
        self.animate_progress()
        
        # Mostra botão de cancelar
        self.cancel_btn.pack(pady=5)
        
        # Para a gravação e obtém o arquivo
        if self.audio_recorder:
            audio_file = self.audio_recorder.stop_recording()
            if audio_file:
                # Faz a transcrição em thread separada
                threading.Thread(target=self.transcribe_and_process, args=(audio_file,), daemon=True).start()
            else:
                self.stop_progress_animation()
                self.instruction.config(text="Erro na gravação. Tente novamente.", bg=COLORS['danger'], fg="white")
                self.record_btn.config(text="Tentar Novamente", bg=COLORS['primary'], state="normal")
                messagebox.showerror("Erro", "Não foi possível gravar o áudio.")
    
    def transcribe_and_process(self, audio_file):
        """Transcreve o áudio e processa os participantes"""
        transcription = None
        try:
            # Faz a transcrição
            transcription = self.audio_recorder.transcribe_audio(audio_file)
        except Exception as e:
            print(f"Erro na transcrição: {e}")
            transcription = None
        
        # Tenta limpar o arquivo temporário com delay
        try:
            # Aguarda um pouco antes de limpar para garantir que o arquivo foi liberado
            import time
            time.sleep(0.5)
            if hasattr(self.audio_recorder, 'cleanup'):
                self.audio_recorder.cleanup()
        except Exception as e:
            print(f"Aviso: Não foi possível limpar arquivo temporário: {e}")
        
        # Atualiza a UI na thread principal
        self.after(0, lambda: self.process_participants(transcription))
    
    def process_participants(self, transcription):
        """Processa a transcrição para extrair nomes dos participantes"""
        # Para animação de progresso
        self.stop_progress_animation()
        
        if not transcription:
            self.instruction.config(text="❌ Não foi possível transcrever.", bg=COLORS['danger'], fg="white")
            self.record_btn.config(text="Tentar Novamente", bg=COLORS['primary'], state="normal")
            messagebox.showerror("Erro na Transcrição", 
                "Não foi possível transcrever o áudio.\n\n" +
                "Possíveis causas:\n" +
                "- Áudio muito baixo\n" +
                "- Ruído excessivo\n" +
                "- Silêncio na gravação\n\n" +
                "Tente falar mais próximo do microfone.")
            return
        
        # Atualiza para indicar processamento dos participantes
        self.instruction.config(text="🔍 Identificando participantes...", bg=COLORS['primary'], fg="white")
        self.update()
        
        # Mostra a transcrição temporariamente
        self.transcription_text = transcription
        self.after(500, lambda: self.instruction.config(
            text=f"Transcrição: {transcription[:100]}..." if len(transcription) > 100 else f"Transcrição: {transcription}", 
            bg=COLORS['secondary'], 
            fg=COLORS['fg']
        ))
        
        # Extrai nomes da transcrição
        participants = self.extract_names(transcription)
        
        if participants:
            # Valida e corrige os nomes usando fuzzy matching
            validated_participants = validate_names(participants)
            self.controller.shared_data['participants'] = validated_participants
            self.controller.shared_data['participants_transcription'] = transcription
            # Mostra sucesso antes de avançar
            self.instruction.config(text=f"✅ {len(validated_participants)} participante(s) identificado(s)!", bg=COLORS['success'], fg="white")
            self.record_btn.config(text="Aguarde...", bg=COLORS['success'], state="disabled")
            # Aguarda um momento para o usuário ver a transcrição
            self.after(2000, lambda: self.controller.show_frame("ConfirmationScreen"))
        else:
            self.instruction.config(text="⚠️ Nenhum participante identificado.", bg=COLORS['warning'], fg=COLORS['bg'])
            self.record_btn.config(text="Tentar Novamente", bg=COLORS['primary'], state="normal")
            messagebox.showwarning("Atenção", 
                "Não foi possível identificar participantes na gravação.\n\n" +
                "Dicas:\n" +
                "- Fale claramente cada nome\n" +
                "- Faça uma pausa entre os nomes\n" +
                "- Evite ruídos de fundo\n\n" +
                f"Sua fala: '{transcription[:100]}...'" if len(transcription) > 100 else f"Sua fala: '{transcription}'")
    
    def extract_names(self, text):
        """Extrai nomes próprios da transcrição"""
        names = []
        
        # Normaliza o texto
        text = text.strip()
        
        # Padrões para identificar listas de participantes
        patterns = [
            r"participantes?(?:\s+são)?[:\s]+([\w\s,e]+)",
            r"presentes?(?:\s+estão)?[:\s]+([\w\s,e]+)",
            r"pessoas?(?:\s+são)?[:\s]+([\w\s,e]+)",
            r"reunião(?:\s+com)?[:\s]+([\w\s,e]+)"
        ]
        
        # Tenta encontrar um padrão de lista
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                names_str = match.group(1)
                # Separa por vírgulas ou 'e'
                potential_names = re.split(r'[,e]|\se\s', names_str)
                for name in potential_names:
                    name = name.strip()
                    if self.is_valid_name(name):
                        names.append(name.title())
        
        # Se não encontrou padrão, procura por palavras capitalizadas
        if not names:
            # Encontra todas as palavras que começam com maiúscula
            words = text.split()
            i = 0
            while i < len(words):
                word = words[i].strip('.,;:')
                # Verifica se é uma palavra capitalizada
                if word and word[0].isupper() and len(word) > 2:
                    # Verifica se a próxima palavra também é capitalizada (nome composto)
                    full_name = word
                    j = i + 1
                    while j < len(words) and words[j].strip('.,;:')[0].isupper():
                        full_name += " " + words[j].strip('.,;:')
                        j += 1
                    
                    if self.is_valid_name(full_name):
                        names.append(full_name)
                    i = j
                else:
                    i += 1
        
        # Remove duplicatas mantendo a ordem
        seen = set()
        unique_names = []
        for name in names:
            if name.lower() not in seen:
                seen.add(name.lower())
                unique_names.append(name)
        
        return unique_names
    
    def is_valid_name(self, name):
        """Verifica se uma string é um nome válido"""
        if not name or len(name) < 2:
            return False
        
        # Lista de palavras comuns que não são nomes
        common_words = {
            'são', 'está', 'estão', 'foram', 'foi', 'ser', 'ter', 'haver',
            'participantes', 'participante', 'pessoas', 'pessoa', 'reunião',
            'presentes', 'presente', 'todos', 'todas', 'aqui', 'hoje',
            'amanhã', 'ontem', 'agora', 'depois', 'antes', 'durante',
            'para', 'com', 'sem', 'sobre', 'entre', 'através'
        }
        
        # Verifica se não é uma palavra comum
        if name.lower() in common_words:
            return False
        
        # Verifica se tem pelo menos uma letra
        if not any(c.isalpha() for c in name):
            return False
        
        # Aceita nomes com espaços (nomes compostos)
        if ' ' in name:
            parts = name.split()
            return all(part[0].isupper() or part.lower() in ['de', 'da', 'do', 'dos', 'das'] for part in parts if part)
        
        # Nome simples deve começar com maiúscula
        return name[0].isupper()
    
    def animate_recording(self):
        """Anima o indicador visual durante a gravação"""
        if self.is_recording:
            # Alterna a cor do microfone com efeito pulsante
            current_color = self.mic_canvas.itemcget(self.mic_canvas.find_all()[0], 'fill')
            new_color = COLORS['danger'] if current_color == COLORS['secondary'] else COLORS['secondary']
            for item in self.mic_canvas.find_all():
                self.mic_canvas.itemconfig(item, fill=new_color)
            
            # Atualiza contador de tempo
            if hasattr(self, 'recording_start_time'):
                elapsed = (datetime.now() - self.recording_start_time).total_seconds()
                self.instruction.config(text=f"🎵 Gravando... {int(elapsed)}s", bg=COLORS['danger'], fg="white")
            else:
                self.recording_start_time = datetime.now()
            
            # Obtém níveis de áudio se disponível
            if self.audio_recorder and hasattr(self.audio_recorder, 'get_audio_levels'):
                levels = self.audio_recorder.get_audio_levels()
                if levels:
                    # Usa o último nível para animar o microfone
                    level = min(levels[-1] / 1000, 1.0)  # Normaliza o nível
                    # Ajusta a velocidade da animação baseado no nível
                    delay = 300 if level > 0.5 else 500
                    self.audio_level_job = self.after(delay, self.animate_recording)
                else:
                    self.audio_level_job = self.after(500, self.animate_recording)
            else:
                self.audio_level_job = self.after(500, self.animate_recording)
        else:
            # Restaura cor original ao parar
            for item in self.mic_canvas.find_all():
                self.mic_canvas.itemconfig(item, fill=COLORS['secondary'])
            if hasattr(self, 'recording_start_time'):
                delattr(self, 'recording_start_time')
    
    def animate_progress(self):
        """Anima o indicador de progresso durante o processamento"""
        dots = ". " * (self.progress_dots % 4)  # Usa espaço não quebrável
        self.progress_dots += 1
        current_text = self.instruction.cget("text")
        base_text = current_text.split(".")[0] if "." in current_text else current_text
        self.instruction.config(text=f"{base_text}{dots}")
        self.progress_animation_job = self.after(500, self.animate_progress)
    
    def stop_progress_animation(self):
        """Para a animação de progresso"""
        if self.progress_animation_job:
            self.after_cancel(self.progress_animation_job)
            self.progress_animation_job = None
        self.progress_dots = 0
        # Esconde botão de cancelar
        self.cancel_btn.pack_forget()
    
    def cancel_processing(self):
        """Cancela o processamento em andamento"""
        self.stop_progress_animation()
        self.instruction.config(text="Processamento cancelado", bg=COLORS['secondary'], fg=COLORS['fg'])
        self.record_btn.config(text="Iniciar Gravação", bg=COLORS['primary'], state="normal")
        
        # Limpa recursos
        if self.audio_recorder:
            try:
                self.audio_recorder.cleanup()
            except:
                pass
            self.audio_recorder = None
    
    def reset(self):
        self.is_recording = False
        self.record_btn.config(text="Iniciar Gravação", bg=COLORS['primary'], state="normal")
        self.instruction.config(text="Fale os nomes dos participantes", bg=COLORS['bg'], fg=COLORS['muted'])
        self.transcription_text = ""
        # Restaura cor do microfone
        for item in self.mic_canvas.find_all():
            self.mic_canvas.itemconfig(item, fill=COLORS['secondary'])
        if self.audio_recorder:
            self.audio_recorder.cleanup()
            self.audio_recorder = None
        if self.audio_level_job:
            self.after_cancel(self.audio_level_job)
            self.audio_level_job = None
        if self.progress_animation_job:
            self.after_cancel(self.progress_animation_job)
            self.progress_animation_job = None

class ConfirmationScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        self.participants = []
        
        # Container principal
        container = tk.Frame(self, bg=COLORS['bg'])
        container.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Título
        title = tk.Label(
            container,
            text="Participantes Identificados",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS['bg'],
            fg=COLORS['fg']
        )
        title.pack(pady=(0, 5))
        
        # Instrução sobre ícones
        instruction = tk.Label(
            container,
            text="✏️ = nome corrigido automaticamente",
            font=("Segoe UI", 8),
            bg=COLORS['bg'],
            fg=COLORS['muted']
        )
        instruction.pack(pady=(0, 5))
        
        # Label para mostrar a transcrição
        self.transcription_label = tk.Label(
            container,
            text="",
            font=("Segoe UI", 8),
            bg=COLORS['bg'],
            fg=COLORS['muted'],
            wraplength=280
        )
        self.transcription_label.pack(pady=(0, 10))
        
        # Frame para lista customizada
        self.list_container = tk.Frame(container, bg=COLORS['secondary'])
        self.list_container.pack(fill="both", expand=True, pady=5)
        
        # Canvas com scrollbar para lista customizada
        canvas = tk.Canvas(self.list_container, bg=COLORS['secondary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.list_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=COLORS['secondary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame para botões
        button_frame = tk.Frame(container, bg=COLORS['bg'])
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Botão Voltar
        back_btn = tk.Button(
            button_frame,
            text="← Regravar",
            font=("Segoe UI", 10),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            command=lambda: controller.show_frame("ParticipantsScreen"),
            cursor="hand2"
        )
        back_btn.pack(side="left")
        
        # Botão Finalizar
        finish_btn = tk.Button(
            button_frame,
            text="Finalizar ✓",
            font=("Segoe UI", 10),
            bg=COLORS['success'],
            fg="white",
            command=self.finish_meeting,
            cursor="hand2"
        )
        finish_btn.pack(side="right")
    
    def reset(self):
        # Limpa o frame scrollable
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        participants = self.controller.shared_data.get('participants', [])
        transcription = self.controller.shared_data.get('participants_transcription', '')
        
        # Mostra a transcrição original
        if transcription:
            self.transcription_label.config(text=f'Transcrição: "{transcription}"')
        else:
            self.transcription_label.config(text="")
        
        # Mostra os participantes identificados
        if participants:
            for i, participant in enumerate(participants):
                # Frame para cada participante
                participant_frame = tk.Frame(self.scrollable_frame, bg=COLORS['secondary'])
                participant_frame.pack(fill="x", padx=10, pady=5)
                
                if isinstance(participant, dict):
                    # Ícone de status
                    icon = "✏️" if participant['corrigido'] else "✓"
                    icon_label = tk.Label(
                        participant_frame,
                        text=icon,
                        font=("Segoe UI", 10),
                        bg=COLORS['secondary'],
                        fg=COLORS['warning'] if participant['corrigido'] else COLORS['success']
                    )
                    icon_label.pack(side="left", padx=(0, 5))
                    
                    # Nome corrigido (principal)
                    name_label = tk.Label(
                        participant_frame,
                        text=participant['correto'],
                        font=("Segoe UI", 10, "bold"),
                        bg=COLORS['secondary'],
                        fg=COLORS['fg']
                    )
                    name_label.pack(side="left")
                    
                    # Se foi corrigido, mostra o original e a similaridade
                    if participant['corrigido']:
                        # Nome original
                        original_label = tk.Label(
                            participant_frame,
                            text=f" (original: {participant['original']})",
                            font=("Segoe UI", 8),
                            bg=COLORS['secondary'],
                            fg=COLORS['muted']
                        )
                        original_label.pack(side="left")
                        
                        # Similaridade
                        similarity_label = tk.Label(
                            participant_frame,
                            text=f" {participant['similaridade']*100:.1f}%",
                            font=("Segoe UI", 8),
                            bg=COLORS['secondary'],
                            fg=COLORS['primary']
                        )
                        similarity_label.pack(side="right")
                else:
                    # Fallback para formato antigo (string simples)
                    icon_label = tk.Label(
                        participant_frame,
                        text="✓",
                        font=("Segoe UI", 10),
                        bg=COLORS['secondary'],
                        fg=COLORS['success']
                    )
                    icon_label.pack(side="left", padx=(0, 5))
                    
                    name_label = tk.Label(
                        participant_frame,
                        text=participant,
                        font=("Segoe UI", 10),
                        bg=COLORS['secondary'],
                        fg=COLORS['fg']
                    )
                    name_label.pack(side="left")
        else:
            # Nenhum participante identificado
            no_participant_label = tk.Label(
                self.scrollable_frame,
                text="Nenhum participante identificado",
                font=("Segoe UI", 10),
                bg=COLORS['secondary'],
                fg=COLORS['muted']
            )
            no_participant_label.pack(padx=10, pady=10)
    
    def transcribe_meeting_audio(self, audio_path):
        """Transcreve o áudio completo da reunião"""
        if not audio_path or not os.path.exists(audio_path):
            print(f"Arquivo de áudio não encontrado: {audio_path}")
            return None
        
        try:
            # Verifica o tamanho do arquivo
            file_size = os.path.getsize(audio_path)
            print(f"Transcrevendo arquivo: {audio_path}")
            print(f"Tamanho do arquivo: {file_size} bytes")
            
            if file_size == 0:
                print("Arquivo de áudio vazio!")
                return None
            
            # Cria uma instância temporária do AudioRecorder para transcrição
            if AudioRecorder:
                temp_recorder = AudioRecorder()
                print("Iniciando transcrição com Whisper API...")
                transcription = temp_recorder.transcribe_audio(audio_path)
                
                if transcription:
                    print(f"Transcrição concluída! Tamanho: {len(transcription)} caracteres")
                    print(f"Primeiros 100 caracteres: {transcription[:100]}...")
                else:
                    print("Transcrição retornou vazia")
                
                return transcription
            else:
                print("AudioRecorder não disponível")
                return None
                
        except Exception as e:
            print(f"Erro ao transcrever áudio: {e}")
            return None
    
    def finish_meeting(self):
        # Desabilita botões durante processamento
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state="disabled")
        
        # Mostra indicador de processamento
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "🔄 Processando transcrição...")
        self.listbox.insert(tk.END, "⏳ Isso pode levar alguns segundos...")
        self.listbox.itemconfig(0, fg=COLORS['warning'])
        self.listbox.itemconfig(1, fg=COLORS['muted'])
        self.update()
        
        # Salva os dados da reunião
        data = self.controller.shared_data
        meeting_id = self.controller.get_next_meeting_id()
        
        # Cria o nome do arquivo
        timestamp = datetime.now()
        filename = f"{meeting_id:02d}_{data['responsible']}_{timestamp.strftime('%d_%m_%Y_%H_%M')}.txt"
        filepath = os.path.join("reunioes", filename)
        
        # Calcula a duração
        duration_seconds = int(data.get('duration', 0))
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Calcula horário de início e fim
        start_time = data.get('start_time', timestamp)
        end_time = start_time + timedelta(seconds=duration_seconds) if duration_seconds > 0 else timestamp
        
        # Atualiza status para transcrição
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "🎵 Transcrevendo áudio da reunião...")
        self.listbox.itemconfig(0, fg=COLORS['primary'])
        self.update()
        
        # Transcreve o áudio da reunião
        transcription = self.transcribe_meeting_audio(data.get('audio_path'))
        
        # Atualiza status para salvamento
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "💾 Salvando reunião...")
        self.listbox.itemconfig(0, fg=COLORS['success'])
        self.update()
        
        # Monta o conteúdo do arquivo
        content = f"""REUNIÃO - ID: {meeting_id:02d}
Data: {timestamp.strftime('%d/%m/%Y')}
Horário: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}
Duração: {duration_str}
Responsável: {data['responsible']}
Objetivo: {data['objective']}

PARTICIPANTES:
"""
        
        # Adiciona os participantes
        for participant in data.get('participants', []):
            if isinstance(participant, dict):
                # Usa o nome corrigido
                content += f"- {participant['correto']}\n"
            else:
                # Fallback para formato antigo
                content += f"- {participant}\n"
        
        # Adiciona a transcrição
        content += "\nTRANSCRIÇÃO:\n"
        if transcription:
            content += transcription
        else:
            content += "[Erro ao transcrever o áudio da reunião]"
        
        # Salva o arquivo
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Mostra sucesso
            self.listbox.delete(0, tk.END)
            self.listbox.insert(tk.END, "✅ Reunião salva com sucesso!")
            self.listbox.insert(tk.END, f"📄 {filename}")
            self.listbox.itemconfig(0, fg=COLORS['success'])
            self.listbox.itemconfig(1, fg=COLORS['muted'])
            self.update()
            
            # Aguarda um momento antes de mostrar o diálogo
            self.after(1000, lambda: messagebox.showinfo(
                "Sucesso",
                f"Reunião finalizada!\nArquivo: {filename}\n\nDados salvos com sucesso."
            ))
        except Exception as e:
            # Mostra erro
            self.listbox.delete(0, tk.END)
            self.listbox.insert(tk.END, "❌ Erro ao salvar reunião")
            self.listbox.itemconfig(0, fg=COLORS['danger'])
            self.update()
            
            messagebox.showerror(
                "Erro",
                f"Erro ao salvar o arquivo: {str(e)}"
            )
        
        # Reinicia para nova reunião
        self.controller.reset_data()
        self.controller.show_frame("StartScreen")

class ViewMeetingsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        
        # Container principal
        container = tk.Frame(self, bg=COLORS['bg'])
        container.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Título
        title = tk.Label(
            container,
            text="Reuniões Gravadas",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS['bg'],
            fg=COLORS['fg']
        )
        title.pack(pady=(0, 10))
        
        # Frame para lista
        list_frame = tk.Frame(container, bg=COLORS['secondary'])
        list_frame.pack(fill="both", expand=True, pady=5)
        
        # Scrollbar e Listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 9),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            selectbackground=COLORS['primary'],
            yscrollcommand=scrollbar.set,
            height=8
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind('<Double-Button-1>', self.open_meeting)
        
        # Frame para botões
        button_frame = tk.Frame(container, bg=COLORS['bg'])
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Botão Voltar
        back_btn = tk.Button(
            button_frame,
            text="← Voltar",
            font=("Segoe UI", 10),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            command=lambda: controller.show_frame("StartScreen"),
            cursor="hand2"
        )
        back_btn.pack(side="left")
        
        # Botão Abrir
        self.open_btn = tk.Button(
            button_frame,
            text="Abrir Reunião",
            font=("Segoe UI", 10),
            bg=COLORS['primary'],
            fg="white",
            command=self.open_meeting,
            cursor="hand2"
        )
        self.open_btn.pack(side="right")
        
        # Armazena os arquivos
        self.meeting_files = []
    
    def reset(self):
        """Atualiza a lista de reuniões"""
        self.listbox.delete(0, tk.END)
        self.meeting_files = []
        
        if os.path.exists('reunioes'):
            files = [f for f in os.listdir('reunioes') if f.endswith('.txt')]
            files.sort(reverse=True)  # Mais recentes primeiro
            
            for filename in files:
                try:
                    # Lê as informações básicas do arquivo
                    filepath = os.path.join('reunioes', filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Extrai informações do cabeçalho
                    meeting_id = ""
                    responsible = ""
                    date = ""
                    duration = ""
                    
                    for line in lines[:10]:  # Lê apenas as primeiras linhas
                        if line.startswith("REUNIÃO - ID:"):
                            meeting_id = line.split(":")[1].strip()
                        elif line.startswith("Data:"):
                            date = line.split(":")[1].strip()
                        elif line.startswith("Responsável:"):
                            responsible = line.split(":")[1].strip()
                        elif line.startswith("Duração:"):
                            duration = line.split(":")[1].strip()
                    
                    # Adiciona à lista
                    display_text = f"ID {meeting_id} | {responsible} | {date} | {duration}"
                    self.listbox.insert(tk.END, display_text)
                    self.meeting_files.append(filename)
                    
                except Exception as e:
                    print(f"Erro ao ler arquivo {filename}: {e}")
        
        # Desabilita o botão abrir se não houver seleção
        if not self.meeting_files:
            self.open_btn.config(state="disabled")
        else:
            self.open_btn.config(state="normal")
    
    def open_meeting(self, event=None):
        """Abre a reunião selecionada"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione uma reunião.")
            return
        
        index = selection[0]
        filename = self.meeting_files[index]
        filepath = os.path.join('reunioes', filename)
        
        # Abre a tela de visualização
        self.controller.current_meeting_file = filepath
        self.controller.show_frame("MeetingDetailScreen")

class MeetingDetailScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        
        # Container principal
        container = tk.Frame(self, bg=COLORS['bg'])
        container.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Título
        self.title_label = tk.Label(
            container,
            text="Detalhes da Reunião",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS['bg'],
            fg=COLORS['fg']
        )
        self.title_label.pack(pady=(0, 5))
        
        # Frame para texto
        text_frame = tk.Frame(container, bg=COLORS['secondary'])
        text_frame.pack(fill="both", expand=True, pady=5)
        
        # Scrollbar e Text widget
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.text_widget = tk.Text(
            text_frame,
            font=("Segoe UI", 9),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            padx=5,
            pady=5
        )
        self.text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.text_widget.yview)
        
        # Torna o texto somente leitura
        self.text_widget.config(state="disabled")
        
        # Botão Voltar
        back_btn = tk.Button(
            container,
            text="← Voltar",
            font=("Segoe UI", 10),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            command=lambda: controller.show_frame("ViewMeetingsScreen"),
            cursor="hand2"
        )
        back_btn.pack(pady=(10, 0))
    
    def reset(self):
        """Carrega o conteúdo da reunião"""
        filepath = self.controller.current_meeting_file
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Atualiza o texto
                self.text_widget.config(state="normal")
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(1.0, content)
                self.text_widget.config(state="disabled")
                
                # Extrai o ID da reunião para o título
                for line in content.split('\n'):
                    if line.startswith("REUNIÃO - ID:"):
                        meeting_id = line.split(":")[1].strip()
                        self.title_label.config(text=f"Reunião ID: {meeting_id}")
                        break
                        
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir arquivo: {str(e)}")
                self.controller.show_frame("ViewMeetingsScreen")

class App(tk.Tk):
    """Aplicação principal do Gravador de Reuniões"""
    
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.title("Gravador de Reuniões")
        self.geometry("320x240")
        self.resizable(False, False)
        self.configure(bg=COLORS['bg'])
        
        # Centraliza a janela na tela
        self.center_window()
        
        # Container principal
        self.container = tk.Frame(self, bg=COLORS['bg'])
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Dicionário para armazenar as telas
        self.frames = {}
        
        # Dados compartilhados entre telas
        self.shared_data = {
            'responsible': '',
            'objective': '',
            'duration': 0,
            'participants': [],
            'audio_path': None,
            'transcription': '',
            'meeting_id': 1
        }
        
        # Cria todas as telas
        for F in (StartScreen, ResponsibleScreen, ObjectiveScreen, 
                  RecordingScreen, ParticipantsScreen, ConfirmationScreen,
                  ViewMeetingsScreen, MeetingDetailScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Mostra a tela inicial
        self.show_frame("StartScreen")
        
        # Cria diretório de reuniões se não existir
        os.makedirs("reunioes", exist_ok=True)
        
        # Variável para armazenar o arquivo atual sendo visualizado
        self.current_meeting_file = None
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_frame(self, page_name):
        """Mostra uma tela específica"""
        frame = self.frames[page_name]
        frame.tkraise()
        
        # Chama o método de reset da tela se existir
        if hasattr(frame, 'reset'):
            frame.reset()
    
    def get_next_meeting_id(self):
        """Obtém o próximo ID de reunião disponível"""
        if not os.path.exists('reunioes'):
            return 1
            
        existing_files = [f for f in os.listdir('reunioes') if f.endswith('.txt')]
        if not existing_files:
            return 1
            
        # Extrai os IDs dos arquivos existentes
        ids = []
        for filename in existing_files:
            try:
                id_str = filename.split('_')[0]
                ids.append(int(id_str))
            except (ValueError, IndexError):
                continue
                
        return max(ids) + 1 if ids else 1
    
    def reset_data(self):
        """Reinicia os dados para nova reunião"""
        self.shared_data = {
            'responsible': '',
            'objective': '',
            'duration': 0,
            'participants': [],
            'audio_path': None,
            'transcription': '',
            'meeting_id': self.get_next_meeting_id()
        }

def main():
    """Função principal"""
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()