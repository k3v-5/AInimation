import { SFXMetadata } from "../types/index.js";

export const BuiltinSFXCatalog: SFXMetadata[] = [
  {
    id: "sfx_whoosh_fast",
    name: "Fast Kinetic Whoosh",
    category: "whoosh",
    energy: "high",
    duration: 0.35,
    tags: ["text", "slide", "fast", "whoosh"],
  },
  {
    id: "sfx_impact_deep",
    name: "Sub Bass Impact",
    category: "impact",
    energy: "high",
    duration: 0.8,
    tags: ["hook", "emphasis", "punch", "impact"],
  },
  {
    id: "sfx_pop_ui",
    name: "Modern UI Pop",
    category: "pop",
    energy: "medium",
    duration: 0.2,
    tags: ["pop", "word", "tag", "counter"],
  },
  {
    id: "sfx_riser_cinematic",
    name: "Cinematic Tension Riser",
    category: "riser",
    energy: "high",
    duration: 2.0,
    tags: ["riser", "build", "transition", "reveal"],
  },
  {
    id: "sfx_click_tech",
    name: "Crisp Tech Click",
    category: "click",
    energy: "low",
    duration: 0.1,
    tags: ["click", "button", "ui", "subtle"],
  },
];

/**
 * Catálogo semántico de efectos de sonido con búsqueda guiada por intención y energía (Fase 13).
 */
export class SemanticSFXLibrary {
  private static catalog: SFXMetadata[] = [...BuiltinSFXCatalog];

  public static list(): SFXMetadata[] {
    return this.catalog;
  }

  public static get(id: string): SFXMetadata | undefined {
    return this.catalog.find((s) => s.id === id);
  }

  public static findSFX(query: {
    category?: SFXMetadata["category"];
    energy?: SFXMetadata["energy"];
    intent?: string;
  }): SFXMetadata | undefined {
    const candidates = this.catalog.filter((sfx) => {
      const catMatch = !query.category || sfx.category === query.category;
      const energyMatch = !query.energy || sfx.energy === query.energy;
      const tagMatch =
        !query.intent || sfx.tags.some((t) => t.toLowerCase() === query.intent?.toLowerCase());
      return catMatch && energyMatch && tagMatch;
    });

    if (candidates.length > 0) return candidates[0];

    // Fallback por categoría
    if (query.category) {
      return this.catalog.find((sfx) => sfx.category === query.category);
    }

    return this.catalog[0];
  }
}
