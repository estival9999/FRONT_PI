import tkinter as tk
from tkinter import ttk
import threading
import time

# Cores constantes
COLORS = {
    'bg': '#F0F4F8',
    'white': '#FFFFFF',
    'primary': '#4A90E2',
    'primary_hover': '#357ABD',
    'secondary': '#95A5A6',
    'secondary_hover': '#7F8C8D',
    'success': '#27AE60',
    'danger': '#E74C3C',
    'text': '#2C3E50',
    'text_light': '#7F8C8D',
    'border': '#E1E8ED'
}

# Fontes constantes
FONTS = {
    'title': ('Segoe UI', 24, 'bold'),
    'subtitle': ('Segoe UI', 16),
    'body': ('Segoe UI', 12),
    'small': ('Segoe UI', 10),
    'button': ('Segoe UI', 12, 'bold')
}


def create_title(parent, text, size='title'):
    """Cria um título padronizado"""
    title = tk.Label(
        parent,
        text=text,
        font=FONTS[size],
        bg=parent.cget('bg'),
        fg=COLORS['text']
    )
    return title


def create_styled_button(parent, text, command, style='primary', width=None):
    """Cria um botão estilizado com hover effect"""
    # Cores baseadas no estilo
    if style == 'primary':
        bg_color = COLORS['primary']
        hover_color = COLORS['primary_hover']
        text_color = COLORS['white']
    elif style == 'secondary':
        bg_color = COLORS['secondary']
        hover_color = COLORS['secondary_hover']
        text_color = COLORS['white']
    elif style == 'danger':
        bg_color = COLORS['danger']
        hover_color = '#C0392B'
        text_color = COLORS['white']
    else:  # ghost
        bg_color = COLORS['white']
        hover_color = COLORS['bg']
        text_color = COLORS['text']
    
    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=FONTS['button'],
        bg=bg_color,
        fg=text_color,
        bd=0,
        padx=30,
        pady=12,
        cursor='hand2',
        relief=tk.FLAT,
        activebackground=hover_color,
        activeforeground=text_color
    )
    
    if width:
        button.config(width=width)
    
    # Hover effects
    def on_enter(e):
        button.config(bg=hover_color)
    
    def on_leave(e):
        button.config(bg=bg_color)
    
    button.bind('<Enter>', on_enter)
    button.bind('<Leave>', on_leave)
    
    return button


def create_circular_button(parent, text, command, size=80, style='primary'):
    """Cria um botão circular"""
    # Canvas para desenhar o círculo
    canvas = tk.Canvas(
        parent,
        width=size,
        height=size,
        bg=parent.cget('bg'),
        highlightthickness=0
    )
    
    # Cores baseadas no estilo
    if style == 'primary':
        fill_color = COLORS['primary']
        hover_color = COLORS['primary_hover']
        text_color = COLORS['white']
    elif style == 'danger':
        fill_color = COLORS['danger']
        hover_color = '#C0392B'
        text_color = COLORS['white']
    else:
        fill_color = COLORS['secondary']
        hover_color = COLORS['secondary_hover']
        text_color = COLORS['white']
    
    # Desenhar círculo
    circle = canvas.create_oval(
        2, 2, size-2, size-2,
        fill=fill_color,
        outline='',
        width=0
    )
    
    # Adicionar texto
    text_item = canvas.create_text(
        size/2, size/2,
        text=text,
        fill=text_color,
        font=FONTS['button']
    )
    
    # Hover effects
    def on_enter(e):
        canvas.itemconfig(circle, fill=hover_color)
        canvas.config(cursor='hand2')
    
    def on_leave(e):
        canvas.itemconfig(circle, fill=fill_color)
        canvas.config(cursor='')
    
    # Click handler
    def on_click(e):
        # Animação de clique
        canvas.itemconfig(circle, fill=hover_color)
        canvas.after(100, lambda: canvas.itemconfig(circle, fill=fill_color))
        command()
    
    canvas.bind('<Enter>', on_enter)
    canvas.bind('<Leave>', on_leave)
    canvas.bind('<Button-1>', on_click)
    
    return canvas


def create_styled_entry(parent, placeholder="", width=40):
    """Cria um campo de entrada estilizado"""
    # Frame container
    entry_frame = tk.Frame(parent, bg=COLORS['white'], highlightthickness=1)
    entry_frame.config(highlightbackground=COLORS['border'], highlightcolor=COLORS['primary'])
    
    # Entry widget
    entry = tk.Entry(
        entry_frame,
        font=FONTS['body'],
        bg=COLORS['white'],
        fg=COLORS['text'],
        bd=0,
        width=width,
        insertbackground=COLORS['primary']
    )
    entry.pack(padx=15, pady=12)
    
    # Placeholder
    if placeholder:
        entry.insert(0, placeholder)
        entry.config(fg=COLORS['text_light'])
        
        def on_focus_in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=COLORS['text'])
        
        def on_focus_out(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=COLORS['text_light'])
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
    
    # Focus effects
    def on_entry_focus_in(e):
        entry_frame.config(highlightthickness=2)
    
    def on_entry_focus_out(e):
        entry_frame.config(highlightthickness=1)
    
    entry.bind('<FocusIn>', on_entry_focus_in, add='+')
    entry.bind('<FocusOut>', on_entry_focus_out, add='+')
    
    return entry_frame, entry


def create_styled_text(parent, placeholder="", width=40, height=5):
    """Cria um campo de texto multilinha estilizado"""
    # Frame container
    text_frame = tk.Frame(parent, bg=COLORS['white'], highlightthickness=1)
    text_frame.config(highlightbackground=COLORS['border'], highlightcolor=COLORS['primary'])
    
    # Text widget
    text = tk.Text(
        text_frame,
        font=FONTS['body'],
        bg=COLORS['white'],
        fg=COLORS['text'],
        bd=0,
        width=width,
        height=height,
        wrap=tk.WORD,
        insertbackground=COLORS['primary']
    )
    text.pack(padx=15, pady=12)
    
    # Placeholder
    if placeholder:
        text.insert('1.0', placeholder)
        text.config(fg=COLORS['text_light'])
        
        def on_focus_in(e):
            if text.get('1.0', 'end-1c') == placeholder:
                text.delete('1.0', tk.END)
                text.config(fg=COLORS['text'])
        
        def on_focus_out(e):
            if not text.get('1.0', 'end-1c').strip():
                text.insert('1.0', placeholder)
                text.config(fg=COLORS['text_light'])
        
        text.bind('<FocusIn>', on_focus_in)
        text.bind('<FocusOut>', on_focus_out)
    
    # Focus effects
    def on_text_focus_in(e):
        text_frame.config(highlightthickness=2)
    
    def on_text_focus_out(e):
        text_frame.config(highlightthickness=1)
    
    text.bind('<FocusIn>', on_text_focus_in, add='+')
    text.bind('<FocusOut>', on_text_focus_out, add='+')
    
    return text_frame, text


def create_styled_frame(parent, padding=40):
    """Cria um frame estilizado com bordas arredondadas (simulado)"""
    frame = tk.Frame(
        parent,
        bg=COLORS['white'],
        highlightthickness=1,
        highlightbackground=COLORS['border'],
        highlightcolor=COLORS['border']
    )
    
    # Padding interno
    inner_frame = tk.Frame(frame, bg=COLORS['white'])
    inner_frame.pack(expand=True, fill="both", padx=padding, pady=padding)
    
    return frame


def create_progress_bar(parent, width=300, height=6):
    """Cria uma barra de progresso customizada"""
    # Canvas para a barra
    canvas = tk.Canvas(
        parent,
        width=width,
        height=height,
        bg=COLORS['bg'],
        highlightthickness=0
    )
    
    # Barra de fundo
    canvas.create_rectangle(
        0, 0, width, height,
        fill=COLORS['border'],
        outline=''
    )
    
    # Barra de progresso
    progress_rect = canvas.create_rectangle(
        0, 0, 0, height,
        fill=COLORS['primary'],
        outline=''
    )
    
    def set_progress(value):
        """Define o progresso (0-100)"""
        progress_width = int(width * value / 100)
        canvas.coords(progress_rect, 0, 0, progress_width, height)
    
    canvas.set_progress = set_progress
    return canvas


def fade_in_widget(widget, duration=0.3):
    """Animação de fade in para um widget"""
    def animate():
        steps = 10
        delay = duration / steps
        
        for i in range(steps + 1):
            alpha = i / steps
            widget.update_idletasks()
            time.sleep(delay)
    
    # Executar em thread separada para não bloquear a UI
    thread = threading.Thread(target=animate)
    thread.daemon = True
    thread.start()


def fade_out_widget(widget, duration=0.3, callback=None):
    """Animação de fade out para um widget"""
    def animate():
        steps = 10
        delay = duration / steps
        
        for i in range(steps, -1, -1):
            alpha = i / steps
            widget.update_idletasks()
            time.sleep(delay)
        
        if callback:
            widget.after(0, callback)
    
    # Executar em thread separada para não bloquear a UI
    thread = threading.Thread(target=animate)
    thread.daemon = True
    thread.start()


def create_loading_spinner(parent, size=40, color=None):
    """Cria um spinner de carregamento animado"""
    if color is None:
        color = COLORS['primary']
    
    canvas = tk.Canvas(
        parent,
        width=size,
        height=size,
        bg=parent.cget('bg'),
        highlightthickness=0
    )
    
    # Criar arco
    arc = canvas.create_arc(
        5, 5, size-5, size-5,
        start=0,
        extent=60,
        outline=color,
        width=3,
        style='arc'
    )
    
    def animate():
        angle = 0
        while True:
            canvas.itemconfig(arc, start=angle)
            angle = (angle + 10) % 360
            canvas.update_idletasks()
            time.sleep(0.05)
    
    # Iniciar animação em thread separada
    thread = threading.Thread(target=animate)
    thread.daemon = True
    thread.start()
    
    return canvas


def show_tooltip(widget, text):
    """Mostra um tooltip ao passar o mouse sobre o widget"""
    tooltip = None
    
    def on_enter(e):
        nonlocal tooltip
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + widget.winfo_height() + 5
        
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            tooltip,
            text=text,
            font=FONTS['small'],
            bg=COLORS['text'],
            fg=COLORS['white'],
            padx=8,
            pady=4
        )
        label.pack()
    
    def on_leave(e):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None
    
    widget.bind('<Enter>', on_enter)
    widget.bind('<Leave>', on_leave)