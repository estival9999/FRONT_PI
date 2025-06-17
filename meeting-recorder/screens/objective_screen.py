"""
Tela para inserir o objetivo da reunião
"""
import tkinter as tk
from utils.ui_components import BaseScreen, StyledText, NavigationButtons, COLORS

class ObjectiveScreen(BaseScreen):
    """Tela para capturar o objetivo da reunião"""
    def __init__(self, parent, on_next=None, on_back=None):
        super().__init__(parent, on_next=on_next, on_back=on_back)
        
        # Container principal
        main_container = tk.Frame(self, bg=COLORS['bg'])
        main_container.pack(expand=True, fill=tk.BOTH, padx=20)
        
        # Título
        self.create_title("Objetivo da Reunião", pady=(30, 10))
        
        # Subtítulo
        self.create_subtitle("Descreva brevemente o propósito desta reunião", pady=(0, 20))
        
        # Campo de texto
        text_frame = tk.Frame(main_container, bg=COLORS['bg'])
        text_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Frame com borda para o campo de texto
        text_border = tk.Frame(text_frame, bg=COLORS['border'], bd=1)
        text_border.pack(fill=tk.BOTH, expand=True)
        
        self.objective_text = StyledText(
            text_border,
            placeholder="Ex: Discutir o progresso do projeto X e definir próximos passos...",
            height=5,
            width=35
        )
        self.objective_text.pack(padx=1, pady=1)
        
        # Contador de caracteres
        self.char_counter = tk.Label(
            main_container,
            text="0/200 caracteres",
            font=('Arial', 8),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg']
        )
        self.char_counter.pack(anchor=tk.E)
        
        # Bind para atualizar contador
        self.objective_text.bind('<KeyRelease>', self.update_counter)
        
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
        
    def update_counter(self, event=None):
        """Atualiza o contador de caracteres"""
        text = self.objective_text.get_value()
        length = len(text)
        
        self.char_counter.config(text=f"{length}/200 caracteres")
        
        # Mudar cor se exceder limite
        if length > 200:
            self.char_counter.config(fg=COLORS['error'])
        else:
            self.char_counter.config(fg=COLORS['text_secondary'])
            
    def validate_and_proceed(self):
        """Valida o objetivo e prossegue"""
        objective = self.objective_text.get_value().strip()
        
        if not objective:
            self.show_error("Por favor, descreva o objetivo da reunião")
            return
            
        if len(objective) < 10:
            self.show_error("O objetivo deve ter pelo menos 10 caracteres")
            return
            
        if len(objective) > 200:
            self.show_error("O objetivo não pode exceder 200 caracteres")
            return
            
        # Objetivo válido, prosseguir
        self.hide_error()
        if self.on_next:
            self.on_next(objective)
            
    def show_error(self, message):
        """Mostra mensagem de erro"""
        self.error_label.config(text=message)
        
    def hide_error(self):
        """Esconde mensagem de erro"""
        self.error_label.config(text="")
        
    def get_objective(self):
        """Retorna o objetivo da reunião"""
        return self.objective_text.get_value().strip()