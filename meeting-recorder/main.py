#!/usr/bin/env python3
"""
Aplicativo de Gravação de Reuniões - VERSÃO CORRIGIDA
Resolução: 320x240 pixels
Design minimalista e profissional
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys
from datetime import datetime
import time
import threading

# Carrega variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Adiciona o diretório atual ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Verifica se a API key foi carregada
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("AVISO: OPENAI_API_KEY não encontrada no arquivo .env")
    print("A transcrição de áudio não funcionará sem a API key.")
else:
    print(f"API Key carregada com sucesso! Primeiros 10 caracteres: {OPENAI_API_KEY[:10]}...")

# Tenta importar o AudioRecorder
try:
    from audio_recorder_standalone import AudioRecorder
    print("AudioRecorder importado com sucesso!")
except ImportError as e:
    print(f"Erro ao importar AudioRecorder: {e}")
    print("A gravação de áudio não funcionará. Instale as dependências necessárias.")
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

import json
import difflib

def load_funcionarios():
    """Carrega a lista de funcionários do arquivo JSON"""
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'data', 'funcionarios.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Arquivo funcionarios.json não encontrado. Criando arquivo de exemplo...")
        # Cria um arquivo de exemplo
        os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
        example_data = {
            "funcionarios": [
                {"id": 1, "nome": "Mateus Estival", "departamento": "TI", "cargo": "Desenvolvedor"},
                {"id": 2, "nome": "João Silva", "departamento": "Vendas", "cargo": "Gerente"},
                {"id": 3, "nome": "Maria Santos", "departamento": "RH", "cargo": "Analista"},
                {"id": 4, "nome": "Pedro Oliveira", "departamento": "Financeiro", "cargo": "Coordenador"},
                {"id": 5, "nome": "Ana Costa", "departamento": "Marketing", "cargo": "Designer"}
            ]
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(example_data, f, ensure_ascii=False, indent=2)
        return example_data
    except Exception as e:
        print(f"Erro ao carregar funcionarios.json: {e}")
        return {"funcionarios": []}

def validate_names(transcribed_names):
    """Valida e corrige nomes usando fuzzy matching"""
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
        
        # Botão Ver Reuniões (se houver reuniões salvas)
        self.check_and_add_view_button(container)
        
        # Versão
        version = tk.Label(
            self,
            text="v1.0.0",
            font=("Segoe UI", 8),
            bg=COLORS['bg'],
            fg=COLORS['muted']
        )
        version.pack(side="bottom", pady=5)
    
    def check_and_add_view_button(self, container):
        """Verifica se há reuniões salvas e adiciona o botão Ver Reuniões"""
        reunioes_dir = os.path.join(os.path.dirname(__file__), 'reunioes')
        if os.path.exists(reunioes_dir):
            files = [f for f in os.listdir(reunioes_dir) if f.endswith('.txt')]
            meeting_count = len(files)
            
            if meeting_count > 0:
                # Botão com cores vibrantes e texto claro
                view_btn = tk.Button(
                    container,
                    text=f"Ver Reuniões ({meeting_count})",
                    font=("Segoe UI", 11, "bold"),
                    bg=COLORS['primary'],  # Azul vibrante
                    fg="white",            # Texto branco
                    bd=2,                  # Borda maior
                    relief="raised",       # Relevo para destaque
                    padx=15,
                    pady=8,
                    command=lambda: self.controller.show_frame("ViewMeetingsScreen"),
                    cursor="hand2",
                    activebackground=COLORS['success'],  # Verde ao clicar
                    activeforeground="white"
                )
                view_btn.pack(pady=(15, 0))
            else:
                # Botão desabilitado quando não há reuniões
                view_btn = tk.Button(
                    container,
                    text="Ver Reuniões (0)",
                    font=("Segoe UI", 10),
                    bg=COLORS['secondary'],
                    fg=COLORS['muted'],
                    bd=1,
                    relief="flat",
                    state="disabled"
                )
                view_btn.pack(pady=(15, 0))
    
    def on_click(self, event):
        self.controller.show_frame("ResponsibleScreen")
    
    def reset(self):
        """Atualiza o botão de ver reuniões quando a tela é mostrada"""
        # Remove o botão antigo se existir
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button) and "Ver Reuniões" in child.cget("text"):
                        child.destroy()
        
        # Adiciona o botão atualizado
        container = self.winfo_children()[0]  # Pega o container principal
        self.check_and_add_view_button(container)

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
        self.audio_recorder = None
        
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
            if self.audio_recorder and AudioRecorder:
                self.audio_recorder.pause_recording()
        else:
            self.pause_btn.config(text="⏸")
            self.status_label.config(text="GRAVANDO", fg=COLORS['danger'])
            if self.audio_recorder and AudioRecorder:
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
            if self.audio_recorder and AudioRecorder and hasattr(self.audio_recorder, 'get_audio_level'):
                # Usa o nível real de áudio
                level = self.audio_recorder.get_audio_level()
                for i, bar in enumerate(self.audio_bars):
                    # Cria uma onda baseada no nível de áudio
                    import math
                    wave_offset = math.sin((i + level * 10) * 0.3) * 20
                    height = max(5, min(40, level * 100 + wave_offset))
                    self.audio_canvas.coords(bar, i * 6, 60 - height, i * 6 + 4, 60)
            else:
                # Animação simulada se não houver gravação real
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
        
        # Para a gravação de áudio e salva o arquivo
        if self.audio_recorder and AudioRecorder:
            print("Finalizando gravação...")
            audio_file = self.audio_recorder.stop_recording()
            if audio_file:
                self.controller.shared_data['audio_path'] = audio_file
                print(f"Áudio salvo em: {audio_file}")
                # Verifica o tamanho do arquivo
                if os.path.exists(audio_file):
                    size = os.path.getsize(audio_file)
                    print(f"Tamanho do arquivo: {size} bytes")
        
        self.controller.show_frame("ParticipantsScreen")
    
    def reset(self):
        self.is_recording = True
        self.is_paused = False
        self.start_time = datetime.now()
        self.pause_btn.config(text="⏸")
        self.status_label.config(text="GRAVANDO", fg=COLORS['danger'])
        
        # Inicia a gravação de áudio real
        if AudioRecorder:
            try:
                self.audio_recorder = AudioRecorder()
                self.audio_recorder.start_recording()
                print("Gravação de áudio iniciada com sucesso")
            except Exception as e:
                print(f"Erro ao iniciar gravação de áudio: {e}")
                self.audio_recorder = None
        
        self.update_timer()
        self.animate_audio()

class ParticipantsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        self.is_recording = False
        self.audio_recorder = None
        self.recording_start_time = None
        self.animation_running = False
        self.processing = False
        
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
        self.mic_body = self.mic_canvas.create_oval(25, 10, 55, 50, fill=COLORS['secondary'], outline=COLORS['fg'], width=2)
        self.mic_base = self.mic_canvas.create_rectangle(35, 45, 45, 60, fill=COLORS['secondary'], outline=COLORS['fg'], width=2)
        self.mic_arc = self.mic_canvas.create_arc(20, 40, 60, 65, start=0, extent=-180, style="arc", outline=COLORS['fg'], width=2)
        
        # Instrução
        self.instruction = tk.Label(
            container,
            text="Fale os nomes dos participantes",
            font=("Segoe UI", 10),
            bg=COLORS['bg'],
            fg=COLORS['muted']
        )
        self.instruction.pack(pady=5)
        
        # Botão de gravação com visual melhorado
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
            cursor="hand2",
            activebackground="#5ba0f2",      # Cor mais clara ao clicar
            activeforeground="white"
        )
        self.record_btn.pack(pady=10)
    
    def toggle_recording(self):
        if self.processing:
            return  # Ignora cliques durante processamento
            
        if not self.is_recording:
            self.is_recording = True
            self.recording_start_time = time.time()
            self.record_btn.config(text="Parar Gravação", bg=COLORS['danger'], state="normal")
            self.instruction.config(text="🎤 Gravando... Fale os nomes", fg=COLORS['danger'], bg=COLORS['bg'])
            
            # Inicia a gravação de áudio real
            if AudioRecorder:
                try:
                    self.audio_recorder = AudioRecorder()
                    self.audio_recorder.start_recording()
                    self.animate_recording()
                except Exception as e:
                    print(f"Erro ao iniciar gravação: {e}")
                    self.stop_recording()
            else:
                # Simulação se não houver AudioRecorder
                self.animate_recording()
        else:
            self.stop_recording()
    
    def animate_recording(self):
        """Anima o microfone durante a gravação com feedback visual do áudio"""
        if self.is_recording and not self.processing:
            # Tempo decorrido
            elapsed = int(time.time() - self.recording_start_time)
            self.instruction.config(text=f"🎵 Gravando... {elapsed}s", fg=COLORS['danger'])
            
            # Anima o microfone baseado no nível de áudio
            if self.audio_recorder and hasattr(self.audio_recorder, 'get_audio_level'):
                level = self.audio_recorder.get_audio_level()
                # Muda a cor do microfone baseado no nível
                if level > 0.5:
                    color = COLORS['danger']  # Vermelho para som alto
                else:
                    color = COLORS['primary']  # Azul para som baixo
                self.mic_canvas.itemconfig(self.mic_body, fill=color)
            else:
                # Animação simples se não houver nível de áudio
                import random
                color = COLORS['danger'] if random.random() > 0.5 else COLORS['secondary']
                self.mic_canvas.itemconfig(self.mic_body, fill=color)
            
            # Continua a animação
            self.animation_running = self.after(100, self.animate_recording)
    
    def stop_recording(self):
        self.is_recording = False
        self.processing = True
        
        # Para a animação
        if self.animation_running:
            self.after_cancel(self.animation_running)
            self.animation_running = False
        
        # Restaura cor do microfone
        self.mic_canvas.itemconfig(self.mic_body, fill=COLORS['secondary'])
        
        # Atualiza interface para mostrar processamento
        self.record_btn.config(text="Processando...", bg=COLORS['warning'], state="disabled")
        self.instruction.config(text="🔄 Transcrevendo áudio...", fg=COLORS['warning'])
        
        # Para a gravação e pega o arquivo
        if self.audio_recorder and AudioRecorder:
            try:
                audio_file = self.audio_recorder.stop_recording()
                if audio_file and os.path.exists(audio_file):
                    # Faz a transcrição em thread separada com tratamento de erro melhorado
                    threading.Thread(target=self.transcribe_and_process, args=(audio_file,), daemon=True).start()
                else:
                    self.processing = False
                    self.instruction.config(text="❌ Erro na gravação", fg=COLORS['danger'])
                    self.record_btn.config(text="Tentar Novamente", bg=COLORS['primary'], state="normal")
                    messagebox.showerror("Erro", "Não foi possível gravar o áudio.")
            except Exception as e:
                print(f"Erro ao parar gravação: {e}")
                self.processing = False
                self.instruction.config(text="❌ Erro na gravação", fg=COLORS['danger'])
                self.record_btn.config(text="Tentar Novamente", bg=COLORS['primary'], state="normal")
    
    def transcribe_and_process(self, audio_file):
        """Transcreve o áudio e processa os participantes com tratamento de erro melhorado"""
        transcription = None
        try:
            # Faz a transcrição
            transcription = self.audio_recorder.transcribe_audio(audio_file)
        except Exception as e:
            print(f"Erro na transcrição: {e}")
            transcription = None
        
        # Limpa o arquivo temporário com delay para evitar erro de permissão
        try:
            # Aguarda um pouco antes de limpar para garantir que o arquivo foi liberado
            time.sleep(0.5)
            if hasattr(self.audio_recorder, 'cleanup'):
                self.audio_recorder.cleanup()
        except Exception as e:
            print(f"Aviso: Não foi possível limpar arquivo temporário: {e}")
        
        # Atualiza a UI na thread principal
        self.after(0, lambda: self.process_participants(transcription))
    
    def process_participants(self, transcription):
        """Processa a transcrição para extrair nomes dos participantes"""
        self.processing = False
        
        if not transcription:
            self.instruction.config(text="❌ Não foi possível transcrever.", fg=COLORS['danger'])
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
        self.instruction.config(text="🔍 Identificando participantes...", fg=COLORS['primary'])
        
        # Mostra a transcrição temporariamente
        self.transcription_text = transcription
        print(f"Transcrição: {transcription}")
        
        # Extrai nomes da transcrição
        participants = self.extract_names(transcription)
        
        if participants:
            # Valida e corrige os nomes usando fuzzy matching
            validated_participants = validate_names(participants)
            self.controller.shared_data['participants'] = validated_participants
            self.controller.shared_data['participants_transcription'] = transcription
            
            # Atualiza interface com sucesso
            count = len(validated_participants)
            self.instruction.config(
                text=f"✅ {count} participante(s) identificado(s)!", 
                fg=COLORS['success']
            )
            
            # Avança após um breve delay
            self.after(1500, lambda: self.controller.show_frame("ConfirmationScreen"))
        else:
            # Nenhum participante detectado
            self.instruction.config(
                text="⚠️ Nenhum participante identificado.", 
                fg=COLORS['warning']
            )
            self.record_btn.config(text="Tentar Novamente", bg=COLORS['primary'], state="normal")
            
            # Mostra ajuda
            messagebox.showinfo(
                "Dica",
                f"Nenhum nome foi identificado na transcrição.\n\n" +
                f"Transcrição: \"{transcription[:100]}...\"\n\n" +
                "Tente falar claramente, por exemplo:\n" +
                "- 'Os participantes são João Silva, Maria Santos e Pedro Oliveira'\n" +
                "- 'Presentes: Ana Costa e Carlos Ferreira'\n" +
                "- 'João Silva, Maria Santos, Pedro Oliveira'"
            )
    
    def extract_names(self, transcription):
        """Extrai nomes próprios da transcrição de forma inteligente"""
        import re
        
        # Remove pontuação e normaliza
        text = transcription.replace(',', ' ').replace('.', ' ').replace(';', ' ')
        
        # Padrões para identificar contexto de nomes
        patterns = [
            r'participantes?\s+(?:são|sao|é|e)?\s*(.*)',
            r'presentes?\s+(?:estão|estao|são|sao)?\s*(.*)',
            r'reunião\s+com\s+(.*)',
            r'presença\s+de\s+(.*)',
            r'com\s+a\s+presença\s+de\s+(.*)'
        ]
        
        names_text = ""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                names_text = match.group(1)
                break
        
        # Se não encontrou padrão, usa o texto todo
        if not names_text:
            names_text = text
        
        # Identifica palavras que podem ser nomes (começam com maiúscula)
        words = names_text.split()
        potential_names = []
        i = 0
        
        while i < len(words):
            word = words[i].strip()
            # Verifica se é uma palavra capitalizada
            if word and word[0].isupper() and len(word) > 2:
                # Pode ser início de um nome
                name_parts = [word]
                
                # Verifica palavras seguintes para nomes compostos
                j = i + 1
                while j < len(words):
                    next_word = words[j].strip()
                    # Conectivos comuns em nomes
                    if next_word.lower() in ['de', 'da', 'do', 'dos', 'das', 'e']:
                        name_parts.append(next_word)
                        j += 1
                    elif next_word and next_word[0].isupper():
                        name_parts.append(next_word)
                        j += 1
                    else:
                        break
                
                # Forma o nome completo
                full_name = ' '.join(name_parts)
                if self.is_valid_name(full_name):
                    potential_names.append(full_name)
                
                i = j
            else:
                i += 1
        
        # Remove duplicatas mantendo a ordem
        seen = set()
        unique_names = []
        for name in potential_names:
            if name.lower() not in seen:
                seen.add(name.lower())
                unique_names.append(name)
        
        return unique_names
    
    def is_valid_name(self, name):
        """Verifica se uma string é um nome válido"""
        # Lista de palavras comuns que não são nomes
        common_words = {
            'reunião', 'participantes', 'presentes', 'pessoas', 'equipe',
            'todos', 'estão', 'são', 'foram', 'serão', 'com', 'para',
            'aqui', 'hoje', 'agora', 'sim', 'não', 'ok', 'okay'
        }
        
        # Verifica se não é uma palavra comum
        if name.lower() in common_words:
            return False
        
        # Verifica se tem pelo menos 2 partes (nome e sobrenome)
        parts = name.split()
        if len(parts) < 2:
            return False
        
        # Verifica se não tem números
        if any(char.isdigit() for char in name):
            return False
        
        return True
    
    def reset(self):
        self.is_recording = False
        self.processing = False
        self.record_btn.config(text="Iniciar Gravação", bg=COLORS['primary'], state="normal")
        self.instruction.config(text="Fale os nomes dos participantes", fg=COLORS['muted'], bg=COLORS['bg'])
        self.mic_canvas.itemconfig(self.mic_body, fill=COLORS['secondary'])

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
        
        # Frame para lista
        list_frame = tk.Frame(container, bg=COLORS['secondary'])
        list_frame.pack(fill="both", expand=True, pady=5)
        
        # Canvas e Scrollbar para lista customizada
        self.canvas = tk.Canvas(list_frame, bg=COLORS['secondary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS['secondary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Label para mostrar a transcrição original
        self.transcription_label = tk.Label(
            container,
            text="",
            font=("Segoe UI", 8),
            bg=COLORS['bg'],
            fg=COLORS['muted'],
            wraplength=280
        )
        self.transcription_label.pack(pady=(5, 5))
        
        # Frame para botões
        button_frame = tk.Frame(container, bg=COLORS['bg'])
        button_frame.pack(fill="x", pady=(5, 0))
        
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
        
        # Label de status
        self.status_label = tk.Label(
            container,
            text="",
            font=("Segoe UI", 9),
            bg=COLORS['bg'],
            fg=COLORS['muted']
        )
        self.status_label.pack(pady=(5, 0))
    
    def create_participant_item(self, participant_data):
        """Cria um item visual para cada participante"""
        frame = tk.Frame(self.scrollable_frame, bg=COLORS['secondary'], pady=5)
        frame.pack(fill="x", padx=10, pady=2)
        
        # Ícone de status
        if participant_data['corrigido']:
            icon = "✏️"
            name_color = COLORS['primary']
        else:
            icon = "✓"
            name_color = COLORS['success']
        
        # Label com ícone e nome
        main_label = tk.Label(
            frame,
            text=f"{icon} {participant_data['correto']}",
            font=("Segoe UI", 11),
            bg=COLORS['secondary'],
            fg=name_color
        )
        main_label.pack(anchor="w")
        
        # Se foi corrigido, mostra o nome original
        if participant_data['corrigido']:
            original_label = tk.Label(
                frame,
                text=f"   (detectado: {participant_data['original']})",
                font=("Segoe UI", 9),
                bg=COLORS['secondary'],
                fg=COLORS['muted']
            )
            original_label.pack(anchor="w")
            
            # Mostra similaridade
            similarity_percent = int(participant_data['similaridade'] * 100)
            similarity_label = tk.Label(
                frame,
                text=f"   Similaridade: {similarity_percent}%",
                font=("Segoe UI", 8),
                bg=COLORS['secondary'],
                fg=COLORS['muted']
            )
            similarity_label.pack(anchor="w")
    
    def reset(self):
        # Limpa a lista anterior
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Pega os participantes validados
        participants = self.controller.shared_data.get('participants', [])
        
        if not participants:
            # Mostra mensagem quando não há participantes
            empty_label = tk.Label(
                self.scrollable_frame,
                text="Nenhum participante identificado",
                font=("Segoe UI", 10),
                bg=COLORS['secondary'],
                fg=COLORS['muted']
            )
            empty_label.pack(pady=20)
        else:
            # Cria item visual para cada participante
            for participant in participants:
                self.create_participant_item(participant)
        
        # Mostra a transcrição original se disponível
        transcription = self.controller.shared_data.get('participants_transcription', '')
        if transcription:
            self.transcription_label.config(
                text=f"Transcrição: \"{transcription[:100]}...\"" if len(transcription) > 100 else f"Transcrição: \"{transcription}\""
            )
        
        # Adiciona legenda
        if any(p['corrigido'] for p in participants):
            self.status_label.config(
                text="✏️ = nome corrigido automaticamente | ✓ = nome correto",
                fg=COLORS['muted']
            )
    
    def transcribe_meeting_audio(self):
        """Transcreve o áudio completo da reunião"""
        audio_path = self.controller.shared_data.get('audio_path')
        if not audio_path or not os.path.exists(audio_path):
            print("Arquivo de áudio não encontrado para transcrição")
            return ""
        
        try:
            # Verifica o tamanho do arquivo
            file_size = os.path.getsize(audio_path)
            print(f"Transcrevendo arquivo de áudio: {audio_path}")
            print(f"Tamanho do arquivo: {file_size} bytes")
            
            # Cria uma instância temporária do AudioRecorder para transcrever
            if AudioRecorder:
                temp_recorder = AudioRecorder()
                transcription = temp_recorder.transcribe_audio(audio_path)
                if transcription:
                    print(f"Transcrição concluída. Tamanho: {len(transcription)} caracteres")
                    print(f"Primeiros 100 caracteres: {transcription[:100]}...")
                    return transcription
                else:
                    print("Transcrição retornou vazia")
            else:
                print("AudioRecorder não disponível")
        except Exception as e:
            print(f"Erro ao transcrever áudio da reunião: {e}")
        
        return ""
    
    def finish_meeting(self):
        # Mostra indicador de processamento
        self.status_label.config(text="🔄 Processando transcrição...", fg=COLORS['primary'])
        self.update()
        
        # Transcreve o áudio completo da reunião
        full_transcription = self.transcribe_meeting_audio()
        
        # Salva os dados da reunião
        data = self.controller.shared_data
        meeting_id = self.controller.get_next_meeting_id()
        
        # Formata data e hora
        start_time = data.get('start_time', datetime.now())
        end_time = datetime.now()
        duration_seconds = data.get('duration', 0)
        
        # Converte duração para formato legível
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Formata participantes (apenas nomes corrigidos)
        participants_list = []
        for p in data.get('participants', []):
            participants_list.append(p['correto'])
        
        # Cria o conteúdo do arquivo
        content = f"""REUNIÃO - ID: {meeting_id:02d}
Data: {start_time.strftime('%d/%m/%Y')}
Horário: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}
Duração: {duration_str}
Responsável: {data.get('responsible', 'Não informado')}
Objetivo: {data.get('objective', 'Não informado')}

PARTICIPANTES:
"""
        for participant in participants_list:
            content += f"- {participant}\n"
        
        content += f"\nTRANSCRIÇÃO:\n{full_transcription if full_transcription else 'Transcrição não disponível'}\n"
        
        # Cria o nome do arquivo
        filename = f"{meeting_id:02d}_{data['responsible']}_{start_time.strftime('%d_%m_%Y_%H_%M')}.txt"
        
        # Salva o arquivo
        try:
            self.status_label.config(text="💾 Salvando reunião...", fg=COLORS['primary'])
            self.update()
            
            reunioes_dir = os.path.join(os.path.dirname(__file__), 'reunioes')
            os.makedirs(reunioes_dir, exist_ok=True)
            
            filepath = os.path.join(reunioes_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.status_label.config(text="✅ Reunião salva com sucesso!", fg=COLORS['success'])
            self.update()
            
            # Aguarda um momento antes de mostrar o diálogo
            self.after(1000, lambda: self.show_success_dialog(filename))
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar reunião: {str(e)}")
            self.controller.reset_data()
            self.controller.show_frame("StartScreen")
    
    def show_success_dialog(self, filename):
        """Mostra diálogo de sucesso e reseta a aplicação"""
        messagebox.showinfo(
            "Sucesso",
            f"Reunião finalizada!\nArquivo: {filename}\n\nDados salvos com sucesso."
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
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        title = tk.Label(
            container,
            text="Reuniões Salvas",
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
            font=("Segoe UI", 10),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            selectbackground=COLORS['primary'],
            yscrollcommand=scrollbar.set,
            height=8
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Bind duplo clique para abrir
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_meeting())
        
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
            cursor="hand2",
            state="disabled"
        )
        self.open_btn.pack(side="right")
        
        # Bind seleção para habilitar botão
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
    
    def reset(self):
        """Carrega a lista de reuniões quando a tela é mostrada"""
        self.listbox.delete(0, tk.END)
        self.meetings_data = []
        
        reunioes_dir = os.path.join(os.path.dirname(__file__), 'reunioes')
        if os.path.exists(reunioes_dir):
            files = sorted([f for f in os.listdir(reunioes_dir) if f.endswith('.txt')], reverse=True)
            
            for filename in files:
                try:
                    # Extrai informações do nome do arquivo
                    parts = filename[:-4].split('_')  # Remove .txt
                    if len(parts) >= 6:
                        meeting_id = parts[0]
                        responsible = parts[1]
                        date = f"{parts[2]}/{parts[3]}/{parts[4]}"
                        time = f"{parts[5]}:{parts[6] if len(parts) > 6 else '00'}"
                        
                        # Lê o arquivo para pegar a duração
                        filepath = os.path.join(reunioes_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Procura pela linha de duração
                            for line in content.split('\n'):
                                if line.startswith('Duração:'):
                                    duration = line.split(':', 1)[1].strip()
                                    break
                            else:
                                duration = "00:00:00"
                        
                        # Adiciona à lista
                        display_text = f"{meeting_id} - {responsible} - {date} - {duration}"
                        self.listbox.insert(tk.END, display_text)
                        self.meetings_data.append(filename)
                except Exception as e:
                    print(f"Erro ao processar arquivo {filename}: {e}")
        
        if not self.meetings_data:
            self.listbox.insert(tk.END, "Nenhuma reunião encontrada")
            self.open_btn.config(state="disabled")
    
    def on_select(self, event):
        """Habilita/desabilita o botão baseado na seleção"""
        selection = self.listbox.curselection()
        if selection and self.meetings_data:
            self.open_btn.config(state="normal")
        else:
            self.open_btn.config(state="disabled")
    
    def open_meeting(self):
        """Abre a reunião selecionada"""
        selection = self.listbox.curselection()
        if selection and self.meetings_data:
            index = selection[0]
            if index < len(self.meetings_data):
                filename = self.meetings_data[index]
                self.controller.current_meeting_file = filename
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
        self.title_label.pack(pady=(0, 10))
        
        # Frame para texto
        text_frame = tk.Frame(container, bg=COLORS['secondary'])
        text_frame.pack(fill="both", expand=True)
        
        # Scrollbar e Text
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.text = tk.Text(
            text_frame,
            font=("Segoe UI", 9),
            bg=COLORS['secondary'],
            fg=COLORS['fg'],
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set
        )
        self.text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.text.yview)
        
        # Desabilita edição
        self.text.config(state="disabled")
        
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
        """Carrega o conteúdo da reunião quando a tela é mostrada"""
        if hasattr(self.controller, 'current_meeting_file'):
            filename = self.controller.current_meeting_file
            reunioes_dir = os.path.join(os.path.dirname(__file__), 'reunioes')
            filepath = os.path.join(reunioes_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Atualiza o título
                meeting_id = filename.split('_')[0]
                self.title_label.config(text=f"Reunião ID: {meeting_id}")
                
                # Mostra o conteúdo
                self.text.config(state="normal")
                self.text.delete(1.0, tk.END)
                self.text.insert(1.0, content)
                self.text.config(state="disabled")
            except Exception as e:
                self.text.config(state="normal")
                self.text.delete(1.0, tk.END)
                self.text.insert(1.0, f"Erro ao carregar reunião: {str(e)}")
                self.text.config(state="disabled")

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