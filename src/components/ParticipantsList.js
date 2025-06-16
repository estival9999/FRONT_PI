import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fileManager } from '../utils/fileManager';
import TranscriptionService from '../services/transcription';

function ParticipantsList() {
  const navigate = useNavigate();
  const [participants, setParticipants] = useState([]);
  const [responsible, setResponsible] = useState('');
  const [objective, setObjective] = useState('');
  const [duration, setDuration] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    // Carregar dados do localStorage
    const savedParticipants = JSON.parse(localStorage.getItem('participants') || '[]');
    const savedResponsible = localStorage.getItem('responsibleName') || '';
    const savedObjective = localStorage.getItem('objective') || '';
    const savedDuration = localStorage.getItem('recordingDuration') || '00:00:00';

    setParticipants(savedParticipants);
    setResponsible(savedResponsible);
    setObjective(savedObjective);
    setDuration(savedDuration);
  }, []);

  const handleProcessAndSave = async () => {
    setIsProcessing(true);
    setError('');
    
    try {
      setProcessingStatus('Carregando transcrição...');
      
      // Get transcription result
      const transcriptionResult = JSON.parse(localStorage.getItem('transcriptionResult') || '{}');
      const meetingInfo = JSON.parse(localStorage.getItem('meetingInfo') || '{}');
      
      if (!transcriptionResult.text) {
        throw new Error('Nenhuma transcrição disponível');
      }

      // Update meeting info with final participants
      meetingInfo.participants = participants.map(p => p.name).join(', ');
      
      // Process transcription with participant names for better detection
      const participantNames = participants.map(p => p.name);
      const transcriptionService = new TranscriptionService('');
      transcriptionService.setParticipants(participantNames);
      
      // Format transcription with speaker identification
      let formattedTranscription = '';
      
      if (transcriptionResult.groupedSegments) {
        transcriptionResult.groupedSegments.forEach(segment => {
          const time = formatSegmentTime(segment.start);
          formattedTranscription += `\n[${time}] ${segment.speaker}:\n${segment.text}\n`;
        });
      } else if (transcriptionResult.segments) {
        transcriptionResult.segments.forEach(segment => {
          const time = formatSegmentTime(segment.start);
          const speaker = segment.speaker || 'Não identificado';
          formattedTranscription += `\n[${time}] ${speaker}:\n${segment.text}\n`;
        });
      } else {
        formattedTranscription = transcriptionResult.text;
      }
      
      setProcessingStatus('Salvando transcrição...');
      
      // Save transcription and analysis
      const result = await fileManager.processMeeting(formattedTranscription, meetingInfo);
      
      if (result.success) {
        setProcessingStatus('Arquivos salvos com sucesso!');
        
        // Show success message
        setTimeout(() => {
          alert(`Reunião processada com sucesso!\n\nTranscrição: ${result.transcription.fileName}\nAnálise: ${result.analysis.fileName}`);
          
          // Clear storage and go to home
          localStorage.clear();
          navigate('/');
        }, 1500);
      }
    } catch (error) {
      console.error('Erro ao processar:', error);
      setError(error.message);
    } finally {
      setIsProcessing(false);
    }
  };
  
  const formatSegmentTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleNewRecording = () => {
    // Limpar dados e voltar ao início
    localStorage.clear();
    navigate('/');
  };

  const handleEdit = () => {
    navigate('/participants-form');
  };

  return (
    <div className="electron-container bg-gray-50">
      <div className="card-electron" style={{ maxWidth: '100%', padding: '6px' }}>
        <h2 className="text-base-electron font-medium text-gray-800 mb-2 text-center">
          Resumo da Gravação
        </h2>

        <div className="space-y-2">
          <div className="compact-section">
            <p className="text-xs-electron font-medium text-gray-600">
              Responsável: <span className="text-gray-900">{responsible}</span>
            </p>
          </div>

          <div className="compact-section">
            <p className="text-xs-electron font-medium text-gray-600">
              Objetivo:
            </p>
            <p className="text-xs-electron text-gray-900" style={{ maxHeight: '30px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {objective}
            </p>
          </div>

          <div className="compact-section">
            <p className="text-xs-electron font-medium text-gray-600">
              Duração: <span className="text-gray-900">{duration}</span>
            </p>
          </div>

          <div className="compact-section">
            <p className="text-xs-electron font-medium text-gray-600 mb-1">
              Participantes ({participants.length})
            </p>
            {participants.length > 0 ? (
              <div className="scroll-area-electron" style={{ maxHeight: '60px' }}>
                {participants.map((participant, index) => (
                  <div
                    key={participant.id}
                    className="list-item-electron flex justify-between"
                  >
                    <span className="text-xs-electron">
                      {index + 1}. {participant.name}
                    </span>
                    {participant.validated && (
                      <span className="text-green-600 text-xs">✓</span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs-electron text-gray-500 italic">Nenhum participante</p>
            )}
          </div>
        </div>

        {error && (
          <div className="text-xs-electron text-red-600 mt-2">
            {error}
          </div>
        )}
        
        {processingStatus && (
          <div className="text-xs-electron text-blue-600 mt-2">
            {processingStatus}
          </div>
        )}

        <div className="nav-electron mt-3">
          <button
            onClick={handleEdit}
            className="btn-sm-electron bg-gray-500 text-white hover:bg-gray-600"
          >
            Editar
          </button>
          <button
            onClick={handleProcessAndSave}
            disabled={isProcessing}
            className="btn-sm-electron bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {isProcessing ? 'Processando...' : 'Finalizar'}
          </button>
          <button
            onClick={handleNewRecording}
            className="btn-sm-electron bg-gray-800 text-white hover:bg-gray-700"
          >
            Nova
          </button>
        </div>
      </div>
    </div>
  );
}

export default ParticipantsList;