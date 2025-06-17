"""
Tela de confirmação com lista de participantes e checkboxes
"""
import tkinter as tk
from tkinter import ttk
from utils.ui_components import BaseScreen, CheckboxList, NavigationButtons, StyledButton, COLORS

class ConfirmationScreen(BaseScreen):
    """Tela para confirmar participantes antes de finalizar"""
    def __init__(self, parent, participants=None, on_confirm=None, on_back=None):
        super().__init__(parent, on_next=on_confirm, on_back=on_back)
        
        self.participants = participants or []
        
        # Container principal
        main_container = tk.Frame(self, bg=COLORS['bg'])
        main_container.pack(expand=True, fill=tk.BOTH, padx=20)
        
        # Título
        self.create_title("Confirmar Participantes", pady=(20, 10))
        
        # Subtítulo
        self.create_subtitle(
            "Marque os participantes que estavam presentes",
            pady=(0, 20)
        )
        
        # Container com scroll para lista
        list_container = tk.Frame(main_container, bg=COLORS['bg'])
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(list_container, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Lista de checkboxes
        self.checkbox_list = CheckboxList(scrollable_frame, self.participants)
        self.checkbox_list.pack(fill=tk.BOTH, expand=True, padx=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        
        # Mostrar scrollbar apenas se necessário
        if len(self.participants) > 5:
            scrollbar.pack(side="right", fill="y")
            
        # Botão adicionar participante
        add_frame = tk.Frame(main_container, bg=COLORS['bg'])
        add_frame.pack(pady=10)
        
        self.add_button = StyledButton(
            add_frame,
            text="+ Adicionar Participante",
            command=self.add_participant,
            style='secondary'
        )
        self.add_button.pack()
        
        # Estatísticas
        self.stats_label = tk.Label(
            main_container,
            text=self.get_stats_text(),
            font=('Arial', 9),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg']
        )
        self.stats_label.pack(pady=5)
        
        # Botões de navegação
        nav_frame = NavigationButtons(
            self,
            on_back=self.on_back,
            on_next=self.confirm_and_finish,
            next_text="Finalizar"
        )
        nav_frame.pack(side=tk.BOTTOM, pady=10)
        
    def get_stats_text(self):
        """Retorna texto com estatísticas"""
        total = len(self.participants)
        selected = len(self.checkbox_list.get_selected())
        return f"{selected} de {total} participantes confirmados"
        
    def add_participant(self):
        """Abre diálogo para adicionar novo participante"""
        dialog = tk.Toplevel(self)
        dialog.title("Adicionar Participante")
        dialog.geometry("250x120")
        dialog.configure(bg=COLORS['bg'])
        
        # Centralizar diálogo
        dialog.transient(self)
        dialog.grab_set()
        
        # Label
        label = tk.Label(
            dialog,
            text="Nome do participante:",
            font=('Arial', 10),
            fg=COLORS['text'],
            bg=COLORS['bg']
        )
        label.pack(pady=10)
        
        # Entry
        from utils.ui_components import StyledEntry
        entry = StyledEntry(dialog, width=25)
        entry.pack(padx=20)
        entry.focus()
        
        # Botões
        button_frame = tk.Frame(dialog, bg=COLORS['bg'])
        button_frame.pack(pady=10)
        
        def add_and_close():
            name = entry.get_value().strip()
            if name:
                self.participants.append(name)
                self.checkbox_list.add_item(name)
                self.stats_label.config(text=self.get_stats_text())
                dialog.destroy()
                
        StyledButton(
            button_frame,
            text="Adicionar",
            command=add_and_close
        ).pack(side=tk.LEFT, padx=5)
        
        StyledButton(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            style='secondary'
        ).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter para adicionar
        entry.bind('<Return>', lambda e: add_and_close())
        
    def confirm_and_finish(self):
        """Confirma seleção e finaliza"""
        selected = self.checkbox_list.get_selected()
        
        if not selected:
            # Mostrar aviso
            self.stats_label.config(
                text="Selecione pelo menos um participante!",
                fg=COLORS['error']
            )
            return
            
        if self.on_next:
            self.on_next(selected)
            
    def set_participants(self, participants):
        """Define a lista de participantes"""
        self.participants = participants
        self.checkbox_list.clear()
        for participant in participants:
            self.checkbox_list.add_item(participant)
        self.stats_label.config(text=self.get_stats_text())
        
    def get_confirmed_participants(self):
        """Retorna lista de participantes confirmados"""
        return self.checkbox_list.get_selected()