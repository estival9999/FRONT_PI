#!/usr/bin/env python3
"""
Gravador de Reuniões - Aplicação Principal
Sistema de gravação de reuniões com transcrição e análise
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Adiciona o diretório atual ao path para importações
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importações das telas (serão criadas posteriormente)
try:
    from screens.home_screen import HomeScreen
    from screens.recording_screen import RecordingScreen
    from screens.transcription_screen import TranscriptionScreen
    from screens.analysis_screen import AnalysisScreen
except ImportError:
    # Placeholder para quando as telas ainda não existirem
    class HomeScreen:
        def __init__(self, parent, app):
            self.parent = parent
            self.app = app
            label = tk.Label(parent, text="Tela Inicial", bg="#1a1a1a", fg="#f0f0f0")
            label.pack(expand=True)
    
    class RecordingScreen:
        def __init__(self, parent, app):
            self.parent = parent
            self.app = app
            label = tk.Label(parent, text="Tela de Gravação", bg="#1a1a1a", fg="#f0f0f0")
            label.pack(expand=True)
    
    class TranscriptionScreen:
        def __init__(self, parent, app):
            self.parent = parent
            self.app = app
            label = tk.Label(parent, text="Tela de Transcrição", bg="#1a1a1a", fg="#f0f0f0")
            label.pack(expand=True)
    
    class AnalysisScreen:
        def __init__(self, parent, app):
            self.parent = parent
            self.app = app
            label = tk.Label(parent, text="Tela de Análise", bg="#1a1a1a", fg="#f0f0f0")
            label.pack(expand=True)


class App:
    """Classe principal da aplicação"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gravador de Reuniões")
        
        # Configurações da janela
        self.root.geometry("320x240")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a1a")
        
        # Centralizar a janela na tela
        self.center_window()
        
        # Container principal para as telas
        self.container = tk.Frame(self.root, bg="#1a1a1a")
        self.container.pack(fill="both", expand=True)
        
        # Dicionário para armazenar as telas
        self.screens = {}
        self.current_screen = None
        
        # Inicializar as telas
        self.initialize_screens()
        
        # Mostrar a tela inicial
        self.show_screen("home")
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def initialize_screens(self):
        """Inicializa todas as telas da aplicação"""
        # Criar frames para cada tela
        for screen_name in ["home", "recording", "transcription", "analysis"]:
            frame = tk.Frame(self.container, bg="#1a1a1a")
            frame.grid(row=0, column=0, sticky="nsew")
            self.screens[screen_name] = frame
        
        # Configurar o grid
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Instanciar as telas
        self.home_screen = HomeScreen(self.screens["home"], self)
        self.recording_screen = RecordingScreen(self.screens["recording"], self)
        self.transcription_screen = TranscriptionScreen(self.screens["transcription"], self)
        self.analysis_screen = AnalysisScreen(self.screens["analysis"], self)
    
    def show_screen(self, screen_name):
        """Mostra a tela especificada com animação simples"""
        if screen_name not in self.screens:
            print(f"Erro: Tela '{screen_name}' não encontrada")
            return
        
        # Ocultar a tela atual com fade out
        if self.current_screen:
            self.fade_out(self.screens[self.current_screen], 
                         lambda: self.fade_in(self.screens[screen_name]))
        else:
            # Se não há tela atual, apenas mostrar a nova
            self.fade_in(self.screens[screen_name])
        
        self.current_screen = screen_name
    
    def fade_out(self, widget, callback=None):
        """Animação de fade out"""
        alpha = widget.winfo_toplevel().attributes("-alpha")
        if alpha > 0.3:
            widget.winfo_toplevel().attributes("-alpha", alpha - 0.1)
            widget.after(20, lambda: self.fade_out(widget, callback))
        else:
            widget.tkraise()
            widget.winfo_toplevel().attributes("-alpha", 1.0)
            if callback:
                callback()
    
    def fade_in(self, widget):
        """Animação de fade in"""
        widget.tkraise()
        alpha = 0.3
        self._fade_in_step(widget, alpha)
    
    def _fade_in_step(self, widget, alpha):
        """Passo da animação de fade in"""
        if alpha < 1.0:
            widget.winfo_toplevel().attributes("-alpha", alpha)
            widget.after(20, lambda: self._fade_in_step(widget, alpha + 0.1))
        else:
            widget.winfo_toplevel().attributes("-alpha", 1.0)
    
    def get_color_scheme(self):
        """Retorna o esquema de cores da aplicação"""
        return {
            "bg": "#1a1a1a",
            "fg": "#f0f0f0",
            "highlight": "#4a90e2",
            "button_bg": "#2a2a2a",
            "button_hover": "#3a3a3a",
            "success": "#4caf50",
            "error": "#f44336",
            "warning": "#ff9800"
        }
    
    def run(self):
        """Inicia a aplicação"""
        print("Iniciando Gravador de Reuniões...")
        self.root.mainloop()


def main():
    """Função principal"""
    app = App()
    app.run()


if __name__ == "__main__":
    main()