/**
 * Audio Visualizer Service
 * Integrates with WaveSurfer.js for audio visualization
 */

import WaveSurfer from 'wavesurfer.js';
import RecordPlugin from 'wavesurfer.js/dist/plugins/record.js';

class AudioVisualizer {
  constructor(container, options = {}) {
    this.container = container;
    this.wavesurfer = null;
    this.recordPlugin = null;
    this.isInitialized = false;
    
    // Default options
    this.options = {
      waveColor: '#4F9CF9',
      progressColor: '#1E40AF',
      cursorColor: '#1E40AF',
      barWidth: 2,
      barGap: 1,
      barRadius: 3,
      barHeight: 1,
      height: 100,
      normalize: true,
      responsive: true,
      interact: false,
      ...options
    };
  }

  /**
   * Initialize WaveSurfer instance
   */
  async initialize() {
    try {
      // Create WaveSurfer instance
      this.wavesurfer = WaveSurfer.create({
        container: this.container,
        ...this.options
      });

      // Initialize record plugin
      this.recordPlugin = this.wavesurfer.registerPlugin(
        RecordPlugin.create({
          renderRecordedAudio: false,
          scrollingWaveform: true,
          scrollingWaveformWindow: 10
        })
      );

      this.isInitialized = true;
      return true;
    } catch (error) {
      console.error('Error initializing audio visualizer:', error);
      throw error;
    }
  }

  /**
   * Start recording with visualization
   * @param {Object} deviceId - Optional audio input device ID
   */
  async startRecording(deviceId = null) {
    if (!this.isInitialized) {
      throw new Error('Visualizer not initialized. Call initialize() first.');
    }

    try {
      // Start recording with the record plugin
      await this.recordPlugin.startRecording({ deviceId });
      return true;
    } catch (error) {
      console.error('Error starting recording:', error);
      throw error;
    }
  }

  /**
   * Pause recording
   */
  pauseRecording() {
    if (this.recordPlugin && this.recordPlugin.isPaused()) {
      console.warn('Recording already paused');
      return;
    }
    
    this.recordPlugin.pauseRecording();
  }

  /**
   * Resume recording
   */
  resumeRecording() {
    if (this.recordPlugin && !this.recordPlugin.isPaused()) {
      console.warn('Recording not paused');
      return;
    }
    
    this.recordPlugin.resumeRecording();
  }

  /**
   * Stop recording and get the recorded blob
   * @returns {Promise<Blob>} The recorded audio blob
   */
  async stopRecording() {
    if (!this.recordPlugin || !this.recordPlugin.isRecording()) {
      console.warn('Not recording');
      return null;
    }

    const blob = await this.recordPlugin.stopRecording();
    return blob;
  }

  /**
   * Load and display audio file
   * @param {Blob|string} audio - Audio blob or URL
   */
  async loadAudio(audio) {
    if (!this.isInitialized) {
      throw new Error('Visualizer not initialized. Call initialize() first.');
    }

    try {
      if (audio instanceof Blob) {
        const url = URL.createObjectURL(audio);
        await this.wavesurfer.load(url);
        URL.revokeObjectURL(url);
      } else {
        await this.wavesurfer.load(audio);
      }
    } catch (error) {
      console.error('Error loading audio:', error);
      throw error;
    }
  }

  /**
   * Create real-time waveform visualization
   * @param {MediaStream} stream - Audio stream
   * @returns {Function} Stop function
   */
  createRealtimeWaveform(stream) {
    if (!this.isInitialized) {
      throw new Error('Visualizer not initialized. Call initialize() first.');
    }

    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;
    source.connect(analyser);

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const canvas = document.createElement('canvas');
    const canvasContext = canvas.getContext('2d');
    
    canvas.width = this.container.offsetWidth;
    canvas.height = this.options.height;
    this.container.appendChild(canvas);

    let animationId;
    
    const draw = () => {
      animationId = requestAnimationFrame(draw);
      analyser.getByteTimeDomainData(dataArray);

      canvasContext.fillStyle = 'rgb(255, 255, 255)';
      canvasContext.fillRect(0, 0, canvas.width, canvas.height);

      canvasContext.lineWidth = 2;
      canvasContext.strokeStyle = this.options.waveColor;
      canvasContext.beginPath();

      const sliceWidth = canvas.width * 1.0 / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = v * canvas.height / 2;

        if (i === 0) {
          canvasContext.moveTo(x, y);
        } else {
          canvasContext.lineTo(x, y);
        }

        x += sliceWidth;
      }

      canvasContext.lineTo(canvas.width, canvas.height / 2);
      canvasContext.stroke();
    };

    draw();

    // Return cleanup function
    return () => {
      cancelAnimationFrame(animationId);
      source.disconnect();
      audioContext.close();
      canvas.remove();
    };
  }

  /**
   * Create frequency bars visualization
   * @param {MediaStream} stream - Audio stream
   * @returns {Function} Stop function
   */
  createFrequencyBars(stream) {
    if (!this.isInitialized) {
      throw new Error('Visualizer not initialized. Call initialize() first.');
    }

    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    source.connect(analyser);

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const canvas = document.createElement('canvas');
    const canvasContext = canvas.getContext('2d');
    
    canvas.width = this.container.offsetWidth;
    canvas.height = this.options.height;
    this.container.appendChild(canvas);

    let animationId;
    
    const draw = () => {
      animationId = requestAnimationFrame(draw);
      analyser.getByteFrequencyData(dataArray);

      canvasContext.fillStyle = 'rgb(255, 255, 255)';
      canvasContext.fillRect(0, 0, canvas.width, canvas.height);

      const barWidth = (canvas.width / bufferLength) * 2.5;
      let barHeight;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        barHeight = (dataArray[i] / 255) * canvas.height;

        const r = barHeight + (25 * (i / bufferLength));
        const g = 250 * (i / bufferLength);
        const b = 50;

        canvasContext.fillStyle = `rgb(${r},${g},${b})`;
        canvasContext.fillRect(x, canvas.height - barHeight, barWidth, barHeight);

        x += barWidth + 1;
      }
    };

    draw();

    // Return cleanup function
    return () => {
      cancelAnimationFrame(animationId);
      source.disconnect();
      audioContext.close();
      canvas.remove();
    };
  }

  /**
   * Play loaded audio
   */
  play() {
    if (this.wavesurfer) {
      this.wavesurfer.play();
    }
  }

  /**
   * Pause loaded audio
   */
  pause() {
    if (this.wavesurfer) {
      this.wavesurfer.pause();
    }
  }

  /**
   * Stop loaded audio
   */
  stop() {
    if (this.wavesurfer) {
      this.wavesurfer.stop();
    }
  }

  /**
   * Get current playback time
   * @returns {number} Current time in seconds
   */
  getCurrentTime() {
    return this.wavesurfer ? this.wavesurfer.getCurrentTime() : 0;
  }

  /**
   * Get total duration
   * @returns {number} Duration in seconds
   */
  getDuration() {
    return this.wavesurfer ? this.wavesurfer.getDuration() : 0;
  }

  /**
   * Set playback volume
   * @param {number} volume - Volume level (0-1)
   */
  setVolume(volume) {
    if (this.wavesurfer) {
      this.wavesurfer.setVolume(volume);
    }
  }

  /**
   * Export peaks data
   * @returns {Array} Peaks data
   */
  exportPeaks() {
    return this.wavesurfer ? this.wavesurfer.exportPeaks() : [];
  }

  /**
   * Update visualization options
   * @param {Object} options - New options
   */
  updateOptions(options) {
    this.options = { ...this.options, ...options };
    if (this.wavesurfer) {
      this.wavesurfer.setOptions(this.options);
    }
  }

  /**
   * Destroy the visualizer and cleanup resources
   */
  destroy() {
    if (this.recordPlugin) {
      this.recordPlugin.destroy();
    }
    
    if (this.wavesurfer) {
      this.wavesurfer.destroy();
    }
    
    this.wavesurfer = null;
    this.recordPlugin = null;
    this.isInitialized = false;
  }

  /**
   * Get recording state
   * @returns {Object} Current state
   */
  getState() {
    return {
      isInitialized: this.isInitialized,
      isRecording: this.recordPlugin ? this.recordPlugin.isRecording() : false,
      isPaused: this.recordPlugin ? this.recordPlugin.isPaused() : false,
      currentTime: this.getCurrentTime(),
      duration: this.getDuration()
    };
  }

  /**
   * Set event listeners
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   */
  on(event, callback) {
    if (this.wavesurfer) {
      this.wavesurfer.on(event, callback);
    }
  }

  /**
   * Remove event listener
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   */
  off(event, callback) {
    if (this.wavesurfer) {
      this.wavesurfer.un(event, callback);
    }
  }
}

export default AudioVisualizer;