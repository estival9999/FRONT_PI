#!/usr/bin/env python3
"""
Script de teste standalone para validação fuzzy de nomes
"""

import json
import difflib

def load_funcionarios():
    """Carrega a lista de funcionários do arquivo JSON"""
    try:
        with open('data/funcionarios.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar funcionários: {e}")
        return {"funcionarios": []}

def validate_names(transcribed_names):
    """
    Valida e corrige nomes transcritos usando correspondência fuzzy.
    
    Args:
        transcribed_names: Lista de nomes transcritos
        
    Returns:
        Lista de dicionários com informações sobre cada nome validado
    """
    funcionarios = load_funcionarios()
    nomes_funcionarios = [f['nome'] for f in funcionarios['funcionarios']]
    
    validated = []
    for name in transcribed_names:
        # Remove espaços extras e normaliza
        name = ' '.join(name.strip().split())
        
        # Busca correspondência mais próxima
        matches = difflib.get_close_matches(name, nomes_funcionarios, n=1, cutoff=0.6)
        
        if matches:
            correto = matches[0]
            # Calcula a similaridade
            ratio = difflib.SequenceMatcher(None, name.lower(), correto.lower()).ratio()
            
            validated.append({
                'original': name,
                'correto': correto,
                'corrigido': name.lower() != correto.lower(),
                'similaridade': ratio
            })
        else:
            # Nome não encontrado - mantém original
            validated.append({
                'original': name,
                'correto': name,
                'corrigido': False,
                'similaridade': 1.0
            })
    
    return validated

def test_fuzzy_validation():
    """Testa a validação fuzzy com casos reais"""
    
    print("=== TESTE DE VALIDAÇÃO FUZZY DE NOMES ===\n")
    
    # Carrega e mostra os funcionários disponíveis
    funcionarios = load_funcionarios()
    print("Funcionários na base de dados:")
    for func in funcionarios['funcionarios']:
        print(f"  - {func['nome']}")
    print("\n")
    
    # Casos de teste específicos solicitados
    print("=== CASOS ESPECÍFICOS SOLICITADOS ===")
    print("-" * 60)
    
    test_cases = [
        ("mateus estivau", "Mateus Estival"),    # Erro de digitação
        ("joao silva", "João Silva"),             # Falta acento
        ("maria santo", "Maria Santos"),          # Nome incompleto
        ("Matheus estivao", "Mateus Estival"),    # Variação do nome
        ("pedro oliveira", "Pedro Oliveira"),     # Apenas capitalização
        ("ana costa", "Ana Costa"),               # Apenas capitalização
        ("carlos ferreira", "Carlos Ferreira"),   # Apenas capitalização
        ("Nome Inexistente", None),               # Nome não encontrado
    ]
    
    for original, expected in test_cases:
        validated = validate_names([original])
        result = validated[0]
        
        print(f"\nEntrada: '{original}'")
        print(f"Resultado: '{result['correto']}'")
        
        if result['corrigido']:
            print(f"Status: ✏️  Corrigido")
            print(f"Similaridade: {result['similaridade']*100:.1f}%")
        else:
            if expected is None or result['correto'] == original:
                print(f"Status: ❌ Não encontrado (mantido como está)")
            else:
                print(f"Status: ✓ Correspondência exata")
        
        if expected and result['correto'] != expected:
            print(f"⚠️  ESPERADO: '{expected}' mas obteve '{result['correto']}'")
    
    print("\n" + "="*60 + "\n")
    
    # Teste em lote
    print("=== TESTE EM LOTE ===")
    print("-" * 60)
    
    batch_names = [
        "mateus estivau",
        "joao silva", 
        "maria santo",
        "Pedro Oliveira",
        "ana costa",
        "Nome Desconhecido"
    ]
    
    print(f"\nProcessando {len(batch_names)} nomes...")
    validated_batch = validate_names(batch_names)
    
    print("\nResultados:")
    for result in validated_batch:
        if result['corrigido']:
            print(f"  ✏️  '{result['original']}' → '{result['correto']}' ({result['similaridade']*100:.1f}%)")
        else:
            funcionarios = load_funcionarios()
            nomes_funcionarios = [f['nome'] for f in funcionarios['funcionarios']]
            if result['correto'] in nomes_funcionarios:
                print(f"  ✓  '{result['original']}' (encontrado)")
            else:
                print(f"  ❌ '{result['original']}' (não encontrado)")

if __name__ == "__main__":
    test_fuzzy_validation()