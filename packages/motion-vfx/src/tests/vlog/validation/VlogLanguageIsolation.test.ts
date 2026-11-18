import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  MultilingualVoiceoverEngine,
  VlogAudioMixer,
  VlogSubtitleEngine,
} from "../../../vlog/index.js";

describe("Milestone 9 — Language Isolation Validation Suite", () => {
  it("strictly isolates locales: modifying English text does not alter Spanish voiceover or subtitles", async () => {
    const voEngine = new MultilingualVoiceoverEngine();

    // 1. Generar voz en español y subtítulos
    const esText = "Explorando la arquitectura de Guadalajara.";
    const { track: esTrack1 } = await voEngine.generateVoiceover("proj_iso", esText, "es-MX");
    const esSub1 = VlogSubtitleEngine.generateTrack("sub_es", esTrack1);

    // 2. Generar inglés original
    const enTextA = "Exploring Guadalajara architecture.";
    const { track: enTrackA } = await voEngine.generateVoiceover("proj_iso", enTextA, "en-US");

    // 3. Modificar texto en inglés
    const enTextB = "Discovering the historic buildings in downtown Guadalajara with our team.";
    const { track: enTrackB } = await voEngine.generateVoiceover("proj_iso", enTextB, "en-US");

    // 4. Regenerar español y verificar que permanece byte-a-byte idéntico
    const { track: esTrack2 } = await voEngine.generateVoiceover("proj_iso", esText, "es-MX");
    const esSub2 = VlogSubtitleEngine.generateTrack("sub_es", esTrack2);

    assert.equal(esTrack1.checksumSha256, esTrack2.checksumSha256);
    assert.equal(esSub1.checksumSha256, esSub2.checksumSha256);
    assert.notEqual(enTrackA.checksumSha256, enTrackB.checksumSha256);
  });
});
