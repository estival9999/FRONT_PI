# Sistema de Transcrição de Reuniões - Guia de Integração

## Visão Geral

Este sistema oferece um fluxo completo para gravação, transcrição e análise de reuniões usando as APIs da OpenAI (Whisper e GPT-4).

## Fluxo Completo do Sistema

### 1. Configuração Inicial
- Na tela inicial, clique em "⚙️ Configurações"
- Configure suas API Keys:
  - **OpenAI API Key (Whisper)**: Para transcrição de áudio
  - **OpenAI API Key (GPT-4)**: Para análise de reuniões
- As chaves são salvas localmente no Electron

### 2. Gravação de Áudio
1. **Tela Inicial**: Clique em "Iniciar"
2. **Responsável**: Informe o nome do responsável pela reunião
3. **Objetivo**: Descreva o objetivo da reunião
4. **Gravação**: 
   - Clique em "Iniciar" para começar a gravação
   - A transcrição em tempo real aparecerá na tela
   - Use "Pausar" para pausar temporariamente
   - Clique em "Parar" quando terminar

### 3. Cadastro de Participantes
1. Digite o nome do participante
2. Clique em "Gravar nome" para capturar áudio do nome
3. O sistema validará o nome contra o banco de funcionários
4. Participantes validados aparecem com ✓
5. Clique em "Finalizar" quando todos estiverem cadastrados

### 4. Processamento Final
- O sistema automaticamente:
  1. Processa a transcrição completa
  2. Identifica os falantes usando os nomes dos participantes
  3. Gera dois arquivos:
     - **Transcrição**: Arquivo numerado com a transcrição completa
     - **Análise**: Arquivo X_[nome] com análise GPT-4

## Estrutura dos Arquivos Gerados

### Arquivo de Transcrição
```
01_reuniao_projeto_15_03_2024_1430.txt
- ID sequencial
- Nome da reunião
- Data e hora
- Transcrição completa com timestamps
```

### Arquivo de Análise
```
X_01_reuniao_projeto_15_03_2024_1430.txt
- Pauta da reunião
- Participantes identificados
- Pendências
- Itens resolvidos
- Problemas identificados
- Tarefas atribuídas
- Resumo executivo
```

## Componentes Integrados

### 1. RecordingScreen.js
- Usa `TranscriptionService` para gravação e transcrição em tempo real
- Exibe feedback visual do áudio
- Mostra prévia da transcrição durante a gravação

### 2. ParticipantsForm.js
- Integra com `nameValidator` para validar nomes
- Usa `WhisperService` para transcrever nomes gravados
- Valida contra banco de funcionários

### 3. ParticipantsList.js
- Processa e salva a transcrição final
- Usa `fileManager` para gerenciar arquivos
- Integra análise GPT-4

### 4. Serviços

#### TranscriptionService
- Gravação de áudio com transcrição em tempo real
- Detecção de falantes usando fuzzy matching
- Exportação em múltiplos formatos

#### WhisperService
- Interface com API Whisper da OpenAI
- Transcrição com timestamps
- Suporte a múltiplos idiomas

#### NameValidator
- Validação fuzzy de nomes
- Integração com banco de funcionários
- Correção automática de nomes

#### FileManager
- Gerenciamento de arquivos de reunião
- Numeração sequencial automática
- Integração com análise GPT-4

## Configurações do Electron

### Preload.js
Expõe APIs seguras para:
- Gerenciamento de arquivos
- Configurações
- Diálogos do sistema

### Main.js
Implementa handlers para:
- Operações de arquivo
- Armazenamento de configurações
- Comunicação IPC

## Testes de Integração

Execute no console do navegador:
```javascript
testIntegration()
```

Isso verificará:
1. APIs do Electron disponíveis
2. Configuração de API Keys
3. Criação de diretórios
4. Salvamento de arquivos
5. Leitura de arquivos
6. Listagem de arquivos

## Troubleshooting

### Erro: "Configure suas API Keys primeiro"
- Acesse Configurações e adicione ambas as API Keys

### Erro: "Serviço não inicializado"
- Verifique se a API Key do Whisper está configurada
- Confirme permissões de microfone

### Transcrição não detecta falantes
- Certifique-se de cadastrar os participantes corretamente
- Grave os nomes claramente

### Análise GPT-4 falha
- Verifique a API Key do GPT-4
- O sistema usa análise local como fallback

## Melhorias Futuras

1. **Suporte a múltiplos idiomas**
2. **Exportação para Word/PDF**
3. **Integração com calendário**
4. **Backup automático na nuvem**
5. **Reconhecimento de voz melhorado**

## Estrutura de Pastas

```
/reunioes
  ├── 01_reuniao_projeto_15_03_2024_1430.txt
  ├── X_01_reuniao_projeto_15_03_2024_1430.txt
  ├── 02_daily_standup_16_03_2024_0900.txt
  └── X_02_daily_standup_16_03_2024_0900.txt
```

## Segurança

- API Keys armazenadas localmente
- Isolamento de contexto no Electron
- Validação de entrada de usuário
- Sanitização de nomes de arquivo