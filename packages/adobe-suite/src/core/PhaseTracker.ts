import fs from 'fs';
import path from 'path';

export interface PhaseInfo {
  phase: number;
  title: string;
  description: string;
  completedAt?: string;
}

export interface RoadmapState {
  currentPhase: number;
  status: 'IN_PROGRESS' | 'COMPLETED';
  nextPhase: number | null;
  completedPhases: PhaseInfo[];
  pendingPhases: PhaseInfo[];
  lastUpdated: string;
}

const ROADMAP_PHASES: PhaseInfo[] = [
  {
    phase: 1,
    title: 'Fundación del Servidor MCP Nativo',
    description: 'Arquitectura modular limpia, detección automática del sistema, 14 tools básicas y 0 mocks.'
  },
  {
    phase: 2,
    title: 'Rigging Profundo Character Animator',
    description: 'Físicas reactivas (Dangle, Draggable, Fixed), 14 visemas gráficos estilizados, parallax 2.5D y hand swap sets.'
  },
  {
    phase: 3,
    title: 'Illustrator Vector Studio & Image-to-Rig',
    description: 'Vectorización Image Trace, despiece anatómico inteligente y generación de paletas procedimentales.'
  },
  {
    phase: 4,
    title: 'Voz Neuronal Edge-TTS & Lip-Sync Preciso',
    description: 'Síntesis multilingüe con modulación emocional y marcadores de línea de tiempo.'
  },
  {
    phase: 5,
    title: 'Interoperabilidad con Motor de After Effects del Usuario',
    description: 'Scene Manifest JSON, composiciones con cámaras 2.5D y expresiones de rebote/squash & stretch.'
  },
  {
    phase: 6,
    title: 'Blender 3D & Grease Pencil Híbrido',
    description: 'Fondos 3D procedurales, pases de render con canal alfa y trazos Grease Pencil 2D en espacio 3D.'
  },
  {
    phase: 7,
    title: 'Visión Multimodal & Pipelines de 1 Clic',
    description: 'Inspección de fotogramas en Base64 para modelos multimodales y macros end-to-end automatizados.'
  }
];

export class PhaseTracker {
  private static getStatePath(): string {
    return path.resolve(process.cwd(), '.animation_roadmap_state.json');
  }

  public static getState(): RoadmapState {
    const filePath = this.getStatePath();
    if (fs.existsSync(filePath)) {
      try {
        return JSON.parse(fs.readFileSync(filePath, 'utf8'));
      } catch {}
    }

    // Default state: Phase 1 completed, Phase 2 in progress
    return {
      currentPhase: 2,
      status: 'IN_PROGRESS',
      nextPhase: 3,
      completedPhases: [
        {
          ...ROADMAP_PHASES[0],
          completedAt: new Date().toISOString()
        }
      ],
      pendingPhases: ROADMAP_PHASES.slice(1),
      lastUpdated: new Date().toISOString()
    };
  }

  public static markPhaseCompleted(phaseNumber: number): RoadmapState {
    const state = this.getState();
    const phaseDef = ROADMAP_PHASES.find(p => p.phase === phaseNumber);

    if (!state.completedPhases.some(p => p.phase === phaseNumber)) {
      state.completedPhases.push({
        ...(phaseDef || { phase: phaseNumber, title: `Fase ${phaseNumber}`, description: '' }),
        completedAt: new Date().toISOString()
      });
    }

    state.currentPhase = phaseNumber;
    state.status = 'COMPLETED';
    state.nextPhase = phaseNumber < ROADMAP_PHASES.length ? phaseNumber + 1 : null;
    state.pendingPhases = ROADMAP_PHASES.filter(p => !state.completedPhases.some(cp => cp.phase === p.phase));
    state.lastUpdated = new Date().toISOString();

    fs.writeFileSync(this.getStatePath(), JSON.stringify(state, null, 2), 'utf8');
    return state;
  }
}
