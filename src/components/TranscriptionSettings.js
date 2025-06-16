import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function TranscriptionSettings() {
  const navigate = useNavigate();
  const [apiKey, setApiKey] = useState('');
  const [gptApiKey, setGptApiKey] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Load API keys from electron settings
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    if (window.electronAPI && window.electronAPI.settings) {
      const savedWhisperKey = await window.electronAPI.settings.get('openai_api_key');
      const savedGptKey = await window.electronAPI.settings.get('gpt_api_key');
      if (savedWhisperKey) {
        setApiKey(savedWhisperKey);
      }
      if (savedGptKey) {
        setGptApiKey(savedGptKey);
      }
    }
  };

  const saveApiKeys = async () => {
    if (!apiKey || !gptApiKey) {
      setMessage('Por favor, preencha ambas as API Keys');
      return;
    }
    
    setIsSaving(true);
    try {
      if (window.electronAPI && window.electronAPI.settings) {
        await window.electronAPI.settings.set('openai_api_key', apiKey);
        await window.electronAPI.settings.set('gpt_api_key', gptApiKey);
        setMessage('API Keys salvas com sucesso!');
        
        setTimeout(() => {
          navigate('/');
        }, 1500);
      }
    } catch (error) {
      setMessage('Erro ao salvar API Keys: ' + error.message);
    } finally {
      setIsSaving(false);
    }
  };


  return (
    <div className="electron-container bg-gray-50">
      <div className="card-electron">
        <h2 className="compact-header text-gray-800 text-center">
          Configuração de API Keys
        </h2>

        <div className="space-y-3">
          <div>
            <label className="label-electron text-gray-700">
              OpenAI API Key (Whisper)
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-..."
              className="input-electron"
            />
            <p className="text-xs text-gray-500 mt-1">
              Usada para transcrição de áudio
            </p>
          </div>

          <div>
            <label className="label-electron text-gray-700">
              OpenAI API Key (GPT-4)
            </label>
            <input
              type="password"
              value={gptApiKey}
              onChange={(e) => setGptApiKey(e.target.value)}
              placeholder="sk-..."
              className="input-electron"
            />
            <p className="text-xs text-gray-500 mt-1">
              Usada para análise de reuniões
            </p>
          </div>

          {message && (
            <div className={`text-xs-electron ${message.includes('sucesso') ? 'text-green-600' : 'text-red-600'}`}>
              {message}
            </div>
          )}

          <div className="flex gap-2">
            <button
              onClick={() => navigate('/')}
              className="btn-electron bg-gray-500 text-white hover:bg-gray-600 flex-1"
            >
              Cancelar
            </button>
            <button
              onClick={saveApiKeys}
              disabled={isSaving || !apiKey || !gptApiKey}
              className="btn-electron bg-blue-600 text-white hover:bg-blue-700 flex-1 disabled:opacity-50"
            >
              {isSaving ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TranscriptionSettings;