import tkinter as tk
from tkinter import ttk
import math
import random
import time


class RecordingScreen(tk.Frame):
    def __init__(self, parent, on_finalize=None):
        super().__init__(parent, bg="#1a1a1a")
        self.parent = parent
        self.on_finalize = on_finalize
        self.is_recording = True
        self.is_paused = False
        self.start_time = time.time()
        self.pause_time = 0
        self.total_pause_duration = 0
        
        self.setup_ui()
        self.update_timer()
        self.animate_recording_indicator()
        self.animate_audio_visualizer()
        
    def setup_ui(self):
        # Timer grande centralizado
        self.timer_frame = tk.Frame(self, bg="#1a1a1a")
        self.timer_frame.pack(expand=True, fill="both", pady=(50, 20))
        
        self.timer_label = tk.Label(
            self.timer_frame,
            text="00:00:00",
            font=("Arial", 72, "bold"),
            fg="#ffffff",
            bg="#1a1a1a"
        )
        self.timer_label.pack()
        
        # Indicador de gravação (círculo vermelho pulsante)
        self.recording_indicator_frame = tk.Frame(self, bg="#1a1a1a")
        self.recording_indicator_frame.pack(pady=10)
        
        self.recording_canvas = tk.Canvas(
            self.recording_indicator_frame,
            width=30,
            height=30,
            bg="#1a1a1a",
            highlightthickness=0
        )
        self.recording_canvas.pack(side="left", padx=5)
        
        self.recording_circle = self.recording_canvas.create_oval(
            5, 5, 25, 25,
            fill="#ff0000",
            outline=""
        )
        
        self.recording_text = tk.Label(
            self.recording_indicator_frame,
            text="GRAVANDO",
            font=("Arial", 14, "bold"),
            fg="#ff0000",
            bg="#1a1a1a"
        )
        self.recording_text.pack(side="left")
        
        # Visualizador de áudio
        self.visualizer_frame = tk.Frame(self, bg="#1a1a1a")
        self.visualizer_frame.pack(expand=True, fill="both", padx=50, pady=20)
        
        self.audio_canvas = tk.Canvas(
            self.visualizer_frame,
            bg="#1a1a1a",
            highlightthickness=0,
            height=150
        )
        self.audio_canvas.pack(expand=True, fill="both")
        
        # Controles
        self.controls_frame = tk.Frame(self, bg="#1a1a1a")
        self.controls_frame.pack(pady=(20, 50))
        
        # Botão circular de pause/play
        self.play_pause_canvas = tk.Canvas(
            self.controls_frame,
            width=80,
            height=80,
            bg="#1a1a1a",
            highlightthickness=0
        )
        self.play_pause_canvas.pack(side="left", padx=20)
        
        # Círculo de fundo
        self.play_pause_bg = self.play_pause_canvas.create_oval(
            5, 5, 75, 75,
            fill="#2d2d2d",
            outline="#444444",
            width=2
        )
        
        # Ícone de pause (duas barras verticais)
        self.pause_icon = [
            self.play_pause_canvas.create_rectangle(
                28, 25, 35, 55,
                fill="#ffffff",
                outline="",
                state="normal"
            ),
            self.play_pause_canvas.create_rectangle(
                45, 25, 52, 55,
                fill="#ffffff",
                outline="",
                state="normal"
            )
        ]
        
        # Ícone de play (triângulo) - inicialmente oculto
        self.play_icon = self.play_pause_canvas.create_polygon(
            30, 20, 30, 60, 55, 40,
            fill="#ffffff",
            outline="",
            state="hidden"
        )
        
        self.play_pause_canvas.bind("<Button-1>", self.toggle_play_pause)
        self.play_pause_canvas.bind("<Enter>", lambda e: self.on_hover_play_pause(True))
        self.play_pause_canvas.bind("<Leave>", lambda e: self.on_hover_play_pause(False))
        
        # Botão Finalizar
        self.finalize_button = tk.Button(
            self.controls_frame,
            text="Finalizar",
            font=("Arial", 16, "bold"),
            bg="#d32f2f",
            fg="white",
            padx=30,
            pady=15,
            bd=0,
            activebackground="#b71c1c",
            activeforeground="white",
            cursor="hand2",
            command=self.finalize_recording
        )
        self.finalize_button.pack(side="left", padx=20)
        
        # Número de barras no visualizador
        self.num_bars = 50
        self.bars = []
        self.bar_heights = [0] * self.num_bars
        
    def on_hover_play_pause(self, entering):
        if entering:
            self.play_pause_canvas.itemconfig(
                self.play_pause_bg,
                fill="#3d3d3d"
            )
        else:
            self.play_pause_canvas.itemconfig(
                self.play_pause_bg,
                fill="#2d2d2d"
            )
            
    def toggle_play_pause(self, event=None):
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            # Mostrar ícone de play, esconder pause
            for bar in self.pause_icon:
                self.play_pause_canvas.itemconfig(bar, state="hidden")
            self.play_pause_canvas.itemconfig(self.play_icon, state="normal")
            
            # Pausar gravação
            self.pause_time = time.time()
            self.recording_text.config(text="PAUSADO", fg="#ffa500")
            
        else:
            # Mostrar ícone de pause, esconder play
            for bar in self.pause_icon:
                self.play_pause_canvas.itemconfig(bar, state="normal")
            self.play_pause_canvas.itemconfig(self.play_icon, state="hidden")
            
            # Retomar gravação
            if self.pause_time > 0:
                self.total_pause_duration += time.time() - self.pause_time
            self.recording_text.config(text="GRAVANDO", fg="#ff0000")
            
    def update_timer(self):
        if self.is_recording and not self.is_paused:
            elapsed = time.time() - self.start_time - self.total_pause_duration
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_str)
            
        self.after(100, self.update_timer)
        
    def animate_recording_indicator(self):
        if self.is_recording and not self.is_paused:
            # Animação pulsante
            current_color = self.recording_canvas.itemcget(self.recording_circle, "fill")
            new_color = "#ff0000" if current_color == "#cc0000" else "#cc0000"
            self.recording_canvas.itemconfig(self.recording_circle, fill=new_color)
            
        self.after(500, self.animate_recording_indicator)
        
    def animate_audio_visualizer(self):
        if not hasattr(self, 'bars') or not self.bars:
            self.setup_audio_bars()
            
        # Simular níveis de áudio
        if self.is_recording and not self.is_paused:
            for i in range(self.num_bars):
                # Criar efeito de onda
                base_height = 30 + 20 * math.sin((i / self.num_bars) * math.pi)
                variation = random.uniform(0.8, 1.2)
                target_height = base_height * variation
                
                # Suavizar transição
                current = self.bar_heights[i]
                self.bar_heights[i] = current + (target_height - current) * 0.3
                
                # Atualizar barra
                if i < len(self.bars):
                    bar = self.bars[i]
                    height = max(5, self.bar_heights[i])
                    canvas_height = self.audio_canvas.winfo_height()
                    y1 = (canvas_height - height) / 2
                    y2 = (canvas_height + height) / 2
                    
                    self.audio_canvas.coords(bar, 
                        bar_x := self.audio_canvas.coords(bar)[0],
                        y1,
                        bar_x + self.bar_width - 2,
                        y2
                    )
        else:
            # Quando pausado, reduzir gradualmente
            for i in range(self.num_bars):
                self.bar_heights[i] *= 0.9
                if i < len(self.bars) and self.bar_heights[i] > 5:
                    bar = self.bars[i]
                    height = self.bar_heights[i]
                    canvas_height = self.audio_canvas.winfo_height()
                    y1 = (canvas_height - height) / 2
                    y2 = (canvas_height + height) / 2
                    
                    self.audio_canvas.coords(bar,
                        bar_x := self.audio_canvas.coords(bar)[0],
                        y1,
                        bar_x + self.bar_width - 2,
                        y2
                    )
                    
        self.after(50, self.animate_audio_visualizer)
        
    def setup_audio_bars(self):
        self.audio_canvas.delete("all")
        self.bars = []
        
        canvas_width = self.audio_canvas.winfo_width()
        if canvas_width <= 1:
            self.after(100, self.setup_audio_bars)
            return
            
        self.bar_width = canvas_width / self.num_bars
        canvas_height = self.audio_canvas.winfo_height()
        
        for i in range(self.num_bars):
            x = i * self.bar_width
            bar = self.audio_canvas.create_rectangle(
                x, canvas_height/2 - 5, 
                x + self.bar_width - 2, canvas_height/2 + 5,
                fill="#4CAF50",
                outline=""
            )
            self.bars.append(bar)
            
    def finalize_recording(self):
        self.is_recording = False
        if self.on_finalize:
            elapsed = time.time() - self.start_time - self.total_pause_duration
            self.on_finalize(elapsed)
            
    def on_configure(self, event=None):
        # Recriar barras quando a janela for redimensionada
        if hasattr(self, 'audio_canvas'):
            self.setup_audio_bars()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gravação")
    root.geometry("800x600")
    root.configure(bg="#1a1a1a")
    
    def on_finalize(duration):
        print(f"Gravação finalizada. Duração: {duration:.2f} segundos")
        root.quit()
    
    screen = RecordingScreen(root, on_finalize=on_finalize)
    screen.pack(expand=True, fill="both")
    
    root.bind("<Configure>", screen.on_configure)
    root.mainloop()