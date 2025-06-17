"""
Tela para gravar nomes dos participantes por voz
"""
import tkinter as tk
from utils.ui_components import BaseScreen, AnimatedMicrophone, StyledButton, NavigationButtons, COLORS

class ParticipantsScreen(BaseScreen):
    """Tela para capturar participantes por voz"""
    def __init__(self, parent, on_next=None, on_back=None):
        super().__init__(parent, on_next=on_next, on_back=on_back)
        
        self.participants = []
        self.is_recording = False
        
        # Container principal
        main_container = tk.Frame(self, bg=COLORS['bg'])
        main_container.pack(expand=True, fill=tk.BOTH, padx=20)
        
        # Título
        self.create_title("Participantes da Reunião", pady=(20, 10))
        
        # Subtítulo
        self.instruction_label = tk.Label(
            main_container,
            text="Clique no microfone e diga os nomes",
            font=('Arial', 10),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg']
        )
        self.instruction_label.pack(pady=(0, 20))
        
        # Microfone animado
        mic_container = tk.Frame(main_container, bg=COLORS['bg'])
        mic_container.pack(pady=20)
        
        self.microphone = AnimatedMicrophone(mic_container, size=80)
        self.microphone.pack()
        
        # Botão do microfone
        self.mic_button = RoundButton(
            mic_container,
            size=80,
            text="🎤",
            command=self.toggle_recording,
            color=COLORS['primary']
        )
        self.mic_button.place(x=0, y=0)
        
        # Status da gravação
        self.status_label = tk.Label(
            main_container,
            text="",
            font=('Arial', 9),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg']
        )
        self.status_label.pack()
        
        # Lista de participantes detectados
        list_frame = tk.Frame(main_container, bg=COLORS['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        list_label = tk.Label(
            list_frame,
            text="Participantes detectados:",
            font=('Arial', 9),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg']
        )
        list_label.pack(anchor=tk.W)
        
        # Frame com scroll para lista
        self.participants_frame = tk.Frame(list_frame, bg='#2a2a2a', height=60)
        self.participants_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.participants_list = tk.Label(
            self.participants_frame,
            text="Nenhum participante ainda",
            font=('Arial', 9),
            fg=COLORS['text_secondary'],
            bg='#2a2a2a',
            justify=tk.LEFT,
            anchor=tk.W
        )
        self.participants_list.pack(padx=10, pady=5, anchor=tk.W)
        
        # Botões de navegação
        nav_frame = NavigationButtons(
            self,
            on_back=self.on_back,
            on_next=self.proceed_to_next,
            next_text="Confirmar"
        )
        nav_frame.pack(side=tk.BOTTOM, pady=10)
        
    def toggle_recording(self):
        """Alterna entre gravar e parar"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
            
    def start_recording(self):
        """Inicia a gravação de voz"""
        self.is_recording = True
        self.microphone.start_animation()
        self.mic_button.itemconfig(self.mic_button.text, text="⏹")
        self.mic_button.color = COLORS['error']
        self.status_label.config(text="Gravando... Diga os nomes dos participantes", fg=COLORS['error'])
        self.instruction_label.config(text="Fale claramente: 'João Silva, Maria Santos...'")
        
        # Simular detecção de nomes após 3 segundos
        self.after(3000, self.simulate_name_detection)
        
    def stop_recording(self):
        """Para a gravação de voz"""
        self.is_recording = False
        self.microphone.stop_animation()
        self.mic_button.itemconfig(self.mic_button.text, text="🎤")
        self.mic_button.color = COLORS['primary']
        self.status_label.config(text="Gravação finalizada", fg=COLORS['success'])
        self.instruction_label.config(text="Clique no microfone para adicionar mais nomes")
        
    def simulate_name_detection(self):
        """Simula a detecção de nomes (substituir por reconhecimento real)"""
        if self.is_recording:
            # Simular alguns nomes detectados
            detected_names = ["João Silva", "Maria Santos", "Pedro Oliveira"]
            self.add_participants(detected_names)
            self.stop_recording()
            
    def add_participants(self, names):
        """Adiciona participantes à lista"""
        for name in names:
            if name not in self.participants:
                self.participants.append(name)
                
        self.update_participants_display()
        
    def update_participants_display(self):
        """Atualiza a exibição da lista de participantes"""
        if self.participants:
            text = "\n".join([f"• {name}" for name in self.participants])
            self.participants_list.config(text=text, fg=COLORS['text'])
        else:
            self.participants_list.config(
                text="Nenhum participante ainda",
                fg=COLORS['text_secondary']
            )
            
    def proceed_to_next(self):
        """Prossegue para próxima tela"""
        if not self.participants:
            self.status_label.config(
                text="Adicione pelo menos um participante",
                fg=COLORS['error']
            )
            return
            
        if self.on_next:
            self.on_next(self.participants)
            
    def get_participants(self):
        """Retorna a lista de participantes"""
        return self.participants.copy()