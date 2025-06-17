#!/usr/bin/env python3
"""
Script de teste para verificar a classe AudioRecorder
"""

import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa apenas a classe AudioRecorder e constantes necessárias
from main import AudioRecorder, OPENAI_API_KEY

def test_audio_recorder():
    print("Testando AudioRecorder...")
    print(f"API Key configurada: {'Sim' if OPENAI_API_KEY else 'Não'}")
    
    # Verifica se a classe foi criada corretamente
    try:
        recorder = AudioRecorder()
        print("✓ Classe AudioRecorder criada com sucesso")
        
        # Verifica os métodos
        methods = ['start_recording', 'pause_recording', 'resume_recording', 
                   'stop_recording', 'get_audio_levels', 'transcribe_audio', 'cleanup']
        
        for method in methods:
            if hasattr(recorder, method):
                print(f"✓ Método {method} encontrado")
            else:
                print(f"✗ Método {method} NÃO encontrado")
                
        # Verifica parâmetros de áudio
        print(f"\nParâmetros de áudio:")
        print(f"- Taxa de amostragem: {recorder.RATE} Hz")
        print(f"- Canais: {recorder.CHANNELS}")
        print(f"- Tamanho do chunk: {recorder.CHUNK}")
        print(f"- Tamanho máximo do chunk: {recorder.MAX_CHUNK_SIZE / (1024*1024):.1f} MB")
        
    except Exception as e:
        print(f"✗ Erro ao criar AudioRecorder: {e}")

if __name__ == "__main__":
    test_audio_recorder()