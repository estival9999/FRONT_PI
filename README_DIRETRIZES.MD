# 📋 INSTRUÇÕES QUE DEVEM SER SEGUIDAS

## 📁 1. DOCUMENTAÇÃO OBRIGATÓRIA

### 1.1 Estrutura de Documentação
```
EXEC_FASES_CLAUDE/
├── README_FASE_1.md
├── README_FASE_2.md
├── README_FASE_3.md
└── ...
```

### 1.2 Conteúdo do README de cada fase
- **Detalhamento máximo** do que foi executado
- Código implementado
- Configurações realizadas
- Resultados dos testes
- Problemas encontrados e soluções aplicadas

### 1.3 Registro de Alterações
- Quando houver correções/melhorias em uma fase já documentada:
  - Acessar o README da fase correspondente
  - Adicionar ao final: `## Alterações - [DATA]`
  - Explicar detalhadamente o que foi modificado e por quê

## 🧪 2. PROCESSO DE TESTES

### 2.1 Teste Obrigatório
Após **CADA** implementação:
1. Executar teste para verificar funcionamento
2. Se houver problemas:
   - Informar o problema encontrado
   - Aplicar soluções
   - Testar novamente até funcionar
3. Após funcionamento confirmado:
   - Excluir arquivos de teste
   - Documentar no README da fase

### 2.2 Validação com Usuário
- Executar teste junto ao usuário
- **AGUARDAR** confirmação de que está OK
- Só prosseguir após receber instrução explícita

## ⚠️ 3. REGRAS DE PRESERVAÇÃO

### 3.1 Consulta Obrigatória
- **SEMPRE** consultar `README_REGRAS` antes de implementar
- Verificar histórico de modificações já realizadas
- **NUNCA** sobrescrever/modificar código funcional já testado

### 3.2 Prevenção de Desastres
- Não alterar implementações que já foram validadas
- Manter compatibilidade com código existente
- Documentar dependências entre módulos

## 🚀 4. CONTROLE DE VERSÃO

### 4.1 GitHub
- Repositório: `https://github.com/estival9999/AURALIS_CLAUDI.git`
- Faça essa conexão utilizando SSH, gere a chave e informe pro usuário adicioa-la no GITHUB
- Status: **PRIVADO** (seguro para chaves API)

### 4.2 Estratégia de Branches
```
main
├── fase-1-configuracao-inicial
├── fase-2-conexao-supabase
├── fase-3-implementacao-funcionalidades
└── ...
```

### 4.3 Processo de Commit
1. Completar fase 100%
2. Receber aprovação do usuário
3. Criar novo branch: `git checkout -b fase-X-descricao`
4. Fazer commit com mensagem descritiva
5. Push para o repositório

## 🛑 5. CRITÉRIOS DE PROGRESSÃO

### 5.1 Não Avançar Se:
- ❌ Etapa não está 100% concluída
- ❌ Funcionalidade não está testada
- ❌ Usuário não confirmou que está OK
- ❌ Documentação não foi criada/atualizada

### 5.2 Exemplo Específico
**Conexão com Supabase:**
- ✅ Deve conectar com credenciais reais do Supabase
- ❌ NÃO usar dados mockados ou salvos localmente
- ✅ Login deve funcionar com dados reais do banco
- ❌ NÃO prosseguir se não estiver 100% funcional

## 💬 6. INTERAÇÃO COM USUÁRIO

### 6.1 Quando Perguntar
- Precisar de credenciais específicas
- Dúvidas sobre requisitos de negócio
- Escolhas de implementação que afetem o usuário
- Confirmação antes de ações críticas

### 6.2 Processo de Interação
1. Formular pergunta clara e específica
2. **AGUARDAR** resposta do usuário
3. Só prosseguir após receber informação completa
4. Documentar decisão no README da fase

## 🎯 7. IMPLEMENTAÇÃO ESPECÍFICA

### 7.1 AÇÃO 1.2: Configuração da Conexão Python-Supabase
- Utilizar como instrução base: `@README_MCP`
- Seguir orientações do Model Context Protocol
- Implementar servidor MCP em Python
- Testar conexão com credenciais reais

---

## ✅ CHECKLIST ANTES DE CADA FASE

- [ ] README_REGRAS foi consultado?
- [ ] Documentação da fase anterior foi criada?
- [ ] Testes foram executados com sucesso?
- [ ] Arquivos de teste foram removidos?
- [ ] Usuário validou a implementação?
- [ ] Branch do Git foi criado?
- [ ] Código foi commitado?
- [ ] Está pronto para próxima fase?

---

**🔴 IMPORTANTE**: Estas instruções devem ser seguidas **RIGOROSAMENTE** em todas as fases do desenvolvimento. Qualquer desvio deve ser justificado e documentado.