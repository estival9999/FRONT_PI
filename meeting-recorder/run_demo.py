#!/usr/bin/env python3
"""
Script para executar o demo da interface do aplicativo
"""

import subprocess
import sys
import os

def check_and_install_requirements():
    """Verifica e instala as dependências necessárias"""
    print("Verificando dependências...")
    
    try:
        import tkinter
        print("✓ tkinter já está instalado")
    except ImportError:
        print("✗ tkinter não encontrado - é necessário instalar via sistema")
        print("  Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  Fedora: sudo dnf install python3-tkinter")
        print("  macOS: já vem instalado com Python")
        return False
    
    # Verifica se o Pillow está instalado (necessário para algumas funcionalidades)
    try:
        import PIL
        print("✓ Pillow já está instalado")
    except ImportError:
        print("Instalando Pillow...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    
    return True

def main():
    """Executa o aplicativo"""
    print("=" * 50)
    print("DEMO - Interface do Gravador de Reuniões")
    print("Resolução: 320x240 pixels")
    print("=" * 50)
    
    # Verifica dependências
    if not check_and_install_requirements():
        print("\nPor favor, instale as dependências necessárias e tente novamente.")
        return
    
    # Muda para o diretório do projeto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print("\nIniciando aplicativo...")
    print("Navegue pelas telas usando os botões disponíveis.")
    print("\nFluxo das telas:")
    print("1. Tela Inicial (botão Iniciar)")
    print("2. Nome do Responsável")
    print("3. Objetivo da Reunião") 
    print("4. Gravação (timer e controles)")
    print("5. Informar Participantes")
    print("6. Confirmação dos Nomes")
    print("\nPressione Ctrl+C no terminal para encerrar.\n")
    
    # Executa o aplicativo principal
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    main()