import { Composition } from "../../core/composition.js";
import { Layer } from "../../core/layer.js";
import { Clip } from "../../timeline/core/Clip.js";
import { Track } from "../../timeline/core/Track.js";
import { VideoTimeline } from "../../timeline/core/VideoTimeline.js";
import { EditingPlan } from "../types/index.js";
import { PlanValidator } from "./PlanValidator.js";

export interface CompiledProjectOutput {
  id: string;
  name: string;
  duration: number;
  width: number;
  height: number;
  fps: number;
  composition: Composition;
  timeline: VideoTimeline;
  sectionCount: number;
  shotCount: number;
}

/**
 * Compilador determinista de planes de edición a proyectos ejecutables (Fase 7).
 */
export class EditingPlanCompiler {
  /**
   * Compila un EditingPlan validado en un proyecto del motor audiovisual.
   */
  public static compile(plan: EditingPlan): CompiledProjectOutput {
    // 1. Validar integridad antes de compilar
    PlanValidator.assertValid(plan);

    const isVertical =
      plan.brief.platform === "tiktok" ||
      plan.brief.platform === "youtube-shorts" ||
      plan.brief.platform === "instagram-reels";
    const width = isVertical ? 1080 : 1920;
    const height = isVertical ? 1920 : 1080;
    const fps = 30;
    const duration = plan.brief.targetDuration;

    const composition = new Composition({ width, height, fps, duration });
    const videoTimeline = new VideoTimeline({ duration, timeBase: { fps } });

    // Track 0: Video Principal
    const videoTrack = new Track({
      id: "track_video_01",
      name: "Main Video Track",
      type: "video",
      order: 0,
    });
    videoTimeline.addTrack(videoTrack);

    // Track 1: Audio / Música
    const audioTrack = new Track({
      id: "track_audio_01",
      name: "Background Music Track",
      type: "audio",
      order: 1,
    });
    videoTimeline.addTrack(audioTrack);

    let totalShots = 0;

    // Crear capas y clips para cada escena y toma
    for (const scene of plan.scenes) {
      for (const shot of scene.shots) {
        const shotLayer = new Layer({
          id: `layer_${shot.id}`,
          name: `Shot: ${shot.purpose}`,
          startTime: shot.start,
          endTime: shot.start + shot.duration,
        });
        composition.addLayer(shotLayer);

        videoTrack.addClip(
          new Clip({
            id: `clip_${shot.id}`,
            name: shot.purpose,
            elementId: shot.assetId ?? `layer_${shot.id}`,
            timelineRange: {
              start: shot.start,
              end: shot.start + shot.duration,
            },
            sourceRange: {
              start: 0,
              end: shot.duration,
            },
          })
        );

        totalShots++;
      }
    }

    // Si hay música definida en el plan
    if (plan.audio?.musicAssetId) {
      audioTrack.addClip(
        new Clip({
          id: "clip_music_01",
          name: "Background Music",
          elementId: plan.audio.musicAssetId,
          timelineRange: { start: 0, end: duration },
          sourceRange: { start: 0, end: duration },
        })
      );
    }

    return {
      id: `proj_${plan.id}`,
      name: plan.brief.objective,
      duration,
      width,
      height,
      fps,
      composition,
      timeline: videoTimeline,
      sectionCount: plan.sections.length,
      shotCount: totalShots,
    };
  }
}
