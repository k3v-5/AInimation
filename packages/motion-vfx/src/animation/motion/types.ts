/**
 * Interfaz base para todas las funciones de movimiento avanzadas (Fase 3C).
 */
export interface MotionFunction {
  readonly type: string;
  evaluate(progress: number): number;
  toJSON(): Record<string, unknown>;
}

export interface MotionMetadata {
  type: string;
  name: string;
  description: string;
  parameters: Record<string, { type: string; default: unknown; min?: number; max?: number; description?: string }>;
}

export interface OvershootOptions {
  amount?: number; // Factor de sobrepaso (default: 1.0)
}

export type SpringPresetName = "gentle" | "snappy" | "bouncy" | "heavy";

export interface SpringOptions {
  mass?: number; // masa m > 0 (default: 1.0)
  stiffness?: number; // rigidez k > 0 (default: 100)
  damping?: number; // amortiguamiento c >= 0 (default: 10)
  velocity?: number; // velocidad inicial v0 (default: 0)
  preset?: SpringPresetName;
}

export interface BounceOptions {
  bounces?: number; // Número de rebotes (default: 3)
  decay?: number; // Factor de decaimiento [0, 1] (default: 0.5)
}

export interface ElasticOptions {
  amplitude?: number; // Amplitud oscilatoria (default: 1.0)
  period?: number; // Período oscilatorio (default: 0.3)
}

export interface ShakeOptions {
  amplitude?: number; // Amplitud de vibración (default: 1.0)
  frequency?: number; // Frecuencia de vibración en Hz (default: 10)
  decay?: boolean; // Si decae a 0 al final del progreso (default: true)
  seed?: number; // Semilla determinista (default: 42)
}

export interface WiggleOptions {
  amplitude?: number; // Amplitud continua (default: 1.0)
  frequency?: number; // Frecuencia continua (default: 2)
  seed?: number; // Semilla determinista (default: 123)
}
