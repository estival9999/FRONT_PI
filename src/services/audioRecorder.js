/**
 * Audio Recorder Service
 * Handles audio recording using MediaRecorder API
 * Saves audio in format compatible with OpenAI Whisper
 */

class AudioRecorder {
  constructor() {
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.stream = null;
    this.isRecording = false;
    this.isPaused = false;
    this.startTime = null;
    this.pausedTime = 0;
    this.analyser = null;
    this.audioContext = null;
    this.dataArray = null;
    this.animationId = null;
    this.onDataAvailable = null;
    this.onVisualizationUpdate = null;
  }

  /**
   * Initialize the audio recorder
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    try {
      // Request microphone access
      this.stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000, // Optimal for Whisper
          channelCount: 1    // Mono audio
        } 
      });

      // Setup audio context for visualization
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const source = this.audioContext.createMediaStreamSource(this.stream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 2048;
      source.connect(this.analyser);
      
      const bufferLength = this.analyser.frequencyBinCount;
      this.dataArray = new Uint8Array(bufferLength);

      // Initialize MediaRecorder with webm format (compatible with Whisper)
      const options = {
        mimeType: 'audio/webm;codecs=opus'
      };

      // Fallback for browsers that don't support webm
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options.mimeType = 'audio/ogg;codecs=opus';
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
          options.mimeType = 'audio/mpeg';
          if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options.mimeType = 'audio/wav';
          }
        }
      }

      this.mediaRecorder = new MediaRecorder(this.stream, options);

      // Handle data available event
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
          if (this.onDataAvailable) {
            this.onDataAvailable(event.data);
          }
        }
      };

      return true;
    } catch (error) {
      console.error('Error initializing audio recorder:', error);
      throw error;
    }
  }

  /**
   * Start recording audio
   * @param {number} timeslice - Optional timeslice in milliseconds for data chunks
   */
  start(timeslice = 1000) {
    if (!this.mediaRecorder) {
      throw new Error('Audio recorder not initialized. Call initialize() first.');
    }

    if (this.isRecording && !this.isPaused) {
      console.warn('Already recording');
      return;
    }

    this.audioChunks = [];
    this.startTime = Date.now();
    this.pausedTime = 0;
    this.isRecording = true;
    this.isPaused = false;

    this.mediaRecorder.start(timeslice);
    this.startVisualization();
  }

  /**
   * Pause recording
   */
  pause() {
    if (!this.isRecording || this.isPaused) {
      console.warn('Not recording or already paused');
      return;
    }

    if (this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.pause();
      this.isPaused = true;
      this.pausedTime += Date.now() - this.startTime;
      this.stopVisualization();
    }
  }

  /**
   * Resume recording after pause
   */
  resume() {
    if (!this.isRecording || !this.isPaused) {
      console.warn('Not paused');
      return;
    }

    if (this.mediaRecorder.state === 'paused') {
      this.mediaRecorder.resume();
      this.isPaused = false;
      this.startTime = Date.now();
      this.startVisualization();
    }
  }

  /**
   * Stop recording and return the audio blob
   * @returns {Promise<Blob>} The recorded audio blob
   */
  async stop() {
    if (!this.isRecording) {
      console.warn('Not recording');
      return null;
    }

    return new Promise((resolve) => {
      this.mediaRecorder.onstop = () => {
        const mimeType = this.mediaRecorder.mimeType;
        const audioBlob = new Blob(this.audioChunks, { type: mimeType });
        this.audioChunks = [];
        this.isRecording = false;
        this.isPaused = false;
        this.stopVisualization();
        resolve(audioBlob);
      };

      if (this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop();
      }
    });
  }

  /**
   * Get current recording duration in seconds
   * @returns {number} Duration in seconds
   */
  getDuration() {
    if (!this.isRecording) return 0;
    
    const currentTime = this.isPaused ? 0 : (Date.now() - this.startTime);
    return Math.floor((this.pausedTime + currentTime) / 1000);
  }

  /**
   * Start audio visualization
   */
  startVisualization() {
    if (!this.analyser || !this.onVisualizationUpdate) return;

    const draw = () => {
      this.animationId = requestAnimationFrame(draw);
      this.analyser.getByteTimeDomainData(this.dataArray);
      
      // Calculate audio level
      let sum = 0;
      for (let i = 0; i < this.dataArray.length; i++) {
        const normalized = (this.dataArray[i] - 128) / 128;
        sum += normalized * normalized;
      }
      const rms = Math.sqrt(sum / this.dataArray.length);
      const db = 20 * Math.log10(rms);
      const normalizedDb = Math.max(0, (db + 60) / 60); // Normalize to 0-1 range

      if (this.onVisualizationUpdate) {
        this.onVisualizationUpdate({
          waveformData: this.dataArray,
          audioLevel: normalizedDb,
          frequency: this.getFrequencyData()
        });
      }
    };

    draw();
  }

  /**
   * Stop audio visualization
   */
  stopVisualization() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  /**
   * Get frequency data for visualization
   * @returns {Uint8Array} Frequency data
   */
  getFrequencyData() {
    if (!this.analyser) return new Uint8Array(0);
    
    const frequencyData = new Uint8Array(this.analyser.frequencyBinCount);
    this.analyser.getByteFrequencyData(frequencyData);
    return frequencyData;
  }

  /**
   * Convert audio blob to format compatible with OpenAI Whisper
   * @param {Blob} audioBlob - The audio blob to convert
   * @returns {Promise<Blob>} Converted audio blob
   */
  async convertForWhisper(audioBlob) {
    // Whisper supports: mp3, mp4, mpeg, mpga, m4a, wav, webm
    // Our recording is already in webm format, which is compatible
    // If needed, we can convert to other formats here
    return audioBlob;
  }

  /**
   * Download the recorded audio
   * @param {Blob} audioBlob - The audio blob to download
   * @param {string} filename - The filename for download
   */
  downloadAudio(audioBlob, filename = 'recording.webm') {
    const url = URL.createObjectURL(audioBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /**
   * Get audio blob as base64 string
   * @param {Blob} audioBlob - The audio blob to convert
   * @returns {Promise<string>} Base64 encoded audio
   */
  async getBase64(audioBlob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result.split(',')[1]);
      reader.onerror = reject;
      reader.readAsDataURL(audioBlob);
    });
  }

  /**
   * Cleanup resources
   */
  destroy() {
    this.stopVisualization();
    
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }
    
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
    }
    
    if (this.audioContext) {
      this.audioContext.close();
    }
    
    this.mediaRecorder = null;
    this.stream = null;
    this.audioContext = null;
    this.analyser = null;
    this.dataArray = null;
    this.audioChunks = [];
    this.isRecording = false;
    this.isPaused = false;
  }

  /**
   * Set visualization update callback
   * @param {Function} callback - Callback function for visualization updates
   */
  setVisualizationCallback(callback) {
    this.onVisualizationUpdate = callback;
  }

  /**
   * Set data available callback
   * @param {Function} callback - Callback function for when data is available
   */
  setDataAvailableCallback(callback) {
    this.onDataAvailable = callback;
  }

  /**
   * Get recording state
   * @returns {Object} Current state of the recorder
   */
  getState() {
    return {
      isRecording: this.isRecording,
      isPaused: this.isPaused,
      duration: this.getDuration(),
      isInitialized: !!this.mediaRecorder,
      mimeType: this.mediaRecorder ? this.mediaRecorder.mimeType : null
    };
  }
}

export default AudioRecorder;