import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class ObjectiveScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1a1a1a")
        self.controller = controller
        self.max_chars = 200
        
        # Título no topo
        title_label = tk.Label(
            self,
            text="Objetivo da Reunião",
            bg="#1a1a1a",
            fg="white",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(50, 30))
        
        # Container para o texto
        text_container = tk.Frame(self, bg="#1a1a1a")
        text_container.pack(expand=True, fill="both", padx=50)
        
        # Frame para o Text widget e contador
        text_frame = tk.Frame(text_container, bg="#1a1a1a")
        text_frame.pack(fill="both", expand=True)
        
        # Text area
        self.objective_text = tk.Text(
            text_frame,
            height=4,
            font=("Arial", 12),
            bg="#2a2a2a",
            fg="white",
            insertbackground="white",
            relief="flat",
            wrap="word",
            padx=10,
            pady=10
        )
        self.objective_text.pack(fill="both", expand=True)
        
        # Adiciona placeholder
        self.placeholder_text = "Descreva brevemente o objetivo desta reunião..."
        self.objective_text.insert("1.0", self.placeholder_text)
        self.objective_text.config(fg="#666666")
        
        # Eventos para placeholder e contador
        self.objective_text.bind("<FocusIn>", self.on_text_focus_in)
        self.objective_text.bind("<FocusOut>", self.on_text_focus_out)
        self.objective_text.bind("<KeyRelease>", self.update_char_count)
        
        # Contador de caracteres
        self.char_counter = tk.Label(
            text_container,
            text=f"0/{self.max_chars} caracteres",
            bg="#1a1a1a",
            fg="#666666",
            font=("Arial", 10)
        )
        self.char_counter.pack(anchor="e", pady=(5, 0))
        
        # Container para botões no rodapé
        button_container = tk.Frame(self, bg="#1a1a1a")
        button_container.pack(side="bottom", fill="x", padx=50, pady=30)
        
        # Botão Voltar
        self.back_button = tk.Button(
            button_container,
            text="Voltar",
            bg="#666666",
            fg="white",
            font=("Arial", 12),
            relief="flat",
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.on_back_click
        )
        self.back_button.pack(side="left")
        
        # Botão Próximo
        self.next_button = tk.Button(
            button_container,
            text="Próximo",
            bg="#4a90e2",
            fg="white",
            font=("Arial", 12),
            relief="flat",
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.on_next_click
        )
        self.next_button.pack(side="right")
        
        # Efeitos de hover
        self.back_button.bind("<Enter>", lambda e: self.back_button.config(bg="#777777"))
        self.back_button.bind("<Leave>", lambda e: self.back_button.config(bg="#666666"))
        self.next_button.bind("<Enter>", lambda e: self.next_button.config(bg="#5ba0f2"))
        self.next_button.bind("<Leave>", lambda e: self.next_button.config(bg="#4a90e2"))
    
    def on_text_focus_in(self, event):
        """Remove placeholder ao focar"""
        current_text = self.objective_text.get("1.0", "end-1c")
        if current_text == self.placeholder_text:
            self.objective_text.delete("1.0", tk.END)
            self.objective_text.config(fg="white")
    
    def on_text_focus_out(self, event):
        """Adiciona placeholder se campo estiver vazio"""
        current_text = self.objective_text.get("1.0", "end-1c").strip()
        if not current_text:
            self.objective_text.insert("1.0", self.placeholder_text)
            self.objective_text.config(fg="#666666")
    
    def update_char_count(self, event=None):
        """Atualiza contador de caracteres"""
        current_text = self.objective_text.get("1.0", "end-1c")
        
        # Não conta o placeholder
        if current_text == self.placeholder_text:
            char_count = 0
        else:
            char_count = len(current_text)
        
        # Limita a entrada se exceder o máximo
        if char_count > self.max_chars:
            self.objective_text.delete(f"1.0 + {self.max_chars} chars", "end-1c")
            char_count = self.max_chars
        
        # Atualiza o label
        self.char_counter.config(text=f"{char_count}/{self.max_chars} caracteres")
        
        # Muda cor se estiver próximo do limite
        if char_count >= self.max_chars * 0.9:
            self.char_counter.config(fg="#ff6666")
        else:
            self.char_counter.config(fg="#666666")
    
    def on_back_click(self):
        """Volta para tela anterior"""
        self.controller.show_frame("ResponsibleScreen")
    
    def on_next_click(self):
        """Valida e avança para próxima tela"""
        objective = self.objective_text.get("1.0", "end-1c").strip()
        
        # Verifica se não é o placeholder ou campo vazio
        if not objective or objective == self.placeholder_text:
            messagebox.showwarning(
                "Campo obrigatório",
                "Por favor, descreva o objetivo da reunião."
            )
            return
        
        # Salva o objetivo e avança
        if hasattr(self.controller, 'data'):
            self.controller.data['objective'] = objective
        
        # Próxima tela seria ParticipantsScreen
        self.controller.show_frame("ParticipantsScreen")
    
    def reset(self):
        """Limpa o campo ao voltar para esta tela"""
        self.objective_text.delete("1.0", tk.END)
        self.objective_text.insert("1.0", self.placeholder_text)
        self.objective_text.config(fg="#666666")
        self.update_char_count()


# Exemplo de uso standalone
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Objetivo da Reunião")
    root.geometry("800x600")
    root.configure(bg="#1a1a1a")
    
    # Simulando um controller básico
    class DummyController:
        def __init__(self):
            self.data = {}
        
        def show_frame(self, frame_name):
            print(f"Navegando para: {frame_name}")
            print(f"Dados salvos: {self.data}")
    
    controller = DummyController()
    screen = ObjectiveScreen(root, controller)
    screen.pack(fill="both", expand=True)
    
    root.mainloop()