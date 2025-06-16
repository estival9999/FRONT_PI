import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AudioRecorder from '../services/audioRecorder';
import nameValidator from '../services/nameValidator';
import TranscriptionService from '../services/transcription';
import WhisperService from '../services/whisperService';
import { fileManager } from '../utils/fileManager';

function ParticipantsForm() {
  const navigate = useNavigate();
  const [participantName, setParticipantName] = useState('');
  const [participants, setParticipants] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const audioRecorderRef = useRef(null);
  const whisperServiceRef = useRef(null);

  useEffect(() => {
    // Load API key and initialize services
    const loadApiKey = async () => {
      if (window.electronAPI && window.electronAPI.settings) {
        const key = await window.electronAPI.settings.get('openai_api_key');
        if (key) {
          setApiKey(key);
          whisperServiceRef.current = new WhisperService(key);
        }
      }
    };
    loadApiKey();
  }, []);

  const handleStartRecording = async () => {
    if (!audioRecorderRef.current) {
      audioRecorderRef.current = new AudioRecorder();
      await audioRecorderRef.current.initialize();
    }
    
    if (!isRecording) {
      setIsRecording(true);
      audioRecorderRef.current.start();
      
      // Stop after 3 seconds
      setTimeout(async () => {
        const audioBlob = await audioRecorderRef.current.stop();
        setIsRecording(false);
        
        // Validate participant name with audio
        await validateParticipantName(audioBlob);
      }, 3000);
    }
  };

  const validateParticipantName = async (audioBlob) => {
    if (!whisperServiceRef.current) {
      setValidationResult({ error: 'Serviço de transcrição não configurado' });
      return;
    }

    setIsValidating(true);
    try {
      // Transcribe audio
      const result = await whisperServiceRef.current.transcribe(audioBlob, {
        language: 'pt',
        response_format: 'json'
      });

      if (result && result.text) {
        // Validate against employee database
        const validation = nameValidator.validarNome(result.text);
        
        if (validation) {
          setValidationResult({
            success: true,
            nomeCorreto: validation.nomeCorreto,
            score: validation.score,
            funcionario: validation.funcionario
          });
          setParticipantName(validation.nomeCorreto);
        } else {
          setValidationResult({
            warning: true,
            nomeTranscrito: result.text,
            message: 'Nome não encontrado no banco de dados'
          });
          setParticipantName(result.text);
        }
      }
    } catch (error) {
      setValidationResult({ error: 'Erro na validação: ' + error.message });
    } finally {
      setIsValidating(false);
    }
  };

  const handleAddParticipant = () => {
    if (participantName.trim()) {
      const newParticipant = {
        id: Date.now(),
        name: participantName,
        validated: validationResult && validationResult.success,
        funcionario: validationResult && validationResult.funcionario
      };
      setParticipants([...participants, newParticipant]);
      setParticipantName('');
      setValidationResult(null);
    }
  };

  const handleFinish = async () => {
    if (participants.length === 0) return;
    
    try {
      // Update transcription service with participants
      const transcriptionResult = JSON.parse(localStorage.getItem('transcriptionResult') || '{}');
      
      // Prepare meeting info
      const meetingInfo = {
        name: localStorage.getItem('objective') || 'Reunião',
        date: new Date(localStorage.getItem('recordingTimestamp')),
        duration: localStorage.getItem('recordingDuration'),
        participants: participants.map(p => p.name).join(', '),
        responsible: localStorage.getItem('responsibleName') || 'Não especificado',
        location: 'Sistema de Transcrição'
      };

      // Save participants for next screen
      localStorage.setItem('participants', JSON.stringify(participants));
      localStorage.setItem('meetingInfo', JSON.stringify(meetingInfo));
      
      navigate('/participants-list');
    } catch (error) {
      console.error('Erro ao finalizar:', error);
    }
  };

  return (
    <div className="electron-container bg-gray-50">
      <div className="card-electron" style={{ maxWidth: '100%' }}>
        <h2 className="compact-header text-gray-800 text-center">
          Participantes
        </h2>

        <div className="space-y-2">
          <div>
            <label className="label-electron text-gray-700">
              Nome do participante
            </label>
            <input
              type="text"
              value={participantName}
              onChange={(e) => setParticipantName(e.target.value)}
              placeholder="Digite o nome"
              className="input-electron"
            />
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleStartRecording}
              disabled={!participantName.trim() || isRecording || isValidating}
              className={`btn-sm-electron flex-1 ${
                isRecording
                  ? 'bg-red-600 text-white'
                  : isValidating
                  ? 'bg-yellow-600 text-white'
                  : 'bg-gray-600 text-white hover:bg-gray-700'
              } ${!participantName.trim() ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isRecording ? 'Gravando...' : isValidating ? 'Validando...' : 'Gravar nome'}
            </button>
            <button
              onClick={handleAddParticipant}
              disabled={!participantName.trim()}
              className="btn-sm-electron bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
            >
              Adicionar
            </button>
          </div>

          {/* Validation result display */}
          {validationResult && (
            <div className={`p-2 rounded text-xs-electron ${
              validationResult.success ? 'bg-green-100 text-green-700' :
              validationResult.warning ? 'bg-yellow-100 text-yellow-700' :
              'bg-red-100 text-red-700'
            }`}>
              {validationResult.success && (
                <div>
                  ✓ Nome validado: <strong>{validationResult.nomeCorreto}</strong>
                  {validationResult.funcionario && (
                    <div className="text-xs mt-1">
                      Cargo: {validationResult.funcionario.cargo}
                    </div>
                  )}
                </div>
              )}
              {validationResult.warning && (
                <div>
                  ⚠ {validationResult.message}
                  <div className="text-xs mt-1">
                    Transcrito: {validationResult.nomeTranscrito}
                  </div>
                </div>
              )}
              {validationResult.error && (
                <div>✗ {validationResult.error}</div>
              )}
            </div>
          )}

          {participants.length > 0 && (
            <div className="compact-section">
              <p className="text-xs-electron font-medium text-gray-700 mb-1">
                Adicionados: {participants.length}
              </p>
              <div className="scroll-area-electron" style={{ maxHeight: '60px' }}>
                {participants.map((participant) => (
                  <div
                    key={participant.id}
                    className="list-item-electron flex justify-between items-center"
                  >
                    <span>{participant.name}</span>
                    {participant.validated && (
                      <span className="text-green-600 text-xs">✓</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="nav-electron pt-2">
            <button
              onClick={() => navigate('/recording')}
              className="btn-electron bg-gray-500 text-white hover:bg-gray-600"
            >
              Voltar
            </button>
            <button
              onClick={handleFinish}
              disabled={participants.length === 0}
              className="btn-electron bg-gray-800 text-white hover:bg-gray-700 disabled:opacity-50"
            >
              Finalizar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ParticipantsForm;