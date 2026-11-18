import { MotionMacro } from "../types/index.js";
import { KineticTypographyEngine } from "./KineticTypographyEngine.js";
import { MotionMacroRegistry } from "./MotionMacroRegistry.js";

/**
 * Compilador de macros y directivas cinéticas a estructuras ejecutables (Fase 11).
 */
export class MotionCompiler {
  /**
   * Compila un Macro cinético por ID resolviendo sus parámetros e hijos.
   */
  public static compileMacro(
    macroId: string,
    parameterOverrides: Record<string, unknown> = {}
  ): { macro: MotionMacro; compiledElements: any[] } {
    const baseMacro = MotionMacroRegistry.get(macroId);
    if (!baseMacro) {
      throw new Error(`MOTION_MACRO_NOT_FOUND: Macro '${macroId}' is not registered.`);
    }

    const mergedParams = { ...baseMacro.parameters, ...parameterOverrides };
    const compiledElements: any[] = [];

    for (const elem of baseMacro.elements) {
      if (elem.type === "text" && typeof mergedParams.text === "string") {
        const segments = KineticTypographyEngine.segmentText(mergedParams.text, {
          emphasizedWords: mergedParams.accentWord ? [mergedParams.accentWord as string] : [],
        });
        compiledElements.push({
          type: "kinetic_text",
          timing: elem.timing,
          segments,
        });
      } else {
        compiledElements.push({
          type: elem.type,
          timing: elem.timing,
          params: { ...elem.params, ...parameterOverrides },
        });
      }
    }

    return {
      macro: { ...baseMacro, parameters: mergedParams },
      compiledElements,
    };
  }

  /**
   * Vincula una señal de audio reactiva a una propiedad de escala o resplandor (Audio-Reactive).
   */
  public static evaluateAudioReactiveScale(
    baseScale: number,
    audioAmplitude: number,
    sensitivity = 0.25
  ): number {
    return baseScale + Math.max(0, audioAmplitude) * sensitivity;
  }
}
