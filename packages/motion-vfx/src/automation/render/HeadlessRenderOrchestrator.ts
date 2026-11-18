import { MotionEngineError } from "../../errors/index.js";

export class RenderOrchestrationError extends MotionEngineError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`Render Orchestration Error: ${message}`);
  }
}

export interface AERenderOptions {
  aerenderExecutablePath?: string; // Por defecto busca en ruta estándar
  outputModuleTemplate?: string; // ej. "H.264 - Match Source" o "Lossless"
  startFrame?: number;
  endFrame?: number;
  sound?: boolean;
  logFilePath?: string;
  multiProcess?: boolean;
}

export interface FFmpegEncodeOptions {
  codec?: "libx264" | "libx265" | "hevc_nvenc" | "h264_nvenc";
  crf?: number; // ej. 18 (alta calidad)
  preset?: "ultrafast" | "fast" | "medium" | "slow";
  audioBitrate?: string; // ej. "320k"
  pixelFormat?: "yuv420p";
}

/**
 * Orquestador determinista de renderizado desatendido / headless (Suite de Automatización).
 */
export class HeadlessRenderOrchestrator {
  public static readonly DEFAULT_AE_RENDER_PATH =
    "C:/Program Files/Adobe/Adobe After Effects 2024/Support Files/aerender.exe";

  /**
   * Genera el comando CLI para ejecutar el renderizado en segundo plano con aerender de After Effects.
   */
  public static buildAERenderCommand(
    projectAepPath: string,
    compName: string,
    outputFilePath: string,
    options: AERenderOptions = {}
  ): string {
    if (!projectAepPath || !compName || !outputFilePath) {
      throw new RenderOrchestrationError("projectAepPath, compName and outputFilePath are required.");
    }

    const exe = options.aerenderExecutablePath ?? this.DEFAULT_AE_RENDER_PATH;
    const cleanExe = exe.replace(/\\/g, "/");
    const cleanProj = projectAepPath.replace(/\\/g, "/");
    const cleanOut = outputFilePath.replace(/\\/g, "/");
    const omTemplate = options.outputModuleTemplate ?? "H.264";

    let cmd = `"${cleanExe}" -project "${cleanProj}" -comp "${compName}" -output "${cleanOut}" -OMtemplate "${omTemplate}"`;

    if (options.startFrame !== undefined && options.endFrame !== undefined) {
      cmd += ` -s ${options.startFrame} -e ${options.endFrame}`;
    }
    if (options.sound === false) {
      cmd += " -sound OFF";
    }
    if (options.multiProcess) {
      cmd += " -mp";
    }
    if (options.logFilePath) {
      const cleanLog = options.logFilePath.replace(/\\/g, "/");
      cmd += ` -log "${cleanLog}"`;
    }

    return cmd;
  }

  /**
   * Genera el comando CLI para renderizado nativo headless con FFmpeg.
   */
  public static buildFFmpegRenderCommand(
    inputVisualPath: string,
    outputVideoPath: string,
    inputAudioPath?: string,
    options: FFmpegEncodeOptions = {}
  ): string {
    if (!inputVisualPath || !outputVideoPath) {
      throw new RenderOrchestrationError("inputVisualPath and outputVideoPath are required.");
    }

    const codec = options.codec ?? "libx264";
    const crf = options.crf ?? 18;
    const preset = options.preset ?? "fast";
    const pixFmt = options.pixelFormat ?? "yuv420p";
    const aBitrate = options.audioBitrate ?? "320k";

    const cleanIn = inputVisualPath.replace(/\\/g, "/");
    const cleanOut = outputVideoPath.replace(/\\/g, "/");

    let cmd = `ffmpeg -y -i "${cleanIn}"`;
    if (inputAudioPath) {
      const cleanAudio = inputAudioPath.replace(/\\/g, "/");
      cmd += ` -i "${cleanAudio}" -c:a aac -b:a ${aBitrate} -shortest`;
    }

    cmd += ` -c:v ${codec} -crf ${crf} -preset ${preset} -pix_fmt ${pixFmt} "${cleanOut}"`;
    return cmd;
  }
}
