/**
 * Whisper Service
 * Handles audio transcription using OpenAI Whisper API
 */

class WhisperService {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.apiUrl = 'https://api.openai.com/v1/audio/transcriptions';
    this.supportedFormats = ['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'];
    this.maxFileSize = 25 * 1024 * 1024; // 25MB
  }

  /**
   * Validate audio file
   * @param {Blob} audioBlob - Audio blob to validate
   * @returns {boolean} Validation result
   */
  validateAudio(audioBlob) {
    if (!audioBlob || !(audioBlob instanceof Blob)) {
      throw new Error('Invalid audio blob');
    }

    if (audioBlob.size > this.maxFileSize) {
      throw new Error(`File size exceeds maximum allowed size of ${this.maxFileSize / 1024 / 1024}MB`);
    }

    const fileType = audioBlob.type.split('/')[1];
    if (!this.supportedFormats.includes(fileType)) {
      console.warn(`File type ${fileType} may not be supported. Supported formats: ${this.supportedFormats.join(', ')}`);
    }

    return true;
  }

  /**
   * Transcribe audio using OpenAI Whisper API
   * @param {Blob} audioBlob - Audio blob to transcribe
   * @param {Object} options - Transcription options
   * @returns {Promise<Object>} Transcription result
   */
  async transcribe(audioBlob, options = {}) {
    try {
      // Validate audio
      this.validateAudio(audioBlob);

      // Prepare form data
      const formData = new FormData();
      formData.append('file', audioBlob, 'audio.webm');
      formData.append('model', options.model || 'whisper-1');

      // Optional parameters
      if (options.prompt) {
        formData.append('prompt', options.prompt);
      }
      if (options.response_format) {
        formData.append('response_format', options.response_format);
      }
      if (options.temperature) {
        formData.append('temperature', options.temperature.toString());
      }
      if (options.language) {
        formData.append('language', options.language);
      }

      // Make API request
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Transcription failed');
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Transcription error:', error);
      throw error;
    }
  }

  /**
   * Transcribe audio with timestamps
   * @param {Blob} audioBlob - Audio blob to transcribe
   * @param {Object} options - Transcription options
   * @returns {Promise<Object>} Transcription with timestamps
   */
  async transcribeWithTimestamps(audioBlob, options = {}) {
    return this.transcribe(audioBlob, {
      ...options,
      response_format: 'verbose_json'
    });
  }

  /**
   * Translate audio to English
   * @param {Blob} audioBlob - Audio blob to translate
   * @param {Object} options - Translation options
   * @returns {Promise<Object>} Translation result
   */
  async translate(audioBlob, options = {}) {
    try {
      // Validate audio
      this.validateAudio(audioBlob);

      // Prepare form data
      const formData = new FormData();
      formData.append('file', audioBlob, 'audio.webm');
      formData.append('model', options.model || 'whisper-1');

      // Optional parameters
      if (options.prompt) {
        formData.append('prompt', options.prompt);
      }
      if (options.response_format) {
        formData.append('response_format', options.response_format);
      }
      if (options.temperature) {
        formData.append('temperature', options.temperature.toString());
      }

      // Make API request to translation endpoint
      const response = await fetch('https://api.openai.com/v1/audio/translations', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Translation failed');
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Translation error:', error);
      throw error;
    }
  }

  /**
   * Stream transcription for real-time processing
   * @param {MediaStream} stream - Audio stream
   * @param {Function} onTranscript - Callback for transcription updates
   * @param {Object} options - Streaming options
   * @returns {Function} Stop streaming function
   */
  streamTranscription(stream, onTranscript, options = {}) {
    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    });
    
    const chunks = [];
    let isRunning = true;
    let transcriptionInterval;

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    // Process chunks periodically
    transcriptionInterval = setInterval(async () => {
      if (chunks.length > 0 && isRunning) {
        const blob = new Blob(chunks.splice(0, chunks.length), { type: 'audio/webm' });
        
        try {
          const result = await this.transcribe(blob, {
            ...options,
            response_format: 'json'
          });
          
          if (result.text && onTranscript) {
            onTranscript(result.text);
          }
        } catch (error) {
          console.error('Streaming transcription error:', error);
        }
      }
    }, options.interval || 5000); // Process every 5 seconds by default

    // Start recording
    mediaRecorder.start(1000); // Collect data every second

    // Return stop function
    return () => {
      isRunning = false;
      mediaRecorder.stop();
      clearInterval(transcriptionInterval);
      
      // Process any remaining chunks
      if (chunks.length > 0) {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        this.transcribe(blob, options).then(result => {
          if (result.text && onTranscript) {
            onTranscript(result.text);
          }
        }).catch(console.error);
      }
    };
  }

  /**
   * Format transcription result with timestamps
   * @param {Object} result - Verbose JSON result from Whisper
   * @returns {string} Formatted transcription
   */
  formatTranscriptionWithTimestamps(result) {
    if (!result.segments) {
      return result.text || '';
    }

    return result.segments.map(segment => {
      const start = this.formatTime(segment.start);
      const end = this.formatTime(segment.end);
      return `[${start} - ${end}] ${segment.text}`;
    }).join('\n');
  }

  /**
   * Format time in seconds to MM:SS format
   * @param {number} seconds - Time in seconds
   * @returns {string} Formatted time
   */
  formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  /**
   * Split long audio into chunks for processing
   * @param {Blob} audioBlob - Large audio blob
   * @param {number} chunkDuration - Duration of each chunk in seconds
   * @returns {Promise<Array<Blob>>} Array of audio chunks
   */
  async splitAudioIntoChunks(audioBlob, chunkDuration = 300) {
    // This is a simplified example. In production, you'd use a proper audio processing library
    // like ffmpeg.wasm to split audio accurately
    const chunks = [];
    const chunkSize = Math.floor((audioBlob.size / this.estimateAudioDuration(audioBlob)) * chunkDuration);
    
    for (let i = 0; i < audioBlob.size; i += chunkSize) {
      const chunk = audioBlob.slice(i, Math.min(i + chunkSize, audioBlob.size));
      chunks.push(chunk);
    }
    
    return chunks;
  }

  /**
   * Estimate audio duration from blob size (rough estimate)
   * @param {Blob} audioBlob - Audio blob
   * @returns {number} Estimated duration in seconds
   */
  estimateAudioDuration(audioBlob) {
    // Rough estimate: assume 128kbps bitrate
    const bitrate = 128 * 1024 / 8; // bytes per second
    return audioBlob.size / bitrate;
  }

  /**
   * Process long audio by splitting and transcribing chunks
   * @param {Blob} audioBlob - Large audio blob
   * @param {Object} options - Transcription options
   * @returns {Promise<Object>} Combined transcription result
   */
  async transcribeLongAudio(audioBlob, options = {}) {
    if (audioBlob.size <= this.maxFileSize) {
      return this.transcribe(audioBlob, options);
    }

    const chunks = await this.splitAudioIntoChunks(audioBlob);
    const results = [];

    for (let i = 0; i < chunks.length; i++) {
      const result = await this.transcribe(chunks[i], {
        ...options,
        prompt: i > 0 ? results[i - 1].text.slice(-500) : options.prompt // Use previous context
      });
      results.push(result);
    }

    // Combine results
    return {
      text: results.map(r => r.text).join(' '),
      chunks: results
    };
  }
}

export default WhisperService;