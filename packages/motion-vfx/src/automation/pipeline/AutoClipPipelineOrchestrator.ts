import fs from "node:fs";
import path from "node:path";
import { SoundBankManager, SFXType } from "../../audio-design/SoundBankManager.js";
import { MotionEngineError } from "../../errors/index.js";
import { ViralCandidateClip, ViralMomentDetector } from "../clipping/ViralMomentDetector.js";
import { SocialLaunchPackager, YouTubeLaunchPackage, TikTokLaunchPackage } from "../packaging/SocialLaunchPackager.js";
import { ActiveSpeakerReframingEngine } from "../reframing/ActiveSpeakerReframingEngine.js";
import { LocalWhisperTranscriptionBridge } from "../transcription/LocalWhisperTranscriptionBridge.js";

export class AutoClipError extends MotionEngineError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`AutoClip Error: ${message}`);
  }
}

export interface AutoClipOptions {
  inputVideoPath: string;
  transcriptText?: string;
  totalDurationSec?: number;
  stylePreset?: "hormozi_cashflow_captions" | "mrbeast_hyper_retention" | "time_editorial_poster" | "johnny_harris_investigative";
  outputDir?: string;
  topK?: number;
  projectName?: string;
  includeSoundBank?: boolean;
}

export interface GeneratedClipOutput {
  clipIndex: number;
  clipData: ViralCandidateClip;
  jsxScriptPath: string;
  manifestPath: string;
  youtubePackage: YouTubeLaunchPackage;
  tiktokPackage: TikTokLaunchPackage;
}

export interface AutoClipPipelineResult {
  projectName: string;
  inputVideoPath: string;
  totalClipsGenerated: number;
  clips: GeneratedClipOutput[];
  soundBankDir?: string;
}

/**
 * Orquestador determinista del Pipeline de 1-Clic Auto-Clip (Long-to-Shorts / TikTok & YouTube).
 */
export class AutoClipPipelineOrchestrator {
  /**
   * Ejecuta el pipeline completo de auto-clip desde video crudo hasta scripts JSX y metadatos listos.
   */
  public static run(options: AutoClipOptions): AutoClipPipelineResult {
    if (!options.inputVideoPath) {
      throw new AutoClipError("inputVideoPath is required.");
    }

    const projName = options.projectName ?? "AutoClip_Production";
    const outDir = options.outputDir ?? "./dist/autoclip";
    const topK = options.topK ?? 3;
    const stylePreset = options.stylePreset ?? "hormozi_cashflow_captions";

    if (!fs.existsSync(outDir)) {
      fs.mkdirSync(outDir, { recursive: true });
    }

    // 1. Obtener o sintetizar la transcripción
    const transcriptText = options.transcriptText ?? "DESCUBRE EL SECRETO VIRAL QUE CAMBIARÁ TU CONTENIDO PARA SIEMPRE";
    const totalDuration = options.totalDurationSec ?? 60.0;
    const transcriptDoc = LocalWhisperTranscriptionBridge.synthesizeDeterministicTranscript(
      transcriptText,
      totalDuration
    );

    // 2. Detectar los mejores momentos virales
    const viralClips = ViralMomentDetector.detectViralMoments(
      transcriptDoc,
      [],
      [15.0, 45.0],
      topK
    );

    // 3. Generar el banco de sonidos SFX si está habilitado
    let sfxDir: string | undefined;
    if (options.includeSoundBank !== false) {
      sfxDir = path.join(outDir, "sfx");
      SoundBankManager.ensureSoundBank(sfxDir);
    }

    const generatedClips: GeneratedClipOutput[] = [];

    // 4. Generar cada clip individual en 9:16 con su JSX
    for (let i = 0; i < viralClips.length; i++) {
      const clip = viralClips[i];
      const clipName = `${projName}_Clip_${i + 1}`;
      const clipJsxPath = path.join(outDir, `${clipName}.jsx`);
      const clipManifestPath = path.join(outDir, `${clipName}_manifest.json`);

      // Paquete de lanzamiento
      const ytPkg = SocialLaunchPackager.generateYouTubePackage(
        clipName,
        clip.transcriptSlice.slice(0, 30),
        [{ title: "Hook", startTimeSec: 0 }]
      );
      const ttPkg = SocialLaunchPackager.generateTikTokPackage(
        clipName,
        clip.transcriptSlice.slice(0, 40)
      );

      // Ensamblar script JSX universal
      const cleanVideo = options.inputVideoPath.replace(/\\/g, "/");
      const jsxContent = [
        `// Auto-Generated ExtendScript for ${clipName}`,
        `app.beginUndoGroup("Generate ${clipName}");`,
        `try {`,
        `  var proj = app.project || app.newProject();`,
        `  var comp = proj.items.addComp("${clipName}", 1080, 1920, 1.0, ${clip.duration}, 60.0);`,
        `  comp.bgColor = [0.03, 0.03, 0.05];`,
        `  try { comp.motionBlur = true; } catch(e) {}`,
        `  var rawFile = new File("${cleanVideo}");`,
        `  if (rawFile.exists) {`,
        `    var item = proj.importFile(new ImportOptions(rawFile));`,
        `    var layer = comp.layers.add(item);`,
        `    layer.startTime = 0; layer.inPoint = ${clip.startTime}; layer.outPoint = ${clip.endTime};`,
        `    var sX = (1080 / layer.source.width) * 100;`,
        `    var sY = (1920 / layer.source.height) * 100;`,
        `    var maxS = Math.max(sX, sY);`,
        `    layer.transform.scale.setValue([maxS, maxS]);`,
        `    layer.transform.position.setValue([540, 960]);`,
        `  }`,
        `  // Subtítulo Viral`,
        `  var txt = comp.layers.addText("${clip.transcriptSlice.slice(0, 30).toUpperCase()}");`,
        `  txt.transform.position.setValue([540, 1200]);`,
        `  var tProp = txt.property("ADBE Text Properties") ? txt.property("ADBE Text Properties").property("ADBE Text Document") : (txt.property("Source Text") || txt.property("Texto de origen"));`,
        `  if (!tProp && txt.text) { tProp = txt.text.sourceText; }`,
        `  if (tProp) {`,
        `    var tDoc = tProp.value;`,
        `    tDoc.fontSize = 72;`,
        `    try { tDoc.font = "Impact"; } catch(e) {}`,
        `    tDoc.fillColor = [1.0, 0.9, 0.1]; // Amarillo Viral`,
        `    tDoc.justification = ParagraphJustification.CENTER_JUSTIFY;`,
        `    tProp.setValue(tDoc);`,
        `  }`,
        `  alert("Clip '${clipName}' montado exitosamente en After Effects!");`,
        `} catch(err) { alert("Error: " + err.toString()); }`,
        `app.endUndoGroup();`,
      ].join("\n");

      fs.writeFileSync(clipJsxPath, jsxContent, "utf-8");

      const manifestData = {
        clipName,
        clipData: clip,
        stylePreset,
        aspectRatio: "9:16",
        resolution: { width: 1080, height: 1920 },
        youtube: ytPkg,
        tiktok: ttPkg,
      };

      fs.writeFileSync(clipManifestPath, JSON.stringify(manifestData, null, 2), "utf-8");

      generatedClips.push({
        clipIndex: i + 1,
        clipData: clip,
        jsxScriptPath: clipJsxPath,
        manifestPath: clipManifestPath,
        youtubePackage: ytPkg,
        tiktokPackage: ttPkg,
      });
    }

    return {
      projectName: projName,
      inputVideoPath: options.inputVideoPath,
      totalClipsGenerated: generatedClips.length,
      clips: generatedClips,
      soundBankDir: sfxDir,
    };
  }
}
