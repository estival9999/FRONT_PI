# 📼 Sistema de Gravação e Transcrição de Reuniões - Documentação Completa

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Fluxo de Funcionamento](#fluxo-de-funcionamento)
4. [Componentes e Funcionalidades](#componentes-e-funcionalidades)
5. [Instalação e Configuração](#instalação-e-configuração)
6. [Guia de Uso](#guia-de-uso)
7. [Estrutura Técnica](#estrutura-técnica)
8. [APIs e Integrações](#apis-e-integrações)
9. [Segurança](#segurança)
10. [FAQ e Solução de Problemas](#faq-e-solução-de-problemas)

---

## 🎯 Visão Geral

O **Sistema de Gravação e Transcrição de Reuniões** é uma aplicação desktop desenvolvida em Electron + React, projetada especificamente para rodar em uma resolução de 320x240 pixels. O sistema permite gravar reuniões, transcrever o áudio automaticamente usando OpenAI Whisper, validar participantes contra uma base de dados e gerar relatórios estruturados com análise via GPT-4.

### Principais Características:
- ✅ Interface minimalista otimizada para 320x240px
- ✅ Gravação de áudio em alta qualidade
- ✅ Transcrição automática via OpenAI Whisper
- ✅ Validação inteligente de nomes com fuzzy matching
- ✅ Geração automática de relatórios estruturados
- ✅ Análise semântica com GPT-4
- ✅ Armazenamento local organizado

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      ELECTRON (Main Process)                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   main.js   │  │  preload.js  │  │  File System     │  │
│  │             │  │              │  │  Management      │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
                               │ IPC
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    REACT (Renderer Process)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Components                         │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐   │  │
│  │  │ Start  │→│ Forms  │→│Recording│→│Participants│   │  │
│  │  └────────┘ └────────┘ └────────┘ └────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                     Services                          │  │
│  │  ┌────────────┐ ┌──────────────┐ ┌──────────────┐   │  │
│  │  │AudioRecorder│ │Transcription │ │NameValidator │   │  │
│  │  └────────────┘ └──────────────┘ └──────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
                               │ API Calls
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      EXTERNAL APIs                           │
│  ┌──────────────────┐           ┌──────────────────────┐   │
│  │  OpenAI Whisper  │           │     OpenAI GPT-4     │   │
│  │  (Transcription) │           │     (Analysis)       │   │
│  └──────────────────┘           └──────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Stack Tecnológica:
- **Frontend**: React 18 com React Router
- **Desktop**: Electron 36
- **Estilização**: Tailwind CSS
- **Transcrição**: OpenAI Whisper API
- **Análise**: OpenAI GPT-4 API
- **Validação**: FuzzySet.js
- **Áudio**: Web Audio API + MediaRecorder
- **Visualização**: WaveSurfer.js

---

## 🔄 Fluxo de Funcionamento

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   INÍCIO    │────▶│ RESPONSÁVEL  │────▶│   OBJETIVO   │
│  (Botão)    │     │   (Input)    │     │  (Textarea)  │
└─────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ VALIDAÇÃO   │◀────│PARTICIPANTES │◀────│   GRAVAÇÃO   │
│  (Lista)    │     │  (Gravação)  │     │ (Timer/Ctrl) │
└─────────────┘     └──────────────┘     └──────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│                    PROCESSAMENTO                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Transcrição │─▶│   Validação  │─▶│   Análise    │  │
│  │  (Whisper)  │  │ (FuzzyMatch) │  │   (GPT-4)    │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │  ARQUIVOS GERADOS   │
                  │ • Transcrição (.txt)│
                  │ • Análise (X_.txt)  │
                  └─────────────────────┘
```

### Descrição do Fluxo:

1. **Tela Inicial**: Botão redondo "Iniciar"
2. **Nome do Responsável**: Input para identificar quem conduz a reunião
3. **Objetivo da Reunião**: Textarea para descrever o propósito
4. **Gravação**: 
   - Timer em tempo real
   - Visualização de áudio
   - Controles: Play/Pause/Stop
   - Preview da transcrição
5. **Participantes**:
   - Gravação de áudio com nomes
   - Transcrição automática
6. **Validação**:
   - Lista de participantes detectados
   - Validação contra base de funcionários
   - Correção automática de nomes
7. **Processamento**:
   - Salvamento da transcrição completa
   - Geração de análise estruturada

---

## 🧩 Componentes e Funcionalidades

### Componentes React:

#### 1. StartScreen.js
- **Função**: Tela inicial com botão de início
- **Estado**: Verifica configuração de API keys
- **Props**: `onStart`, `onSettings`
- **Features**: Animação do botão, verificação de pré-requisitos

#### 2. ResponsibleForm.js
- **Função**: Captura nome do responsável
- **Estado**: `name` (string)
- **Validação**: Nome obrigatório, mínimo 3 caracteres
- **Armazenamento**: localStorage

#### 3. ObjectiveForm.js
- **Função**: Define objetivo da reunião
- **Estado**: `objective` (string)
- **Validação**: Texto obrigatório, mínimo 10 caracteres
- **Navegação**: Voltar/Próximo

#### 4. RecordingScreen.js
- **Função**: Gravação principal da reunião
- **Estados**: 
  - `isRecording` (boolean)
  - `isPaused` (boolean)
  - `duration` (number)
  - `transcriptionPreview` (string)
- **Features**:
  - Timer com formato HH:MM:SS
  - Visualização de áudio em canvas
  - Preview de transcrição em tempo real
  - Controles de gravação

#### 5. ParticipantsForm.js
- **Função**: Captura nomes dos participantes
- **Estado**: `participants` (array)
- **Features**:
  - Gravação individual por participante
  - Transcrição automática do nome
  - Lista editável

#### 6. ParticipantsList.js
- **Função**: Validação e processamento final
- **Features**:
  - Validação fuzzy de nomes
  - Geração de arquivos
  - Análise com GPT-4

### Serviços:

#### audioRecorder.js
```javascript
class AudioRecorder {
  - startRecording() // Inicia gravação
  - pauseRecording() // Pausa gravação
  - resumeRecording() // Retoma gravação
  - stopRecording() // Para e retorna blob
  - getAudioLevel() // Nível de áudio atual
  - downloadRecording() // Baixa arquivo
}
```

#### transcription.js
```javascript
class TranscriptionService {
  - initialize(validNames) // Configura serviço
  - startRecording(callbacks) // Inicia com transcrição
  - stopRecording() // Para e retorna resultado
  - transcribeAudio(blob) // Transcreve áudio
  - detectParticipants(text) // Identifica falantes
}
```

#### nameValidator.js
```javascript
class NameValidator {
  - validarNome(nome, threshold) // Valida nome
  - validarMultiplosNomes(nomes) // Valida lista
  - buscarPorParteNome(parte) // Busca parcial
}
```

#### fileManager.js
```javascript
class FileManager {
  - processMeeting(transcription, info) // Processa reunião
  - saveTranscription(content, info) // Salva transcrição
  - generateAnalysis(transcription) // Gera análise
  - getNextId() // Próximo ID sequencial
}
```

---

## 💻 Instalação e Configuração

### Pré-requisitos:
- Node.js 16+ 
- NPM 8+
- Windows 10/11
- Microfone funcional
- Conexão com internet (para APIs)

### Instalação:

```bash
# Clone o repositório
git clone https://github.com/estival9999/FRONT_PI.git
cd FRONT_PI

# Instale as dependências
npm install

# Execute o aplicativo
npm start
```

### Configuração Inicial:

1. **API Keys**: 
   - Clique no ícone ⚙️ na tela inicial
   - Insira sua OpenAI API Key
   - Insira sua GPT-4 API Key (opcional)

2. **Base de Funcionários**:
   - Edite `data/funcionarios.json`
   - Adicione funcionários da empresa

---

## 📖 Guia de Uso

### 1. Iniciando uma Gravação:

```
┌─────────────────────────┐
│   Audio Transcription   │
│                         │
│      ┌─────────┐       │
│      │ INICIAR │       │
│      └─────────┘       │
│                         │
│         ⚙️              │
└─────────────────────────┘
```

### 2. Preenchendo Informações:

**Nome do Responsável:**
```
┌─────────────────────────┐
│  Nome do Responsável    │
│ ┌─────────────────────┐ │
│ │ João Silva          │ │
│ └─────────────────────┘ │
│                         │
│ [Voltar]    [Próximo]   │
└─────────────────────────┘
```

**Objetivo da Reunião:**
```
┌─────────────────────────┐
│  Objetivo da Reunião    │
│ ┌─────────────────────┐ │
│ │ Discussão do novo   │ │
│ │ projeto de vendas   │ │
│ └─────────────────────┘ │
│                         │
│ [Voltar]    [Próximo]   │
└─────────────────────────┘
```

### 3. Durante a Gravação:

```
┌─────────────────────────┐
│     GRAVANDO...         │
│                         │
│      00:15:42          │
│                         │
│  ▂▄▆█▆▄▂▁▂▄▆▄▂▁       │
│                         │
│  [⏸️ Pausar] [⏹️ Parar] │
└─────────────────────────┘
```

### 4. Arquivos Gerados:

**Transcrição (01_joao_16_06_2025_1430.txt):**
```
======================================
TRANSCRIÇÃO DE REUNIÃO
======================================
Data: 16/06/2025
Horário: 14:30 - 16:00
Duração: 1h 30min
Responsável: João Silva
Objetivo: Discussão do novo projeto de vendas
Participantes: João Silva, Maria Santos, Pedro Costa

======================================
TRANSCRIÇÃO:
======================================
[00:00:00] João Silva: Boa tarde a todos...
[00:00:15] Maria Santos: Boa tarde, João...
```

**Análise (X_01_joao_16_06_2025_1430.txt):**
```
======================================
ANÁLISE DE REUNIÃO
======================================

PAUTA:
- Apresentação do novo projeto
- Discussão de metas
- Definição de prazos

PARTICIPANTES:
- João Silva (Responsável)
- Maria Santos
- Pedro Costa

PENDÊNCIAS:
- Revisar proposta comercial
- Agendar reunião com cliente

RESOLVIDOS:
- Definição da equipe
- Aprovação do orçamento

TAREFAS ATRIBUÍDAS:
- Maria: Preparar apresentação (até 20/06)
- Pedro: Contatar fornecedores (até 18/06)

RESUMO GERAL:
Reunião produtiva onde foram definidas...
```

---

## 🔧 Estrutura Técnica

### Estrutura de Diretórios:
```
FRONT_PI/
├── main.js              # Processo principal Electron
├── preload.js           # Bridge de segurança
├── package.json         # Configurações e dependências
├── src/
│   ├── App.js          # Componente principal
│   ├── index.js        # Entrada React
│   ├── index.css       # Estilos globais
│   ├── components/     # Componentes React
│   ├── services/       # Serviços de negócio
│   └── utils/          # Utilitários
├── data/
│   └── funcionarios.json # Base de funcionários
├── reunioes/           # Arquivos de reunião
└── dist-electron/      # Build final
```

### Configurações Importantes:

**package.json:**
```json
{
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "dev": "vite",
    "build": "vite build",
    "electron-dev": "node electron-dev.js"
  }
}
```

**vite.config.js:**
```javascript
{
  base: './',
  esbuild: {
    loader: 'jsx',
    include: /src\/.*\.js$/
  }
}
```

---

## 🔌 APIs e Integrações

### OpenAI Whisper API:
- **Endpoint**: `https://api.openai.com/v1/audio/transcriptions`
- **Modelo**: `whisper-1`
- **Formatos**: webm, mp3, mp4, wav
- **Limite**: 25MB por arquivo
- **Custo**: ~$0.006/minuto

### OpenAI GPT-4 API:
- **Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Modelo**: `gpt-4-turbo-preview`
- **Tokens**: ~2000 por análise
- **Custo**: ~$0.02/análise

### Configuração de API:
```javascript
// .env
OPENAI_API_KEY=sk-...
GPT4_API_KEY=sk-...
```

---

## 🔒 Segurança

### Context Isolation:
```javascript
// preload.js
contextBridge.exposeInMainWorld('electronAPI', {
  saveAudio: (data) => ipcRenderer.invoke('save-audio', data),
  saveTranscription: (data) => ipcRenderer.invoke('save-transcription', data)
});
```

### Validações:
- Input sanitization em todos os formulários
- Validação de tipos de arquivo
- Limite de tamanho de gravação
- Rate limiting nas APIs

### Armazenamento:
- Arquivos salvos localmente
- Sem upload para nuvem
- Criptografia opcional

---

## ❓ FAQ e Solução de Problemas

### Perguntas Frequentes:

**P: Quanto custa usar o sistema?**
R: Aproximadamente $0.40 por hora de gravação (transcrição + análise).

**P: Funciona offline?**
R: A gravação funciona offline, mas transcrição e análise precisam de internet.

**P: Quais idiomas são suportados?**
R: Português, inglês, espanhol e mais 90 idiomas pelo Whisper.

**P: Posso usar em reuniões longas?**
R: Sim, o sistema divide automaticamente áudios longos.

### Problemas Comuns:

**Erro: "API Key inválida"**
- Verifique se a key está correta
- Confirme se tem créditos na OpenAI

**Erro: "Microfone não encontrado"**
- Verifique permissões do Windows
- Teste o microfone em outras aplicações

**Erro: "Falha ao salvar arquivo"**
- Verifique permissões da pasta
- Confirme espaço em disco

### Requisitos Mínimos:
- **CPU**: Dual-core 2GHz+
- **RAM**: 4GB
- **Disco**: 1GB livre
- **OS**: Windows 10 build 1903+
- **Internet**: 10 Mbps para upload

---

## 📞 Suporte

- **GitHub Issues**: https://github.com/estival9999/FRONT_PI/issues
- **Email**: estival9999@gmail.com
- **Documentação**: Este arquivo

---

## 📄 Licença

Este projeto é proprietário. Todos os direitos reservados.

---

*Última atualização: 16/06/2025*