import fs from 'fs';
import path from 'path';
import os from 'os';
import { PuppetBuilder } from './PuppetBuilder.js';
import { NeuralSpeechEngine, EmotionPreset } from './NeuralSpeechEngine.js';
import { AdobeDetector } from './AdobeDetector.js';
import { SceneManifestBuilder, SceneManifest } from './SceneManifestBuilder.js';
import { BlenderEngine } from './BlenderEngine.js';
import { execFile, spawn } from 'child_process';
import util from 'util';

const execFileAsync = util.promisify(execFile);

export interface TalkingCharacterPipelineOptions {
  characterName: string;
  dialogueText: string;
  outputDir: string;
  voice?: string;
  emotionPreset?: EmotionPreset;
  launchCharacterAnimator?: boolean;
  puppetDimensions?: { width: number; height: number };
}

export interface TalkingCharacterPipelineResult {
  status: 'SUCCESS';
  characterName: string;
  puppetPsd: string;
  dialogueWav: string;
  lipSyncMarkers: {
    json: string;
    afterEffectsJsx: string;
    csv: string;
  };
  audioStats: {
    durationSeconds: number;
    sampleRate: string;
    voiceUsed: string;
  };
  characterAnimatorLaunched: boolean;
  nextSteps: string[];
}

export interface SocialClipPipelineOptions {
  projectName: string;
  outputDir: string;
  aspectRatio: '9:16' | '16:9' | '1:1';
  characterFile: string;
  backgroundFile?: string;
  dialogueAudioFile?: string;
  lipSyncMarkersFile?: string;
  durationSeconds?: number;
  enableSecondaryBounce?: boolean;
}

export interface SocialClipPipelineResult {
  status: 'SUCCESS';
  projectName: string;
  sceneManifestPath: string;
  afterEffectsJsxPath: string;
  resolution: { width: number; height: number };
  aspectRatio: string;
  layersIncluded: string[];
  readyForRender: boolean;
}

export class PipelineManager {
  /**
   * Reads an image from disk or renders a frame and returns standard MCP Base64 image payload.
   */
  public static async getFrameBase64(imagePath: string, maxWidth?: number): Promise<{
    base64Data: string;
    mimeType: string;
    fileSizeBytes: number;
    resolvedPath: string;
    resolution?: { width: number; height: number };
  }> {
    const resolved = path.resolve(imagePath);
    if (!fs.existsSync(resolved)) {
      throw new Error(`File does not exist: ${resolved}`);
    }

    const ext = path.extname(resolved).toLowerCase();
    let mimeType = 'image/png';
    if (ext === '.jpg' || ext === '.jpeg') mimeType = 'image/jpeg';
    else if (ext === '.webp') mimeType = 'image/webp';
    else if (ext === '.svg') mimeType = 'image/svg+xml';

    const buffer = fs.readFileSync(resolved);
    const base64Data = buffer.toString('base64');
    const fileSizeBytes = buffer.length;

    // Fast PNG dimensions parser
    let resolution: { width: number; height: number } | undefined;
    if (ext === '.png' && buffer.length >= 24) {
      const width = buffer.readUInt32BE(16);
      const height = buffer.readUInt32BE(20);
      resolution = { width, height };
    }

    return {
      base64Data,
      mimeType,
      fileSizeBytes,
      resolvedPath: resolved,
      resolution
    };
  }

  /**
   * One-Click Director Macro: Assembles an anatomically rigged puppet, synthesizes
   * emotional dialogue, computes frame-accurate lip-sync markers, and optionally opens Character Animator.
   */
  public static async createTalkingCharacter(options: TalkingCharacterPipelineOptions): Promise<TalkingCharacterPipelineResult> {
    const outDir = path.resolve(options.outputDir);
    fs.mkdirSync(outDir, { recursive: true });

    const safeName = options.characterName.replace(/[^a-zA-Z0-9_-]/g, '_');
    const puppetPsd = path.join(outDir, `${safeName}_rigged.psd`);
    const dialogueWav = path.join(outDir, `${safeName}_dialogue.wav`);
    const markersBase = path.join(outDir, `${safeName}_lip_sync`);

    // 1. Scaffold Deep Character Animator Puppet
    const dims = options.puppetDimensions || { width: 1080, height: 1080 };
    PuppetBuilder.scaffoldPuppet({
      characterName: options.characterName,
      outPath: puppetPsd,
      width: dims.width,
      height: dims.height,
      includePhysicsTags: true,
      includeHandTriggers: true,
      includeFaceParallax: true
    });

    // 2. Synthesize Broadcast-Quality 48kHz Neural Audio
    const speechResult = await NeuralSpeechEngine.synthesizeSpeech({
      text: options.dialogueText,
      outputPath: dialogueWav,
      voice: options.voice || 'mexico_female',
      emotionPreset: options.emotionPreset || 'cheerful'
    });

    // 3. Export Lip-Sync Markers Track (JSON, After Effects JSX, and CSV)
    const markerResult = NeuralSpeechEngine.exportLipSyncMarkers(options.dialogueText, markersBase, {
      audioPath: dialogueWav,
      fps: 24,
      format: 'all'
    });

    // 4. Optionally launch Character Animator with the generated puppet
    let launched = false;
    if (options.launchCharacterAnimator) {
      const chPath = AdobeDetector.getCharacterAnimatorPath();
      if (chPath) {
        try {
          const child = spawn(chPath, [puppetPsd], { detached: true, stdio: 'ignore' });
          child.unref();
          launched = true;
        } catch {}
      }
    }

    return {
      status: 'SUCCESS',
      characterName: options.characterName,
      puppetPsd,
      dialogueWav,
      lipSyncMarkers: {
        json: markerResult.jsonPath || '',
        afterEffectsJsx: markerResult.jsxPath || '',
        csv: markerResult.csvPath || ''
      },
      audioStats: {
        durationSeconds: speechResult.durationSeconds,
        sampleRate: `${speechResult.sampleRate} Hz Mono 16-bit PCM`,
        voiceUsed: speechResult.voiceUsed
      },
      characterAnimatorLaunched: launched,
      nextSteps: [
        `1. Open Character Animator and import "${puppetPsd}"`,
        `2. Drag "${dialogueWav}" into the Scene timeline`,
        `3. Select Timeline -> "Compute Lip Sync Take from Scene Audio" to instantly sync mouth visemes`,
        `4. To composite with 3D background in After Effects, use "ae_setup_25d_stage"`
      ]
    };
  }

  /**
   * One-Click Director Macro: Builds an optimized social video project (9:16, 16:9, or 1:1)
   * with 2.5D camera parallax, character staging, synchronized audio, and secondary animation bounce.
   */
  public static async createSocialClip(options: SocialClipPipelineOptions): Promise<SocialClipPipelineResult> {
    const outDir = path.resolve(options.outputDir);
    fs.mkdirSync(outDir, { recursive: true });

    let width = 1080;
    let height = 1920; // Default 9:16 vertical for TikTok / Shorts / Reels

    if (options.aspectRatio === '16:9') {
      width = 1920;
      height = 1080;
    } else if (options.aspectRatio === '1:1') {
      width = 1080;
      height = 1080;
    }

    const layersIncluded: string[] = [];
    const layers: any[] = [];

    // Background Layer
    if (options.backgroundFile) {
      layers.push({
        name: 'Background',
        filePath: path.resolve(options.backgroundFile),
        layerType: 'background',
        zDepth: 1600,
        scaleCompensation: true
      });
      layersIncluded.push('Background');
    }

    // Character Layer with optional squash & stretch
    const charExpressions = options.enableSecondaryBounce !== false ? [
      {
        property: 'Scale',
        type: 'squash_and_stretch',
        params: { maxAmplitude: 10, frequency: 3.5, decay: 6 }
      }
    ] : [];

    layers.push({
      name: 'Character_Puppet',
      filePath: path.resolve(options.characterFile),
      layerType: 'character',
      zDepth: 0,
      scaleCompensation: false,
      expressions: charExpressions
    });
    layersIncluded.push('Character_Puppet');

    // Audio Track
    const audioTracks: any[] = [];
    if (options.dialogueAudioFile) {
      audioTracks.push({
        name: 'Main_Dialogue',
        filePath: path.resolve(options.dialogueAudioFile),
        inPoint: 0.0
      });
      layersIncluded.push('Main_Dialogue');
    }

    const sceneManifest: SceneManifest = {
      schemaVersion: '1.0.0',
      sceneName: `${options.projectName}_${options.aspectRatio.replace(':', '_')}`,
      width,
      height,
      fps: 24,
      durationSeconds: options.durationSeconds || 10,
      layers,
      audioTracks,
      lipSyncMarkersPath: options.lipSyncMarkersFile,
      camera: {
        enabled: true,
        createController: true,
        depthOfField: false
      }
    };

    const manifestPath = path.join(outDir, `${options.projectName}_manifest.json`);
    const saved = SceneManifestBuilder.saveManifestAndScript(sceneManifest, manifestPath);

    return {
      status: 'SUCCESS',
      projectName: options.projectName,
      sceneManifestPath: saved.jsonPath,
      afterEffectsJsxPath: saved.jsxPath,
      resolution: { width, height },
      aspectRatio: options.aspectRatio,
      layersIncluded,
      readyForRender: true
    };
  }
}
