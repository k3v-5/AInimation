/**
 * Utilidades matemáticas y acústicas para el motor de audio (Fase 5D).
 */
export class AudioMath {
  /**
   * Convierte un valor de ganancia en decibeles a factor multiplicador lineal.
   */
  public static dbToGain(db: number): number {
    return Math.pow(10, db / 20);
  }

  /**
   * Convierte un factor multiplicador lineal a decibeles.
   */
  public static gainToDb(gain: number): number {
    if (gain <= 1e-12) return -120; // Silencio práctico
    return 20 * Math.log10(gain);
  }

  /**
   * Calcula los coeficientes estéreo de paneo usando la ley de igual potencia (Equal-Power Pan Rule).
   * pan: [-1 (left), 0 (center), +1 (right)]
   */
  public static calculateStereoPan(pan: number): { left: number; right: number } {
    const clampedPan = Math.max(-1, Math.min(1, pan));
    const angle = ((clampedPan + 1) * Math.PI) / 4; // 0 -> PI/2
    return {
      left: Math.cos(angle),
      right: Math.sin(angle),
    };
  }

  /**
   * Aplica limitador suave / soft-clipping para prevenir distorsión digital sin truncar bruscamente.
   */
  public static softLimit(sample: number, threshold = 0.95): number {
    if (Math.abs(sample) <= threshold) {
      return sample;
    }
    const sign = sample < 0 ? -1 : 1;
    const excess = Math.abs(sample) - threshold;
    const compressed = threshold + (1 - threshold) * Math.tanh(excess / (1 - threshold));
    return sign * Math.min(1.0, compressed);
  }
}
