/**
 * Transcription Service
 * Complete service for audio transcription with OpenAI Whisper API
 * Includes real-time transcription, participant detection, and fuzzy matching
 */

import FuzzySet from 'fuzzyset';
import WhisperService from './whisperService.js';
import AudioRecorder from './audioRecorder.js';

class TranscriptionService {
  constructor(apiKey) {
    this.whisperService = new WhisperService(apiKey);
    this.audioRecorder = new AudioRecorder();
    this.participants = [];
    this.participantsFuzzy = null;
    this.transcriptionBuffer = [];
    this.isInitialized = false;
    this.realtimeInterval = null;
    this.realtimeCallback = null;
    this.participantDetectionEnabled = true;
    this.transcriptionHistory = [];
    this.lastProcessedChunkIndex = 0;
    this.audioChunksBuffer = [];
    this.isProcessingRealtime = false;
    this.realtimeOptions = {
      interval: 5000, // Process audio every 5 seconds
      language: 'pt', // Default to Portuguese
      model: 'whisper-1',
      temperature: 0.2, // Lower temperature for more accurate transcription
      prompt: null
    };
  }

  /**
   * Initialize the transcription service
   * @param {Array} participants - List of participant names
   * @param {Object} options - Initialization options
   * @returns {Promise<boolean>} Success status
   */
  async initialize(participants = [], options = {}) {
    try {
      // Initialize audio recorder
      await this.audioRecorder.initialize();

      // Set up participants for fuzzy matching
      this.setParticipants(participants);

      // Apply options
      this.realtimeOptions = { ...this.realtimeOptions, ...options };

      // Set up real-time data collection
      this.audioRecorder.setDataAvailableCallback((chunk) => {
        this.audioChunksBuffer.push(chunk);
      });

      this.isInitialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize transcription service:', error);
      throw error;
    }
  }

  /**
   * Set participants for name detection
   * @param {Array} participants - Array of participant names
   */
  setParticipants(participants) {
    this.participants = participants;
    if (participants.length > 0) {
      // Create fuzzy set for participant name matching
      this.participantsFuzzy = FuzzySet(participants);
    }
  }

  /**
   * Start recording with real-time transcription
   * @param {Function} onTranscriptionUpdate - Callback for transcription updates
   * @param {Function} onVisualizationUpdate - Callback for audio visualization
   * @returns {Promise<void>}
   */
  async startRecording(onTranscriptionUpdate, onVisualizationUpdate) {
    if (!this.isInitialized) {
      throw new Error('Transcription service not initialized');
    }

    // Set callbacks
    this.realtimeCallback = onTranscriptionUpdate;
    if (onVisualizationUpdate) {
      this.audioRecorder.setVisualizationCallback(onVisualizationUpdate);
    }

    // Start recording
    this.audioRecorder.start(1000); // Collect data every second
    
    // Start real-time transcription processing
    this.startRealtimeTranscription();
  }

  /**
   * Start real-time transcription processing
   */
  startRealtimeTranscription() {
    // Clear any existing interval
    if (this.realtimeInterval) {
      clearInterval(this.realtimeInterval);
    }

    // Process audio chunks periodically
    this.realtimeInterval = setInterval(async () => {
      if (this.audioChunksBuffer.length > 0 && !this.isProcessingRealtime) {
        await this.processRealtimeChunk();
      }
    }, this.realtimeOptions.interval);
  }

  /**
   * Process a chunk of audio for real-time transcription
   */
  async processRealtimeChunk() {
    if (this.isProcessingRealtime || this.audioChunksBuffer.length === 0) {
      return;
    }

    this.isProcessingRealtime = true;

    try {
      // Create blob from buffered chunks
      const chunks = this.audioChunksBuffer.splice(0, this.audioChunksBuffer.length);
      const audioBlob = new Blob(chunks, { type: 'audio/webm' });

      // Skip if blob is too small
      if (audioBlob.size < 1000) {
        this.isProcessingRealtime = false;
        return;
      }

      // Generate context prompt from recent transcriptions
      const contextPrompt = this.generateContextPrompt();

      // Transcribe the chunk
      const result = await this.whisperService.transcribe(audioBlob, {
        ...this.realtimeOptions,
        prompt: contextPrompt,
        response_format: 'verbose_json'
      });

      if (result && result.text) {
        // Process the transcription
        const processedResult = this.processTranscription(result);
        
        // Add to history
        this.transcriptionHistory.push(processedResult);

        // Call the callback with the update
        if (this.realtimeCallback) {
          this.realtimeCallback({
            text: processedResult.text,
            segments: processedResult.segments,
            participants: processedResult.detectedParticipants,
            timestamp: new Date().toISOString(),
            isPartial: true
          });
        }
      }
    } catch (error) {
      console.error('Real-time transcription error:', error);
    } finally {
      this.isProcessingRealtime = false;
    }
  }

  /**
   * Generate context prompt from recent transcriptions
   * @returns {string} Context prompt
   */
  generateContextPrompt() {
    if (this.transcriptionHistory.length === 0) {
      // Initial prompt with participant names
      if (this.participants.length > 0) {
        return `Conversa entre: ${this.participants.join(', ')}. `;
      }
      return null;
    }

    // Get last few transcriptions for context
    const recentHistory = this.transcriptionHistory.slice(-3);
    const context = recentHistory.map(h => h.text).join(' ');
    
    // Limit context length
    return context.slice(-500);
  }

  /**
   * Process transcription result with participant detection
   * @param {Object} result - Raw transcription result
   * @returns {Object} Processed result
   */
  processTranscription(result) {
    const processed = {
      text: result.text,
      segments: result.segments || [],
      detectedParticipants: [],
      duration: result.duration
    };

    // Detect participants in segments
    if (this.participantDetectionEnabled && this.participantsFuzzy && result.segments) {
      processed.segments = result.segments.map(segment => {
        const detectedParticipant = this.detectParticipantInText(segment.text);
        if (detectedParticipant) {
          segment.speaker = detectedParticipant.name;
          segment.confidence = detectedParticipant.confidence;
          
          // Add to detected participants list
          if (!processed.detectedParticipants.find(p => p.name === detectedParticipant.name)) {
            processed.detectedParticipants.push(detectedParticipant);
          }
        }
        return segment;
      });
    }

    return processed;
  }

  /**
   * Detect participant name in text using fuzzy matching
   * @param {string} text - Text to analyze
   * @returns {Object|null} Detected participant info
   */
  detectParticipantInText(text) {
    if (!this.participantsFuzzy || !text) {
      return null;
    }

    // Common patterns for speaker identification in Portuguese
    const speakerPatterns = [
      /^([A-Za-zÀ-ÿ\s]+):\s*/i, // Name followed by colon
      /^([A-Za-zÀ-ÿ\s]+)\s*-\s*/i, // Name followed by dash
      /^([A-Za-zÀ-ÿ\s]+)\s*falou:\s*/i, // "Name spoke:"
      /^([A-Za-zÀ-ÿ\s]+)\s*disse:\s*/i, // "Name said:"
      /^([A-Za-zÀ-ÿ\s]+)\s*perguntou:\s*/i, // "Name asked:"
      /^([A-Za-zÀ-ÿ\s]+)\s*respondeu:\s*/i, // "Name answered:"
    ];

    for (const pattern of speakerPatterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        const potentialName = match[1].trim();
        
        // Try fuzzy matching
        const fuzzyResults = this.participantsFuzzy.get(potentialName);
        if (fuzzyResults && fuzzyResults.length > 0) {
          const [confidence, matchedName] = fuzzyResults[0];
          
          // Accept match if confidence is above threshold
          if (confidence > 0.7) {
            return {
              name: matchedName,
              confidence: confidence,
              originalText: potentialName
            };
          }
        }
      }
    }

    // Try to find participant names mentioned in the text
    const words = text.split(/\s+/);
    for (let i = 0; i < words.length; i++) {
      // Try single word
      const fuzzyResults = this.participantsFuzzy.get(words[i]);
      if (fuzzyResults && fuzzyResults.length > 0) {
        const [confidence, matchedName] = fuzzyResults[0];
        if (confidence > 0.8) {
          return {
            name: matchedName,
            confidence: confidence,
            context: 'mentioned'
          };
        }
      }

      // Try two-word combinations for full names
      if (i < words.length - 1) {
        const twoWords = `${words[i]} ${words[i + 1]}`;
        const fuzzyResults2 = this.participantsFuzzy.get(twoWords);
        if (fuzzyResults2 && fuzzyResults2.length > 0) {
          const [confidence, matchedName] = fuzzyResults2[0];
          if (confidence > 0.75) {
            return {
              name: matchedName,
              confidence: confidence,
              context: 'mentioned'
            };
          }
        }
      }
    }

    return null;
  }

  /**
   * Pause recording
   */
  pauseRecording() {
    this.audioRecorder.pause();
    // Keep real-time processing active to process buffered chunks
  }

  /**
   * Resume recording
   */
  resumeRecording() {
    this.audioRecorder.resume();
  }

  /**
   * Stop recording and get final transcription
   * @returns {Promise<Object>} Final transcription result
   */
  async stopRecording() {
    // Stop real-time processing
    if (this.realtimeInterval) {
      clearInterval(this.realtimeInterval);
      this.realtimeInterval = null;
    }

    // Process any remaining chunks
    if (this.audioChunksBuffer.length > 0) {
      await this.processRealtimeChunk();
    }

    // Stop recording and get the complete audio
    const audioBlob = await this.audioRecorder.stop();

    if (!audioBlob) {
      return null;
    }

    try {
      // Perform final complete transcription for best accuracy
      const finalResult = await this.performFinalTranscription(audioBlob);
      
      return finalResult;
    } catch (error) {
      console.error('Final transcription error:', error);
      throw error;
    }
  }

  /**
   * Perform final transcription with enhanced processing
   * @param {Blob} audioBlob - Complete audio recording
   * @returns {Promise<Object>} Final transcription result
   */
  async performFinalTranscription(audioBlob) {
    // Generate comprehensive prompt with all participant names
    let prompt = '';
    if (this.participants.length > 0) {
      prompt = `Esta é uma transcrição de uma reunião com os seguintes participantes: ${this.participants.join(', ')}. `;
      prompt += 'Por favor, identifique quem está falando quando possível. ';
    }

    // Transcribe with detailed output
    const result = await this.whisperService.transcribeWithTimestamps(audioBlob, {
      language: this.realtimeOptions.language,
      model: this.realtimeOptions.model,
      temperature: 0.1, // Lower temperature for final transcription
      prompt: prompt
    });

    // Process the final result
    const processedResult = this.processTranscription(result);

    // Enhance with speaker diarization if possible
    const enhancedResult = this.enhanceSpeakerIdentification(processedResult);

    // Generate summary statistics
    const statistics = this.generateTranscriptionStatistics(enhancedResult);

    return {
      ...enhancedResult,
      statistics,
      audioBlob,
      duration: this.audioRecorder.getDuration(),
      timestamp: new Date().toISOString(),
      isPartial: false,
      participants: this.participants,
      detectedSpeakers: this.extractUniqueSpeakers(enhancedResult)
    };
  }

  /**
   * Enhance speaker identification using context
   * @param {Object} result - Transcription result
   * @returns {Object} Enhanced result
   */
  enhanceSpeakerIdentification(result) {
    if (!result.segments || result.segments.length === 0) {
      return result;
    }

    const enhanced = { ...result };
    let lastSpeaker = null;

    // Pass 1: Identify speakers based on patterns
    enhanced.segments = enhanced.segments.map((segment, index) => {
      // Check if speaker was already detected
      if (segment.speaker) {
        lastSpeaker = segment.speaker;
        return segment;
      }

      // Try to detect speaker
      const detected = this.detectParticipantInText(segment.text);
      if (detected) {
        segment.speaker = detected.name;
        segment.confidence = detected.confidence;
        lastSpeaker = detected.name;
      } else if (lastSpeaker && index > 0) {
        // Check if this seems like continuation of previous speaker
        const timeDiff = segment.start - enhanced.segments[index - 1].end;
        if (timeDiff < 2.0) { // Less than 2 seconds gap
          segment.speaker = lastSpeaker;
          segment.confidence = 0.6; // Lower confidence for inferred speaker
        }
      }

      return segment;
    });

    // Pass 2: Group consecutive segments by the same speaker
    const groupedSegments = [];
    let currentGroup = null;

    enhanced.segments.forEach(segment => {
      if (!currentGroup || currentGroup.speaker !== segment.speaker) {
        // Start new group
        currentGroup = {
          speaker: segment.speaker || 'Não identificado',
          start: segment.start,
          end: segment.end,
          text: segment.text,
          segments: [segment]
        };
        groupedSegments.push(currentGroup);
      } else {
        // Add to current group
        currentGroup.end = segment.end;
        currentGroup.text += ' ' + segment.text;
        currentGroup.segments.push(segment);
      }
    });

    enhanced.groupedSegments = groupedSegments;
    return enhanced;
  }

  /**
   * Extract unique speakers from transcription
   * @param {Object} result - Transcription result
   * @returns {Array} Unique speakers
   */
  extractUniqueSpeakers(result) {
    const speakers = new Map();

    if (result.segments) {
      result.segments.forEach(segment => {
        if (segment.speaker) {
          if (!speakers.has(segment.speaker)) {
            speakers.set(segment.speaker, {
              name: segment.speaker,
              segmentCount: 0,
              totalDuration: 0,
              firstAppearance: segment.start
            });
          }
          
          const speaker = speakers.get(segment.speaker);
          speaker.segmentCount++;
          speaker.totalDuration += (segment.end - segment.start);
        }
      });
    }

    return Array.from(speakers.values()).sort((a, b) => a.firstAppearance - b.firstAppearance);
  }

  /**
   * Generate transcription statistics
   * @param {Object} result - Transcription result
   * @returns {Object} Statistics
   */
  generateTranscriptionStatistics(result) {
    const stats = {
      totalDuration: 0,
      wordCount: 0,
      segmentCount: 0,
      speakerStats: {},
      averageSegmentDuration: 0,
      transcriptionConfidence: 0
    };

    if (!result.segments || result.segments.length === 0) {
      return stats;
    }

    // Calculate basic statistics
    stats.segmentCount = result.segments.length;
    let totalConfidence = 0;
    let confidenceCount = 0;

    result.segments.forEach(segment => {
      const duration = segment.end - segment.start;
      stats.totalDuration = Math.max(stats.totalDuration, segment.end);
      stats.wordCount += segment.text.split(/\s+/).length;

      // Speaker statistics
      const speaker = segment.speaker || 'Não identificado';
      if (!stats.speakerStats[speaker]) {
        stats.speakerStats[speaker] = {
          wordCount: 0,
          duration: 0,
          segmentCount: 0
        };
      }
      
      stats.speakerStats[speaker].wordCount += segment.text.split(/\s+/).length;
      stats.speakerStats[speaker].duration += duration;
      stats.speakerStats[speaker].segmentCount++;

      // Confidence tracking
      if (segment.confidence !== undefined) {
        totalConfidence += segment.confidence;
        confidenceCount++;
      }
    });

    // Calculate averages
    stats.averageSegmentDuration = stats.totalDuration / stats.segmentCount;
    stats.transcriptionConfidence = confidenceCount > 0 ? totalConfidence / confidenceCount : 0;

    // Calculate speaking time percentages
    Object.keys(stats.speakerStats).forEach(speaker => {
      stats.speakerStats[speaker].percentage = 
        (stats.speakerStats[speaker].duration / stats.totalDuration) * 100;
    });

    return stats;
  }

  /**
   * Export transcription in various formats
   * @param {Object} transcriptionResult - Transcription result
   * @param {string} format - Export format (txt, srt, json, docx)
   * @returns {Object} Exported data
   */
  exportTranscription(transcriptionResult, format = 'txt') {
    switch (format) {
      case 'txt':
        return this.exportAsText(transcriptionResult);
      case 'srt':
        return this.exportAsSRT(transcriptionResult);
      case 'json':
        return this.exportAsJSON(transcriptionResult);
      case 'markdown':
        return this.exportAsMarkdown(transcriptionResult);
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  }

  /**
   * Export as plain text
   * @param {Object} result - Transcription result
   * @returns {string} Plain text
   */
  exportAsText(result) {
    let text = `Transcrição da Reunião\n`;
    text += `Data: ${new Date(result.timestamp).toLocaleString('pt-BR')}\n`;
    text += `Duração: ${this.formatDuration(result.duration)}\n`;
    text += `Participantes: ${result.participants.join(', ')}\n`;
    text += `\n${'='.repeat(50)}\n\n`;

    if (result.groupedSegments) {
      result.groupedSegments.forEach(group => {
        text += `${group.speaker} [${this.formatTime(group.start)} - ${this.formatTime(group.end)}]:\n`;
        text += `${group.text}\n\n`;
      });
    } else {
      text += result.text;
    }

    return text;
  }

  /**
   * Export as SRT subtitle format
   * @param {Object} result - Transcription result
   * @returns {string} SRT format
   */
  exportAsSRT(result) {
    if (!result.segments || result.segments.length === 0) {
      return '';
    }

    return result.segments.map((segment, index) => {
      const start = this.formatTimeSRT(segment.start);
      const end = this.formatTimeSRT(segment.end);
      const speaker = segment.speaker ? `[${segment.speaker}] ` : '';
      
      return `${index + 1}\n${start} --> ${end}\n${speaker}${segment.text}\n`;
    }).join('\n');
  }

  /**
   * Export as JSON
   * @param {Object} result - Transcription result
   * @returns {string} JSON string
   */
  exportAsJSON(result) {
    return JSON.stringify(result, null, 2);
  }

  /**
   * Export as Markdown
   * @param {Object} result - Transcription result
   * @returns {string} Markdown format
   */
  exportAsMarkdown(result) {
    let md = `# Transcrição da Reunião\n\n`;
    md += `**Data:** ${new Date(result.timestamp).toLocaleString('pt-BR')}\n\n`;
    md += `**Duração:** ${this.formatDuration(result.duration)}\n\n`;
    md += `**Participantes:** ${result.participants.join(', ')}\n\n`;
    
    if (result.statistics) {
      md += `## Estatísticas\n\n`;
      md += `- Total de palavras: ${result.statistics.wordCount}\n`;
      md += `- Número de segmentos: ${result.statistics.segmentCount}\n`;
      
      if (Object.keys(result.statistics.speakerStats).length > 0) {
        md += `\n### Tempo de fala por participante\n\n`;
        Object.entries(result.statistics.speakerStats).forEach(([speaker, stats]) => {
          md += `- **${speaker}**: ${stats.percentage.toFixed(1)}% (${this.formatDuration(stats.duration)})\n`;
        });
      }
    }

    md += `\n## Transcrição\n\n`;

    if (result.groupedSegments) {
      result.groupedSegments.forEach(group => {
        md += `### ${group.speaker} *[${this.formatTime(group.start)} - ${this.formatTime(group.end)}]*\n\n`;
        md += `${group.text}\n\n`;
      });
    } else {
      md += result.text;
    }

    return md;
  }

  /**
   * Format time for display (MM:SS)
   * @param {number} seconds - Time in seconds
   * @returns {string} Formatted time
   */
  formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  /**
   * Format time for SRT format (HH:MM:SS,mmm)
   * @param {number} seconds - Time in seconds
   * @returns {string} SRT formatted time
   */
  formatTimeSRT(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 1000);
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')},${ms.toString().padStart(3, '0')}`;
  }

  /**
   * Format duration for display
   * @param {number} seconds - Duration in seconds
   * @returns {string} Formatted duration
   */
  formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}min ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}min ${secs}s`;
    } else {
      return `${secs}s`;
    }
  }

  /**
   * Get current recording state
   * @returns {Object} Current state
   */
  getState() {
    return {
      ...this.audioRecorder.getState(),
      isInitialized: this.isInitialized,
      participantCount: this.participants.length,
      transcriptionCount: this.transcriptionHistory.length,
      isProcessing: this.isProcessingRealtime
    };
  }

  /**
   * Cleanup resources
   */
  destroy() {
    if (this.realtimeInterval) {
      clearInterval(this.realtimeInterval);
    }
    
    this.audioRecorder.destroy();
    this.transcriptionBuffer = [];
    this.transcriptionHistory = [];
    this.audioChunksBuffer = [];
    this.isInitialized = false;
  }

  /**
   * Toggle participant detection
   * @param {boolean} enabled - Enable/disable participant detection
   */
  setParticipantDetection(enabled) {
    this.participantDetectionEnabled = enabled;
  }

  /**
   * Update real-time options
   * @param {Object} options - New options
   */
  updateRealtimeOptions(options) {
    this.realtimeOptions = { ...this.realtimeOptions, ...options };
    
    // Restart real-time processing if interval changed
    if (options.interval && this.realtimeInterval) {
      this.startRealtimeTranscription();
    }
  }

  /**
   * Get transcription history
   * @returns {Array} Transcription history
   */
  getTranscriptionHistory() {
    return this.transcriptionHistory;
  }

  /**
   * Clear transcription history
   */
  clearHistory() {
    this.transcriptionHistory = [];
    this.transcriptionBuffer = [];
  }
}

export default TranscriptionService;