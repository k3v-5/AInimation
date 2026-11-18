import { EditorialClipInput, EditorialIR } from "../ir/editorial-ir.types.js";
import { EditorialIRBuilder } from "../ir/editorial-ir-builder.js";
import {
  LocalizedTrackPair,
  LocalizedTrackPairSchema,
} from "./editorial-localization.types.js";

/**
 * REQ-071, REQ-072 & REQ-073: Master Localization Orchestrator 2.0.
 * Produces isolated, language-specific Editorial IR timelines, swapping dialogue audio
 * and subtitle tracks while preserving all visual edits, B-roll, and music beds.
 */
export class EditorialLocalizationOrchestrator {
  /**
   * Generates a fully localized Editorial IR timeline for a target locale.
   */
  public static createLocalizedIR(params: {
    masterIR: EditorialIR;
    localizedTrack: LocalizedTrackPair;
    deterministicTimestamp?: string;
  }): EditorialIR {
    const { masterIR } = params;
    const localized = LocalizedTrackPairSchema.parse(params.localizedTrack);

    const localizedProjectId = `${masterIR.projectId}_${localized.locale.replace("-", "_")}`;
    const localizedTitle = `${masterIR.metadata.title} (${localized.locale})`;

    const builder = new EditorialIRBuilder(localizedProjectId, {
      ...masterIR.metadata,
      title: localizedTitle,
    });

    // 1. Re-create all tracks, swapping or inserting localized dialogue and subtitles
    for (const track of masterIR.tracks) {
      if (track.type === "AUDIO_DIALOGUE") {
        // Swap dialogue audio with localized asset
        builder.createTrack({
          id: `t_audio_dialogue_${localized.locale}`,
          name: `Dialogue (${localized.locale})`,
          type: "AUDIO_DIALOGUE",
          index: track.index,
        });

        // Insert primary localized voiceover clip
        const totalDuration = this.computeTrackDuration(masterIR);
        const localizedDialogueClip: EditorialClipInput = {
          id: `clip_dialogue_${localized.locale}`,
          assetId: localized.audioDialogueAssetId,
          label: `Voiceover ${localized.locale}`,
          sourceRange: { startSeconds: 0.0, durationSeconds: totalDuration },
          timelineRange: {
            startSeconds: localized.timingOffsetSeconds,
            durationSeconds: totalDuration,
          },
          volumeDb: 0.0,
          pan: 0.0,
        };

        builder.addClip(`t_audio_dialogue_${localized.locale}`, localizedDialogueClip);
      } else if (track.type === "SUBTITLE") {
        // Skip master subtitles, we will insert the localized ones
        continue;
      } else {
        // Keep visual and music/sound tracks intact
        builder.createTrack({
          id: track.id,
          name: track.name,
          type: track.type,
          index: track.index,
          isMuted: track.isMuted,
          isLocked: track.isLocked,
        });

        for (const clip of track.clips) {
          builder.addClip(track.id, {
            id: clip.id,
            assetId: clip.assetId,
            label: clip.label,
            sourceRange: clip.sourceRange,
            timelineRange: clip.timelineRange,
            speed: clip.speed,
            volumeDb: clip.volumeDb,
            pan: clip.pan,
            scale: clip.scale,
          });
        }
      }
    }

    // 2. Insert localized Subtitle Track if cues exist
    if (localized.subtitleCues.length > 0) {
      const subtitleTrackId = `t_subtitles_${localized.locale}`;
      builder.createTrack({
        id: subtitleTrackId,
        name: `Subtitles (${localized.locale})`,
        type: "SUBTITLE",
        index: masterIR.tracks.length + 1,
      });

      for (let i = 0; i < localized.subtitleCues.length; i++) {
        const cue = localized.subtitleCues[i];
        const duration = Math.max(0.1, cue.endSeconds - cue.startSeconds);

        const subClip: EditorialClipInput = {
          id: `sub_${localized.locale}_${i}`,
          assetId: `text://${encodeURIComponent(cue.text)}`,
          label: cue.text,
          sourceRange: { startSeconds: 0, durationSeconds: duration },
          timelineRange: { startSeconds: cue.startSeconds, durationSeconds: duration },
        };

        builder.addClip(subtitleTrackId, subClip);
      }
    }

    // Preserve markers
    for (const marker of masterIR.markers) {
      builder.addMarker(marker);
    }

    const timestamp = params.deterministicTimestamp ?? masterIR.createdAt;
    return builder.build(timestamp);
  }

  private static computeTrackDuration(ir: EditorialIR): number {
    let maxEnd = 10.0;
    for (const track of ir.tracks) {
      for (const clip of track.clips) {
        const end = clip.timelineRange.startSeconds + clip.timelineRange.durationSeconds;
        if (end > maxEnd) {
          maxEnd = end;
        }
      }
    }
    return maxEnd;
  }
}
