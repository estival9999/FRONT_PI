import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class ResponsibleScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1a1a1a")
        self.controller = controller
        
        # Título no topo
        title_label = tk.Label(
            self,
            text="Responsável pela Reunião",
            bg="#1a1a1a",
            fg="white",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(50, 30))
        
        # Container para o campo de entrada
        input_container = tk.Frame(self, bg="#1a1a1a")
        input_container.pack(expand=True, fill="x", padx=50)
        
        # Campo de entrada
        self.name_entry = tk.Entry(
            input_container,
            font=("Arial", 14),
            bg="#2a2a2a",
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=10
        )
        self.name_entry.pack(fill="x", ipady=10)
        
        # Placeholder
        self.name_entry.insert(0, "Digite o nome do responsável")
        self.name_entry.config(fg="#666666")
        
        # Eventos para placeholder
        self.name_entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.name_entry.bind("<FocusOut>", self.on_entry_focus_out)
        self.name_entry.bind("<Return>", lambda e: self.on_next_click())
        
        # Container para botões no rodapé
        button_container = tk.Frame(self, bg="#1a1a1a")
        button_container.pack(side="bottom", fill="x", padx=50, pady=30)
        
        # Botão Próximo (alinhado à direita)
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
        self.next_button.bind("<Enter>", lambda e: self.next_button.config(bg="#5ba0f2"))
        self.next_button.bind("<Leave>", lambda e: self.next_button.config(bg="#4a90e2"))
    
    def on_entry_focus_in(self, event):
        """Remove placeholder ao focar"""
        if self.name_entry.get() == "Digite o nome do responsável":
            self.name_entry.delete(0, tk.END)
            self.name_entry.config(fg="white")
    
    def on_entry_focus_out(self, event):
        """Adiciona placeholder se campo estiver vazio"""
        if not self.name_entry.get():
            self.name_entry.insert(0, "Digite o nome do responsável")
            self.name_entry.config(fg="#666666")
    
    def on_next_click(self):
        """Valida e avança para próxima tela"""
        name = self.name_entry.get().strip()
        
        # Verifica se não é o placeholder ou campo vazio
        if not name or name == "Digite o nome do responsável":
            messagebox.showwarning(
                "Campo obrigatório",
                "Por favor, digite o nome do responsável pela reunião."
            )
            return
        
        # Salva o nome e avança
        if hasattr(self.controller, 'data'):
            self.controller.data['responsible'] = name
        
        self.controller.show_frame("ObjectiveScreen")
    
    def reset(self):
        """Limpa o campo ao voltar para esta tela"""
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, "Digite o nome do responsável")
        self.name_entry.config(fg="#666666")


# Exemplo de uso standalone
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Responsável pela Reunião")
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
    screen = ResponsibleScreen(root, controller)
    screen.pack(fill="both", expand=True)
    
    root.mainloop()