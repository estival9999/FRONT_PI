"""
Tela para inserir o nome do responsável pela reunião
"""
import tkinter as tk
from utils.ui_components import BaseScreen, StyledEntry, NavigationButtons, COLORS

class ResponsibleScreen(BaseScreen):
    """Tela para capturar o nome do responsável"""
    def __init__(self, parent, on_next=None, on_back=None):
        super().__init__(parent, on_next=on_next, on_back=on_back)
        
        # Container principal
        main_container = tk.Frame(self, bg=COLORS['bg'])
        main_container.pack(expand=True, fill=tk.BOTH, padx=20)
        
        # Título
        self.create_title("Responsável pela Reunião", pady=(40, 10))
        
        # Subtítulo
        self.create_subtitle("Quem está conduzindo esta reunião?", pady=(0, 20))
        
        # Campo de entrada
        entry_frame = tk.Frame(main_container, bg=COLORS['bg'])
        entry_frame.pack(pady=20)
        
        self.name_entry = StyledEntry(
            entry_frame,
            placeholder="Digite seu nome completo",
            width=30
        )
        self.name_entry.pack()
        
        # Mensagem de erro (inicialmente oculta)
        self.error_label = tk.Label(
            main_container,
            text="",
            font=('Arial', 9),
            fg=COLORS['error'],
            bg=COLORS['bg']
        )
        self.error_label.pack()
        
        # Botões de navegação
        nav_frame = NavigationButtons(
            self,
            on_back=self.on_back,
            on_next=self.validate_and_proceed
        )
        nav_frame.pack(side=tk.BOTTOM, pady=20)
        
    def validate_and_proceed(self):
        """Valida o nome e prossegue"""
        name = self.name_entry.get_value().strip()
        
        if not name:
            self.show_error("Por favor, insira seu nome")
            return
            
        if len(name) < 3:
            self.show_error("O nome deve ter pelo menos 3 caracteres")
            return
            
        # Nome válido, prosseguir
        self.hide_error()
        if self.on_next:
            self.on_next(name)
            
    def show_error(self, message):
        """Mostra mensagem de erro"""
        self.error_label.config(text=message)
        
    def hide_error(self):
        """Esconde mensagem de erro"""
        self.error_label.config(text="")
        
    def get_responsible_name(self):
        """Retorna o nome do responsável"""
        return self.name_entry.get_value().strip()