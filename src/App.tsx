import React, { useEffect } from 'react';
import {
  Film,
  Cpu,
  Radio,
  Sparkles,
  RefreshCw,
  HardDrive,
  Activity,
} from 'lucide-react';
import { MediaDropzone } from './components/dropzone';
import { CopilotChat } from './components/copilot';
import { Viewport3D } from './components/viewport';
import { Timeline } from './components/timeline';
import { useUIStore } from './store';
import type { ProductionPlan } from './types';

export const App: React.FC = () => {
  const {
    activePlan,
    setActivePlan,
    setAudioAnalysis,
    setAudioPath,
    setImagePath,
    setVideoPath,
    audioAnalysis,
    telemetryEvents,
    addTelemetryEvent,
  } = useUIStore();

  // Load initial demo state on mount if empty
  useEffect(() => {
    if (!activePlan) {
      const demoPlan: ProductionPlan = {
        plan_id: 'plan_cyberpunk_demo',
        title: 'Video Musical Cyberpunk (128 BPM)',
        description:
          'Orquestación completa con Unreal Engine 5, Nanite, iluminación Lumen reactiva a la batería y pase estético ComfyUI.',
        steps: [
          {
            step_id: 'step_1_audio',
            index: 0,
            tool_name: 'analyze_audio',
            title: 'Análisis de Audio y Detección de BPM',
            description:
              'Extracción de tempo (128 BPM) y 32 beats para sincronizar cortes de cámara y pulsos de luz.',
            parameters: { audio_path: 'input_track_128bpm.wav', bpm_hint: 128 },
            risk_level: 'low',
            requires_confirmation: false,
            status: 'completed',
            output_preview: 'outputs/stems/vocals.wav,drums.wav,bass.wav,other.wav',
          },
          {
            step_id: 'step_2_mesh',
            index: 1,
            tool_name: 'image_to_3d',
            title: 'Generación de Malla 3D desde Imagen',
            description:
              'Creación de personaje 3D estructurado en formato GLB con topología limpia y texturas PBR completas.',
            parameters: { image_path: 'character_concept.png' },
            risk_level: 'medium',
            requires_confirmation: true,
            status: 'approved',
            output_preview: 'outputs/character_mesh.glb',
          },
          {
            step_id: 'step_3_rig',
            index: 2,
            tool_name: 'auto_rig',
            title: 'Auto-Rigging Bípedo',
            description:
              'Inyección de esqueleto estándar de 53 huesos compatible con Unreal Engine y cálculo de skinning.',
            parameters: { mesh_path: 'character_mesh.glb' },
            risk_level: 'medium',
            requires_confirmation: true,
            status: 'proposed',
            output_preview: 'outputs/character_rigged.glb',
          },
          {
            step_id: 'step_4_mocap',
            index: 3,
            tool_name: 'extract_mocap',
            title: 'Extracción de Mocap sin Marcadores (GVHMR)',
            description:
              'Reconstrucción de movimiento 3D a partir de video de baile con rotoscopia y limpieza de fondo.',
            parameters: { video_path: 'dance_reference.mp4' },
            risk_level: 'medium',
            requires_confirmation: true,
            status: 'proposed',
            output_preview: 'outputs/dance_mocap.glb',
          },
          {
            step_id: 'step_5_scene',
            index: 4,
            tool_name: 'build_ue5_scene',
            title: 'Construcción de Escena en Unreal Engine 5',
            description:
              'Spawn de CineCameras sincronizadas con el beat, configuración de luces de neón y rigs audio-reactivos.',
            parameters: { style: 'cyberpunk' },
            risk_level: 'low',
            requires_confirmation: false,
            status: 'proposed',
            output_preview: '/Game/Sequences/LS_Stage_Main',
          },
          {
            step_id: 'step_6_render',
            index: 5,
            tool_name: 'render_video',
            title: 'Render Cinemático MRQ + ComfyUI',
            description:
              'Exportación a 4K 60fps con Movie Render Queue y pase final de estilizado neural.',
            parameters: { resolution: '3840x2160', fps: 60 },
            risk_level: 'high',
            requires_confirmation: true,
            status: 'proposed',
            output_preview: 'outputs/final_music_video.mp4',
          },
        ],
        status: 'proposed',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        total_estimated_duration_seconds: 45,
      };

      setActivePlan(demoPlan);
      setAudioPath('input_track_128bpm.wav');
      setImagePath('character_concept.png');
      setVideoPath('dance_reference.mp4');
      setAudioAnalysis({
        bpm: 128.0,
        beat_timestamps: [
          0.0, 0.468, 0.937, 1.406, 1.875, 2.343, 2.812, 3.281, 3.75, 4.218, 4.687, 5.156,
          5.625, 6.093, 6.562, 7.031, 7.5, 7.968, 8.437, 8.906, 9.375, 9.843,
        ],
        duration_seconds: 10.0,
        onset_envelope: [0.1, 0.8, 0.9, 0.3, 0.7, 0.95, 0.85, 0.4, 0.9, 1.0],
        time_signature: '4/4',
        danceability: 0.85,
      });
      addTelemetryEvent({
        type: 'log',
        level: 'info',
        source: 'FastMCP-Orchestrator',
        message: 'Plan de producción cyberpunk cargado con 6 pasos atómicos y puertas de aprobación HITL.',
        timestamp: new Date().toISOString(),
      });
    }
  }, [activePlan, setActivePlan, setAudioAnalysis, setAudioPath, setImagePath, setVideoPath, addTelemetryEvent]);

  const loadDemo = () => {
    setActivePlan(null);
  };

  const latestTelemetry = telemetryEvents[telemetryEvents.length - 1];

  const formatTelemetry = (event: typeof latestTelemetry): string => {
    if (!event) return 'Esperando comandos del copiloto...';
    if (event.type === 'progress') return `[${event.percentage}%] ${event.message}`;
    if (event.type === 'log') return `[${event.level.toUpperCase()}] ${event.message}`;
    if (event.type === 'asset_ready') return `Asset listo: ${event.asset_id} (${event.file_path})`;
    if (event.type === 'plan_proposal') return `Plan propuesto: ${event.plan_id} (${event.steps.length} pasos)`;
    return 'Evento registrado';
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-zinc-950 text-zinc-100 overflow-hidden font-sans">
      {/* Top Application Bar */}
      <header className="h-14 border-b border-zinc-800 bg-zinc-900/80 px-4 flex items-center justify-between backdrop-blur-md z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-tr from-cyan-600 to-cyan-400 rounded-lg text-black shadow-lg shadow-cyan-500/20">
            <Film className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm tracking-wide text-zinc-100">IANIMATION</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-cyan-400 border border-zinc-700">
                v0.1.0-alpha
              </span>
            </div>
            <p className="text-[10px] text-zinc-400">Orquestador 3D con IA y FastMCP</p>
          </div>
        </div>

        {/* System Status Indicators */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/40 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>UE5 Remote Control (Puerto 30010)</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/40 text-cyan-400">
            <Cpu className="w-3.5 h-3.5" />
            <span>FastMCP (6 Herramientas Activas)</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-zinc-800/80 border border-zinc-700 text-zinc-300">
            <Activity className="w-3.5 h-3.5 text-fuchsia-400" />
            <span>60 FPS | Nanite | Lumen</span>
          </div>
        </div>

        {/* Global Toolbar */}
        <div className="flex items-center gap-2">
          <button
            onClick={loadDemo}
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-lg border border-zinc-700 transition"
          >
            <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
            <span>Reiniciar Escena</span>
          </button>
          <button className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg shadow transition">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Auto-Producir</span>
          </button>
        </div>
      </header>

      {/* Main Studio Workspace Grid */}
      <main className="flex-1 p-3 grid grid-cols-12 gap-3 overflow-hidden bg-zinc-950">
        {/* Left Column (Dropzone & Copilot Chat) - 5 cols */}
        <div className="col-span-5 flex flex-col gap-3 h-full overflow-hidden">
          <div className="flex-shrink-0">
            <MediaDropzone />
          </div>
          <div className="flex-1 overflow-hidden">
            <CopilotChat />
          </div>
        </div>

        {/* Right Column (3D Viewport & Audio/Timeline) - 7 cols */}
        <div className="col-span-7 flex flex-col gap-3 h-full overflow-hidden">
          <div className="flex-[3] min-h-[300px] overflow-hidden">
            <Viewport3D />
          </div>
          <div className="flex-[2] min-h-[200px] overflow-hidden">
            <Timeline />
          </div>
        </div>
      </main>

      {/* Global Status Footer */}
      <footer className="h-8 border-t border-zinc-800 bg-zinc-900/90 px-4 flex items-center justify-between text-[11px] font-mono text-zinc-400">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-zinc-300">
            <Radio className="w-3.5 h-3.5 text-cyan-400" />
            <span>Telemetría en Vivo:</span>
          </span>
          <span className="text-zinc-400 truncate max-w-md">
            {formatTelemetry(latestTelemetry)}
          </span>
        </div>

        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <HardDrive className="w-3.5 h-3.5 text-zinc-500" />
            <span>Almacén CAS: Activo (SHA-256)</span>
          </span>
          <span className="text-zinc-600">|</span>
          <span className="text-cyan-400">
            BPM: {audioAnalysis?.bpm ? audioAnalysis.bpm.toFixed(1) : '--'}
          </span>
          <span className="text-zinc-600">|</span>
          <span className="text-emerald-400">Modo Copiloto: HITL Aprobado</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
