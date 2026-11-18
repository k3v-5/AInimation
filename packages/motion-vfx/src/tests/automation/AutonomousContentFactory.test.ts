import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  LocalWhisperTranscriptionBridge,
  ViralMomentDetector,
  ActiveSpeakerReframingEngine,
  VoiceoverTimingSynchronizer,
  SocialLaunchPackager,
  HeadlessRenderOrchestrator,
} from "../../automation/index.js";

describe("Automation Suite — Autonomous Content Factory (TikTok & YouTube)", () => {
  describe("1. Local Whisper Transcription Bridge", () => {
    it("builds valid ffmpeg audio extraction command for 16kHz WAV", () => {
      const cmd = LocalWhisperTranscriptionBridge.buildAudioExtractionCommand(
        "C:\\Videos\\Input.mp4",
        "C:\\Audios\\Output.wav"
      );
      assert.ok(cmd.includes("16000"));
      assert.ok(cmd.includes("pcm_s16le"));
      assert.ok(cmd.includes("-vn"));
    });

    it("builds whisper CLI command with word timestamps and language flags", () => {
      const cmd = LocalWhisperTranscriptionBridge.buildWhisperCLICommand("audio.wav", {
        model: "small",
        language: "es",
        wordTimestamps: true,
        outputDir: "./output",
      });
      assert.ok(cmd.includes("--model small"));
      assert.ok(cmd.includes("--language es"));
      assert.ok(cmd.includes("--word_timestamps True"));
    });

    it("synthesizes deterministic transcript with word timings", () => {
      const doc = LocalWhisperTranscriptionBridge.synthesizeDeterministicTranscript(
        "EL SECRETO DE GUADALAJARA NUNCA ANTES REVELADO",
        7.0
      );
      assert.equal(doc.segments.length, 1);
      assert.equal(doc.segments[0].words.length, 7);
      assert.equal(doc.segments[0].words[0].start, 0.0);
      assert.equal(doc.segments[0].words[6].end, 7.0);
    });
  });

  describe("2. Viral Moment Detector & Long-to-Shorts Clipper", () => {
    it("calculates high hook score for trigger words and question marks", () => {
      const words = [
        { id: "1", text: "¿El", start: 0.0, end: 0.4 },
        { id: "2", text: "secreto", start: 0.4, end: 0.9 },
        { id: "3", text: "millonario?", start: 0.9, end: 1.5 },
      ];
      const hookScore = ViralMomentDetector.calculateHookScore(words, 0.8);
      assert.ok(hookScore >= 80, `Expected hookScore >= 80, got ${hookScore}`);
    });

    it("detects viral moments from a full transcript and sorts by virality index", () => {
      const longTranscript = LocalWhisperTranscriptionBridge.synthesizeDeterministicTranscript(
        "¿Cuál es el secreto oculto de este gran misterio? Nadie te dice la verdad sobre el dinero y el éxito en este mundo moderno. Pero hoy descubrí algo totalmente increíble que cambiará tu forma de ver las cosas para siempre.",
        45.0
      );

      const energySamples = [
        { timestamp: 0.0, rms: 0.8 },
        { timestamp: 15.0, rms: 0.4 },
        { timestamp: 35.0, rms: 0.9 },
        { timestamp: 44.0, rms: 0.95 },
      ];

      const clips = ViralMomentDetector.detectViralMoments(
        longTranscript,
        energySamples,
        [30.0, 45.0],
        2
      );

      assert.ok(clips.length >= 1);
      assert.ok(clips[0].viralityIndex >= 60);
      assert.ok(clips[0].duration >= 30.0);
    });
  });

  describe("3. Active Speaker Reframing Engine (16:9 to 9:16)", () => {
    it("generates smooth pan-and-scan keyframes with deadzone protection", () => {
      const focalPoints = [
        { timeSec: 0.0, normalizedX: 0.5, confidence: 0.99 },
        { timeSec: 2.0, normalizedX: 0.52, confidence: 0.99 }, // Pequeño cambio: deadzone lo absorbe
        { timeSec: 5.0, normalizedX: 0.80, confidence: 0.99 }, // Cambio grande: se desplaza suavemente
      ];

      const res = ActiveSpeakerReframingEngine.calculateReframing(
        "dynamic_pan_and_scan",
        focalPoints,
        1920,
        1080,
        1080,
        1920,
        45.0,
        0.20
      );

      assert.equal(res.mode, "dynamic_pan_and_scan");
      assert.equal(res.targetResolution.width, 1080);
      assert.equal(res.targetResolution.height, 1920);
      assert.equal(res.keyframes.length, 3);
      assert.ok(res.keyframes[0].scale[0] >= 170); // Escala para cubrir altura
    });

    it("generates split-screen stacked layout config for multi-speaker/gameplay", () => {
      const res = ActiveSpeakerReframingEngine.calculateReframing(
        "split_screen_stacked",
        [],
        1920,
        1080,
        1080,
        1920
      );

      assert.equal(res.mode, "split_screen_stacked");
      assert.ok(res.splitScreenConfig);
      assert.equal(res.splitScreenConfig.topLayer.bounds[3], 960);
      assert.equal(res.splitScreenConfig.bottomLayer.bounds[3], 960);
    });
  });

  describe("4. Voiceover Timing Synchronizer", () => {
    it("detects breath pauses and snaps scene cuts to natural gaps", () => {
      const words = [
        { id: "1", text: "Primera", start: 0.0, end: 1.0 },
        { id: "2", text: "frase", start: 1.0, end: 1.8 },
        // Pausa de 0.6s entre 1.8s y 2.4s
        { id: "3", text: "Segunda", start: 2.4, end: 3.2 },
        { id: "4", text: "frase", start: 3.2, end: 4.0 },
      ];

      const pauses = VoiceoverTimingSynchronizer.detectBreathPauses(words, 0.30);
      assert.equal(pauses.length, 1);
      assert.equal(pauses[0].startTime, 1.8);
      assert.equal(pauses[0].endTime, 2.4);

      const scenes = [
        { id: "scene_1", nominalDurationSec: 2.0 },
        { id: "scene_2", nominalDurationSec: 2.0 },
      ];

      const aligned = VoiceoverTimingSynchronizer.alignScenesToVoiceover(scenes, words);
      assert.equal(aligned.length, 2);
      assert.equal(aligned[0].endTimeSec, 2.1); // Punto medio de la pausa (1.8 + 2.4)/2
      assert.equal(aligned[0].snapCutToPause, true);
    });

    it("bounds safe pacing dilation between 0.85x and 1.15x", () => {
      assert.equal(VoiceoverTimingSynchronizer.computeSafePacingDilation(10, 10), 1.0);
      assert.equal(VoiceoverTimingSynchronizer.computeSafePacingDilation(10, 20), 0.85); // Clamped
      assert.equal(VoiceoverTimingSynchronizer.computeSafePacingDilation(20, 10), 1.15); // Clamped
    });
  });

  describe("5. Social Launch Packager & Headless Render Orchestrator", () => {
    it("generates 3 A/B High-CTR title formulas with character counts", () => {
      const titles = SocialLaunchPackager.generateHighCTRTitles("INTELIGENCIA ARTIFICIAL", ["FUTURO"]);
      assert.equal(titles.length, 3);
      assert.ok(titles[0].title.includes("SECRETO"));
      assert.ok(titles[1].title.includes("POR QUÉ"));
      assert.ok(titles[2].title.includes("CÓMO"));
    });

    it("generates YouTube launch package with formatted timestamps and SEO tags", () => {
      const pkg = SocialLaunchPackager.generateYouTubePackage(
        "IA Documental",
        "El Futuro de la IA",
        [
          { title: "Introducción", startTimeSec: 0 },
          { title: "El Gran Descubrimiento", startTimeSec: 65 },
          { title: "Conclusión", startTimeSec: 150 },
        ],
        ["tecnologia", "futuro"]
      );

      assert.ok(pkg.descriptionWithTimestamps.includes("00:00 - Introducción"));
      assert.ok(pkg.descriptionWithTimestamps.includes("01:05 - El Gran Descubrimiento"));
      assert.ok(pkg.tags.includes("tecnologia"));
      assert.equal(pkg.thumbnailPrompt.contrastColors[0], "#FF1424");
    });

    it("generates headless aerender CLI command with multi-process and output module", () => {
      const cmd = HeadlessRenderOrchestrator.buildAERenderCommand(
        "F:/Projects/Guadalajara.aep",
        "MainComp",
        "F:/Renders/Guadalajara.mp4",
        { multiProcess: true, sound: true, outputModuleTemplate: "H.264" }
      );

      assert.ok(cmd.includes("-project \"F:/Projects/Guadalajara.aep\""));
      assert.ok(cmd.includes("-comp \"MainComp\""));
      assert.ok(cmd.includes("-output \"F:/Renders/Guadalajara.mp4\""));
      assert.ok(cmd.includes("-OMtemplate \"H.264\""));
      assert.ok(cmd.includes("-mp"));
    });
  });
});
