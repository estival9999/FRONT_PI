# Serviço de Transcrição com OpenAI Whisper

## Visão Geral

O `TranscriptionService` é um serviço completo para transcrição de áudio que integra com a API OpenAI Whisper. Ele oferece:

- ✅ Transcrição em tempo real durante a gravação
- ✅ Transcrição completa com alta precisão após finalizar
- ✅ Detecção automática de participantes com validação fuzzy
- ✅ Exportação em múltiplos formatos (TXT, SRT, JSON, Markdown)
- ✅ Estatísticas detalhadas da transcrição
- ✅ Suporte para múltiplos idiomas

## Instalação e Configuração

### 1. Dependências Necessárias

```bash
npm install openai fuzzyset
```

### 2. Configuração da API Key

Crie um arquivo `.env` na raiz do projeto:

```env
REACT_APP_OPENAI_API_KEY=sua-chave-api-aqui
```

## Uso Básico

### Inicialização

```javascript
import TranscriptionService from './services/transcription';

// Criar instância do serviço
const transcriptionService = new TranscriptionService(apiKey);

// Inicializar com lista de participantes
const participants = ['João Silva', 'Maria Santos', 'Pedro Oliveira'];
await transcriptionService.initialize(participants, {
  language: 'pt',
  interval: 5000 // Atualização em tempo real a cada 5 segundos
});
```

### Gravação com Transcrição em Tempo Real

```javascript
// Iniciar gravação
await transcriptionService.startRecording(
  // Callback para atualizações em tempo real
  (update) => {
    console.log('Texto parcial:', update.text);
    console.log('Participantes detectados:', update.participants);
  },
  // Callback para visualização de áudio (opcional)
  (visualization) => {
    console.log('Nível de áudio:', visualization.audioLevel);
  }
);

// Pausar/Retomar
transcriptionService.pauseRecording();
transcriptionService.resumeRecording();

// Parar e obter transcrição final
const result = await transcriptionService.stopRecording();
```

### Resultado da Transcrição

O resultado final inclui:

```javascript
{
  text: "Transcrição completa...",
  segments: [
    {
      text: "João Silva: Bom dia a todos",
      start: 0,
      end: 2.5,
      speaker: "João Silva",
      confidence: 0.95
    }
    // ... mais segmentos
  ],
  groupedSegments: [...], // Segmentos agrupados por falante
  statistics: {
    totalDuration: 120,
    wordCount: 450,
    speakerStats: {
      "João Silva": {
        wordCount: 150,
        duration: 40,
        percentage: 33.3
      }
      // ... outros participantes
    }
  },
  audioBlob: Blob, // Áudio gravado
  detectedSpeakers: [...], // Lista de falantes detectados
  timestamp: "2024-01-01T10:00:00Z"
}
```

## Recursos Avançados

### Detecção de Participantes

O serviço detecta automaticamente quem está falando usando:

1. **Padrões de Fala**: Reconhece padrões como "Nome:", "Nome -", etc.
2. **Validação Fuzzy**: Corrige pequenos erros de digitação/transcrição
3. **Contexto**: Usa transcrições anteriores para melhorar precisão

```javascript
// Configurar detecção de participantes
transcriptionService.setParticipantDetection(true); // Ativar/desativar

// Atualizar lista de participantes durante gravação
transcriptionService.setParticipants(['Novo Participante', ...]);
```

### Exportação em Múltiplos Formatos

```javascript
// Exportar como texto simples
const text = transcriptionService.exportAsText(result);

// Exportar como SRT (legendas)
const srt = transcriptionService.exportAsSRT(result);

// Exportar como JSON
const json = transcriptionService.exportAsJSON(result);

// Exportar como Markdown
const markdown = transcriptionService.exportAsMarkdown(result);
```

### Configurações de Transcrição

```javascript
// Atualizar opções em tempo real
transcriptionService.updateRealtimeOptions({
  interval: 3000,      // Intervalo de atualização (ms)
  language: 'en',      // Idioma
  temperature: 0.2,    // Precisão (0-1, menor = mais preciso)
  model: 'whisper-1'   // Modelo do Whisper
});
```

### Gerenciamento de Histórico

```javascript
// Obter histórico de transcrições
const history = transcriptionService.getTranscriptionHistory();

// Limpar histórico
transcriptionService.clearHistory();
```

## Tratamento de Erros

```javascript
try {
  await transcriptionService.initialize(participants);
} catch (error) {
  if (error.message.includes('microphone')) {
    console.error('Acesso ao microfone negado');
  } else if (error.message.includes('API')) {
    console.error('Erro na API OpenAI:', error);
  }
}
```

## Exemplos de Uso

### 1. Reunião com Múltiplos Participantes

```javascript
// Configurar para reunião
const participants = ['CEO João', 'CTO Maria', 'Dev Pedro'];
await transcriptionService.initialize(participants, {
  language: 'pt',
  interval: 5000,
  temperature: 0.1 // Alta precisão para reuniões importantes
});

// Iniciar gravação
await transcriptionService.startRecording(
  (update) => {
    // Mostrar transcrição em tempo real na UI
    updateTranscriptionUI(update.text);
    
    // Destacar quem está falando
    if (update.participants.length > 0) {
      highlightSpeaker(update.participants[0].name);
    }
  }
);
```

### 2. Transcrição de Entrevista

```javascript
// Configurar para entrevista
const participants = ['Entrevistador', 'Candidato'];
await transcriptionService.initialize(participants, {
  language: 'pt',
  prompt: 'Entrevista de emprego para vaga de desenvolvedor'
});

// Após terminar
const result = await transcriptionService.stopRecording();

// Gerar relatório em Markdown
const report = transcriptionService.exportAsMarkdown(result);
saveToFile('entrevista_transcricao.md', report);
```

### 3. Podcast/Gravação de Áudio

```javascript
// Configurar para podcast
await transcriptionService.initialize([], { // Sem participantes pré-definidos
  language: 'pt',
  interval: 10000 // Atualizações menos frequentes
});

// Gravar episódio completo
// ... gravação ...

// Exportar como SRT para legendas
const srt = transcriptionService.exportAsSRT(result);
saveToFile('podcast_legendas.srt', srt);
```

## Performance e Otimização

### Dicas de Performance

1. **Intervalo de Atualização**: Use intervalos maiores (10s+) para economizar requisições
2. **Tamanho do Buffer**: O serviço automaticamente gerencia buffers de áudio
3. **Processamento em Lote**: Chunks muito pequenos são ignorados automaticamente

### Limites da API

- Tamanho máximo de arquivo: 25MB
- Formatos suportados: mp3, mp4, mpeg, mpga, m4a, wav, webm
- Taxa de amostragem recomendada: 16kHz

## Solução de Problemas

### Problema: Transcrição em tempo real não funciona

```javascript
// Verificar estado do serviço
const state = transcriptionService.getState();
console.log('Estado:', state);

// Verificar se está processando
if (state.isProcessing) {
  console.log('Aguarde o processamento anterior terminar');
}
```

### Problema: Participantes não são detectados

```javascript
// Verificar se detecção está ativada
transcriptionService.setParticipantDetection(true);

// Verificar lista de participantes
console.log('Participantes:', transcriptionService.participants);

// Testar detecção manualmente
const detected = transcriptionService.detectParticipantInText('João: Olá');
console.log('Detectado:', detected);
```

### Problema: Erro de API

```javascript
// Verificar API key
if (!apiKey || apiKey === 'your-api-key-here') {
  console.error('API key inválida');
}

// Verificar quota da API
// Acesse: https://platform.openai.com/account/usage
```

## Segurança

1. **API Key**: Nunca exponha a API key no código cliente
2. **CORS**: Configure adequadamente se usar em produção
3. **Gravação**: Sempre peça permissão antes de gravar
4. **Armazenamento**: Criptografe transcrições sensíveis

## Próximos Passos

- [ ] Implementar speaker diarization mais avançada
- [ ] Adicionar suporte para múltiplos idiomas simultâneos
- [ ] Integrar com serviços de tradução
- [ ] Adicionar análise de sentimento
- [ ] Implementar resumo automático com GPT