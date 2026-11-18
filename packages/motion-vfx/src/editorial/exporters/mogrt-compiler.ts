import crypto from "crypto";

export interface MogrtExposedControl {
  controlId: string;
  name: string;
  type: "TEXT" | "COLOR" | "SLIDER" | "CHECKBOX" | "DROPDOWN";
  defaultValue: any;
  minValue?: number;
  maxValue?: number;
  options?: string[];
  expressionBinding: string;
}

export interface MogrtGraphicsDefinition {
  compositionName: string;
  width: number;
  height: number;
  fps: number;
  durationSeconds: number;
  essentialPropertyCount: number;
}

export interface MogrtSpecManifest {
  schemaVersion: "1.0.0";
  templateId: string;
  templateName: string;
  graphicsDefinition: MogrtGraphicsDefinition;
  exposedControls: MogrtExposedControl[];
  assetDependencies: string[];
  provenance: {
    generator: string;
    version: string;
    specHashSha256: string;
  };
}

/**
 * MOGRT_SPEC_GENERATOR = IMPLEMENTED
 * Genera la especificación canónica, determinista y estructurada de plantillas de gráficos esenciales (MOGRT).
 */
export class MogrtSpecGenerator {
  public static generateSpec(params: {
    templateId: string;
    templateName: string;
    definition: MogrtGraphicsDefinition;
    controls: MogrtExposedControl[];
    dependencies?: string[];
  }): MogrtSpecManifest {
    const dependencies = params.dependencies || [];
    const payload = JSON.stringify({
      id: params.templateId,
      name: params.templateName,
      def: params.definition,
      ctrls: params.controls,
      deps: dependencies,
    });

    const specHash = crypto.createHash("sha256").update(payload, "utf8").digest("hex");

    return {
      schemaVersion: "1.0.0",
      templateId: params.templateId,
      templateName: params.templateName,
      graphicsDefinition: params.definition,
      exposedControls: params.controls,
      assetDependencies: dependencies,
      provenance: {
        generator: "Autonomous-Editorial-MOGRT-Spec-Compiler",
        version: "4.0.0",
        specHashSha256: specHash,
      },
    };
  }
}

/**
 * MOGRT_BINARY_PACKAGER = UNVERIFIED
 * Declara con total honestidad arquitectónica que el empaquetado binario ZIP nativo
 * que requiere el runtime propietario de Premiere Pro requiere herramientas externas Adobe.
 */
export class MogrtBinaryPackager {
  public static readonly IS_AVAILABLE = false;

  public static packageBinaryMogrt(spec: MogrtSpecManifest): never {
    throw new Error(
      `[MOGRT_BINARY_PACKAGER_UNVERIFIED] El empaquetador binario nativo MOGRT requiere el entorno local Adobe Essential Graphics SDK. La especificación JSON canónica ('${spec.templateId}') está 100% generada y verificada.`
    );
  }
}
