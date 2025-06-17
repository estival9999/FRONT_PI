#!/usr/bin/env python3
"""
Script de teste para verificar gravação e transcrição
"""

import time
from audio_recorder_standalone import AudioRecorder
import os

def test_transcription():
    print("=== TESTE DE GRAVAÇÃO E TRANSCRIÇÃO ===\n")
    
    # Cria instância do gravador
    recorder = AudioRecorder()
    print("✓ AudioRecorder criado")
    
    # Inicia gravação
    print("\n📢 Iniciando gravação de 5 segundos...")
    print("🎤 FALE ALGO AGORA! Por exemplo: 'Esta é uma reunião de teste com João e Maria'")
    
    recorder.start_recording()
    
    # Grava por 5 segundos
    for i in range(5, 0, -1):
        print(f"⏱️  {i} segundos restantes...")
        time.sleep(1)
    
    # Para gravação
    print("\n⏹️  Parando gravação...")
    audio_file = recorder.stop_recording()
    
    if audio_file and os.path.exists(audio_file):
        print(f"✓ Áudio salvo em: {audio_file}")
        
        # Verifica tamanho do arquivo
        file_size = os.path.getsize(audio_file)
        print(f"✓ Tamanho do arquivo: {file_size} bytes")
        
        if file_size > 0:
            # Transcreve
            print("\n🔄 Transcrevendo áudio...")
            transcription = recorder.transcribe_audio(audio_file)
            
            if transcription:
                print(f"\n✅ TRANSCRIÇÃO CONCLUÍDA:")
                print(f"📝 '{transcription}'")
            else:
                print("\n❌ Erro: Transcrição retornou vazia")
        else:
            print("\n❌ Erro: Arquivo de áudio está vazio")
            
        # Limpa arquivo temporário
        recorder.cleanup()
        print("\n✓ Arquivo temporário removido")
    else:
        print("\n❌ Erro: Não foi possível salvar o áudio")

if __name__ == "__main__":
    test_transcription()