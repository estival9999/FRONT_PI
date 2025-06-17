#!/usr/bin/env python3
"""
Script de teste para validação fuzzy de nomes
"""

import json
import difflib
import sys

# Adiciona o diretório atual ao path
sys.path.append('.')

# Importa as funções do main.py
from main import load_funcionarios, validate_names

def test_fuzzy_validation():
    """Testa a validação fuzzy com casos reais"""
    
    print("=== TESTE DE VALIDAÇÃO FUZZY DE NOMES ===\n")
    
    # Casos de teste
    test_cases = [
        ["mateus estivau", "joao silva", "maria santo", "Pedro Oliveira"],
        ["Matheus estivao", "João Silva", "Maria Santos", "pedro oliveira"],
        ["ana costa", "carlos ferreira", "juliana mendes", "roberto alves"],
        ["fernanda lima", "lucas martins", "nome inexistente", "outro nome desconhecido"],
        ["mateus", "joão", "maria", "pedro"],  # Nomes parciais
        ["MATEUS ESTIVAL", "JOÃO SILVA", "MARIA SANTOS"],  # Maiúsculas
    ]
    
    for i, names in enumerate(test_cases, 1):
        print(f"Teste {i}: {names}")
        print("-" * 60)
        
        validated = validate_names(names)
        
        for result in validated:
            if result['corrigido']:
                print(f"✏️  '{result['original']}' → '{result['correto']}' (similaridade: {result['similaridade']*100:.1f}%)")
            else:
                if result['similaridade'] == 1.0 and result['original'] == result['correto']:
                    # Verifica se realmente existe na base de dados
                    funcionarios = load_funcionarios()
                    nomes_funcionarios = [f['nome'] for f in funcionarios['funcionarios']]
                    if result['correto'] in nomes_funcionarios:
                        print(f"✓  '{result['original']}' (encontrado exatamente)")
                    else:
                        print(f"❌ '{result['original']}' (não encontrado na base de dados)")
                else:
                    print(f"✓  '{result['original']}' (correspondência exata)")
        
        print("\n")
    
    # Teste específico com os casos solicitados
    print("=== CASOS ESPECÍFICOS SOLICITADOS ===")
    print("-" * 60)
    
    specific_cases = [
        "mateus estivau",
        "joao silva", 
        "maria santo"
    ]
    
    for name in specific_cases:
        validated = validate_names([name])
        result = validated[0]
        
        if result['corrigido']:
            print(f"'{result['original']}' → '{result['correto']}'")
            print(f"  Similaridade: {result['similaridade']*100:.1f}%")
            print(f"  Status: Corrigido ✏️")
        else:
            print(f"'{result['original']}' → mantido")
            print(f"  Status: Não precisou correção ✓")
        print()

if __name__ == "__main__":
    # Verifica se o arquivo de funcionários existe
    try:
        with open('data/funcionarios.json', 'r') as f:
            data = json.load(f)
            print(f"Base de dados carregada: {len(data['funcionarios'])} funcionários\n")
    except FileNotFoundError:
        print("ERRO: Arquivo 'data/funcionarios.json' não encontrado!")
        print("Por favor, certifique-se de que o arquivo existe no diretório 'data/'")
        exit(1)
    
    # Executa os testes
    test_fuzzy_validation()