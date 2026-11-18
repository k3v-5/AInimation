import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { SRTParser } from "../../captions/transcript/SRTParser.js";
import { WhisperJSONParser } from "../../captions/transcript/WhisperJSONParser.js";
import { CaptionNormalizer } from "../../captions/normalizer/CaptionNormalizer.js";
import { CaptionIntelligenceEngine } from "../../captions/intelligence/CaptionIntelligenceEngine.js";
import { CaptionEvaluator } from "../../captions/core/CaptionEvaluator.js";
import { ViralCaptionPresetRegistry } from "../../captions/presets/ViralCaptionPresets.js";
import { CaptionSerializer } from "../../captions/serialization/CaptionSerializer.js";
import { CaptionSerializationError } from "../../errors/index.js";

describe("Fase 16 — Caption End-to-End Pipeline & Evaluation Tests", () => {
  const srtInput = `1\n00:00:00,500 --> 00:00:02,500\n¡Gana dinero con IA hoy!\n\n2\n00:00:03,000 --> 00:00:05,000\nEl secreto del éxito 🚀`;

  it("executes complete SRT -> Normalize -> Intelligence -> Evaluate pipeline", () => {
    // 1. Parser SRT
    const rawDoc = SRTParser.parse(srtInput, "e2e_pipeline_doc");
    assert.equal(rawDoc.segments.length, 2);

    // 2. Normalizer
    const normalized = CaptionNormalizer.normalize(rawDoc);
    assert.equal(normalized.segments.length, 2);

    // 3. Caption Intelligence Engine
    const intelligenceEngine = new CaptionIntelligenceEngine();
    const enriched = intelligenceEngine.analyzeDocument(normalized);

    const segment0Words = enriched.segments[0].words;
    assert.ok(segment0Words.some((w) => w.emphasis?.isEmphasized));

    // 4. Caption Evaluator con Preset Hormozi Impact
    const hormoziPreset = ViralCaptionPresetRegistry.getPreset("hormozi-impact");

    // Instante 1: Durante palabra activa "dinero" en t = 1.0s
    const stateAt1 = CaptionEvaluator.evaluateDocument(enriched, 1.0, hormoziPreset);
    assert.equal(stateAt1.active, true);
    assert.ok(stateAt1.words.length > 0);

    const activeWord = stateAt1.words.find((w) => w.active);
    assert.ok(activeWord);
    assert.ok(activeWord.scale >= 1.0);

    // Verificar si el emoji "💸" fue asignado a la palabra "dinero"
    const dineroWord = stateAt1.words.find((w) => w.text.toLowerCase().includes("dinero"));
    assert.ok(dineroWord);
    assert.ok(dineroWord.emoji);
    assert.equal(dineroWord.emoji?.assetRef, "💸");

    // Instante 2: Durante silencio entre subtítulos en t = 2.7s
    const stateSilent = CaptionEvaluator.evaluateDocument(enriched, 2.7, hormoziPreset);
    assert.equal(stateSilent.active, false);
    assert.equal(stateSilent.words.length, 0);

    // Instante 3: Durante segmento 2 en t = 4.0s con Preset Neon Glow
    const neonPreset = ViralCaptionPresetRegistry.getPreset("neon-glow");
    const stateAt4 = CaptionEvaluator.evaluateDocument(enriched, 4.0, neonPreset);
    assert.equal(stateAt4.active, true);
    assert.ok(stateAt4.backgrounds.length > 0);
  });

  it("executes Whisper JSON -> Intelligence -> Evaluation pipeline with Karaoke Gradient preset", () => {
    const whisperData = {
      language: "es",
      segments: [
        {
          start: 0.0,
          end: 2.0,
          text: "Prueba fluida",
          words: [
            { word: "Prueba", start: 0.0, end: 0.8, probability: 0.99 },
            { word: "fluida", start: 0.8, end: 2.0, probability: 0.95 },
          ],
        },
      ],
    };

    const rawDoc = WhisperJSONParser.parse(whisperData);
    const normalized = CaptionNormalizer.normalize(rawDoc);
    const enriched = new CaptionIntelligenceEngine().analyzeDocument(normalized);

    const karaokePreset = ViralCaptionPresetRegistry.getPreset("karaoke-gradient");
    const evalState = CaptionEvaluator.evaluateDocument(enriched, 0.4, karaokePreset);

    assert.equal(evalState.active, true);
    assert.equal(evalState.words.length, 2);
    assert.equal(evalState.words[0].active, true);
    assert.equal(evalState.words[1].active, false);
  });
});

describe("Fase 16 — Caption Serializer & Schema Validation Tests", () => {
  it("performs lossless round-trip serialization and deserialization (JSON v1.6.0)", () => {
    const originalDoc = CaptionNormalizer.normalize(
      SRTParser.parse("1\n00:00:01,000 --> 00:00:03,000\nSubtítulo serializable")
    );

    const json = CaptionSerializer.toJSON(originalDoc, true);
    assert.ok(json.includes('"schemaVersion": "1.6.0"'));

    const parsed = CaptionSerializer.fromJSON(json);
    assert.deepEqual(parsed, JSON.parse(JSON.stringify(originalDoc)));
  });

  it("throws CaptionSerializationError on corrupt JSON or schema invalidity", () => {
    assert.throws(() => CaptionSerializer.fromJSON("{ bad json"), CaptionSerializationError);

    const invalidSchemaObj = {
      id: "test",
      duration: -5, // Duración negativa inválida
      segments: [],
    };
    assert.throws(() => CaptionSerializer.fromJSON(invalidSchemaObj), CaptionSerializationError);
  });
});
