import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function ResponsibleForm() {
  const navigate = useNavigate();
  const [name, setName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (name.trim()) {
      // Armazenar nome do responsável (pode usar localStorage ou Context API)
      localStorage.setItem('responsibleName', name);
      navigate('/objective');
    }
  };

  return (
    <div className="electron-container bg-gray-50">
      <div className="card-electron">
        <h2 className="compact-header text-gray-800 text-center">
          Nome do Responsável
        </h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="label-electron text-gray-700">
              Digite seu nome completo
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Nome completo"
              className="input-electron"
              required
            />
          </div>
          <div className="nav-electron">
            <button
              type="button"
              onClick={() => navigate('/')}
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

export default ResponsibleForm;