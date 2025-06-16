import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function ObjectiveForm() {
  const navigate = useNavigate();
  const [objective, setObjective] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (objective.trim()) {
      // Armazenar objetivo (pode usar localStorage ou Context API)
      localStorage.setItem('objective', objective);
      navigate('/recording');
    }
  };

  return (
    <div className="electron-container bg-gray-50">
      <div className="card-electron">
        <h2 className="compact-header text-gray-800 text-center">
          Objetivo da Gravação
        </h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="label-electron text-gray-700">
              Descreva o objetivo
            </label>
            <textarea
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="Ex: Reuniao de planejamento..."
              rows="3"
              className="input-electron resize-none"
              style={{ fontSize: '11px' }}
              required
            />
          </div>
          <div className="nav-electron">
            <button
              type="button"
              onClick={() => navigate('/responsible')}
              className="btn-electron bg-gray-500 text-white hover:bg-gray-600"
            >
              Voltar
            </button>
            <button
              type="submit"
              className="btn-electron bg-gray-800 text-white hover:bg-gray-700"
            >
              Próximo
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ObjectiveForm;