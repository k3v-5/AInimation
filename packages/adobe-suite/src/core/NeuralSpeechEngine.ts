import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { WavGenerator, VisemeCue } from './WavGenerator.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export type EmotionPreset = 'neutral' | 'cheerful' | 'whispering' | 'angry' | 'sad' | 'excited' | 'dramatic';

export interface SpeechSynthesisOptions {
  text: string;
  outputPath: string;
  voice?: string;
  rate?: string;
  pitch?: string;
  volume?: string;
  emotionPreset?: EmotionPreset;
}

export interface SpeechSynthesisResult {
  status: 'SUCCESS' | 'FALLBACK_SAPI' | 'FALLBACK_PCM';
  filePath: string;
  durationSeconds: number;
  sampleRate: number;
  channels: number;
  bitDepth: string;
  normalization: string;
  voiceUsed: string;
  engineUsed: string;
  readyForLipSync: boolean;
}

export interface VisemeMarkerCue {
  index: number;
  timeSeconds: number;
  frame: number;
  durationSeconds: number;
  durationFrames: number;
  viseme: string;
  token: string;
}

export interface MarkerExportResult {
  status: 'SUCCESS';
  jsonPath?: string;
  jsxPath?: string;
  csvPath?: string;
  totalCues: number;
  fps: number;
  durationSeconds: number;
  cues: VisemeMarkerCue[];
}

export class NeuralSpeechEngine {
  public static readonly VOICE_ALIASES: Record<string, string> = {
    // Spanish
    mexico_female: 'es-MX-DaliaNeural',
    mexico_male: 'es-MX-JorgeNeural',
    spain_female: 'es-ES-ElviraNeural',
    spain_male: 'es-ES-AlvaroNeural',
    argentina_female: 'es-AR-ElenaNeural',
    argentina_male: 'es-AR-TomasNeural',
    colombia_female: 'es-CO-SalomeNeural',
    colombia_male: 'es-CO-GonzaloNeural',
    // English
    us_female: 'en-US-JennyNeural',
    us_male: 'en-US-GuyNeural',
    uk_female: 'en-GB-SoniaNeural',
    uk_male: 'en-GB-RyanNeural',
    // Japanese
    japan_female: 'ja-JP-NanamiNeural',
    japan_male: 'ja-JP-KeitaNeural'
  };

  public static readonly EMOTION_SETTINGS: Record<EmotionPreset, { rate: string; pitch: string; volume: string }> = {
    neutral: { rate: '+0%', pitch: '+0Hz', volume: '+0%' },
    cheerful: { rate: '+8%', pitch: '+8Hz', volume: '+5%' },
    whispering: { rate: '-10%', pitch: '-5Hz', volume: '-25%' },
    angry: { rate: '+15%', pitch: '+12Hz', volume: '+15%' },
    sad: { rate: '-18%', pitch: '-10Hz', volume: '-10%' },
    excited: { rate: '+20%', pitch: '+15Hz', volume: '+10%' },
    dramatic: { rate: '-8%', pitch: '-4Hz', volume: '+5%' }
  };

  /**
   * Resolves a voice alias or returns the voice name directly.
   */
  public static resolveVoice(voiceInput?: string): string {
    if (!voiceInput) return 'es-MX-DaliaNeural';
    const lower = voiceInput.toLowerCase().trim();
    return this.VOICE_ALIASES[lower] || voiceInput;
  }

  private static getPythonScriptPath(): string {
    const candidatePaths = [
      path.join(__dirname, 'scripts', 'edge_synth.py'),
      path.join(__dirname, '..', '..', 'src', 'core', 'scripts', 'edge_synth.py'),
      path.join(process.cwd(), 'src', 'core', 'scripts', 'edge_synth.py'),
      path.join(process.cwd(), 'dist', 'core', 'scripts', 'edge_synth.py')
    ];
    for (const p of candidatePaths) {
      if (fs.existsSync(p)) return p;
    }
    return candidatePaths[0];
  }

  /**
   * Synthesizes broadcast-ready 48,000 Hz 16-bit Mono PCM speech using Edge-TTS with multi-tier fallback.
   */
  public static async synthesizeSpeech(options: SpeechSynthesisOptions): Promise<SpeechSynthesisResult> {
    const resolvedPath = path.resolve(options.outputPath);
    fs.mkdirSync(path.dirname(resolvedPath), { recursive: true });

    const selectedVoice = this.resolveVoice(options.voice);
    const emotion = options.emotionPreset || 'neutral';
    const emotionConfig = this.EMOTION_SETTINGS[emotion] || this.EMOTION_SETTINGS.neutral;

    const rate = options.rate || emotionConfig.rate;
    const pitch = options.pitch || emotionConfig.pitch;
    const volume = options.volume || emotionConfig.volume;

    // Tier 1: Try Edge-TTS via python helper
    try {
      const scriptPath = this.getPythonScriptPath();
      const payload = JSON.stringify({
        mode: 'synth',
        text: options.text,
        voice: selectedVoice,
        out_wav: resolvedPath,
        rate,
        pitch,
        volume
      });

      const res = await this.executePythonScript(scriptPath, payload);
      if (res.status === 'SUCCESS' && fs.existsSync(resolvedPath)) {
        return {
          status: 'SUCCESS',
          filePath: resolvedPath,
          durationSeconds: res.duration_seconds || 1.0,
          sampleRate: 48000,
          channels: 1,
          bitDepth: '16-bit PCM',
          normalization: res.normalization || 'Peak -1.0 dBFS',
          voiceUsed: selectedVoice,
          engineUsed: 'Microsoft Edge-TTS (Neural)',
          readyForLipSync: true
        };
      }
    } catch (err: any) {
      console.error(`[NeuralSpeechEngine] Edge-TTS tier failed: ${err.message}. Engaging Tier 2 (SAPI)...`);
    }

    // Tier 2: PowerShell SAPI Fallback
    try {
      await WavGenerator.generateSpeechWav(options.text, resolvedPath, options.voice);
      if (fs.existsSync(resolvedPath) && fs.statSync(resolvedPath).size > 44) {
        return {
          status: 'FALLBACK_SAPI',
          filePath: resolvedPath,
          durationSeconds: 2.0,
          sampleRate: 48000,
          channels: 1,
          bitDepth: '16-bit PCM',
          normalization: 'Standard SAPI',
          voiceUsed: options.voice || 'System Default',
          engineUsed: 'Windows System.Speech (SAPI)',
          readyForLipSync: true
        };
      }
    } catch (err: any) {
      console.error(`[NeuralSpeechEngine] SAPI tier failed: ${err.message}. Engaging Tier 3 (PCM generator)...`);
    }

    // Tier 3: Pure PCM WAV Container Fallback
    WavGenerator.createCleanPcmWav(resolvedPath, 2.0);
    return {
      status: 'FALLBACK_PCM',
      filePath: resolvedPath,
      durationSeconds: 2.0,
      sampleRate: 48000,
      channels: 1,
      bitDepth: '16-bit PCM',
      normalization: 'Generated Sine Tone',
      voiceUsed: 'None (Offline Tone)',
      engineUsed: 'Pure PCM WAV Synthesizer',
      readyForLipSync: true
    };
  }

  /**
   * Lists available neural voices from Edge-TTS and local SAPI voices.
   */
  public static async listVoices(filterLocale?: string): Promise<any[]> {
    const scriptPath = this.getPythonScriptPath();
    const payload = JSON.stringify({ mode: 'list' });
    try {
      const res = await this.executePythonScript(scriptPath, payload);
      if (res && Array.isArray(res.voices)) {
        let list = res.voices;
        if (filterLocale && filterLocale !== 'all') {
          const prefix = filterLocale.toLowerCase();
          list = list.filter((v: any) => v.Locale && v.Locale.toLowerCase().startsWith(prefix));
        }
        return list.map((v: any) => ({
          name: v.ShortName,
          friendlyName: v.FriendlyName,
          gender: v.Gender,
          locale: v.Locale,
          suggestedAlias: Object.keys(this.VOICE_ALIASES).find(k => this.VOICE_ALIASES[k] === v.ShortName) || null
        }));
      }
    } catch (err: any) {
      console.error(`[NeuralSpeechEngine] Voice listing error: ${err.message}`);
    }

    // Return built-in aliases if listing fails
    return Object.entries(this.VOICE_ALIASES).map(([alias, voice]) => ({
      name: voice,
      friendlyName: alias,
      gender: alias.includes('female') ? 'Female' : 'Male',
      locale: alias.startsWith('mexico') || alias.startsWith('spain') || alias.startsWith('colombia') || alias.startsWith('argentina') ? 'es' : 'en',
      suggestedAlias: alias
    }));
  }

  /**
   * Generates frame-accurate viseme timeline cues from text and calibrated audio duration.
   */
  public static generateVisemeTimeline(text: string, durationSeconds?: number, fps: number = 24): VisemeMarkerCue[] {
    const words = text.trim().split(/\s+/).filter(w => w.length > 0);
    const totalDuration = durationSeconds && durationSeconds > 0 
      ? durationSeconds 
      : Math.max(1.0, (words.length / 140) * 60);

    const charToViseme: Record<string, string> = {
      a: 'Ah', á: 'Ah',
      e: 'Ee', é: 'Ee', i: 'Ee', í: 'Ee', y: 'Ee',
      o: 'Oh', ó: 'Oh',
      u: 'Uh', ú: 'Uh',
      w: 'W-Oo',
      m: 'M', b: 'M', p: 'M',
      f: 'F', v: 'F',
      l: 'L',
      r: 'R',
      s: 'S', z: 'S', c: 'S', x: 'S',
      d: 'D', t: 'D', n: 'D'
    };

    const cues: VisemeMarkerCue[] = [];
    let currentTime = 0;
    const cleanChars = text.replace(/[\r\n\t]/g, ' ').split('');
    const secondsPerChar = cleanChars.length > 0 ? totalDuration / cleanChars.length : 0.1;

    let index = 0;
    for (let i = 0; i < cleanChars.length; i++) {
      const ch = cleanChars[i].toLowerCase();
      let viseme = 'Neutral';

      if (charToViseme[ch]) {
        viseme = charToViseme[ch];
      } else if (cleanChars[i] === '!' || cleanChars[i] === '¡') {
        viseme = 'Surprised';
      } else if (ch === ' ' || ch === '.' || ch === ',' || ch === ';' || ch === '?') {
        viseme = 'Neutral';
      }

      // Avoid repeating identical consecutive non-vowel visemes to create natural mouth movement
      if (cues.length > 0 && cues[cues.length - 1].viseme === viseme && viseme !== 'Ah' && viseme !== 'Ee') {
        cues[cues.length - 1].durationSeconds += secondsPerChar;
        cues[cues.length - 1].durationFrames = Math.max(1, Math.round(cues[cues.length - 1].durationSeconds * fps));
        currentTime += secondsPerChar;
        continue;
      }

      const dur = secondsPerChar;
      const startFrame = Math.round(currentTime * fps);
      const durFrames = Math.max(1, Math.round(dur * fps));

      cues.push({
        index: index++,
        timeSeconds: parseFloat(currentTime.toFixed(3)),
        frame: startFrame,
        durationSeconds: parseFloat(dur.toFixed(3)),
        durationFrames: durFrames,
        viseme,
        token: cleanChars[i]
      });

      currentTime += dur;
    }

    return cues;
  }

  /**
   * Exports lip sync markers to JSON, After Effects ExtendScript JSX, and/or Premiere/Audition CSV.
   */
  public static exportLipSyncMarkers(
    text: string,
    outputPath: string,
    options: {
      audioPath?: string;
      fps?: number;
      format?: 'json' | 'after_effects_jsx' | 'csv_markers' | 'all';
    } = {}
  ): MarkerExportResult {
    const fps = options.fps || 24;
    const format = options.format || 'all';

    let duration = 0;
    if (options.audioPath && fs.existsSync(options.audioPath)) {
      try {
        const stats = fs.statSync(options.audioPath);
        // If 48kHz 16-bit mono WAV: 96,000 bytes per second
        if (options.audioPath.endsWith('.wav') && stats.size > 44) {
          duration = (stats.size - 44) / 96000;
        }
      } catch {}
    }

    const cues = this.generateVisemeTimeline(text, duration > 0 ? duration : undefined, fps);
    const totalDuration = cues.length > 0 
      ? cues[cues.length - 1].timeSeconds + cues[cues.length - 1].durationSeconds 
      : 1.0;

    const baseDir = path.dirname(path.resolve(outputPath));
    const baseName = path.basename(outputPath, path.extname(outputPath));
    fs.mkdirSync(baseDir, { recursive: true });

    let jsonPath: string | undefined;
    let jsxPath: string | undefined;
    let csvPath: string | undefined;

    // 1. JSON Export
    if (format === 'json' || format === 'all') {
      jsonPath = path.join(baseDir, `${baseName}.json`);
      const payload = {
        metadata: {
          generator: 'AdobeEngineSuit NeuralSpeechEngine',
          text,
          fps,
          totalDurationSeconds: parseFloat(totalDuration.toFixed(3)),
          totalFrames: Math.round(totalDuration * fps),
          totalCues: cues.length
        },
        cues
      };
      fs.writeFileSync(jsonPath, JSON.stringify(payload, null, 2), 'utf-8');
    }

    // 2. After Effects ExtendScript (.jsx) Export
    if (format === 'after_effects_jsx' || format === 'all') {
      jsxPath = path.join(baseDir, `${baseName}.jsx`);
      const markerItemsJs = cues.map(c => 
        `    { time: ${c.timeSeconds}, name: "${c.viseme}", duration: ${c.durationSeconds}, comment: "Viseme ${c.viseme} (${c.token})" }`
      ).join(',\n');

      const jsxCode = `// Generated by AdobeEngineSuit - Character Lip-Sync Marker Track
(function() {
    var comp = app.project.activeItem;
    if (!comp || !(comp instanceof CompItem)) {
        alert("Please select or open an active composition in After Effects to import viseme markers.");
        return;
    }

    app.beginUndoGroup("Import Character Viseme Markers");
    
    var target = (comp.selectedLayers.length > 0) ? comp.selectedLayers[0] : comp;
    var markers = [
${markerItemsJs}
    ];

    for (var i = 0; i < markers.length; i++) {
        var m = new MarkerValue(markers[i].name);
        m.duration = markers[i].duration;
        m.comment = markers[i].comment;
        
        if (target.markerProperty) {
            target.markerProperty.setValueAtTime(markers[i].time, m);
        } else if (target.property("Marker")) {
            target.property("Marker").setValueAtTime(markers[i].time, m);
        }
    }

    app.endUndoGroup();
})();
`;
      fs.writeFileSync(jsxPath, jsxCode, 'utf-8');
    }

    // 3. Premiere / Audition CSV Marker Export
    if (format === 'csv_markers' || format === 'all') {
      csvPath = path.join(baseDir, `${baseName}.csv`);
      const formatTimecode = (sec: number, fRate: number) => {
        const totalFrames = Math.round(sec * fRate);
        const ff = (totalFrames % fRate).toString().padStart(2, '0');
        const totalSec = Math.floor(sec);
        const ss = (totalSec % 60).toString().padStart(2, '0');
        const mm = (Math.floor(totalSec / 60) % 60).toString().padStart(2, '0');
        const hh = Math.floor(totalSec / 3600).toString().padStart(2, '0');
        return `${hh}:${mm}:${ss}:${ff}`;
      };

      let csvLines = ['Marker Name\tDescription\tIn\tOut\tDuration\tMarker Type'];
      for (const cue of cues) {
        const inTc = formatTimecode(cue.timeSeconds, fps);
        const outTc = formatTimecode(cue.timeSeconds + cue.durationSeconds, fps);
        const durTc = formatTimecode(cue.durationSeconds, fps);
        csvLines.push(`${cue.viseme}\tViseme ${cue.viseme} (${cue.token})\t${inTc}\t${outTc}\t${durTc}\tComment`);
      }
      fs.writeFileSync(csvPath, csvLines.join('\r\n'), 'utf-8');
    }

    return {
      status: 'SUCCESS',
      jsonPath,
      jsxPath,
      csvPath,
      totalCues: cues.length,
      fps,
      durationSeconds: parseFloat(totalDuration.toFixed(3)),
      cues
    };
  }

  private static executePythonScript(scriptPath: string, payload: string): Promise<any> {
    return new Promise((resolve, reject) => {
      const child = spawn('python', [scriptPath], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      child.stdout.on('data', (data) => {
        stdout += data.toString('utf-8');
      });

      child.stderr.on('data', (data) => {
        stderr += data.toString('utf-8');
      });

      child.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python process exited with code ${code}: ${stderr}`));
          return;
        }
        try {
          const parsed = JSON.parse(stdout.trim());
          resolve(parsed);
        } catch (e: any) {
          reject(new Error(`Failed to parse Python output as JSON: ${stdout} (Error: ${e.message})`));
        }
      });

      child.on('error', (err) => {
        reject(err);
      });

      child.stdin.write(payload, 'utf-8');
      child.stdin.end();
    });
  }
}
