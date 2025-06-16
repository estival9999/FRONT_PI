import React, { useState, useRef, useEffect } from 'react';
import AudioRecorder from '../services/audioRecorder';
import AudioVisualizer from '../services/audioVisualizer';

const AudioRecorderComponent = ({ onRecordingComplete, onTranscription }) => {
  const [recorder, setRecorder] = useState(null);
  const [visualizer, setVisualizer] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [duration, setDuration] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);
  
  const visualizerRef = useRef(null);
  const canvasRef = useRef(null);
  const durationInterval = useRef(null);

  // Initialize recorder on component mount
  useEffect(() => {
    initializeRecorder();
    return () => {
      if (recorder) {
        recorder.destroy();
      }
      if (visualizer) {
        visualizer.destroy();
      }
      if (durationInterval.current) {
        clearInterval(durationInterval.current);
      }
    };
  }, []);

  const initializeRecorder = async () => {
    try {
      // Initialize audio recorder
      const audioRecorder = new AudioRecorder();
      await audioRecorder.initialize();
      
      // Set visualization callback
      audioRecorder.setVisualizationCallback((data) => {
        setAudioLevel(data.audioLevel);
        drawWaveform(data.waveformData);
      });
      
      setRecorder(audioRecorder);
      setIsInitialized(true);
      
      // Initialize WaveSurfer visualizer if container is available
      if (visualizerRef.current) {
        const audioVisualizer = new AudioVisualizer(visualizerRef.current, {
          height: 128,
          waveColor: '#3B82F6',
          progressColor: '#1E40AF',
          barWidth: 3,
          barGap: 1,
          responsive: true
        });
        await audioVisualizer.initialize();
        setVisualizer(audioVisualizer);
      }
    } catch (err) {
      setError('Failed to initialize audio recorder: ' + err.message);
      console.error('Initialization error:', err);
    }
  };

  const drawWaveform = (waveformData) => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.fillStyle = '#F3F4F6';
    ctx.fillRect(0, 0, width, height);
    
    // Draw waveform
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#3B82F6';
    ctx.beginPath();
    
    const sliceWidth = width / waveformData.length;
    let x = 0;
    
    for (let i = 0; i < waveformData.length; i++) {
      const v = waveformData[i] / 128.0;
      const y = v * height / 2;
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
      
      x += sliceWidth;
    }
    
    ctx.lineTo(width, height / 2);
    ctx.stroke();
  };

  const startRecording = async () => {
    if (!recorder || !isInitialized) {
      setError('Recorder not initialized');
      return;
    }

    try {
      recorder.start();
      setIsRecording(true);
      setIsPaused(false);
      setDuration(0);
      
      // Start duration counter
      durationInterval.current = setInterval(() => {
        setDuration(recorder.getDuration());
      }, 100);
      
      // Start WaveSurfer recording if available
      if (visualizer) {
        await visualizer.startRecording();
      }
    } catch (err) {
      setError('Failed to start recording: ' + err.message);
      console.error('Recording error:', err);
    }
  };

  const pauseRecording = () => {
    if (!recorder || !isRecording) return;
    
    recorder.pause();
    setIsPaused(true);
    
    if (visualizer) {
      visualizer.pauseRecording();
    }
  };

  const resumeRecording = () => {
    if (!recorder || !isRecording || !isPaused) return;
    
    recorder.resume();
    setIsPaused(false);
    
    if (visualizer) {
      visualizer.resumeRecording();
    }
  };

  const stopRecording = async () => {
    if (!recorder || !isRecording) return;
    
    try {
      // Stop duration counter
      if (durationInterval.current) {
        clearInterval(durationInterval.current);
      }
      
      // Stop recording and get blob
      const audioBlob = await recorder.stop();
      setIsRecording(false);
      setIsPaused(false);
      setDuration(0);
      
      // Stop WaveSurfer recording
      if (visualizer) {
        await visualizer.stopRecording();
      }
      
      // Load the recorded audio for playback
      if (visualizer && audioBlob) {
        await visualizer.loadAudio(audioBlob);
      }
      
      // Callback with the recorded audio
      if (onRecordingComplete && audioBlob) {
        onRecordingComplete(audioBlob);
      }
      
      // Optional: Send to Whisper API for transcription
      if (onTranscription && audioBlob) {
        await transcribeAudio(audioBlob);
      }
    } catch (err) {
      setError('Failed to stop recording: ' + err.message);
      console.error('Stop recording error:', err);
    }
  };

  const transcribeAudio = async (audioBlob) => {
    try {
      // Convert blob to form data
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.webm');
      formData.append('model', 'whisper-1');
      
      // Example API call to OpenAI Whisper
      // Note: You'll need to implement the actual API endpoint
      const response = await fetch('/api/transcribe', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        onTranscription(data.text);
      } else {
        throw new Error('Transcription failed');
      }
    } catch (err) {
      setError('Failed to transcribe audio: ' + err.message);
      console.error('Transcription error:', err);
    }
  };

  const downloadRecording = async () => {
    if (!recorder || isRecording) return;
    
    try {
      const state = recorder.getState();
      if (state.duration > 0) {
        const audioBlob = await recorder.stop();
        if (audioBlob) {
          recorder.downloadAudio(audioBlob, `recording_${Date.now()}.webm`);
        }
      }
    } catch (err) {
      setError('Failed to download recording: ' + err.message);
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="audio-recorder-container p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">Audio Recorder</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {!isInitialized && !error && (
        <div className="text-gray-600 mb-4">Initializing audio recorder...</div>
      )}
      
      {isInitialized && (
        <>
          {/* Real-time waveform canvas */}
          <div className="mb-4 bg-gray-100 rounded p-2">
            <canvas
              ref={canvasRef}
              width={600}
              height={100}
              className="w-full h-24 bg-gray-50 rounded"
            />
          </div>
          
          {/* Audio level indicator */}
          <div className="mb-4">
            <div className="flex items-center">
              <span className="text-sm text-gray-600 mr-2">Level:</span>
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-100"
                  style={{ width: `${audioLevel * 100}%` }}
                />
              </div>
            </div>
          </div>
          
          {/* WaveSurfer visualization container */}
          <div
            ref={visualizerRef}
            className="mb-4 bg-gray-100 rounded p-2"
            style={{ minHeight: '128px' }}
          />
          
          {/* Recording info */}
          <div className="mb-4 text-center">
            <div className="text-3xl font-mono text-gray-700">
              {formatDuration(duration)}
            </div>
            {isRecording && (
              <div className="text-sm text-gray-600 mt-1">
                {isPaused ? 'Paused' : 'Recording...'}
              </div>
            )}
          </div>
          
          {/* Control buttons */}
          <div className="flex justify-center space-x-4">
            {!isRecording ? (
              <button
                onClick={startRecording}
                className="px-6 py-3 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors duration-200 flex items-center"
              >
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <circle cx="10" cy="10" r="8" />
                </svg>
                Start Recording
              </button>
            ) : (
              <>
                {!isPaused ? (
                  <button
                    onClick={pauseRecording}
                    className="px-6 py-3 bg-yellow-500 text-white rounded-full hover:bg-yellow-600 transition-colors duration-200 flex items-center"
                  >
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <rect x="6" y="4" width="3" height="12" />
                      <rect x="11" y="4" width="3" height="12" />
                    </svg>
                    Pause
                  </button>
                ) : (
                  <button
                    onClick={resumeRecording}
                    className="px-6 py-3 bg-green-500 text-white rounded-full hover:bg-green-600 transition-colors duration-200 flex items-center"
                  >
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M6 4l10 6-10 6V4z" />
                    </svg>
                    Resume
                  </button>
                )}
                
                <button
                  onClick={stopRecording}
                  className="px-6 py-3 bg-gray-500 text-white rounded-full hover:bg-gray-600 transition-colors duration-200 flex items-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <rect x="4" y="4" width="12" height="12" />
                  </svg>
                  Stop
                </button>
              </>
            )}
            
            {!isRecording && duration > 0 && (
              <button
                onClick={downloadRecording}
                className="px-6 py-3 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors duration-200 flex items-center"
              >
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" />
                </svg>
                Download
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default AudioRecorderComponent;