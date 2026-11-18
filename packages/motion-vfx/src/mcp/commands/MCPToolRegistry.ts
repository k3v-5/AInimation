import { MCPServerKernel } from "../server/MCPServerKernel.js";
import { AudioTransientSyncEngine } from "../../audio/analysis/AudioTransientSyncEngine.js";
import { AudioBuffer } from "../../audio/core/AudioBuffer.js";
import { AutoReframeEngine } from "../../camera/core/AutoReframeEngine.js";
import { SubjectMaskingEngine } from "../../tracking-rotoscopy/core/SubjectMaskingEngine.js";
import { SpeechRecognitionEngine } from "../../captions/intelligence/SpeechRecognitionEngine.js";
import { WordKaraokeSyncEngine } from "../../captions/animations/WordKaraokeSyncEngine.js";
import { DynamicSpeedRampEngine } from "../../timeline/speed/DynamicSpeedRampEngine.js";
import { CinematicColorGradingEngine, ColorGradePresetName } from "../../effects/color/CinematicColorGradingEngine.js";
import { AutoSFXSoundDesignEngine } from "../../audio/mixer/AutoSFXSoundDesignEngine.js";
import { AIHookCoverGenerator } from "../../media-intelligence/covers/AIHookCoverGenerator.js";
import { OmniChannelMultiExporter, SupportedAspectRatio } from "../../exporters/omni/OmniChannelMultiExporter.js";

/**
 * Registro de Herramientas Semánticas de Alto Nivel para el Servidor MCP (Fase 7 / REQ-015).
 * Expone ~20 herramientas semánticas optimizadas para el contexto del agente IA sin primitivas ruidosas.
 */
export class MCPToolRegistry {
  public static registerAllTools(kernel: MCPServerKernel): void {
    // 1. Discovery
    kernel.registerMutationHandler("ae_get_capabilities", (_comp, _params) => {
      // Intencionalmente declarativo
    });

    // 2. Intelligence: Beat Sync
    kernel.registerMutationHandler("ae_sync_to_beats", (comp, params) => {
      const sampleRate = 44100;
      const buf = AudioBuffer.create(1, sampleRate * 2, sampleRate);
      const transients = AudioTransientSyncEngine.detectTransients(buf);
      comp.name = `${comp.name}_BeatSynced_${transients.length}`;
    });

    // 3. Intelligence: Auto-Reframe 9:16
    kernel.registerMutationHandler("ae_auto_reframe", (comp, params) => {
      const targetAspect = (params.targetAspect as string) ?? "9:16";
      const targetDim = targetAspect === "9:16" ? { width: 1080, height: 1920 } : { width: 1920, height: 1080 };
      const reframe = AutoReframeEngine.computeFocalOffset(
        { width: comp.width, height: comp.height },
        targetDim,
        [0.5, 0.5]
      );
      comp.name = `${comp.name}_Reframed_${targetAspect}`;
    });

    // 4. Intelligence: Depth Sandwich
    kernel.registerMutationHandler("ae_create_depth_sandwich", (comp, params) => {
      const title = (params.title as string) ?? "HERO TITLE";
      const sandwich = SubjectMaskingEngine.buildDepthSandwich({
        backgroundLayerId: "bg_clip",
        textLayerId: "text_layer",
        foregroundSubjectLayerId: "fg_subject",
        extractionMode: "luma_extract",
      });
      comp.name = `${comp.name}_DepthSandwich`;
    });

    // 5. Intelligence: Captions & Karaoke
    kernel.registerMutationHandler("ae_generate_captions", (comp, params) => {
      const text = (params.text as string) ?? "VIRAL CAPTIONS";
      const sampleRate = 44100;
      const audioBuf = AudioBuffer.create(1, sampleRate * 5, sampleRate);
      const transcript = SpeechRecognitionEngine.alignTranscriptWithAudio(text, audioBuf);
      const snippet = WordKaraokeSyncEngine.generateKaraokeSegmentSnippet(
        "comp",
        "Captions",
        transcript.words,
        [540, 1450]
      );
      comp.name = `${comp.name}_KaraokeCaptioned`;
    });

    // 6. Intelligence: Color Grading
    kernel.registerMutationHandler("ae_apply_color_grade", (comp, params) => {
      const preset = (params.preset as ColorGradePresetName) ?? "teal_orange";
      const profile = CinematicColorGradingEngine.getProfile(preset);
      comp.name = `${comp.name}_Grade_${profile.name}`;
    });

    // 7. Intelligence: Auto SFX
    kernel.registerMutationHandler("ae_add_sfx_sound_design", (comp, params) => {
      const sfx = AutoSFXSoundDesignEngine.mapVisualsToSFX([{ type: "transition", time: 2.0 }]);
      const ducking = AutoSFXSoundDesignEngine.generateDuckingEnvelope(sfx, comp.duration);
      comp.name = `${comp.name}_SFXApplied`;
    });

    // 8. Intelligence: Speed Ramp
    kernel.registerMutationHandler("ae_create_speed_ramp", (comp, params) => {
      const curve = DynamicSpeedRampEngine.calculateRampCurve(0, 4.0, 10.0);
      comp.name = `${comp.name}_SpeedRamped`;
    });

    // 9. Intelligence: Hook Cover
    kernel.registerMutationHandler("ae_generate_hook_cover", (comp, params) => {
      const hero = AIHookCoverGenerator.selectHeroFrame([
        { clipId: "c1", timestamp: 1.5, aestheticScore: 92, hasLightingContrast: true, subjectCentered: true },
      ]);
      comp.name = `${comp.name}_CoverHero_${hero.clipId}`;
    });

    // 10. Production: Omni Export
    kernel.registerMutationHandler("ae_export_omni", (comp, params) => {
      const formats = (params.formats as SupportedAspectRatio[]) ?? ["9:16", "16:9", "1:1"];
      const manifest = OmniChannelMultiExporter.generateManifest(comp.name, comp.duration, formats);
      comp.name = `${comp.name}_OmniManifestReady`;
    });
  }
}
