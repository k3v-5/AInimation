import fs from "node:fs";
import path from "node:path";
import {
  TTSModelMissingError,
  TTSOfflineViolationError,
} from "../contracts/errors.js";
import { SupportedLocale, VoiceProfile } from "../contracts/language.types.js";
import {
  TTSProvider,
  TTSRequest,
  TTSResult,
} from "../contracts/voiceover.types.js";
import { SUPPORTED_LOCALES } from "../contracts/vlog.constants.js";
import { VoiceCatalog } from "./voice-catalog.js";

/** Opciones de configuración para LocalPiperTTSProvider */
export interface LocalPiperProviderOptions {
  piperBinaryPath?: string;
  modelsDirectory?: string;
}

/**
 * Proveedor Local de Síntesis de Voz Piper TTS (Milestone 4-03).
 * Opera 100% offline sin dependencias de red ni llamadas HTTP.
 * Requiere aprovisionamiento previo de los modelos neuronales .onnx en disco.
 */
export class LocalPiperTTSProvider implements TTSProvider {
  public readonly id = "piper-local";
  public readonly name = "Local Piper TTS";
  public readonly isOfflineOnly = true;

  private modelsDirectory: string;

  constructor(options: LocalPiperProviderOptions = {}) {
    this.modelsDirectory = options.modelsDirectory ?? path.join(process.cwd(), "models", "piper");
  }

  public async isAvailable(): Promise<boolean> {
    return fs.existsSync(this.modelsDirectory);
  }

  public getSupportedLocales(): SupportedLocale[] {
    return [...SUPPORTED_LOCALES];
  }

  public async getAvailableVoices(locale?: SupportedLocale): Promise<VoiceProfile[]> {
    if (locale) {
      return VoiceCatalog.getVoicesForLocale(locale);
    }
    return VoiceCatalog.getAllVoices();
  }

  public validateRequest(request: TTSRequest): void {
    if (!request) {
      throw new Error("TTSRequest cannot be null");
    }
  }

  public async synthesize(request: TTSRequest): Promise<TTSResult> {
    this.validateRequest(request);

    // 1. Resolver voz y verificar existencia de modelo local en disco
    const voiceEntry = VoiceCatalog.getVoiceById(request.voiceId, request.locale);
    const expectedModelPath = path.join(this.modelsDirectory, voiceEntry.modelName);

    if (!fs.existsSync(expectedModelPath)) {
      throw new TTSModelMissingError(
        this.id,
        voiceEntry.modelName,
        expectedModelPath
      );
    }

    // 2. Si el modelo estuviera presente, invocaría el binario local 'piper'
    throw new TTSModelMissingError(
      this.id,
      voiceEntry.modelName,
      expectedModelPath
    );
  }
}
