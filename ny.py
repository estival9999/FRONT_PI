#!/usr/bin/env python3

import os
import subprocess
import sys
from datetime import datetime

def executar_comando(cmd):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def verificar_git():
    """Verifica se Git está instalado"""
    sucesso, _, _ = executar_comando("git --version")
    if not sucesso:
        print("❌ Git não está instalado!")
        print("Instale com: sudo apt install git")
        sys.exit(1)
    print("✅ Git encontrado")

def inicializar_repo():
    """Inicializa repositório se necessário"""
    if not os.path.exists(".git"):
        print("📁 Inicializando repositório Git...")
        executar_comando("git init")
        
        print("🔗 Adicionando repositório remoto...")
        executar_comando("git remote add origin git@github.com:estival9999/FRONT_PI.git")
    else:
        print("✅ Repositório Git já existe")

def configurar_usuario():
    """Configura usuário Git se necessário"""
    sucesso, nome, _ = executar_comando("git config user.name")
    if not sucesso or not nome.strip():
        print("👤 Configurando usuário Git...")
        nome = input("Digite seu nome: ")
        email = input("Digite seu email: ")
        executar_comando(f'git config user.name "{nome}"')
        executar_comando(f'git config user.email "{email}"')

def fazer_commit():
    """Adiciona arquivos e faz commit"""
    print("📦 Adicionando todos os arquivos...")
    executar_comando("git add .")
    
    mensagem = input("Digite a mensagem do commit (Enter para padrão): ")
    if not mensagem.strip():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mensagem = f"Atualização automática - {timestamp}"
    
    print("💬 Fazendo commit...")
    sucesso, _, erro = executar_comando(f'git commit -m "{mensagem}"')
    
    if not sucesso and "nothing to commit" in erro:
        print("ℹ️ Nenhuma alteração para commitar")
        return False
    
    return sucesso

def fazer_push():
    """Faz push para o repositório"""
    print("⬆️ Fazendo push para o GitHub...")
    executar_comando("git branch -M main")
    
    sucesso, saida, erro = executar_comando("git push -u origin main")
    
    if not sucesso:
        print(f"❌ Erro no push: {erro}")
        if "Permission denied" in erro:
            print("🔑 Verifique sua chave SSH ou use HTTPS:")
            print("git remote set-url origin https://github.com/estival9999/FRONT_PI.git")
        return False
    
    return True

def main():
    """Função principal"""
    print("🚀 Iniciando upload para GitHub...\n")
    
    # Verificações iniciais
    verificar_git()
    inicializar_repo()
    configurar_usuario()
    
    # Commit e push
    if fazer_commit():
        if fazer_push():
            print("\n✅ Upload concluído com sucesso!")
            print("🌐 Acesse: https://github.com/estival9999/FRONT_PI")
        else:
            print("\n❌ Falha no upload")
    else:
        print("\n⚠️ Nada para enviar")

if __name__ == "__main__":
    main()