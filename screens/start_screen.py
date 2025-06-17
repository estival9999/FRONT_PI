import tkinter as tk
from tkinter import ttk


class StartScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1a1a1a")
        self.controller = controller
        
        # Container principal para centralizar conteúdo
        container = tk.Frame(self, bg="#1a1a1a")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Botão circular grande
        self.start_button = tk.Button(
            container,
            text="INICIAR",
            width=10,
            height=5,
            bg="#4a90e2",
            fg="white",
            font=("Arial", 16, "bold"),
            relief="flat",
            activebackground="#5ba0f2",
            cursor="hand2",
            command=self.on_start_click
        )
        self.start_button.pack()
        
        # Adiciona efeitos de hover
        self.start_button.bind("<Enter>", self.on_hover)
        self.start_button.bind("<Leave>", self.on_leave)
        
        # Texto de versão no rodapé
        version_label = tk.Label(
            self,
            text="v1.0.0",
            bg="#1a1a1a",
            fg="#666666",
            font=("Arial", 9)
        )
        version_label.pack(side="bottom", pady=10)
    
    def on_hover(self, event):
        """Efeito hover - cor mais clara"""
        self.start_button.config(bg="#5ba0f2")
    
    def on_leave(self, event):
        """Remove efeito hover"""
        self.start_button.config(bg="#4a90e2")
    
    def on_start_click(self):
        """Ação ao clicar no botão iniciar"""
        self.controller.show_frame("ResponsibleScreen")


# Exemplo de uso standalone
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tela Inicial")
    root.geometry("800x600")
    root.configure(bg="#1a1a1a")
    
    # Simulando um controller básico
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Navegando para: {frame_name}")
    
    controller = DummyController()
    screen = StartScreen(root, controller)
    screen.pack(fill="both", expand=True)
    
    root.mainloop()