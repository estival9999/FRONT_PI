import React from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import StartScreen from './components/StartScreen';
import ResponsibleForm from './components/ResponsibleForm';
import ObjectiveForm from './components/ObjectiveForm';
import RecordingScreen from './components/RecordingScreen';
import ParticipantsForm from './components/ParticipantsForm';
import ParticipantsList from './components/ParticipantsList';
import TranscriptionSettings from './components/TranscriptionSettings';

function App() {
  return (
    <Router>
      <div className="w-full h-screen bg-gray-50 overflow-hidden">
        <Routes>
          <Route path="/" element={<StartScreen />} />
          <Route path="/responsible" element={<ResponsibleForm />} />
          <Route path="/objective" element={<ObjectiveForm />} />
          <Route path="/recording" element={<RecordingScreen />} />
          <Route path="/participants-form" element={<ParticipantsForm />} />
          <Route path="/participants-list" element={<ParticipantsList />} />
          <Route path="/transcription" element={<TranscriptionSettings />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;