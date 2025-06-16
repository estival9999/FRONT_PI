/**
 * Unit tests for TranscriptionService
 */

import TranscriptionService from '../transcription';

// Mock dependencies
jest.mock('../whisperService');
jest.mock('../audioRecorder');

describe('TranscriptionService', () => {
  let transcriptionService;
  const mockApiKey = 'test-api-key';
  const mockParticipants = ['João Silva', 'Maria Santos', 'Pedro Oliveira'];

  beforeEach(() => {
    transcriptionService = new TranscriptionService(mockApiKey);
  });

  afterEach(() => {
    if (transcriptionService) {
      transcriptionService.destroy();
    }
  });

  describe('Initialization', () => {
    test('should initialize with participants', async () => {
      await transcriptionService.initialize(mockParticipants);
      
      expect(transcriptionService.participants).toEqual(mockParticipants);
      expect(transcriptionService.isInitialized).toBe(true);
    });

    test('should create fuzzy set for participant matching', async () => {
      await transcriptionService.initialize(mockParticipants);
      
      expect(transcriptionService.participantsFuzzy).toBeTruthy();
    });
  });

  describe('Participant Detection', () => {
    beforeEach(async () => {
      await transcriptionService.initialize(mockParticipants);
    });

    test('should detect participant with colon pattern', () => {
      const text = 'João Silva: Bom dia a todos!';
      const result = transcriptionService.detectParticipantInText(text);
      
      expect(result).toBeTruthy();
      expect(result.name).toBe('João Silva');
      expect(result.confidence).toBeGreaterThan(0.7);
    });

    test('should detect participant with dash pattern', () => {
      const text = 'Maria Santos - Obrigada pela presença';
      const result = transcriptionService.detectParticipantInText(text);
      
      expect(result).toBeTruthy();
      expect(result.name).toBe('Maria Santos');
    });

    test('should detect participant with fuzzy matching', () => {
      const text = 'Joao Silva: Sem acento também funciona';
      const result = transcriptionService.detectParticipantInText(text);
      
      expect(result).toBeTruthy();
      expect(result.name).toBe('João Silva');
    });

    test('should detect participant mentioned in text', () => {
      const text = 'Concordo com o que o Pedro Oliveira disse';
      const result = transcriptionService.detectParticipantInText(text);
      
      expect(result).toBeTruthy();
      expect(result.name).toBe('Pedro Oliveira');
      expect(result.context).toBe('mentioned');
    });

    test('should return null for unrecognized names', () => {
      const text = 'Carlos Mendes: Este nome não está na lista';
      const result = transcriptionService.detectParticipantInText(text);
      
      expect(result).toBeNull();
    });
  });

  describe('Transcription Processing', () => {
    test('should process transcription with segments', () => {
      const mockResult = {
        text: 'Transcrição completa',
        segments: [
          { text: 'João Silva: Olá', start: 0, end: 2 },
          { text: 'Maria Santos: Oi', start: 2, end: 4 }
        ]
      };

      transcriptionService.setParticipants(mockParticipants);
      const processed = transcriptionService.processTranscription(mockResult);

      expect(processed.segments[0].speaker).toBe('João Silva');
      expect(processed.segments[1].speaker).toBe('Maria Santos');
      expect(processed.detectedParticipants).toHaveLength(2);
    });
  });

  describe('Time Formatting', () => {
    test('should format time correctly', () => {
      expect(transcriptionService.formatTime(65)).toBe('01:05');
      expect(transcriptionService.formatTime(3661)).toBe('61:01');
    });

    test('should format SRT time correctly', () => {
      expect(transcriptionService.formatTimeSRT(65.5)).toBe('00:01:05,500');
      expect(transcriptionService.formatTimeSRT(3661.123)).toBe('01:01:01,123');
    });

    test('should format duration correctly', () => {
      expect(transcriptionService.formatDuration(65)).toBe('1min 5s');
      expect(transcriptionService.formatDuration(3661)).toBe('1h 1min 1s');
      expect(transcriptionService.formatDuration(45)).toBe('45s');
    });
  });

  describe('Export Formats', () => {
    const mockTranscriptionResult = {
      text: 'Transcrição de teste',
      timestamp: '2024-01-01T10:00:00Z',
      duration: 120,
      participants: mockParticipants,
      segments: [
        { text: 'Olá', start: 0, end: 2, speaker: 'João Silva' },
        { text: 'Oi', start: 2, end: 4, speaker: 'Maria Santos' }
      ],
      groupedSegments: [
        { speaker: 'João Silva', start: 0, end: 2, text: 'Olá' },
        { speaker: 'Maria Santos', start: 2, end: 4, text: 'Oi' }
      ],
      statistics: {
        wordCount: 2,
        segmentCount: 2,
        speakerStats: {
          'João Silva': { percentage: 50, duration: 2 },
          'Maria Santos': { percentage: 50, duration: 2 }
        }
      }
    };

    test('should export as text', () => {
      const text = transcriptionService.exportAsText(mockTranscriptionResult);
      
      expect(text).toContain('Transcrição da Reunião');
      expect(text).toContain('João Silva');
      expect(text).toContain('Maria Santos');
      expect(text).toContain('Olá');
      expect(text).toContain('Oi');
    });

    test('should export as SRT', () => {
      const srt = transcriptionService.exportAsSRT(mockTranscriptionResult);
      
      expect(srt).toContain('1\n00:00:00,000 --> 00:00:02,000');
      expect(srt).toContain('[João Silva] Olá');
      expect(srt).toContain('2\n00:00:02,000 --> 00:00:04,000');
      expect(srt).toContain('[Maria Santos] Oi');
    });

    test('should export as JSON', () => {
      const json = transcriptionService.exportAsJSON(mockTranscriptionResult);
      const parsed = JSON.parse(json);
      
      expect(parsed.text).toBe('Transcrição de teste');
      expect(parsed.participants).toEqual(mockParticipants);
    });

    test('should export as Markdown', () => {
      const md = transcriptionService.exportAsMarkdown(mockTranscriptionResult);
      
      expect(md).toContain('# Transcrição da Reunião');
      expect(md).toContain('## Estatísticas');
      expect(md).toContain('### João Silva');
      expect(md).toContain('### Maria Santos');
    });
  });

  describe('Statistics Generation', () => {
    test('should generate correct statistics', () => {
      const mockResult = {
        segments: [
          { text: 'Olá pessoal', start: 0, end: 2, speaker: 'João Silva' },
          { text: 'Oi João', start: 2, end: 4, speaker: 'Maria Santos' },
          { text: 'Vamos começar', start: 4, end: 6, speaker: 'João Silva' }
        ]
      };

      const stats = transcriptionService.generateTranscriptionStatistics(mockResult);

      expect(stats.segmentCount).toBe(3);
      expect(stats.wordCount).toBe(5);
      expect(stats.totalDuration).toBe(6);
      expect(stats.speakerStats['João Silva'].segmentCount).toBe(2);
      expect(stats.speakerStats['Maria Santos'].segmentCount).toBe(1);
    });
  });

  describe('Real-time Options', () => {
    test('should update real-time options', () => {
      const newOptions = {
        interval: 3000,
        language: 'en',
        temperature: 0.5
      };

      transcriptionService.updateRealtimeOptions(newOptions);

      expect(transcriptionService.realtimeOptions.interval).toBe(3000);
      expect(transcriptionService.realtimeOptions.language).toBe('en');
      expect(transcriptionService.realtimeOptions.temperature).toBe(0.5);
    });
  });

  describe('History Management', () => {
    test('should clear history', () => {
      transcriptionService.transcriptionHistory = ['test1', 'test2'];
      transcriptionService.transcriptionBuffer = ['buffer1'];

      transcriptionService.clearHistory();

      expect(transcriptionService.transcriptionHistory).toHaveLength(0);
      expect(transcriptionService.transcriptionBuffer).toHaveLength(0);
    });
  });
});