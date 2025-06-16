/**
 * Example component demonstrating the transcription service usage
 */

import React, { useState, useEffect, useRef } from 'react';
import TranscriptionService from '../services/transcription';

const TranscriptionExample = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [transcriptionText, setTranscriptionText] = useState('');
  const [realtimeText, setRealtimeText] = useState('');
  const [participants, setParticipants] = useState(['João Silva', 'Maria Santos', 'Pedro Oliveira']);
  const [detectedSpeakers, setDetectedSpeakers] = useState([]);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const transcriptionServiceRef = useRef(null);
  const durationIntervalRef = useRef(null);

  // Initialize transcription service
  useEffect(() => {
    const initService = async () => {
      try {
        // Get API key from environment or config
        const apiKey = process.env.REACT_APP_OPENAI_API_KEY || 'your-api-key-here';
        
        transcriptionServiceRef.current = new TranscriptionService(apiKey);
        
        // Initialize with participants
        await transcriptionServiceRef.current.initialize(participants, {
          language: 'pt',
          interval: 5000 // Real-time update every 5 seconds
        });
      } catch (err) {
        setError('Falha ao inicializar serviço de transcrição: ' + err.message);
      }
    };

    initService();

    return () => {
      if (transcriptionServiceRef.current) {
        transcriptionServiceRef.current.destroy();
      }
    };
  }, []);

  // Update participants in service when they change
  useEffect(() => {
    if (transcriptionServiceRef.current) {
      transcriptionServiceRef.current.setParticipants(participants);
    }
  }, [participants]);

  // Start recording
  const startRecording = async () => {
    try {
      setError(null);
      setRealtimeText('');
      setTranscriptionText('');
      setDetectedSpeakers([]);

      // Start recording with callbacks
      await transcriptionServiceRef.current.startRecording(
        // Real-time transcription callback
        (update) => {
          console.log('Real-time update:', update);
          setRealtimeText(prev => prev + ' ' + update.text);
          
          // Update detected speakers
          if (update.participants && update.participants.length > 0) {
            setDetectedSpeakers(update.participants);
          }
        },
        // Audio visualization callback
        (visualization) => {
          setAudioLevel(visualization.audioLevel);
        }
      );

      setIsRecording(true);
      setIsPaused(false);

      // Start duration counter
      durationIntervalRef.current = setInterval(() => {
        const state = transcriptionServiceRef.current.getState();
        setRecordingDuration(state.duration);
      }, 1000);
    } catch (err) {
      setError('Erro ao iniciar gravação: ' + err.message);
    }
  };

  // Pause recording
  const pauseRecording = () => {
    transcriptionServiceRef.current.pauseRecording();
    setIsPaused(true);
  };

  // Resume recording
  const resumeRecording = () => {
    transcriptionServiceRef.current.resumeRecording();
    setIsPaused(false);
  };

  // Stop recording and get final transcription
  const stopRecording = async () => {
    try {
      setIsProcessing(true);
      clearInterval(durationIntervalRef.current);

      // Stop and get final transcription
      const finalResult = await transcriptionServiceRef.current.stopRecording();

      if (finalResult) {
        console.log('Final transcription result:', finalResult);
        
        // Display formatted transcription
        const formatted = transcriptionServiceRef.current.exportAsMarkdown(finalResult);
        setTranscriptionText(formatted);

        // Update detected speakers with statistics
        if (finalResult.detectedSpeakers) {
          setDetectedSpeakers(finalResult.detectedSpeakers);
        }

        // Save audio and transcription
        saveResults(finalResult);
      }

      setIsRecording(false);
      setIsPaused(false);
      setRecordingDuration(0);
    } catch (err) {
      setError('Erro ao parar gravação: ' + err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  // Save transcription results
  const saveResults = (result) => {
    // Save transcription as text file
    const textBlob = new Blob([result.text], { type: 'text/plain' });
    const textUrl = URL.createObjectURL(textBlob);
    const textLink = document.createElement('a');
    textLink.href = textUrl;
    textLink.download = `transcricao_${new Date().toISOString()}.txt`;
    textLink.click();

    // Save audio file
    if (result.audioBlob) {
      const audioUrl = URL.createObjectURL(result.audioBlob);
      const audioLink = document.createElement('a');
      audioLink.href = audioUrl;
      audioLink.download = `audio_${new Date().toISOString()}.webm`;
      audioLink.click();
    }
  };

  // Format duration display
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Add new participant
  const addParticipant = () => {
    const name = prompt('Nome do participante:');
    if (name && name.trim()) {
      setParticipants([...participants, name.trim()]);
    }
  };

  // Remove participant
  const removeParticipant = (index) => {
    const newParticipants = participants.filter((_, i) => i !== index);
    setParticipants(newParticipants);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Serviço de Transcrição com OpenAI Whisper</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Participants Section */}
      <div className="mb-6 bg-gray-100 p-4 rounded">
        <h2 className="text-lg font-semibold mb-3">Participantes</h2>
        <div className="flex flex-wrap gap-2 mb-3">
          {participants.map((participant, index) => (
            <div key={index} className="bg-blue-500 text-white px-3 py-1 rounded-full flex items-center">
              <span>{participant}</span>
              <button
                onClick={() => removeParticipant(index)}
                className="ml-2 text-white hover:text-red-200"
                disabled={isRecording}
              >
                ×
              </button>
            </div>
          ))}
        </div>
        <button
          onClick={addParticipant}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
          disabled={isRecording}
        >
          Adicionar Participante
        </button>
      </div>

      {/* Recording Controls */}
      <div className="mb-6 bg-gray-100 p-4 rounded">
        <h2 className="text-lg font-semibold mb-3">Controles de Gravação</h2>
        <div className="flex items-center gap-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="bg-red-500 text-white px-6 py-3 rounded-full hover:bg-red-600 flex items-center"
            >
              <span className="mr-2">●</span> Iniciar Gravação
            </button>
          ) : (
            <>
              {!isPaused ? (
                <button
                  onClick={pauseRecording}
                  className="bg-yellow-500 text-white px-6 py-3 rounded-full hover:bg-yellow-600"
                >
                  ⏸ Pausar
                </button>
              ) : (
                <button
                  onClick={resumeRecording}
                  className="bg-green-500 text-white px-6 py-3 rounded-full hover:bg-green-600"
                >
                  ▶ Continuar
                </button>
              )}
              <button
                onClick={stopRecording}
                className="bg-gray-500 text-white px-6 py-3 rounded-full hover:bg-gray-600"
                disabled={isProcessing}
              >
                ⏹ Parar
              </button>
            </>
          )}
          
          {/* Duration display */}
          {isRecording && (
            <div className="ml-4 text-lg font-mono">
              {formatDuration(recordingDuration)}
            </div>
          )}
        </div>

        {/* Audio level indicator */}
        {isRecording && (
          <div className="mt-4">
            <div className="h-2 bg-gray-300 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 transition-all duration-100"
                style={{ width: `${audioLevel * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Real-time Transcription */}
      {realtimeText && (
        <div className="mb-6 bg-gray-100 p-4 rounded">
          <h2 className="text-lg font-semibold mb-3">Transcrição em Tempo Real</h2>
          <div className="bg-white p-3 rounded border border-gray-300 max-h-40 overflow-y-auto">
            {realtimeText}
          </div>
        </div>
      )}

      {/* Detected Speakers */}
      {detectedSpeakers.length > 0 && (
        <div className="mb-6 bg-gray-100 p-4 rounded">
          <h2 className="text-lg font-semibold mb-3">Falantes Detectados</h2>
          <div className="flex flex-wrap gap-2">
            {detectedSpeakers.map((speaker, index) => (
              <div key={index} className="bg-green-500 text-white px-3 py-1 rounded-full">
                {speaker.name} ({(speaker.confidence * 100).toFixed(0)}%)
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Processing indicator */}
      {isProcessing && (
        <div className="mb-6 bg-blue-100 p-4 rounded text-center">
          <div className="inline-flex items-center">
            <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Processando transcrição final...
          </div>
        </div>
      )}

      {/* Final Transcription */}
      {transcriptionText && !isRecording && (
        <div className="mb-6 bg-gray-100 p-4 rounded">
          <h2 className="text-lg font-semibold mb-3">Transcrição Final</h2>
          <div className="bg-white p-4 rounded border border-gray-300 max-h-96 overflow-y-auto">
            <pre className="whitespace-pre-wrap font-sans">{transcriptionText}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default TranscriptionExample;