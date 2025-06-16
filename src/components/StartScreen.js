import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function StartScreen() {
  const navigate = useNavigate();
  const [hasApiKeys, setHasApiKeys] = useState(false);

  useEffect(() => {
    checkApiKeys();
  }, []);

  const checkApiKeys = async () => {
    if (window.electronAPI && window.electronAPI.settings) {
      const whisperKey = await window.electronAPI.settings.get('openai_api_key');
      const gptKey = await window.electronAPI.settings.get('gpt_api_key');
      setHasApiKeys(!!whisperKey && !!gptKey);
    }
  };

  const handleStart = () => {
    if (!hasApiKeys) {
      alert('Por favor, configure suas API Keys primeiro');
      navigate('/transcription');
    } else {
      navigate('/responsible');
    }
  };

  return (
    <div className="electron-container bg-gray-50">
      <div className="text-center">
        <h1 className="text-xl-electron font-light text-gray-800 mb-6">
          Sistema de Gravação
        </h1>
        <button
          onClick={handleStart}
          className="w-24 h-24 rounded-full bg-gray-800 text-white hover:bg-gray-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-300"
        >
          <span className="text-base-electron font-medium">Iniciar</span>
        </button>
        <p className="text-xs-electron text-gray-600 mt-4">
          Clique para começar
        </p>
        
        <div className="mt-6">
          <button
            onClick={() => navigate('/transcription')}
            className="btn-sm-electron bg-gray-600 text-white hover:bg-gray-700"
          >
            ⚙️ Configurações
          </button>
        </div>
        
        {!hasApiKeys && (
          <div className="mt-4 text-xs-electron text-yellow-600">
            ⚠️ Configure suas API Keys antes de iniciar
          </div>
        )}
      </div>
    </div>
  );
}

export default StartScreen;