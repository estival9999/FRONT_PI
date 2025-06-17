"""
Tela inicial do aplicativo de gravação de reuniões
"""
import tkinter as tk
from utils.ui_components import BaseScreen, RoundButton, COLORS

class StartScreen(BaseScreen):
    """Tela inicial com botão grande para iniciar"""
    def __init__(self, parent, on_start=None):
        super().__init__(parent, on_next=on_start)
        
        # Container principal
        main_container = tk.Frame(self, bg=COLORS['bg'])
        main_container.pack(expand=True, fill=tk.BOTH)
        
        # Título
        self.create_title("Gravador de Reuniões", pady=(30, 10))
        
        # Subtítulo
        self.create_subtitle("Clique para iniciar uma nova gravação", pady=(0, 30))
        
        # Botão redondo grande
        button_container = tk.Frame(main_container, bg=COLORS['bg'])
        button_container.pack(expand=True)
        
        self.start_button = RoundButton(
            button_container,
            size=100,
            text="INICIAR",
            command=self.on_start_click
        )
        self.start_button.pack()
        
        # Rodapé
        footer = tk.Label(
            self,
            text="v1.0.0",
            font=('Arial', 8),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg']
        )
        footer.pack(side=tk.BOTTOM, pady=10)
        
    def on_start_click(self):
        """Ação ao clicar no botão iniciar"""
        if self.on_next:
            self.on_next()