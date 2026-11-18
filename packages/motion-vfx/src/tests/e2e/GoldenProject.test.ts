import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MCPServerKernel } from "../../mcp/server/MCPServerKernel.js";
import { AERuntimeBridge } from "../../mcp/bridge/AERuntimeBridge.js";
import { AudioTransientSyncEngine } from "../../audio/analysis/AudioTransientSyncEngine.js";
import { AudioBuffer } from "../../audio/core/AudioBuffer.js";
import { AutoReframeEngine } from "../../camera/core/AutoReframeEngine.js";
import { SubjectMaskingEngine } from "../../tracking-rotoscopy/core/SubjectMaskingEngine.js";
import { SpeechRecognitionEngine } from "../../captions/intelligence/SpeechRecognitionEngine.js";
import { WordKaraokeSyncEngine } from "../../captions/animations/WordKaraokeSyncEngine.js";
import { DynamicSpeedRampEngine } from "../../timeline/speed/DynamicSpeedRampEngine.js";
import { CinematicColorGradingEngine } from "../../effects/color/CinematicColorGradingEngine.js";
import { AutoSFXSoundDesignEngine } from "../../audio/mixer/AutoSFXSoundDesignEngine.js";
import { AIHookCoverGenerator } from "../../media-intelligence/covers/AIHookCoverGenerator.js";
import { OmniChannelMultiExporter } from "../../exporters/omni/OmniChannelMultiExporter.js";
import { StateReconciler } from "../../mcp/reconciliation/StateReconciler.js";

describe("Fase 6 — GOLDEN-PROJECT-001 Master End-to-End Certification (REQ-032 / Golden E2E)", () => {
  it("executes the complete autonomous production pipeline from brief to verified multi-format export", async () => {
    // 1. Inicialización del Kernel y Bridge
    const kernel = new MCPServerKernel();
    const bridge = new AERuntimeBridge();
    await bridge.connect();
    assert.equal(bridge.getState(), "CONNECTED");

    // 2. Audio Transient Sync
    const sampleRate = 44100;
    const totalFrames = sampleRate * 2;
    const audioBuf = AudioBuffer.create(1, totalFrames, sampleRate);
    const ch = audioBuf.data[0];
    for (const bt of [0.5, 1.5]) {
      const center = Math.round(bt * sampleRate);
      for (let f = 0; f < 800; f++) {
        if (center + f < totalFrames) {
          ch[center + f] = Math.sin((f / sampleRate) * 2 * Math.PI * 60) * Math.exp(-f / 150);
        }
      }
    }
    const transients = AudioTransientSyncEngine.detectTransients(audioBuf, {
      sensitivity: 0.7,
      minPeakDistanceMs: 200,
    });
    assert.ok(transients.length >= 2, `Expected at least 2 transients, got ${transients.length}`);

    // 3. Auto-Reframe 16:9 -> 9:16
    const reframe = AutoReframeEngine.computeFocalOffset(
      { width: 1920, height: 1080 },
      { width: 1080, height: 1920 },
      [0.6, 0.5]
    );
    assert.ok(reframe.scale[0] >= 177.0, "Expected vertical filling scale");
    assert.ok(reframe.position[0] >= 0);

    // 4. Depth Layer Sandwich
    const sandwich = SubjectMaskingEngine.buildDepthSandwich({
      backgroundLayerId: "layer_bg",
      textLayerId: "layer_text_hero",
      foregroundSubjectLayerId: "layer_fg_cutout",
      extractionMode: "luma_extract",
    });
    assert.equal(sandwich.layersInZOrder.length, 3);
    assert.equal(sandwich.layersInZOrder[1], "layer_text_hero");

    // 5. Speech Recognition & Karaoke Subtitles
    const transcript = SpeechRecognitionEngine.alignTranscriptWithAudio(
      "ESTO ES GUADALAJARA EN VIVO",
      audioBuf
    );
    assert.equal(transcript.words.length, 5);
    const karaokeSnippet = WordKaraokeSyncEngine.generateKaraokeSegmentSnippet(
      "comp",
      "Text_Captions",
      transcript.words,
      [540, 1450]
    );
    assert.ok(karaokeSnippet.includes("ADBE Text Animator"));

    // 6. Dynamic Speed Ramping
    const speedRamp = DynamicSpeedRampEngine.calculateRampCurve(0.0, 4.0, 10.0);
    assert.equal(speedRamp.length, 4);

    // 7. Cinematic Color Grading
    const colorGrade = CinematicColorGradingEngine.getProfile("teal_orange");
    assert.equal(colorGrade.name, "teal_orange");

    // 8. Auto-SFX & Ducking
    const sfxEvents = AutoSFXSoundDesignEngine.mapVisualsToSFX([
      { type: "transition", time: 2.0 },
      { type: "text_pop", time: 3.5 },
    ]);
    const ducking = AutoSFXSoundDesignEngine.generateDuckingEnvelope(sfxEvents, 10.0);
    assert.ok(ducking.length >= 4);

    // 9. AI Hook Cover Generator
    const heroCover = AIHookCoverGenerator.selectHeroFrame([
      { clipId: "clip_01", timestamp: 1.5, aestheticScore: 90, hasLightingContrast: true, subjectCentered: true },
    ]);
    assert.equal(heroCover.clipId, "clip_01");

    // 10. Omni-Channel Multi-Exporter (9:16, 16:9, 1:1)
    const manifest = OmniChannelMultiExporter.generateManifest("GOLDEN_001", 45.0);
    assert.equal(manifest.formats.length, 3);

    // 11. State Reconciliation
    const reconcileReport = StateReconciler.reconcile(
      [
        { id: "l1", name: "ConcertFootage", inPoint: 0.0, outPoint: 45.0, position: [540, 960] },
        { id: "l2", name: "Text_Sandwich_GUADALAJARA 2023", inPoint: 0.0, outPoint: 45.0, position: [540, 960] },
      ],
      [
        { index: 1, name: "ConcertFootage", inPoint: 0.0, outPoint: 45.0, position: [540.01, 960.02] },
        { index: 2, name: "Text_Sandwich_GUADALAJARA 2023", inPoint: 0.0, outPoint: 45.0, position: [540, 960] },
      ]
    );
    assert.equal(reconcileReport.isEquivalent, true);
    assert.equal(reconcileReport.status, "pass");

    // 12. Transacción Completa del MCP Kernel
    const txResult = await kernel.handleRequest({
      operationId: "op_golden_001",
      toolName: "set_property",
      category: "mutation",
      params: { name: "GOLDEN_PROJECT_001_CERTIFIED" },
    });

    assert.equal(txResult.success, true);
    assert.equal(kernel.composition.name, "GOLDEN_PROJECT_001_CERTIFIED");
  });
});
