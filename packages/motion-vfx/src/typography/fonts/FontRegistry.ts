import { ValidationError } from "../../errors/index.js";
import { FontResource, FontStyle } from "../types/index.js";

/**
 * Registro y resolución de recursos tipográficos y fallbacks (Fase 5F).
 */
export class FontRegistry {
  private static fonts = new Map<string, FontResource[]>();
  public static defaultFallbackFamily = "Inter";

  public static register(font: FontResource): void {
    if (!font || !font.family) {
      throw new ValidationError("Font resource requires a valid 'family' name.");
    }
    const familyKey = font.family.toLowerCase();
    const existing = this.fonts.get(familyKey) ?? [];

    // Comprobar si ya existe la variante exacta
    const duplicate = existing.some((f) => f.weight === font.weight && f.style === font.style);
    if (duplicate) {
      throw new ValidationError(
        `DUPLICATE_FONT: Font variant '${font.family}' (weight=${font.weight}, style=${font.style}) is already registered.`
      );
    }

    existing.push(font);
    this.fonts.set(familyKey, existing);
  }

  public static has(family: string): boolean {
    return this.fonts.has(family.toLowerCase());
  }

  /**
   * Resuelve la fuente solicitada o realiza matching inteligente con fallback.
   */
  public static resolve(
    family: string,
    weight = 400,
    style: FontStyle = "normal"
  ): FontResource {
    let variants = this.fonts.get(family.toLowerCase());

    if (!variants || variants.length === 0) {
      // Intentar resolver fallback
      variants = this.fonts.get(this.defaultFallbackFamily.toLowerCase());
      if (!variants || variants.length === 0) {
        // Fallback sintético mínimo garantizado
        return {
          family: this.defaultFallbackFamily,
          weight: 400,
          style: "normal",
          metrics: { ascent: 0.8, descent: 0.2, lineGap: 0.05, unitsPerEm: 1000 },
        };
      }
    }

    // Filtrar por estilo si es posible
    const styleMatches = variants.filter((f) => f.style === style);
    const pool = styleMatches.length > 0 ? styleMatches : variants;

    // Encontrar el peso más cercano
    let best = pool[0];
    let minDiff = Math.abs(best.weight - weight);

    for (let i = 1; i < pool.length; i++) {
      const diff = Math.abs(pool[i].weight - weight);
      if (diff < minDiff) {
        minDiff = diff;
        best = pool[i];
      }
    }

    return best;
  }

  public static list(): FontResource[] {
    const list: FontResource[] = [];
    for (const variants of this.fonts.values()) {
      list.push(...variants);
    }
    return list;
  }

  public static clear(): void {
    this.fonts.clear();
  }
}

// Registrar fuentes del sistema por defecto
FontRegistry.register({
  family: "Inter",
  weight: 400,
  style: "normal",
  metrics: { ascent: 0.82, descent: 0.18, lineGap: 0.0, unitsPerEm: 1000 },
});
FontRegistry.register({
  family: "Inter",
  weight: 700,
  style: "normal",
  metrics: { ascent: 0.82, descent: 0.18, lineGap: 0.0, unitsPerEm: 1000 },
});
FontRegistry.register({
  family: "Montserrat",
  weight: 900,
  style: "normal",
  metrics: { ascent: 0.85, descent: 0.15, lineGap: 0.0, unitsPerEm: 1000 },
});
FontRegistry.register({
  family: "Roboto",
  weight: 400,
  style: "normal",
  metrics: { ascent: 0.8, descent: 0.2, lineGap: 0.0, unitsPerEm: 1000 },
});
