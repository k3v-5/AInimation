import fs from "node:fs";
import path from "node:path";
import { MotionEngineError } from "../errors/index.js";

export class SoundBankError extends MotionEngineError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`SoundBank Error: ${message}`);
  }
}

export type SFXType = "whoosh" | "impact" | "pop" | "shutter" | "chime";

export interface SoundCue {
  id: string;
  type: SFXType;
  startTimeSec: number;
  volumeDb?: number; // ej. 0, -3, -6
  filename: string;
}

/**
 * Gestor y sintetizador procedural de banco de efectos de sonido (SFX) WAV (Suite de Audio / Fase 13).
 * Genera archivos WAV PCM de 16-bit / 44.1kHz de forma determinista sin dependencias externas.
 */
export class SoundBankManager {
  public static readonly SAMPLE_RATE = 44100;

  /**
   * Crea un buffer de audio WAV PCM de 16-bit mono estándar a partir de muestras normalizadas [-1.0, 1.0].
   */
  public static createWavBuffer(samples: Float32Array): Buffer {
    const numSamples = samples.length;
    const byteRate = this.SAMPLE_RATE * 2;
    const dataSize = numSamples * 2;
    const buffer = Buffer.alloc(44 + dataSize);

    // Encabezado RIFF
    buffer.write("RIFF", 0);
    buffer.writeUInt32LE(36 + dataSize, 4);
    buffer.write("WAVE", 8);

    // Sub-chunk 'fmt '
    buffer.write("fmt ", 12);
    buffer.writeUInt32LE(16, 16); // Tamaño del sub-chunk
    buffer.writeUInt16LE(1, 20); // Formato PCM = 1
    buffer.writeUInt16LE(1, 22); // 1 canal (Mono)
    buffer.writeUInt32LE(this.SAMPLE_RATE, 24);
    buffer.writeUInt32LE(byteRate, 28);
    buffer.writeUInt16LE(2, 32); // Block align = 2 bytes
    buffer.writeUInt16LE(16, 34); // 16 bits por muestra

    // Sub-chunk 'data'
    buffer.write("data", 36);
    buffer.writeUInt32LE(dataSize, 40);

    // Muestras PCM int16
    let offset = 44;
    for (let i = 0; i < numSamples; i++) {
      const s = Math.max(-1.0, Math.min(1.0, samples[i]));
      const intSample = s < 0 ? s * 32768 : s * 32767;
      buffer.writeInt16LE(Math.round(intSample), offset);
      offset += 2;
    }

    return buffer;
  }

  /**
   * Sintetiza el sonido de un Whoosh cinemático (barrido de frecuencia con envolvente en campana).
   */
  public static synthesizeWhoosh(durationSec = 0.45): Buffer {
    const totalSamples = Math.round(durationSec * this.SAMPLE_RATE);
    const samples = new Float32Array(totalSamples);

    for (let i = 0; i < totalSamples; i++) {
      const t = i / this.SAMPLE_RATE;
      const progress = t / durationSec;

      // Envolvente de amplitud gaussiana / campana
      const envelope = Math.sin(progress * Math.PI) ** 2;

      // Barrido de frecuencia: 180Hz -> 950Hz -> 120Hz
      const freq = 180 + Math.sin(progress * Math.PI) * 770;
      const phase = 2 * Math.PI * freq * t;

      // Mezcla de seno + ruido suave filtrado
      const noise = (Math.sin(i * 12.9898) % 1) * 0.25;
      samples[i] = (Math.sin(phase) * 0.75 + noise) * envelope * 0.85;
    }

    return this.createWavBuffer(samples);
  }

  /**
   * Sintetiza un Impact Boom / Sub Drop de alta energía.
   */
  public static synthesizeImpact(durationSec = 0.80): Buffer {
    const totalSamples = Math.round(durationSec * this.SAMPLE_RATE);
    const samples = new Float32Array(totalSamples);

    for (let i = 0; i < totalSamples; i++) {
      const t = i / this.SAMPLE_RATE;
      // Decaimiento exponencial
      const envelope = Math.exp(-t * 5.5);

      // Frecuencia descendente: 90Hz -> 32Hz
      const freq = 32 + (90 - 32) * Math.exp(-t * 9.0);
      const phase = 2 * Math.PI * freq * t;

      // Saturación suave
      const raw = Math.sin(phase) * 0.95;
      samples[i] = Math.tanh(raw) * envelope * 0.9;
    }

    return this.createWavBuffer(samples);
  }

  /**
   * Sintetiza un UI Pop / Click breve para aparición de palabras y badges.
   */
  public static synthesizePop(durationSec = 0.08): Buffer {
    const totalSamples = Math.round(durationSec * this.SAMPLE_RATE);
    const samples = new Float32Array(totalSamples);

    for (let i = 0; i < totalSamples; i++) {
      const t = i / this.SAMPLE_RATE;
      const envelope = Math.exp(-t * 60.0);
      const freq = 1600 - t * 4000;
      const phase = 2 * Math.PI * Math.max(200, freq) * t;
      samples[i] = Math.sin(phase) * envelope * 0.8;
    }

    return this.createWavBuffer(samples);
  }

  /**
   * Sintetiza un obturador de cámara fotográfica (doble clic mecánico para fotos / polaroids).
   */
  public static synthesizeCameraShutter(durationSec = 0.18): Buffer {
    const totalSamples = Math.round(durationSec * this.SAMPLE_RATE);
    const samples = new Float32Array(totalSamples);

    for (let i = 0; i < totalSamples; i++) {
      const t = i / this.SAMPLE_RATE;
      // Primer clic en t=0.0, segundo clic en t=0.08
      const env1 = Math.exp(-t * 90.0);
      const env2 = t >= 0.08 ? Math.exp(-(t - 0.08) * 80.0) : 0;

      const click1 = Math.sin(2 * Math.PI * 2200 * t) * env1;
      const click2 = Math.sin(2 * Math.PI * 1800 * (t - 0.08)) * env2;

      samples[i] = (click1 + click2) * 0.75;
    }

    return this.createWavBuffer(samples);
  }

  /**
   * Sintetiza una campana / Chime armónico.
   */
  public static synthesizeChime(durationSec = 0.90): Buffer {
    const totalSamples = Math.round(durationSec * this.SAMPLE_RATE);
    const samples = new Float32Array(totalSamples);

    for (let i = 0; i < totalSamples; i++) {
      const t = i / this.SAMPLE_RATE;
      const env = Math.exp(-t * 3.5);
      const h1 = Math.sin(2 * Math.PI * 880 * t) * 0.5;
      const h2 = Math.sin(2 * Math.PI * 1760 * t) * 0.3;
      const h3 = Math.sin(2 * Math.PI * 2640 * t) * 0.2;
      samples[i] = (h1 + h2 + h3) * env * 0.8;
    }

    return this.createWavBuffer(samples);
  }

  /**
   * Genera el banco completo de archivos WAV en el directorio destino.
   */
  public static ensureSoundBank(targetDir: string): Record<SFXType, string> {
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    const soundMap: Record<SFXType, string> = {
      whoosh: path.join(targetDir, "whoosh_fast.wav"),
      impact: path.join(targetDir, "impact_sub_boom.wav"),
      pop: path.join(targetDir, "ui_pop_click.wav"),
      shutter: path.join(targetDir, "camera_shutter.wav"),
      chime: path.join(targetDir, "bell_chime.wav"),
    };

    fs.writeFileSync(soundMap.whoosh, this.synthesizeWhoosh());
    fs.writeFileSync(soundMap.impact, this.synthesizeImpact());
    fs.writeFileSync(soundMap.pop, this.synthesizePop());
    fs.writeFileSync(soundMap.shutter, this.synthesizeCameraShutter());
    fs.writeFileSync(soundMap.chime, this.synthesizeChime());

    return soundMap;
  }

  /**
   * Genera el fragmento ExtendScript para importar y sincronizar pistas de audio SFX en After Effects.
   */
  public static generateExtendScriptAudioImportSnippet(
    compVar: string,
    sfxDir: string,
    cues: SoundCue[]
  ): string {
    const cleanDir = sfxDir.replace(/\\/g, "/");
    const lines = [
      `  // === AUDIO DESIGN & FOLEY SOUND BANK IMPORT ===`,
      `  var sfxFolder = project.items.addFolder("SFX Sound Bank");`,
      `  var sfxCache = {};`,
      `  function getSFX(filename) {`,
      `    if (!sfxCache[filename]) {`,
      `      var f = new File("${cleanDir}/" + filename);`,
      `      if (f.exists) {`,
      `        var io = new ImportOptions(f);`,
      `        var item = project.importFile(io);`,
      `        if (item) { item.parentFolder = sfxFolder; sfxCache[filename] = item; }`,
      `      }`,
      `    }`,
      `    return sfxCache[filename];`,
      `  }`,
    ];

    for (let i = 0; i < cues.length; i++) {
      const cue = cues[i];
      lines.push(
        `  var sfxItem_${i} = getSFX("${cue.filename}");`,
        `  if (sfxItem_${i}) {`,
        `    var sfxLayer_${i} = ${compVar}.layers.add(sfxItem_${i});`,
        `    sfxLayer_${i}.name = "SFX_${cue.type}_${i + 1}";`,
        `    sfxLayer_${i}.startTime = ${cue.startTimeSec};`,
        `    sfxLayer_${i}.inPoint = ${cue.startTimeSec};`,
        `  }`
      );
    }

    return lines.join("\n");
  }
}
