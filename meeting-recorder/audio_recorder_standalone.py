#!/usr/bin/env python3
"""
Classe AudioRecorder independente para gravação de áudio real
"""

import pyaudio
import wave
import threading
import tempfile
import requests
import json
import numpy as np
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class AudioRecorder:
    """Classe para gravação de áudio real"""
    
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # 16kHz ideal para Whisper
        self.MAX_CHUNK_SIZE = 20 * 1024 * 1024  # 20MB
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.is_paused = False
        self.recording_thread = None
        self.temp_file = None
        self.audio_levels = []  # Para visualização
        
    def start_recording(self):
        """Inicia a gravação de áudio"""
        if self.is_recording:
            return
            
        self.frames = []
        self.is_recording = True
        self.is_paused = False
        
        # Cria arquivo temporário
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        
        # Abre stream de áudio
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        # Inicia thread de gravação
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()
        
    def _record(self):
        """Thread de gravação"""
        while self.is_recording:
            if not self.is_paused:
                try:
                    data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                    self.frames.append(data)
                    
                    # Calcula nível de áudio para visualização
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    level = np.abs(audio_data).mean()
                    self.audio_levels.append(level)
                    
                    # Limita o tamanho do buffer de níveis
                    if len(self.audio_levels) > 50:
                        self.audio_levels.pop(0)
                        
                except Exception as e:
                    print(f"Erro na gravação: {e}")
                    
    def pause_recording(self):
        """Pausa a gravação"""
        self.is_paused = True
        
    def resume_recording(self):
        """Retoma a gravação"""
        self.is_paused = False
        
    def stop_recording(self):
        """Para a gravação e salva o arquivo"""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        
        # Aguarda thread terminar
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)  # Timeout de 2 segundos
            
        # Fecha stream
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            
        # Salva arquivo WAV
        if self.temp_file and self.frames:
            try:
                # Fecha o arquivo temporário antes de escrever
                self.temp_file.close()
                
                # Abre novamente para escrita
                wf = wave.open(self.temp_file.name, 'wb')
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(self.frames))
                wf.close()
                
                return self.temp_file.name
            except Exception as e:
                print(f"Erro ao salvar arquivo WAV: {e}")
                return None
            
        return None
        
    def get_audio_levels(self):
        """Retorna os níveis de áudio para visualização"""
        return self.audio_levels.copy()
        
    def transcribe_audio(self, audio_file):
        """Transcreve áudio usando Whisper API"""
        try:
            with open(audio_file, 'rb') as f:
                response = requests.post(
                    'https://api.openai.com/v1/audio/transcriptions',
                    headers={'Authorization': f'Bearer {OPENAI_API_KEY}'},
                    files={'file': f},
                    data={
                        'model': 'whisper-1',
                        'language': 'pt',
                        'response_format': 'text'
                    },
                    timeout=30  # Timeout de 30 segundos
                )
                
            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"Erro na transcrição: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("Erro: Timeout na transcrição (limite de 30 segundos excedido)")
            return None
        except Exception as e:
            print(f"Erro ao transcrever: {e}")
            return None
            
    def cleanup(self):
        """Limpa recursos"""
        # Fecha o arquivo temporário se ainda estiver aberto
        if self.temp_file:
            try:
                self.temp_file.close()
            except:
                pass
        
        # Tenta deletar o arquivo temporário
        if self.temp_file and hasattr(self.temp_file, 'name'):
            try:
                if os.path.exists(self.temp_file.name):
                    os.unlink(self.temp_file.name)
            except PermissionError as e:
                print(f"Aviso: Arquivo temporário em uso, será deletado posteriormente: {e}")
            except Exception as e:
                print(f"Aviso: Erro ao deletar arquivo temporário: {e}")
        
        # Termina o PyAudio
        try:
            self.audio.terminate()
        except:
            pass

# Exemplo de uso
if __name__ == "__main__":
    print("Teste do AudioRecorder")
    print("=" * 50)
    
    recorder = AudioRecorder()
    print("✓ AudioRecorder criado com sucesso")
    print(f"✓ Taxa de amostragem: {recorder.RATE} Hz")
    print(f"✓ Canais: {recorder.CHANNELS}")
    print(f"✓ API Key configurada: {'Sim' if OPENAI_API_KEY else 'Não'}")
    
    print("\nMétodos disponíveis:")
    methods = ['start_recording', 'pause_recording', 'resume_recording', 
               'stop_recording', 'get_audio_levels', 'transcribe_audio', 'cleanup']
    
    for method in methods:
        print(f"✓ {method}")