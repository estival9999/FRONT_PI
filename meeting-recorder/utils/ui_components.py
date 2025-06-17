"""
Componentes UI reutilizáveis para o aplicativo de gravação de reuniões
"""
import tkinter as tk
from tkinter import ttk

# Cores do tema
COLORS = {
    'bg': '#1a1a1a',
    'primary': '#4a90e2',
    'primary_hover': '#357abd',
    'text': '#f0f0f0',
    'text_secondary': '#b0b0b0',
    'success': '#4caf50',
    'error': '#f44336',
    'border': '#333333'
}

class BaseScreen(tk.Frame):
    """Tela base com configurações padrão"""
    def __init__(self, parent, on_next=None, on_back=None):
        super().__init__(parent, bg=COLORS['bg'])
        self.parent = parent
        self.on_next = on_next
        self.on_back = on_back
        
        # Configurar tamanho da tela
        self.configure(width=320, height=240)
        self.pack_propagate(False)
        
    def create_title(self, text, pady=20):
        """Cria um título estilizado"""
        title = tk.Label(
            self,
            text=text,
            font=('Arial', 16, 'bold'),
            fg=COLORS['text'],
            bg=COLORS['bg']
        )
        title.pack(pady=pady)
        return title
    
    def create_subtitle(self, text, pady=5):
        """Cria um subtítulo"""
        subtitle = tk.Label(
            self,
            text=text,
            font=('Arial', 10),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg']
        )
        subtitle.pack(pady=pady)
        return subtitle

class RoundButton(tk.Canvas):
    """Botão redondo customizado"""
    def __init__(self, parent, size=80, text="", command=None, color=None):
        super().__init__(parent, width=size, height=size, bg=COLORS['bg'], highlightthickness=0)
        
        self.size = size
        self.color = color or COLORS['primary']
        self.hover_color = COLORS['primary_hover']
        self.command = command
        self.is_pressed = False
        
        # Criar círculo
        self.circle = self.create_oval(2, 2, size-2, size-2, fill=self.color, outline="")
        
        # Adicionar texto
        self.text = self.create_text(
            size/2, size/2,
            text=text,
            fill=COLORS['text'],
            font=('Arial', int(size/6), 'bold')
        )
        
        # Bind eventos
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        
    def on_hover(self, event):
        self.itemconfig(self.circle, fill=self.hover_color)
        
    def on_leave(self, event):
        if not self.is_pressed:
            self.itemconfig(self.circle, fill=self.color)
        
    def on_click(self, event):
        self.is_pressed = True
        self.itemconfig(self.circle, fill=self.hover_color)
        
    def on_release(self, event):
        self.is_pressed = False
        self.itemconfig(self.circle, fill=self.color)
        if self.command:
            self.command()

class StyledButton(tk.Button):
    """Botão estilizado padrão"""
    def __init__(self, parent, text, command=None, style='primary', width=None):
        colors = {
            'primary': (COLORS['primary'], COLORS['text']),
            'secondary': (COLORS['border'], COLORS['text']),
            'success': (COLORS['success'], COLORS['text']),
            'error': (COLORS['error'], COLORS['text'])
        }
        
        bg_color, fg_color = colors.get(style, colors['primary'])
        
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2',
            width=width
        )
        
        # Hover effect
        self.bind("<Enter>", lambda e: self.config(bg=COLORS['primary_hover']))
        self.bind("<Leave>", lambda e: self.config(bg=bg_color))

class StyledEntry(tk.Entry):
    """Campo de entrada estilizado"""
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(
            parent,
            bg='#2a2a2a',
            fg=COLORS['text'],
            font=('Arial', 11),
            bd=0,
            insertbackground=COLORS['text'],
            **kwargs
        )
        
        self.placeholder = placeholder
        self.placeholder_color = COLORS['text_secondary']
        self.normal_color = COLORS['text']
        
        if placeholder:
            self.insert(0, placeholder)
            self.config(fg=self.placeholder_color)
            
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        
    def on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.normal_color)
            
    def on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)
            
    def get_value(self):
        """Retorna o valor real (sem placeholder)"""
        value = self.get()
        return "" if value == self.placeholder else value

class StyledText(tk.Text):
    """Campo de texto multilinha estilizado"""
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(
            parent,
            bg='#2a2a2a',
            fg=COLORS['text'],
            font=('Arial', 11),
            bd=0,
            insertbackground=COLORS['text'],
            wrap=tk.WORD,
            **kwargs
        )
        
        self.placeholder = placeholder
        self.placeholder_color = COLORS['text_secondary']
        self.normal_color = COLORS['text']
        
        if placeholder:
            self.insert("1.0", placeholder)
            self.config(fg=self.placeholder_color)
            
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        
    def on_focus_in(self, event):
        if self.get("1.0", "end-1c") == self.placeholder:
            self.delete("1.0", tk.END)
            self.config(fg=self.normal_color)
            
    def on_focus_out(self, event):
        if not self.get("1.0", "end-1c").strip():
            self.insert("1.0", self.placeholder)
            self.config(fg=self.placeholder_color)
            
    def get_value(self):
        """Retorna o valor real (sem placeholder)"""
        value = self.get("1.0", "end-1c")
        return "" if value == self.placeholder else value

class NavigationButtons(tk.Frame):
    """Botões de navegação (Voltar/Próximo)"""
    def __init__(self, parent, on_back=None, on_next=None, next_text="Próximo"):
        super().__init__(parent, bg=COLORS['bg'])
        
        if on_back:
            back_btn = StyledButton(self, "Voltar", on_back, style='secondary')
            back_btn.pack(side=tk.LEFT, padx=5)
            
        if on_next:
            next_btn = StyledButton(self, next_text, on_next)
            next_btn.pack(side=tk.RIGHT, padx=5)

class AnimatedMicrophone(tk.Canvas):
    """Microfone animado para gravação"""
    def __init__(self, parent, size=60):
        super().__init__(parent, width=size, height=size, bg=COLORS['bg'], highlightthickness=0)
        
        self.size = size
        self.center = size / 2
        
        # Desenhar microfone
        self.mic_body = self.create_oval(
            self.center - 10, 10,
            self.center + 10, 35,
            fill=COLORS['primary'],
            outline=""
        )
        
        self.mic_stand = self.create_rectangle(
            self.center - 2, 35,
            self.center + 2, 45,
            fill=COLORS['primary'],
            outline=""
        )
        
        self.mic_base = self.create_rectangle(
            self.center - 8, 45,
            self.center + 8, 48,
            fill=COLORS['primary'],
            outline=""
        )
        
        # Ondas de som (inicialmente invisíveis)
        self.waves = []
        for i in range(3):
            wave = self.create_oval(
                self.center - 20 - i*10, self.center - 20 - i*10,
                self.center + 20 + i*10, self.center + 20 + i*10,
                outline=COLORS['primary'],
                width=2,
                state='hidden'
            )
            self.waves.append(wave)
        
        self.is_recording = False
        self.animation_id = None
        
    def start_animation(self):
        """Inicia a animação do microfone"""
        self.is_recording = True
        self.animate_waves()
        
    def stop_animation(self):
        """Para a animação do microfone"""
        self.is_recording = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
        for wave in self.waves:
            self.itemconfig(wave, state='hidden')
            
    def animate_waves(self, index=0):
        """Anima as ondas de som"""
        if not self.is_recording:
            return
            
        # Mostrar/esconder ondas em sequência
        for i, wave in enumerate(self.waves):
            if i == index:
                self.itemconfig(wave, state='normal')
            else:
                self.itemconfig(wave, state='hidden')
                
        # Próxima onda
        next_index = (index + 1) % len(self.waves)
        self.animation_id = self.after(300, lambda: self.animate_waves(next_index))

class CheckboxList(tk.Frame):
    """Lista com checkboxes"""
    def __init__(self, parent, items=None):
        super().__init__(parent, bg=COLORS['bg'])
        
        self.checkboxes = {}
        self.vars = {}
        
        if items:
            for item in items:
                self.add_item(item)
                
    def add_item(self, text):
        """Adiciona um item à lista"""
        var = tk.BooleanVar(value=True)
        self.vars[text] = var
        
        frame = tk.Frame(self, bg=COLORS['bg'])
        frame.pack(fill=tk.X, pady=2)
        
        checkbox = tk.Checkbutton(
            frame,
            text=text,
            variable=var,
            bg=COLORS['bg'],
            fg=COLORS['text'],
            selectcolor=COLORS['bg'],
            activebackground=COLORS['bg'],
            activeforeground=COLORS['text'],
            font=('Arial', 10)
        )
        checkbox.pack(side=tk.LEFT)
        
        self.checkboxes[text] = checkbox
        
    def get_selected(self):
        """Retorna lista dos itens selecionados"""
        return [text for text, var in self.vars.items() if var.get()]
        
    def clear(self):
        """Limpa a lista"""
        for widget in self.winfo_children():
            widget.destroy()
        self.checkboxes.clear()
        self.vars.clear()