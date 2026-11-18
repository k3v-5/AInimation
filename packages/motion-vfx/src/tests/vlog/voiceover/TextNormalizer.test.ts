import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  SUPPORTED_LOCALES,
  TextNormalizer,
} from "../../../vlog/index.js";

describe("Milestone 4 — Text Normalizer & Entity Preservation Suite", () => {
  it("normalizes currencies correctly according to the target locale", () => {
    // es-MX: pesos y centavos
    const normMx = TextNormalizer.normalize("El precio es $1,250.50 por noche", "es-MX");
    assert.ok(normMx.normalizedText.includes("mil doscientos cincuenta pesos con cincuenta centavos"));

    // en-US: dollars and cents
    const normEn = TextNormalizer.normalize("The room costs $1,250.50 per night", "en-US");
    assert.ok(normEn.normalizedText.includes("one thousand two hundred fifty dollars and fifty cents"));

    // pt-BR: reais e centavos
    const normPt = TextNormalizer.normalize("Custa R$ 1,250.50 aqui", "pt-BR");
    assert.ok(normPt.normalizedText.includes("mil duzentos e cinquenta reais e cinquenta centavos"));

    // fr-FR: euros et centimes
    const normFr = TextNormalizer.normalize("Le prix est €1,250.50", "fr-FR");
    assert.ok(normFr.normalizedText.includes("mille deux cent cinquante euros et cinquante centimes"));

    // de-DE: Euro und Cent
    const normDe = TextNormalizer.normalize("Der Preis ist €1,250.50", "de-DE");
    assert.ok(normDe.normalizedText.includes("eintausendzweihundertfünfzig Euro und fünfzig Cent"));
  });

  it("normalizes percentages across all official locales", () => {
    assert.ok(TextNormalizer.normalize("Descuento del 25%", "es-MX").normalizedText.includes("veinticinco por ciento"));
    assert.ok(TextNormalizer.normalize("25% discount", "en-US").normalizedText.includes("twenty-five percent"));
    assert.ok(TextNormalizer.normalize("Rabais de 25%", "fr-FR").normalizedText.includes("vingt-cinq pour cent"));
    assert.ok(TextNormalizer.normalize("25% Rabatt", "de-DE").normalizedText.includes("fünfundzwanzig Prozent"));
    assert.ok(TextNormalizer.normalize("25% de desconto", "pt-BR").normalizedText.includes("vinte e cinco por cento"));
  });

  it("normalizes clock hours into readable spoken words", () => {
    const normHourEs = TextNormalizer.normalize("La cita es a las 8:42 PM", "es-MX");
    assert.ok(normHourEs.normalizedText.includes("ocho cuarenta y dos PM"));

    const normHourEn = TextNormalizer.normalize("The meeting is at 8:42 PM", "en-US");
    assert.ok(normHourEn.normalizedText.includes("eight forty-two PM"));
  });

  it("strictly preserves protected entities (handles, hashtags, URLs, custom names)", () => {
    const raw = "Visita https://antigravity.ai y sigue a @antigravity_dev en #motion_graphics con código PROMO_2026";
    const norm = TextNormalizer.normalize(raw, "es-MX", {
      protectedEntities: ["PROMO_2026"],
    });

    assert.ok(norm.normalizedText.includes("https://antigravity.ai"));
    assert.ok(norm.normalizedText.includes("@antigravity_dev"));
    assert.ok(norm.normalizedText.includes("#motion_graphics"));
    assert.ok(norm.normalizedText.includes("PROMO_2026"));
  });

  it("strips emojis cleanly without breaking text flow", () => {
    const raw = "¡Increíble atardecer en Guadalajara! 🌅✈️🇲🇽🌮";
    const norm = TextNormalizer.normalize(raw, "es-MX");
    assert.equal(norm.normalizedText, "¡Increíble atardecer en Guadalajara!");
  });

  it("supports all 7 official locales without error", () => {
    for (const loc of SUPPORTED_LOCALES) {
      const res = TextNormalizer.normalize("100%", loc);
      assert.ok(res.normalizedText.length > 0);
      assert.equal(res.locale, loc);
    }
  });

  it("PBT: protected custom entity is guaranteed to appear verbatim in normalized output", () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 3, maxLength: 20 }),
        (customBrand) => {
          // Filtrar caracteres de escape de regex o espacios
          const brand = `BRAND_${customBrand.replace(/[^\w]/g, "")}`;
          if (brand.length < 8) return;

          const rawText = `Compra en ${brand} con un descuento del 15% hoy`;
          const res = TextNormalizer.normalize(rawText, "es-MX", {
            protectedEntities: [brand],
          });

          assert.ok(
            res.normalizedText.includes(brand),
            `Protected entity '${brand}' was modified or missing in: '${res.normalizedText}'`
          );
        }
      )
    );
  });
});
