import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import IncidentDetail from './components/IncidentDetail';
import './index.css';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedIncident, setSelectedIncident] = useState(null);

  const handleSelectIncident = (incident) => {
    setSelectedIncident(incident);
    setCurrentView('detail');
  };

  const handleBackToDashboard = () => {
    setSelectedIncident(null);
    setCurrentView('dashboard');
  };

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      <Sidebar
        currentView={currentView}
        setCurrentView={(view) => {
          if (view !== 'detail') setSelectedIncident(null);
          setCurrentView(view);
        }}
      />

      <main className="flex-1 overflow-hidden relative flex flex-col">
        {currentView === 'dashboard' && (
          <div className="flex-1 overflow-y-auto">
            <Dashboard onSelectIncident={handleSelectIncident} />
          </div>
        )}

        {currentView === 'detail' && selectedIncident && (
          <div className="flex-1 overflow-hidden">
            <IncidentDetail
              incident={selectedIncident}
              onBack={handleBackToDashboard}
            />
          </div>
        )}

        {(currentView === 'history' || currentView === 'settings') && (
          <div className="flex-1 flex items-center justify-center bg-slate-50">
             <div className="text-center">
               <h2 className="text-2xl font-bold text-slate-700 capitalize">{currentView}</h2>
               <p className="text-slate-500 mt-2">This module is under construction.</p>
             </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
