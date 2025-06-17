import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from utils.ui_components import (
    create_title, create_styled_button, create_styled_frame,
    COLORS, FONTS, fade_in_widget
)


class ConfirmationScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        self.participants_vars = {}
        
        self.create_widgets()
        
    def create_widgets(self):
        # Container principal
        main_container = create_styled_frame(self)
        main_container.pack(expand=True, fill="both", padx=60, pady=40)
        
        # Título
        title = create_title(main_container, "Participantes Identificados")
        title.pack(pady=(0, 30))
        
        # Frame para lista scrollável
        list_frame = tk.Frame(main_container, bg=COLORS['white'])
        list_frame.pack(expand=True, fill="both", padx=40, pady=(0, 20))
        
        # Canvas e scrollbar para lista
        canvas = tk.Canvas(list_frame, bg=COLORS['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=COLORS['white'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame para botões
        button_frame = tk.Frame(main_container, bg=COLORS['white'])
        button_frame.pack(fill="x", padx=40, pady=(20, 0))
        
        # Botão Voltar
        btn_back = create_styled_button(
            button_frame,
            "Voltar",
            lambda: self.go_back(),
            style='secondary'
        )
        btn_back.pack(side="left", padx=(0, 10))
        
        # Botão Finalizar
        self.btn_finish = create_styled_button(
            button_frame,
            "Finalizar",
            lambda: self.finish_confirmation(),
            style='primary'
        )
        self.btn_finish.pack(side="right", padx=(10, 0))
        
        # Aplicar fade in
        fade_in_widget(main_container)
        
    def load_participants(self, participants_data):
        """Carrega a lista de participantes para confirmação"""
        # Limpar lista anterior
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.participants_vars.clear()
        
        # Adicionar cada participante
        for i, participant in enumerate(participants_data):
            self.add_participant_item(participant, i)
            
    def add_participant_item(self, participant, index):
        """Adiciona um item de participante na lista"""
        # Frame para o item
        item_frame = tk.Frame(self.scrollable_frame, bg=COLORS['white'])
        item_frame.pack(fill="x", padx=20, pady=10)
        
        # Checkbox
        var = tk.BooleanVar(value=True)
        self.participants_vars[participant['name']] = var
        
        checkbox = tk.Checkbutton(
            item_frame,
            variable=var,
            bg=COLORS['white'],
            activebackground=COLORS['white'],
            highlightthickness=0,
            bd=0
        )
        checkbox.pack(side="left", padx=(0, 10))
        
        # Nome do participante
        name_label = tk.Label(
            item_frame,
            text=participant['name'],
            font=FONTS['body'],
            bg=COLORS['white'],
            fg=COLORS['text']
        )
        name_label.pack(side="left", padx=(0, 10))
        
        # Indicador se foi corrigido
        if participant.get('corrected', False):
            correction_icon = tk.Label(
                item_frame,
                text="✏",  # Ícone de edição
                font=('Segoe UI', 12),
                bg=COLORS['white'],
                fg=COLORS['primary']
            )
            correction_icon.pack(side="left", padx=(5, 0))
            
            # Tooltip mostrando nome original
            original_text = f"Original: {participant.get('original_name', '')}"
            correction_label = tk.Label(
                item_frame,
                text=f"({original_text})",
                font=('Segoe UI', 9),
                bg=COLORS['white'],
                fg=COLORS['secondary']
            )
            correction_label.pack(side="left", padx=(5, 0))
            
    def go_back(self):
        """Volta para a tela de gravação"""
        result = messagebox.askyesno(
            "Voltar",
            "Deseja voltar e regravar? Os dados atuais serão perdidos."
        )
        if result:
            self.controller.show_frame("RecordingScreen")
            
    def finish_confirmation(self):
        """Finaliza o processo e salva os dados"""
        # Coletar participantes confirmados
        confirmed_participants = []
        for name, var in self.participants_vars.items():
            if var.get():
                confirmed_participants.append(name)
                
        if not confirmed_participants:
            messagebox.showwarning(
                "Nenhum participante",
                "Por favor, selecione pelo menos um participante."
            )
            return
            
        # Salvar dados da reunião
        meeting_data = {
            "date": datetime.now().isoformat(),
            "objective": getattr(self.controller, 'meeting_objective', ''),
            "responsible": getattr(self.controller, 'responsible_name', ''),
            "participants": confirmed_participants,
            "audio_file": getattr(self.controller, 'audio_file_path', ''),
            "transcription": getattr(self.controller, 'transcription_text', '')
        }
        
        # Salvar em arquivo JSON
        try:
            filename = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(meeting_data, f, ensure_ascii=False, indent=2)
                
            # Mostrar mensagem de sucesso
            self.show_success_message(filename)
            
        except Exception as e:
            messagebox.showerror(
                "Erro ao salvar",
                f"Não foi possível salvar os dados: {str(e)}"
            )
            
    def show_success_message(self, filename):
        """Mostra mensagem de sucesso após finalizar"""
        # Criar overlay para mensagem
        overlay = tk.Frame(self, bg=COLORS['bg'])
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Frame da mensagem
        msg_frame = create_styled_frame(overlay)
        msg_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Ícone de sucesso
        success_icon = tk.Label(
            msg_frame,
            text="✓",
            font=('Segoe UI', 48),
            bg=COLORS['white'],
            fg=COLORS['success']
        )
        success_icon.pack(pady=(30, 20))
        
        # Título
        title = tk.Label(
            msg_frame,
            text="Reunião Salva com Sucesso!",
            font=FONTS['title'],
            bg=COLORS['white'],
            fg=COLORS['text']
        )
        title.pack(pady=(0, 10))
        
        # Nome do arquivo
        file_label = tk.Label(
            msg_frame,
            text=f"Arquivo: {filename}",
            font=FONTS['body'],
            bg=COLORS['white'],
            fg=COLORS['secondary']
        )
        file_label.pack(pady=(0, 30))
        
        # Botão para nova reunião
        btn_new = create_styled_button(
            msg_frame,
            "Nova Reunião",
            lambda: self.start_new_meeting(),
            style='primary'
        )
        btn_new.pack(pady=(0, 30))
        
        # Aplicar fade in
        fade_in_widget(overlay)
        
    def start_new_meeting(self):
        """Inicia uma nova reunião"""
        # Resetar dados do controller
        self.controller.reset_meeting_data()
        # Voltar para tela inicial
        self.controller.show_frame("StartScreen")