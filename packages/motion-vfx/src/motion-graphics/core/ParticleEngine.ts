import { CameraDynamicsEngine } from "./CameraDynamicsEngine.js";
import { Particle, ParticleEmitterConfig } from "../types/index.js";

/**
 * Emisor determinista de partículas para efectos visuales de celebración y movimiento (Fase 11).
 */
export class ParticleEngine {
  /**
   * Genera el estado de partículas para un tiempo t determinista.
   */
  public static generateParticles(
    config: ParticleEmitterConfig,
    t: number
  ): Particle[] {
    const particles: Particle[] = [];
    const colors = ["#ff0055", "#00e5ff", "#ffeb3b", "#00e676", "#ffffff"];

    for (let i = 0; i < config.count; i++) {
      const pSeed = config.seed + i;
      const angle = CameraDynamicsEngine.seededRandom(pSeed, 1) * Math.PI * 2;
      const speed = 100 + CameraDynamicsEngine.seededRandom(pSeed, 2) * 300;
      const lifetime = 1.0 + CameraDynamicsEngine.seededRandom(pSeed, 3) * 1.5;
      const color = colors[i % colors.length];

      const age = t;
      const progress = Math.min(1.0, age / lifetime);

      // Física simple con gravedad determinista
      const gravity = config.preset === "confetti" ? 150 : 0;
      const posX = Math.cos(angle) * speed * age;
      const posY = Math.sin(angle) * speed * age + 0.5 * gravity * age * age;
      const opacity = Math.max(0, 1.0 - progress);

      particles.push({
        id: i,
        position: { x: posX, y: posY },
        velocity: { x: Math.cos(angle) * speed, y: Math.sin(angle) * speed },
        size: 4 + CameraDynamicsEngine.seededRandom(pSeed, 4) * 6,
        color,
        opacity,
        lifetime,
        age,
      });
    }

    return particles;
  }
}
