import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import TranscriptionService from '../services/transcription';
import { fileManager } from '../utils/fileManager';

function RecordingScreen() {
  const navigate = useNavigate();
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState(null);
  const transcriptionServiceRef = useRef(null);
  const canvasRef = useRef(null);
  const [transcriptionText, setTranscriptionText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    // Initialize transcription service
    const initializeService = async () => {
      try {
        // Get API key from electron settings
        let apiKey = '';
        if (window.electronAPI && window.electronAPI.settings) {
          apiKey = await window.electronAPI.settings.get('openai_api_key');
        }
        
        if (!apiKey) {
          setError('Configure sua API Key do OpenAI em Configurações');
          return;
        }

        transcriptionServiceRef.current = new TranscriptionService(apiKey);
        await transcriptionServiceRef.current.initialize([], {
          language: 'pt',
          interval: 5000 // Real-time transcription every 5 seconds
        });
      } catch (err) {
        setError('Erro ao inicializar serviço: ' + err.message);
      }
    };

    initializeService();

    return () => {
      if (transcriptionServiceRef.current) {
        transcriptionServiceRef.current.destroy();
      }
    };
  }, []);

  useEffect(() => {
    let interval = null;
    if (isRecording && !isPaused) {
      interval = setInterval(() => {
        setSeconds(seconds => seconds + 1);
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isRecording, isPaused]);

  const formatTime = (totalSeconds) => {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const secs = totalSeconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes
      .toString()
      .padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const drawWaveform = (waveformData) => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    ctx.clearRect(0, 0, width, height);
    ctx.lineWidth = 1;
    ctx.strokeStyle = '#10b981';
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
    
    ctx.stroke();
  };

  const handleStart = async () => {
    if (!transcriptionServiceRef.current) {
      setError('Serviço não inicializado');
      return;
    }
    
    try {
      // Start recording with real-time transcription
      await transcriptionServiceRef.current.startRecording(
        // Callback for transcription updates
        (update) => {
          if (update.text) {
            setTranscriptionText(prev => prev + ' ' + update.text);
          }
        },
        // Callback for visualization
        (data) => {
          setAudioLevel(data.audioLevel);
          drawWaveform(data.waveformData);
        }
      );
      
      setIsRecording(true);
      setIsPaused(false);
      setError(null);
      setTranscriptionText('');
    } catch (err) {
      setError('Erro ao iniciar gravação: ' + err.message);
    }
  };

  const handlePause = () => {
    if (!transcriptionServiceRef.current) return;
    
    if (isPaused) {
      transcriptionServiceRef.current.resumeRecording();
    } else {
      transcriptionServiceRef.current.pauseRecording();
    }
    setIsPaused(!isPaused);
  };

  const handleStop = async () => {
    if (!transcriptionServiceRef.current) return;
    
    try {
      setIsProcessing(true);
      setError('Processando transcrição final...');
      
      // Stop recording and get final transcription
      const result = await transcriptionServiceRef.current.stopRecording();
      
      if (result) {
        // Save transcription result to localStorage
        localStorage.setItem('recordingDuration', formatTime(seconds));
        localStorage.setItem('recordingTimestamp', new Date().toISOString());
        localStorage.setItem('transcriptionResult', JSON.stringify(result));
        
        // Convert audio blob to base64 for storage
        const reader = new FileReader();
        reader.onloadend = () => {
          localStorage.setItem('recordedAudio', reader.result);
          
          setIsRecording(false);
          setIsPaused(false);
          navigate('/participants-form');
        };
        reader.readAsDataURL(result.audioBlob);
      } else {
        throw new Error('Falha ao obter transcrição');
      }
    } catch (err) {
      setError('Erro ao parar gravação: ' + err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="electron-container bg-gray-50">
      <div className="card-electron text-center">
        <h2 className="compact-header text-gray-800">
          Gravação de Áudio
        </h2>
        
        {error && (
          <div className="text-xs-electron text-red-600 mb-2">
            {error}
          </div>
        )}
        
        <div className="recording-timer text-gray-800">
          {formatTime(seconds)}
        </div>

        {/* Audio Visualizer */}
        <div className="audio-visualizer relative mb-4">
          <canvas
            ref={canvasRef}
            width={280}
            height={60}
            className="w-full h-full"
          />
          {isRecording && !isPaused && (
            <div className="absolute top-1 right-1">
              <span className="status-dot status-recording"></span>
            </div>
          )}
        </div>

        {/* Audio Level Indicator */}
        <div className="w-full mb-4">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 transition-all duration-100"
              style={{ width: `${audioLevel * 100}%` }}
            />
          </div>
        </div>

        <div className="flex justify-center compact-spacing gap-2">
          {!isRecording ? (
            <button
              onClick={handleStart}
              className="btn-electron bg-green-600 text-white hover:bg-green-700"
            >
              Iniciar
            </button>
          ) : (
            <>
              <button
                onClick={handlePause}
                className="btn-electron bg-yellow-600 text-white hover:bg-yellow-700"
              >
                {isPaused ? 'Retomar' : 'Pausar'}
              </button>
              <button
                onClick={handleStop}
                className="btn-electron bg-red-600 text-white hover:bg-red-700"
              >
                Parar
              </button>
            </>
          )}
        </div>

        <div className="mt-4">
          <p className="text-xs-electron text-gray-600">
            {isRecording ? (isPaused ? 'Gravação pausada' : 'Gravando...') : 'Pronto para gravar'}
          </p>
          
          {/* Real-time transcription display */}
          {transcriptionText && (
            <div className="mt-2 p-2 bg-gray-100 rounded">
              <p className="text-xs-electron text-gray-700">
                <strong>Transcrição:</strong> {transcriptionText.slice(-100)}...
              </p>
            </div>
          )}
          
          {isProcessing && (
            <div className="mt-2">
              <p className="text-xs-electron text-blue-600">
                Processando transcrição final...
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default RecordingScreen;