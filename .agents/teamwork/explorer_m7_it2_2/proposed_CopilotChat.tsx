import React, { useState } from 'react';
import { CheckCircle, XCircle, Send, Sparkles, AlertCircle } from 'lucide-react';
import { useUIStore } from '../../store';
import { IntermediateAssetCard } from './IntermediateAssetCard';
import type { PlanStep } from '../../types';

export const CopilotChat: React.FC = () => {
  const { activePlan, approveStep, rejectStep } = useUIStore();
  const [prompt, setPrompt] = useState('');

  const defaultSteps: PlanStep[] = [
    {
      step_id: 'sample_step_1',
      index: 0,
      tool_name: 'analyze_audio',
      title: 'Análisis de Audio y Detección de BPM',
      description: 'Extracción de BPM y timestamps de beats para sincronizar cortes de cámara.',
      parameters: { bpm_hint: 128 },
      risk_level: 'low',
      requires_confirmation: false,
      status: 'completed',
      output_preview: 'stems:vocals.wav,drums.wav,bass.wav,other.wav',
    },
    {
      step_id: 'sample_step_2',
      index: 1,
      tool_name: 'image_to_3d',
      title: 'Generación de Malla 3D desde Imagen',
      description: 'Creación de personaje 3D estructurado en formato GLB con texturas PBR.',
      parameters: { image_path: 'concept.png' },
      risk_level: 'medium',
      requires_confirmation: true,
      status: 'approved',
      output_preview: 'character_mesh.glb',
    },
    {
      step_id: 'sample_step_3',
      index: 2,
      tool_name: 'render_video',
      title: 'Render Cinemático en Unreal Engine 5',
      description: 'Disparo de Movie Render Queue con iluminación Lumen y pase ComfyUI.',
      parameters: { resolution: '3840x2160', fps: 60 },
      risk_level: 'high',
      requires_confirmation: true,
      status: 'proposed',
      output_preview: 'final_music_video.mp4',
    },
  ];

  const steps = activePlan?.steps || defaultSteps;

  return (
    <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-4 flex flex-col h-[500px]">
      <div className="flex items-center gap-2 border-b border-zinc-800 pb-3 mb-3">
        <Sparkles className="w-4 h-4 text-cyan-400" />
        <h2 className="text-xs font-mono font-bold tracking-wider text-zinc-200">
          COPILOTO DE PRODUCCIÓN (FAST-MCP)
        </h2>
      </div>

      {/* Production Plan Steps Container */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {steps.map((step) => {
          const isPending = step.status === 'proposed';
          const isApproved = step.status === 'approved' || step.status === 'completed';
          const isRejected = step.status === 'rejected';

          return (
            <div
              key={step.step_id}
              className={`p-3.5 rounded-lg border text-xs transition ${
                isApproved
                  ? 'border-emerald-500/30 bg-emerald-950/10'
                  : isRejected
                  ? 'border-red-500/30 bg-red-950/10'
                  : 'border-zinc-800 bg-zinc-900/60'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-cyan-300">
                    {step.tool_name}
                  </span>
                  <span className="font-semibold text-zinc-200">{step.title}</span>
                </div>
                {isApproved && (
                  <span className="flex items-center gap-1 text-[11px] text-emerald-400">
                    <CheckCircle className="w-3.5 h-3.5" /> Aprobado
                  </span>
                )}
                {isRejected && (
                  <span className="flex items-center gap-1 text-[11px] text-red-400">
                    <XCircle className="w-3.5 h-3.5" /> Rechazado
                  </span>
                )}
                {isPending && step.requires_confirmation && (
                  <span className="flex items-center gap-1 text-[11px] text-amber-400 font-mono">
                    <AlertCircle className="w-3.5 h-3.5" /> Confirmación Requerida
                  </span>
                )}
              </div>
              <p className="text-zinc-400 mb-2.5">{step.description}</p>

              {/* Render intermediate asset card when step is completed or approved */}
              {isApproved && (
                <IntermediateAssetCard
                  toolName={step.tool_name}
                  outputPreview={step.output_preview}
                  status={step.status}
                  parameters={step.parameters}
                />
              )}

              {/* Confirmation Gate Action Buttons */}
              {isPending && step.requires_confirmation && (
                <div className="flex gap-2 justify-end mt-2">
                  <button
                    onClick={() => rejectStep(step.step_id)}
                    className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded font-mono text-[11px] transition"
                  >
                    Rechazar
                  </button>
                  <button
                    onClick={() => approveStep(step.step_id)}
                    className="px-3 py-1 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded font-mono text-[11px] transition"
                  >
                    Aprobar y Ejecutar
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Input Prompt Box */}
      <div className="mt-3 pt-3 border-t border-zinc-800 flex gap-2">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Escribe una instrucción (ej: 'Haz un video cyberpunk a 128 BPM')..."
          className="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-cyan-400 font-sans"
        />
        <button
          onClick={() => setPrompt('')}
          className="p-2 bg-cyan-500 hover:bg-cyan-400 text-black rounded-lg transition"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default CopilotChat;
