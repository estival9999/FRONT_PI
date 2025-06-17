import tkinter as tk
from tkinter import ttk
import time
import math
import random


class ParticipantsScreen(tk.Frame):
    def __init__(self, parent, on_complete=None):
        super().__init__(parent, bg="#1a1a1a")
        self.parent = parent
        self.on_complete = on_complete
        self.is_recording = False
        self.start_time = None
        self.max_duration = 10  # segundos
        
        self.setup_ui()
        
    def setup_ui(self):
        # Container principal
        main_container = tk.Frame(self, bg="#1a1a1a")
        main_container.pack(expand=True, fill="both", padx=50, pady=50)
        
        # Título
        title_label = tk.Label(
            main_container,
            text="Informe os Participantes",
            font=("Arial", 32, "bold"),
            fg="#ffffff",
            bg="#1a1a1a"
        )
        title_label.pack(pady=(0, 40))
        
        # Ícone de microfone grande
        self.mic_canvas = tk.Canvas(
            main_container,
            width=200,
            height=200,
            bg="#1a1a1a",
            highlightthickness=0
        )
        self.mic_canvas.pack(pady=20)
        
        # Desenhar microfone
        self.draw_microphone()
        
        # Indicador visual de captura (círculos concêntricos)
        self.audio_rings = []
        
        # Texto de instrução
        self.instruction_label = tk.Label(
            main_container,
            text="Fale os nomes dos participantes",
            font=("Arial", 18),
            fg="#cccccc",
            bg="#1a1a1a"
        )
        self.instruction_label.pack(pady=20)
        
        # Timer
        self.timer_label = tk.Label(
            main_container,
            text="",
            font=("Arial", 16),
            fg="#4CAF50",
            bg="#1a1a1a"
        )
        self.timer_label.pack(pady=10)
        
        # Botão de gravação
        self.record_button = tk.Button(
            main_container,
            text="Iniciar Gravação",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=40,
            pady=15,
            bd=0,
            activebackground="#45a049",
            activeforeground="white",
            cursor="hand2",
            command=self.toggle_recording
        )
        self.record_button.pack(pady=30)
        
        # Indicador de status
        self.status_frame = tk.Frame(main_container, bg="#1a1a1a")
        self.status_frame.pack(pady=10)
        
        self.status_indicator = tk.Canvas(
            self.status_frame,
            width=20,
            height=20,
            bg="#1a1a1a",
            highlightthickness=0
        )
        
        self.status_circle = self.status_indicator.create_oval(
            2, 2, 18, 18,
            fill="#666666",
            outline=""
        )
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Pronto para gravar",
            font=("Arial", 12),
            fg="#999999",
            bg="#1a1a1a"
        )
        
    def draw_microphone(self):
        # Corpo do microfone
        self.mic_body = self.mic_canvas.create_oval(
            70, 40, 130, 120,
            fill="#333333",
            outline="#555555",
            width=3
        )
        
        # Grade do microfone
        for i in range(5):
            y = 50 + i * 15
            self.mic_canvas.create_line(
                80, y, 120, y,
                fill="#555555",
                width=1
            )
            
        # Suporte do microfone
        self.mic_canvas.create_arc(
            60, 100, 140, 140,
            start=0, extent=180,
            outline="#555555",
            width=3,
            style="arc"
        )
        
        # Base do microfone
        self.mic_canvas.create_line(
            100, 140, 100, 160,
            fill="#555555",
            width=3
        )
        self.mic_canvas.create_line(
            80, 160, 120, 160,
            fill="#555555",
            width=5
        )
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        self.is_recording = True
        self.start_time = time.time()
        
        # Atualizar UI
        self.record_button.config(
            text="Parar",
            bg="#d32f2f",
            activebackground="#b71c1c"
        )
        
        self.status_indicator.pack(side="left", padx=5)
        self.status_label.pack(side="left")
        
        self.status_indicator.itemconfig(self.status_circle, fill="#ff0000")
        self.status_label.config(text="Gravando...", fg="#ff0000")
        
        # Mudar cor do microfone
        self.mic_canvas.itemconfig(self.mic_body, fill="#4CAF50")
        
        # Iniciar animações
        self.update_timer()
        self.animate_audio_capture()
        self.pulse_microphone()
        
    def stop_recording(self):
        self.is_recording = False
        
        # Atualizar UI
        self.record_button.config(
            text="Iniciar Gravação",
            bg="#4CAF50",
            activebackground="#45a049"
        )
        
        self.status_indicator.itemconfig(self.status_circle, fill="#666666")
        self.status_label.config(text="Gravação concluída", fg="#999999")
        
        # Voltar cor original do microfone
        self.mic_canvas.itemconfig(self.mic_body, fill="#333333")
        
        # Limpar anéis de áudio
        for ring in self.audio_rings:
            self.mic_canvas.delete(ring)
        self.audio_rings = []
        
        # Callback de conclusão
        if self.on_complete:
            self.on_complete()
            
    def update_timer(self):
        if self.is_recording and self.start_time:
            elapsed = time.time() - self.start_time
            remaining = max(0, self.max_duration - elapsed)
            
            if remaining > 0:
                self.timer_label.config(
                    text=f"Tempo restante: {remaining:.1f}s",
                    fg="#4CAF50" if remaining > 3 else "#ffa500"
                )
                self.after(100, self.update_timer)
            else:
                self.timer_label.config(
                    text="Tempo esgotado!",
                    fg="#d32f2f"
                )
                self.stop_recording()
        else:
            self.timer_label.config(text="")
            
    def animate_audio_capture(self):
        if self.is_recording:
            # Criar novo anel expandindo
            if random.random() > 0.3:  # Não criar anel toda vez
                ring = self.mic_canvas.create_oval(
                    85, 60, 115, 90,
                    outline="#4CAF50",
                    width=2,
                    state="normal"
                )
                self.audio_rings.append({
                    'id': ring,
                    'size': 30,
                    'opacity': 1.0
                })
                
            # Atualizar anéis existentes
            for ring_data in self.audio_rings[:]:
                ring_id = ring_data['id']
                ring_data['size'] += 3
                ring_data['opacity'] -= 0.05
                
                if ring_data['opacity'] <= 0:
                    self.mic_canvas.delete(ring_id)
                    self.audio_rings.remove(ring_data)
                else:
                    # Calcular novas coordenadas
                    center_x, center_y = 100, 75
                    size = ring_data['size']
                    x1 = center_x - size
                    y1 = center_y - size * 0.75  # Elipse
                    x2 = center_x + size
                    y2 = center_y + size * 0.75
                    
                    self.mic_canvas.coords(ring_id, x1, y1, x2, y2)
                    
                    # Simular opacidade com largura da linha
                    width = max(1, int(2 * ring_data['opacity']))
                    self.mic_canvas.itemconfig(ring_id, width=width)
                    
            self.after(50, self.animate_audio_capture)
            
    def pulse_microphone(self):
        if self.is_recording:
            # Efeito pulsante no microfone
            current_fill = self.mic_canvas.itemcget(self.mic_body, "fill")
            new_fill = "#4CAF50" if current_fill == "#45a049" else "#45a049"
            self.mic_canvas.itemconfig(self.mic_body, fill=new_fill)
            
            self.after(500, self.pulse_microphone)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Participantes")
    root.geometry("800x600")
    root.configure(bg="#1a1a1a")
    
    def on_complete():
        print("Gravação de participantes concluída!")
        root.quit()
    
    screen = ParticipantsScreen(root, on_complete=on_complete)
    screen.pack(expand=True, fill="both")
    
    root.mainloop()