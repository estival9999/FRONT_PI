"""
Tela de gravação com timer e visualizador de áudio
"""
import tkinter as tk
from utils.ui_components import BaseScreen, StyledButton, RoundButton, COLORS
import time

class RecordingScreen(BaseScreen):
    """Tela principal de gravação"""
    def __init__(self, parent, on_finish=None, on_back=None):
        super().__init__(parent, on_next=on_finish, on_back=on_back)
        
        self.start_time = None
        self.is_paused = False
        self.pause_time = 0
        self.total_pause_time = 0
        
        # Container principal
        main_container = tk.Frame(self, bg=COLORS['bg'])
        main_container.pack(expand=True, fill=tk.BOTH)
        
        # Status da gravação
        self.status_label = tk.Label(
            main_container,
            text="GRAVANDO",
            font=('Arial', 12, 'bold'),
            fg=COLORS['error'],
            bg=COLORS['bg']
        )
        self.status_label.pack(pady=(20, 10))
        
        # Timer
        self.timer_label = tk.Label(
            main_container,
            text="00:00:00",
            font=('Arial', 24, 'bold'),
            fg=COLORS['text'],
            bg=COLORS['bg']
        )
        self.timer_label.pack(pady=10)
        
        # Visualizador de áudio
        self.audio_frame = tk.Frame(main_container, bg=COLORS['bg'])
        self.audio_frame.pack(pady=20, fill=tk.X, padx=20)
        
        self.audio_canvas = tk.Canvas(
            self.audio_frame,
            height=60,
            bg=COLORS['bg'],
            highlightthickness=0
        )
        self.audio_canvas.pack(fill=tk.X)
        
        # Criar barras do visualizador
        self.audio_bars = []
        self.create_audio_bars()
        
        # Botões de controle
        control_frame = tk.Frame(main_container, bg=COLORS['bg'])
        control_frame.pack(pady=20)
        
        # Botão pausar/continuar
        self.pause_button = RoundButton(
            control_frame,
            size=50,
            text="| |",
            command=self.toggle_pause,
            color=COLORS['primary']
        )
        self.pause_button.pack(side=tk.LEFT, padx=10)
        
        # Botão adicionar participante
        self.add_participant_btn = StyledButton(
            control_frame,
            text="+ Participante",
            command=self.add_participant,
            style='secondary'
        )
        self.add_participant_btn.pack(side=tk.LEFT, padx=10)
        
        # Botão finalizar
        self.finish_button = StyledButton(
            control_frame,
            text="Finalizar",
            command=self.finish_recording,
            style='error'
        )
        self.finish_button.pack(side=tk.LEFT, padx=10)
        
        # Iniciar gravação
        self.start_recording()
        
    def create_audio_bars(self):
        """Cria as barras do visualizador de áudio"""
        bar_width = 4
        bar_spacing = 2
        num_bars = 40
        
        self.audio_canvas.update_idletasks()
        canvas_width = self.audio_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 280  # Largura padrão
            
        start_x = (canvas_width - (num_bars * (bar_width + bar_spacing))) // 2
        
        for i in range(num_bars):
            x = start_x + i * (bar_width + bar_spacing)
            bar = self.audio_canvas.create_rectangle(
                x, 30, x + bar_width, 30,
                fill=COLORS['primary'],
                outline=""
            )
            self.audio_bars.append(bar)
            
    def animate_audio_bars(self):
        """Anima as barras do visualizador"""
        if not self.is_paused and hasattr(self, 'audio_bars'):
            import random
            for bar in self.audio_bars:
                height = random.randint(5, 40)
                coords = self.audio_canvas.coords(bar)
                if coords:
                    self.audio_canvas.coords(
                        bar,
                        coords[0], 60 - height,
                        coords[2], 60
                    )
            
        if not self.is_paused:
            self.after(100, self.animate_audio_bars)
            
    def start_recording(self):
        """Inicia a gravação"""
        self.start_time = time.time()
        self.update_timer()
        self.animate_audio_bars()
        
    def update_timer(self):
        """Atualiza o timer"""
        if self.start_time and not self.is_paused:
            elapsed = time.time() - self.start_time - self.total_pause_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            
            self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
        self.after(1000, self.update_timer)
        
    def toggle_pause(self):
        """Alterna entre pausar e continuar"""
        if self.is_paused:
            # Continuar
            self.total_pause_time += time.time() - self.pause_time
            self.is_paused = False
            self.status_label.config(text="GRAVANDO", fg=COLORS['error'])
            self.pause_button.itemconfig(self.pause_button.text, text="| |")
            self.animate_audio_bars()
        else:
            # Pausar
            self.pause_time = time.time()
            self.is_paused = True
            self.status_label.config(text="PAUSADO", fg=COLORS['primary'])
            self.pause_button.itemconfig(self.pause_button.text, text="▶")
            
    def add_participant(self):
        """Adiciona um novo participante durante a gravação"""
        # Esta função seria implementada para abrir um diálogo ou navegar para tela de participantes
        print("Adicionar participante")
        
    def finish_recording(self):
        """Finaliza a gravação"""
        if self.on_next:
            elapsed_time = time.time() - self.start_time - self.total_pause_time
            self.on_next(elapsed_time)
            
    def get_recording_time(self):
        """Retorna o tempo total de gravação"""
        if self.start_time:
            return time.time() - self.start_time - self.total_pause_time
        return 0