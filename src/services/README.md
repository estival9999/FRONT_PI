# Audio Recording Services

Este diretório contém serviços para gravação e visualização de áudio, compatíveis com a API OpenAI Whisper.

## Instalação

Instale as dependências necessárias:

```bash
npm install wavesurfer.js wavesurfer.js/dist/plugins/record.js
```

Para usar com React:
```bash
npm install react react-dom
```

## Serviços Disponíveis

### 1. AudioRecorder (`audioRecorder.js`)

Serviço principal para gravação de áudio usando MediaRecorder API.

**Funcionalidades:**
- Iniciar, pausar, retomar e parar gravação
- Visualização em tempo real do nível de áudio
- Formato compatível com OpenAI Whisper (webm/opus)
- Download de gravações
- Conversão para base64

**Exemplo de uso:**
```javascript
import AudioRecorder from './services/audioRecorder';

const recorder = new AudioRecorder();

// Inicializar
await recorder.initialize();

// Configurar callback de visualização
recorder.setVisualizationCallback((data) => {
  console.log('Audio level:', data.audioLevel);
  // Usar data.waveformData para desenhar forma de onda
});

// Iniciar gravação
recorder.start();

// Pausar/Retomar
recorder.pause();
recorder.resume();

// Parar e obter áudio
const audioBlob = await recorder.stop();

// Download
recorder.downloadAudio(audioBlob, 'minha-gravacao.webm');
```

### 2. AudioVisualizer (`audioVisualizer.js`)

Integração com WaveSurfer.js para visualização avançada de áudio.

**Funcionalidades:**
- Visualização de forma de onda
- Barras de frequência
- Playback de áudio gravado
- Interface com plugin de gravação do WaveSurfer

**Exemplo de uso:**
```javascript
import AudioVisualizer from './services/audioVisualizer';

const visualizer = new AudioVisualizer(containerElement, {
  height: 128,
  waveColor: '#3B82F6',
  progressColor: '#1E40AF'
});

await visualizer.initialize();

// Iniciar gravação com visualização
await visualizer.startRecording();

// Carregar e visualizar áudio
await visualizer.loadAudio(audioBlob);

// Reproduzir
visualizer.play();
```

### 3. WhisperService (`whisperService.js`)

Serviço para transcrição de áudio usando OpenAI Whisper API.

**Funcionalidades:**
- Transcrição de áudio
- Tradução para inglês
- Suporte a timestamps
- Streaming de transcrição
- Processamento de áudios longos

**Exemplo de uso:**
```javascript
import WhisperService from './services/whisperService';

const whisper = new WhisperService('sua-api-key');

// Transcrever áudio
const result = await whisper.transcribe(audioBlob, {
  language: 'pt',
  prompt: 'Contexto opcional'
});

console.log(result.text);

// Transcrever com timestamps
const verboseResult = await whisper.transcribeWithTimestamps(audioBlob);
console.log(whisper.formatTranscriptionWithTimestamps(verboseResult));

// Traduzir para inglês
const translation = await whisper.translate(audioBlob);
```

## Componente React

O arquivo `AudioRecorderComponent.jsx` fornece um componente React completo com:
- Interface de gravação com botões de controle
- Visualização em tempo real
- Indicador de nível de áudio
- Contador de duração
- Integração com transcrição

**Uso no React:**
```jsx
import AudioRecorderComponent from './components/AudioRecorderComponent';

function App() {
  const handleRecordingComplete = (audioBlob) => {
    console.log('Gravação completa:', audioBlob);
  };

  const handleTranscription = (text) => {
    console.log('Transcrição:', text);
  };

  return (
    <AudioRecorderComponent
      onRecordingComplete={handleRecordingComplete}
      onTranscription={handleTranscription}
    />
  );
}
```

## Configuração da API

Para usar a transcrição com OpenAI Whisper, você precisa:

1. Obter uma API key da OpenAI
2. Configurar um endpoint backend para proxy das requisições (por segurança)
3. Ou usar a API diretamente (não recomendado em produção)

Exemplo de endpoint backend (Node.js/Express):
```javascript
app.post('/api/transcribe', upload.single('file'), async (req, res) => {
  const formData = new FormData();
  formData.append('file', req.file.buffer, req.file.originalname);
  formData.append('model', 'whisper-1');
  
  const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
    },
    body: formData
  });
  
  const result = await response.json();
  res.json(result);
});
```

## Formatos Suportados

- **Gravação:** webm (opus), ogg, mp3, wav
- **Whisper API:** mp3, mp4, mpeg, mpga, m4a, wav, webm
- **Tamanho máximo:** 25MB

## Notas Importantes

1. **Permissões:** O usuário precisa permitir acesso ao microfone
2. **HTTPS:** Em produção, é necessário HTTPS para acessar getUserMedia
3. **Compatibilidade:** Testado em Chrome, Firefox, Edge. Safari pode ter limitações
4. **Performance:** A visualização em tempo real pode impactar performance em dispositivos mais fracos