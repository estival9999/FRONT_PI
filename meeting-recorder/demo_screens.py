"""
Demonstração das telas do aplicativo
"""
import tkinter as tk
from screens import (
    StartScreen,
    ResponsibleScreen,
    ObjectiveScreen,
    RecordingScreen,
    ParticipantsScreen,
    ConfirmationScreen
)

class ScreenDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Meeting Recorder - Demo")
        self.root.geometry("320x240")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a1a')
        
        # Dados da reunião
        self.meeting_data = {
            'responsible': '',
            'objective': '',
            'participants': [],
            'duration': 0
        }
        
        # Tela atual
        self.current_screen = None
        
        # Iniciar com a tela inicial
        self.show_start_screen()
        
    def clear_screen(self):
        """Remove a tela atual"""
        if self.current_screen:
            self.current_screen.destroy()
            
    def show_start_screen(self):
        """Mostra a tela inicial"""
        self.clear_screen()
        self.current_screen = StartScreen(
            self.root,
            on_start=self.show_responsible_screen
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
    def show_responsible_screen(self):
        """Mostra a tela do responsável"""
        self.clear_screen()
        self.current_screen = ResponsibleScreen(
            self.root,
            on_next=self.save_responsible,
            on_back=self.show_start_screen
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
    def save_responsible(self, name):
        """Salva o nome do responsável e vai para próxima tela"""
        self.meeting_data['responsible'] = name
        self.show_objective_screen()
        
    def show_objective_screen(self):
        """Mostra a tela do objetivo"""
        self.clear_screen()
        self.current_screen = ObjectiveScreen(
            self.root,
            on_next=self.save_objective,
            on_back=self.show_responsible_screen
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
    def save_objective(self, objective):
        """Salva o objetivo e vai para a tela de participantes"""
        self.meeting_data['objective'] = objective
        self.show_participants_screen()
        
    def show_participants_screen(self):
        """Mostra a tela de participantes"""
        self.clear_screen()
        self.current_screen = ParticipantsScreen(
            self.root,
            on_next=self.save_participants,
            on_back=self.show_objective_screen
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
    def save_participants(self, participants):
        """Salva os participantes e vai para a gravação"""
        self.meeting_data['participants'] = participants
        self.show_recording_screen()
        
    def show_recording_screen(self):
        """Mostra a tela de gravação"""
        self.clear_screen()
        self.current_screen = RecordingScreen(
            self.root,
            on_finish=self.finish_recording,
            on_back=self.show_participants_screen
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
    def finish_recording(self, duration):
        """Finaliza a gravação e vai para confirmação"""
        self.meeting_data['duration'] = duration
        self.show_confirmation_screen()
        
    def show_confirmation_screen(self):
        """Mostra a tela de confirmação"""
        self.clear_screen()
        self.current_screen = ConfirmationScreen(
            self.root,
            participants=self.meeting_data['participants'],
            on_confirm=self.save_meeting,
            on_back=self.show_recording_screen
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
    def save_meeting(self, confirmed_participants):
        """Salva a reunião finalizada"""
        self.meeting_data['participants'] = confirmed_participants
        
        # Mostrar resumo
        self.clear_screen()
        
        summary_frame = tk.Frame(self.root, bg='#1a1a1a')
        summary_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            summary_frame,
            text="Reunião Salva!",
            font=('Arial', 16, 'bold'),
            fg='#4caf50',
            bg='#1a1a1a'
        ).pack(pady=20)
        
        # Detalhes
        details = f"""
Responsável: {self.meeting_data['responsible']}
Objetivo: {self.meeting_data['objective'][:30]}...
Participantes: {len(self.meeting_data['participants'])}
Duração: {int(self.meeting_data['duration'])} segundos
        """
        
        tk.Label(
            summary_frame,
            text=details,
            font=('Arial', 10),
            fg='#f0f0f0',
            bg='#1a1a1a',
            justify=tk.LEFT
        ).pack(pady=10)
        
        # Botão nova reunião
        from utils.ui_components import StyledButton
        StyledButton(
            summary_frame,
            text="Nova Reunião",
            command=self.reset_and_start
        ).pack(pady=20)
        
    def reset_and_start(self):
        """Reseta os dados e volta ao início"""
        self.meeting_data = {
            'responsible': '',
            'objective': '',
            'participants': [],
            'duration': 0
        }
        self.show_start_screen()
        
    def run(self):
        """Inicia a aplicação"""
        self.root.mainloop()

if __name__ == "__main__":
    demo = ScreenDemo()
    demo.run()