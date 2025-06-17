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
from datetime import datetime

# Adiciona o diretório atual ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
        else:
            self.pause_btn.config(text="⏸")
            self.status_label.config(text="GRAVANDO", fg=COLORS['danger'])
    
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
        self.controller.show_frame("ParticipantsScreen")
    
    def reset(self):
        self.is_recording = True
        self.is_paused = False
        self.start_time = datetime.now()
        self.pause_btn.config(text="⏸")
        self.status_label.config(text="GRAVANDO", fg=COLORS['danger'])
        self.update_timer()
        self.animate_audio()

class ParticipantsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        self.is_recording = False
        
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
        
        # Instrução
        self.instruction = tk.Label(
            container,
            text="Fale os nomes dos participantes",
            font=("Segoe UI", 10),
            bg=COLORS['bg'],
            fg=COLORS['muted']
        )
        self.instruction.pack(pady=5)
        
        # Botão de gravação
        self.record_btn = tk.Button(
            container,
            text="Iniciar Gravação",
            font=("Segoe UI", 10),
            bg=COLORS['primary'],
            fg="white",
            command=self.toggle_recording,
            cursor="hand2"
        )
        self.record_btn.pack(pady=10)
    
    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.record_btn.config(text="Parar", bg=COLORS['danger'])
            self.instruction.config(text="Gravando... Fale os nomes")
            # Simula gravação de 3 segundos
            self.after(3000, self.stop_recording)
        else:
            self.stop_recording()
    
    def stop_recording(self):
        self.is_recording = False
        self.record_btn.config(text="Iniciar Gravação", bg=COLORS['primary'])
        self.instruction.config(text="Processando...")
        
        # Simula processamento
        self.after(1000, self.process_participants)
    
    def process_participants(self):
        # Simula participantes detectados
        participants = ["João Silva", "Maria Santos", "Pedro Oliveira"]
        self.controller.shared_data['participants'] = participants
        self.controller.show_frame("ConfirmationScreen")
    
    def reset(self):
        self.is_recording = False
        self.record_btn.config(text="Iniciar Gravação", bg=COLORS['primary'])
        self.instruction.config(text="Fale os nomes dos participantes")

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
            height=6
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        
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
        self.listbox.delete(0, tk.END)
        participants = self.controller.shared_data.get('participants', [])
        for participant in participants:
            self.listbox.insert(tk.END, f"✓ {participant}")
    
    def finish_meeting(self):
        # Salva os dados da reunião
        data = self.controller.shared_data
        meeting_id = self.controller.get_next_meeting_id()
        
        # Cria o nome do arquivo
        timestamp = datetime.now()
        filename = f"{meeting_id:02d}_{data['responsible']}_{timestamp.strftime('%d_%m_%Y_%H_%M')}.txt"
        
        messagebox.showinfo(
            "Sucesso",
            f"Reunião finalizada!\nArquivo: {filename}\n\nDados salvos com sucesso."
        )
        
        # Reinicia para nova reunião
        self.controller.reset_data()
        self.controller.show_frame("StartScreen")

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
                  RecordingScreen, ParticipantsScreen, ConfirmationScreen):
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