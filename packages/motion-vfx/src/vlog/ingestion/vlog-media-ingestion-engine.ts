import fs from "node:fs";
import path from "node:path";
import { MediaMetadataProbe, ProbedMediaMetadata } from "../../assets/core/MediaMetadataProbe.js";
import {
  AudioStreamMetadata,
  FrameRateMode,
  IngestedMediaFile,
  IngestionReport,
  MediaOrientation,
  VideoStreamMetadata,
} from "../contracts/ingestion.types.js";
import { MediaHasher } from "./media-hasher.js";
import { MediaScanner } from "./media-scanner.js";

/** Opciones de configuración para el motor de ingesta */
export interface IngestionEngineOptions {
  allowDuplicates?: boolean; // Default false (ignora duplicados idénticos en checksum)
  computeStreamingSha256?: boolean; // Default true
}

/**
 * Motor de Ingestión y Análisis de Metraje (Milestone 2-A).
 * Recibe material audiovisual bruto y produce un inventario técnico tipado y reproducible
 * garantizando cero modificaciones destructivas sobre los originales.
 */
export class VlogMediaIngestionEngine {
  /**
   * Ingesta uno o varios directorios de medios audiovisuales.
   */
  public static async ingestDirectories(
    rootDirectories: string[],
    options: IngestionEngineOptions = {}
  ): Promise<IngestionReport> {
    const startTime = Date.now();
    const discoveredPaths = MediaScanner.scanDirectories(rootDirectories);

    const validMediaFiles: IngestedMediaFile[] = [];
    const corruptedOrUnsupportedFiles: Array<{ path: string; reason: string }> = [];
    const seenChecksums = new Set<string>();

    let totalDurationSeconds = 0;

    for (const filePath of discoveredPaths) {
      try {
        const stat = fs.statSync(filePath);
        if (!stat.isFile()) continue;

        const ext = path.extname(filePath).toLowerCase();
        const filename = path.basename(filePath);
        const mimeType = MediaScanner.getMimeType(ext);
        const category = MediaScanner.getMediaCategory(ext);

        // 1. Calcular hash SHA-256 determinista
        const checksumSha256 = options.computeStreamingSha256 !== false
          ? await MediaHasher.hashFileStream(filePath)
          : MediaHasher.hashBuffer(Buffer.from(`${filename}_${stat.size}`));

        // 2. Control de duplicados
        if (!options.allowDuplicates && seenChecksums.has(checksumSha256)) {
          corruptedOrUnsupportedFiles.push({
            path: filePath,
            reason: `Duplicate media file detected (SHA-256 already ingested: ${checksumSha256.substring(0, 12)}...)`,
          });
          continue;
        }
        seenChecksums.add(checksumSha256);

        // 3. Inspeccionar metadatos reales mediante MediaMetadataProbe
        const probed: ProbedMediaMetadata = MediaMetadataProbe.probe(filePath);

        // 4. Determinar orientación y aspecto
        const width = probed.width ?? (category === "IMAGE" ? 1920 : undefined);
        const height = probed.height ?? (category === "IMAGE" ? 1080 : undefined);
        const duration = probed.duration ?? (category === "IMAGE" ? 5.0 : undefined);

        let orientation: MediaOrientation = "LANDSCAPE";
        let aspectRatio = "16:9";

        if (width && height) {
          if (height > width) {
            orientation = "PORTRAIT";
            aspectRatio = "9:16";
          } else if (width === height) {
            orientation = "SQUARE";
            aspectRatio = "1:1";
          } else {
            orientation = "LANDSCAPE";
            aspectRatio = "16:9";
          }
        }

        // 5. Streams de video y audio
        let videoStream: VideoStreamMetadata | undefined;
        if (category === "VIDEO" || category === "IMAGE") {
          const fps = probed.fps ?? 30.0;
          videoStream = {
            codec: probed.codec ?? (category === "IMAGE" ? ext.replace(".", "") : "h264"),
            width: width ?? 1920,
            height: height ?? 1080,
            aspectRatio,
            fps,
            frameRateMode: "CFR",
            durationSeconds: duration ?? 5.0,
            orientation,
          };
        }

        let audioStream: AudioStreamMetadata | undefined;
        if (category === "AUDIO" || (category === "VIDEO" && probed.hasAudio !== false)) {
          audioStream = {
            codec: category === "AUDIO" ? ext.replace(".", "") : "aac",
            sampleRateHz: probed.sampleRate ?? 44100,
            channels: probed.channels ?? 2,
            durationSeconds: duration ?? 0.0,
          };
        }

        // 6. Generar huella determinista
        const fingerprint = MediaHasher.generateFingerprint(
          checksumSha256,
          stat.size,
          stat.mtimeMs,
          duration,
          width,
          height,
          probed.fps
        );

        // 7. Generar ID de activo estable
        const assetId = MediaHasher.generateStableAssetId(checksumSha256);

        const ingestedFile: IngestedMediaFile = {
          id: assetId,
          absolutePath: filePath.replace(/\\/g, "/"),
          filename,
          extension: ext,
          mimeType,
          fingerprint,
          videoStream,
          audioStream,
          isReadOnly: true, // INVARIANTE: los originales nunca se tocan
          ingestedAtTimestamp: Date.now(),
        };

        validMediaFiles.push(ingestedFile);
        if (duration) {
          totalDurationSeconds += duration;
        }
      } catch (err: unknown) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        corruptedOrUnsupportedFiles.push({
          path: filePath,
          reason: `Failed to probe media: ${errorMsg}`,
        });
      }
    }

    return {
      inputDirectory: rootDirectories.join("; "),
      totalFilesScanned: discoveredPaths.length,
      validMediaFiles,
      corruptedOrUnsupportedFiles,
      totalDurationSeconds: Number(totalDurationSeconds.toFixed(4)),
      ingestionDurationMs: Date.now() - startTime,
    };
  }
}
