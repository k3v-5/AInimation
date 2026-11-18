import crypto from "crypto";

export interface DirectorIntentConfig {
  intentId: string;
  version: string;
  tone: "SOMBER" | "INSPIRING" | "URGENT" | "CONTEMPLATIVE" | "INVESTIGATIVE" | "AGGRESSIVE";
  pace: "FAST" | "BALANCED" | "SLOW" | "VARIABLE";
  emotionalIntensity: number; // 0.0 a 1.0
  visualDensity: number; // 0.0 a 1.0
  cameraPreference: "DYNAMIC" | "STEADY" | "INTIMATE" | "OBSERVATIONAL";
  dialoguePriority: number; // 0.0 a 1.0
  musicPriority: number; // 0.0 a 1.0
  silenceToleranceSeconds: number;
  evidencePriority: number; // 0.0 a 1.0
  forbiddenPatterns: string[];
  preferredPatterns: string[];
}

/**
 * REQ-070: Master Director's Intent Engine
 * Representación declarativa, determinista y versionada de los parámetros de dirección ejecutables.
 */
export class DirectorIntent {
  public readonly config: DirectorIntentConfig;
  public readonly canonicalHash: string;

  constructor(config: DirectorIntentConfig) {
    this.config = config;
    const payload = JSON.stringify(config);
    this.canonicalHash = crypto.createHash("sha256").update(payload, "utf8").digest("hex");
  }

  public static createDefaultDocumentaryIntent(): DirectorIntent {
    return new DirectorIntent({
      intentId: "intent_doc_standard",
      version: "1.0.0",
      tone: "INVESTIGATIVE",
      pace: "BALANCED",
      emotionalIntensity: 0.75,
      visualDensity: 0.65,
      cameraPreference: "OBSERVATIONAL",
      dialoguePriority: 0.90,
      musicPriority: 0.50,
      silenceToleranceSeconds: 3.5,
      evidencePriority: 0.95,
      forbiddenPatterns: ["JUMP_CUT_WITHIN_SPEECH", "UNPROTECTED_EMOTIONAL_CUT"],
      preferredPatterns: ["L_CUT_INTO_BROLL", "ROOM_TONE_ACOUSTIC_CONTINUITY"],
    });
  }

  /**
   * Compila la intención a restricciones concretas consumibles por el pipeline editorial
   */
  public compileConstraints(): {
    minShotDuration: number;
    maxShotDuration: number;
    preferredJCutLcut: boolean;
    requireProofForClaims: boolean;
  } {
    const isFast = this.config.pace === "FAST" || (this.config.tone as string) === "URGENT";
    return {
      minShotDuration: isFast ? 1.5 : 2.5,
      maxShotDuration: isFast ? 5.0 : 9.0,
      preferredJCutLcut: this.config.preferredPatterns.includes("L_CUT_INTO_BROLL"),
      requireProofForClaims: this.config.evidencePriority > 0.8,
    };
  }
}
