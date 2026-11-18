import { SoundDesignMacro } from "../types/index.js";
import { SemanticSFXLibrary } from "./SemanticSFXLibrary.js";

export const BuiltinSoundDesignMacros: Record<string, SoundDesignMacro> = {
  "text-pop": {
    id: "text-pop",
    name: "Text Kinetic Pop",
    description: "Plays a snappy UI pop when text or keyword appears.",
    sfxCategory: "pop",
    duckAmount: 0.1,
    timingOffset: 0.0,
  },
  "social-hook": {
    id: "social-hook",
    name: "High Energy Social Hook",
    description: "Plays an impact sound with music ducking for hook opening.",
    sfxCategory: "impact",
    duckAmount: 0.4,
    timingOffset: -0.03, // Sonido ligeramente anticipado para máxima pegada
  },
  "impact-reveal": {
    id: "impact-reveal",
    name: "Cinematic Impact Reveal",
    description: "Plays deep bass impact upon subject or scene reveal.",
    sfxCategory: "impact",
    duckAmount: 0.5,
    timingOffset: 0.0,
  },
};

/**
 * Motor de macros de diseño sonoro de alto nivel (Fase 13).
 */
export class SoundDesignMacroEngine {
  public static resolveMacro(
    macroId: string
  ): { macro: SoundDesignMacro; sfxId: string } {
    const macro = BuiltinSoundDesignMacros[macroId];
    if (!macro) {
      throw new Error(`SOUND_MACRO_NOT_FOUND: Sound macro '${macroId}' is not registered.`);
    }

    const sfx = SemanticSFXLibrary.findSFX({ category: macro.sfxCategory });
    return {
      macro,
      sfxId: sfx ? sfx.id : "sfx_pop_ui",
    };
  }
}
