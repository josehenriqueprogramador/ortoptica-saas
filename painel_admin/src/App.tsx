import React from 'react';

export default function App() {
  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ background: '#0f172a', color: '#fff', padding: '24px', borderRadius: '12px', marginBottom: '24px' }}>
        <h1 style={{ margin: 0 }}>Plataforma Ortóptica SaaS v2.0</h1>
        <p style={{ margin: '8px 0 0 0', opacity: 0.8 }}>Ambiente Enterprise Clinico • Conectado via Docker</p>
      </header>
      <div style={{ background: '#fff', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3 style={{ marginTop: 0, color: '#0f172a' }}>Status dos Sistemas Conectados:</h3>
        <ul>
          <li>Laravel Core Gateway: <code style={{color: '#2563eb'}}>Port 8000</code></li>
          <li>FastAPI Iris Tracking: <code style={{color: '#2563eb'}}>Port 5000</code></li>
          <li>Vector DB Storage: <code style={{color: '#2563eb'}}>Port 6333</code></li>
        </ul>
      </div>
    </div>
  );
}
