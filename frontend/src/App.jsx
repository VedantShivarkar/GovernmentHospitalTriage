import { useState, useEffect } from 'react';
import { collection, onSnapshot, query, orderBy } from 'firebase/firestore';
import { db } from './firebase';

function App() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Query Firestore: Listen to 'patients_queue', order by timestamp
    const q = query(collection(db, 'patients_queue'), orderBy('timestamp', 'desc'));
    
    // onSnapshot creates a real-time WebSocket connection
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const patientData = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      // Sort in memory: Priority 1 & 2 at the top, then by wait time
      const sortedPatients = patientData.sort((a, b) => {
        if (a.triage_results.priority !== b.triage_results.priority) {
          return a.triage_results.priority - b.triage_results.priority;
        }
        return b.queue_analytics.estimated_wait_time_minutes - a.queue_analytics.estimated_wait_time_minutes;
      });

      setPatients(sortedPatients);
      setLoading(false);
    }, (error) => {
      console.error("Firestore Listen Error:", error);
    });

    // Cleanup listener on unmount
    return () => unsubscribe();
  }, []);

  if (loading) {
    return <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center text-2xl">Initializing Enterprise Engine...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-8">
      <header className="mb-8 flex justify-between items-end border-b border-gray-700 pb-4">
        <div>
          <h1 className="text-4xl font-bold text-white tracking-tight">Govt Hospital <span className="text-blue-500">AI Triage</span></h1>
          <p className="text-gray-400 mt-2">Real-time ML Queue Analytics & Routing</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-mono text-blue-400">{patients.length}</p>
          <p className="text-sm text-gray-500 uppercase tracking-widest">Active Patients</p>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-4">
        {patients.map((patient) => {
          const isCritical = patient.triage_results.priority <= 2;
          
          return (
            <div 
              key={patient.id} 
              className={`p-6 rounded-lg border ${isCritical ? 'bg-red-900/20 border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.3)]' : 'bg-gray-800 border-gray-700'} flex flex-col md:flex-row justify-between items-start md:items-center transition-all duration-500`}
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${isCritical ? 'bg-red-500 text-white animate-pulse' : 'bg-blue-500/20 text-blue-300'}`}>
                    Priority {patient.triage_results.priority}
                  </span>
                  <span className="text-xl font-semibold text-white">{patient.triage_results.department}</span>
                  {patient.queue_analytics.is_anomaly && (
                    <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 border border-yellow-500 rounded text-xs">ML Anomaly Detected</span>
                  )}
                </div>
                <p className="text-gray-400 italic mb-2">"{patient.triage_results.clinical_summary}"</p>
                <p className="text-xs text-gray-500 font-mono">ID: {patient.patient_id} | Email: {patient.patient_email}</p>
              </div>

              <div className="mt-4 md:mt-0 md:ml-6 text-left md:text-right border-t md:border-t-0 md:border-l border-gray-700 pt-4 md:pt-0 md:pl-6">
                <p className="text-sm text-gray-400 uppercase tracking-wider mb-1">Dynamic Wait Time</p>
                <p className={`text-4xl font-bold font-mono ${isCritical ? 'text-red-400' : 'text-green-400'}`}>
                  {patient.queue_analytics.estimated_wait_time_minutes} <span className="text-lg text-gray-500">min</span>
                </p>
              </div>
            </div>
          );
        })}

        {patients.length === 0 && (
          <div className="text-center py-20 text-gray-500 border-2 border-dashed border-gray-700 rounded-lg">
            Queue is currently empty. Awaiting automated API ingestion.
          </div>
        )}
      </div>
    </div>
  );
}

export default App;