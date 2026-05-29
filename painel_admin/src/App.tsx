import React, { useState, useEffect, useRef } from 'react';
import { Play, SkipForward, Activity, CheckCircle, AlertTriangle, RefreshCw } from 'lucide-react';

interface TelemetryPoint {
  tracking_active: boolean;
  gaze_x: number;
  gaze_y: number;
  confidence: number;
  head_pose: { pitch: number; yaw: number; roll: number };
  current_target: string;
  status: string;
}

export default function App() {
  const [sessionId, setSessionId] = useState<string>('sessao-homologacao-001');
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [sessionStatus, setSessionStatus] = useState<string>('Aguardando Início');
  const [currentTarget, setCurrentTarget] = useState<string>('CENTER');
  const [latestData, setLatestData] = useState<TelemetryPoint | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    if (!canvasRef.current || !latestData) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(canvas.width / 2, 0);
    ctx.lineTo(canvas.width / 2, canvas.height);
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();

    const xPixel = ((latestData.gaze_x + 1) / 2) * canvas.width;
    const yPixel = ((-latestData.gaze_y + 1) / 2) * canvas.height;

    if (latestData.tracking_active) {
      ctx.fillStyle = latestData.confidence > 0.7 ? '#22c55e' : '#eab308';
      ctx.beginPath();
      ctx.arc(xPixel, yPixel, 8, 0, 2 * Math.PI);
      ctx.fill();

      ctx.strokeStyle = latestData.confidence > 0.7 ? 'rgba(34, 197, 94, 0.3)' : 'rgba(234, 179, 8, 0.3)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(xPixel, yPixel, 20 / (latestData.confidence || 0.5), 0, 2 * Math.PI);
      ctx.stroke();
    }
  }, [latestData]);

  const toggleWebSocketConnection = () => {
    if (isConnected) {
      if (wsRef.current) wsRef.current.close();
      setIsConnected(false);
      setLatestData(null);
      return;
    }

    const wsUrl = `ws://localhost:8000/ws/live/${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
      console.log('📡 Conectado ao stream de telemetria do SaMD.');
    };

    ws.onmessage = (event) => {
      const data: TelemetryPoint = JSON.parse(event.data);
      setLatestData(data);
      setCurrentTarget(data.current_target || 'CENTER');
    };

    ws.onclose = () => {
      setIsConnected(false);
      setLatestData(null);
      console.log('🔌 Conexão do WebSocket encerrada.');
    };

    wsRef.current = ws;
  };

  const triggerStartSession = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/session/start/${sessionId}`, { method: 'POST' });
      if (response.ok) setSessionStatus('Exame em Andamento');
    } catch (err) {
      alert('Falha ao conectar com o servidor HTTP do ml_service.');
    }
  };

  const triggerNextTarget = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/session/transition/${sessionId}`, { method: 'POST' });
      const data = await response.json();
      if (response.ok) {
        setCurrentTarget(data.new_target);
        if (data.status === 'COMPLETED') setSessionStatus('Concluído (Pronto para Análise)');
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans p-6">
      <header className="flex justify-between items-center pb-6 border-b border-slate-800 mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-emerald-400">OrtoPtica SaaS</h1>
          <p className="text-xs text-slate-400">Painel de Controle e Telemetria do Especialista (SaMD Engine)</p>
        </div>
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            disabled={isConnected}
            className="bg-slate-800 border border-slate-700 px-3 py-1.5 rounded text-sm font-mono text-emerald-300 focus:outline-none focus:border-emerald-500 disabled:opacity-50"
          />
          <button
            onClick={toggleWebSocketConnection}
            className={`flex items-center gap-2 px-4 py-1.5 rounded text-sm font-semibold transition-colors ${
              isConnected ? 'bg-rose-600 hover:bg-rose-700' : 'bg-emerald-600 hover:bg-emerald-700'
            }`}
          >
            <Activity className="w-4 h-4" />
            {isConnected ? 'Desconectar' : 'Ligar Telemetria'}
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-800 p-5 rounded-xl border border-slate-700/60 flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-bold border-b border-slate-700 pb-2 mb-4">Comandos do Exame</h2>

            <div className="mb-6">
              <label className="text-xs text-slate-400 uppercase tracking-wider font-bold block mb-1">Status do Ciclo:</label>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-700 text-emerald-300">
                {sessionStatus}
              </span>
            </div>

            <div className="mb-6">
              <label className="text-xs text-slate-400 uppercase tracking-wider font-bold block mb-1">Estímulo Ativo no Paciente:</label>
              <div className="text-3xl font-black text-emerald-400 tracking-wide font-mono bg-slate-900/60 p-3 rounded border border-slate-700">
                {currentTarget}
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-3">
            <button
              onClick={triggerStartSession}
              disabled={!isConnected || sessionStatus === 'Exame em Andamento'}
              className="flex items-center justify-center gap-2 w-full py-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 font-bold disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <Play className="w-4 h-4" /> Iniciar Protocolo
            </button>
            <button
              onClick={triggerNextTarget}
              disabled={!isConnected || sessionStatus === 'Aguardando Início'}
              className="flex items-center justify-center gap-2 w-full py-3 rounded-lg bg-amber-600 hover:bg-amber-700 font-bold disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <SkipForward className="w-4 h-4" /> Próximo Alvo (Mudar Eixo)
            </button>
          </div>
        </div>

        <div className="bg-slate-800 p-5 rounded-xl border border-slate-700/60 lg:col-span-2 flex flex-col items-center">
          <h2 className="text-lg font-bold border-b border-slate-700 pb-2 mb-4 w-full text-left">Foveação Binocular e Desvio Angular</h2>
          <div className="relative bg-slate-950 p-2 rounded-lg border border-slate-800 shadow-inner">
            <canvas
              ref={canvasRef}
              width={500}
              height={350}
              className="bg-slate-950 block rounded"
            />
            {!isConnected && (
              <div className="absolute inset-0 bg-slate-950/80 rounded flex items-center justify-center text-sm font-medium text-slate-400 gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-500" /> Ative a conexão para receber as coordenadas cartesianas.
              </div>
            )}
          </div>
        </div>

        <div className="bg-slate-800 p-5 rounded-xl border border-slate-700/60 lg:col-span-3">
          <h2 className="text-lg font-bold border-b border-slate-700 pb-2 mb-4">Métricas de Postura e Rastreamento (SaMD Stream)</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">

            <div className="bg-slate-900 p-3 rounded border border-slate-700">
              <span className="text-xs text-slate-400 block mb-1">Confiança do Tracker</span>
              <span className={`text-xl font-bold font-mono ${latestData?.tracking_active ? 'text-emerald-400' : 'text-rose-500'}`}>
                {latestData?.tracking_active ? `${((latestData.confidence) * 100).toFixed(1)}%` : 'OFFLINE'}
              </span>
            </div>

            <div className="bg-slate-900 p-3 rounded border border-slate-700">
              <span className="text-xs text-slate-400 block mb-1">Ângulo Pitch (Cabeça)</span>
              <span className="text-xl font-bold font-mono text-indigo-400">
                {latestData ? `${latestData.head_pose.pitch}°` : '0.0°'}
              </span>
            </div>

            <div className="bg-slate-900 p-3 rounded border border-slate-700">
              <span className="text-xs text-slate-400 block mb-1">Ângulo Yaw (Cabeça)</span>
              <span className="text-xl font-bold font-mono text-indigo-400">
                {latestData ? `${latestData.head_pose.yaw}°` : '0.0°'}
              </span>
            </div>

            <div className="bg-slate-900 p-3 rounded border border-slate-700">
              <span className="text-xs text-slate-400 block mb-1">Ângulo Roll (Cabeça)</span>
              <span className="text-xl font-bold font-mono text-indigo-400">
                {latestData ? `${latestData.head_pose.roll}°` : '0.0°'}
              </span>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
