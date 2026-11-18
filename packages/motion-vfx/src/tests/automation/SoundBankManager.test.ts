import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { describe, it } from "node:test";
import { SoundBankManager } from "../../audio-design/SoundBankManager.js";

describe("Audio Design Suite — SoundBankManager & Procedural WAV Synthesis", () => {
  it("synthesizes valid standard 16-bit 44.1kHz mono WAV buffers for all SFX types", () => {
    const whoosh = SoundBankManager.synthesizeWhoosh(0.4);
    const impact = SoundBankManager.synthesizeImpact(0.5);
    const pop = SoundBankManager.synthesizePop(0.05);
    const shutter = SoundBankManager.synthesizeCameraShutter(0.15);
    const chime = SoundBankManager.synthesizeChime(0.6);

    for (const buf of [whoosh, impact, pop, shutter, chime]) {
      assert.ok(buf.length > 44, "WAV buffer must be greater than header size");
      assert.equal(buf.toString("ascii", 0, 4), "RIFF");
      assert.equal(buf.toString("ascii", 8, 12), "WAVE");
      assert.equal(buf.toString("ascii", 12, 16), "fmt ");
      assert.equal(buf.readUInt16LE(20), 1, "Audio format must be PCM");
      assert.equal(buf.readUInt16LE(22), 1, "Channel count must be 1 (Mono)");
      assert.equal(buf.readUInt32LE(24), 44100, "Sample rate must be 44100Hz");
      assert.equal(buf.readUInt16LE(34), 16, "Bit depth must be 16-bit");
    }
  });

  it("ensures physical sound bank files on disk deterministically", () => {
    const tempDir = path.resolve("./dist/test_sfx_bank");
    const map = SoundBankManager.ensureSoundBank(tempDir);

    assert.ok(fs.existsSync(map.whoosh));
    assert.ok(fs.existsSync(map.impact));
    assert.ok(fs.existsSync(map.pop));
    assert.ok(fs.existsSync(map.shutter));
    assert.ok(fs.existsSync(map.chime));

    // Cleanup
    fs.rmSync(tempDir, { recursive: true, force: true });
  });

  it("generates ExtendScript audio import snippet for After Effects", () => {
    const snippet = SoundBankManager.generateExtendScriptAudioImportSnippet("comp", "C:/SFX", [
      { id: "1", type: "whoosh", startTimeSec: 1.0, filename: "whoosh_fast.wav" },
      { id: "2", type: "impact", startTimeSec: 4.5, filename: "impact_sub_boom.wav" },
    ]);

    assert.ok(snippet.includes("SFX Sound Bank"));
    assert.ok(snippet.includes("whoosh_fast.wav"));
    assert.ok(snippet.includes("impact_sub_boom.wav"));
    assert.ok(snippet.includes("comp.layers.add"));
  });
});
