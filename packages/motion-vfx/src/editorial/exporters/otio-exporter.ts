import { EditorialIR } from "../ir/editorial-ir.types.js";

export interface OtioRationalTime {
  OTIO_SCHEMA: "RationalTime.1";
  rate: number;
  value: number;
}

export interface OtioTimeRange {
  OTIO_SCHEMA: "TimeRange.1";
  start_time: OtioRationalTime;
  duration: OtioRationalTime;
}

export interface OtioClipItem {
  OTIO_SCHEMA: "Clip.1";
  name: string;
  source_range: OtioTimeRange;
  media_reference: {
    OTIO_SCHEMA: "ExternalReference.1";
    target_url: string;
    available_range: OtioTimeRange;
  };
  metadata: Record<string, unknown>;
}

export interface OtioGapItem {
  OTIO_SCHEMA: "Gap.1";
  source_range: OtioTimeRange;
}

export interface OtioTrackItem {
  OTIO_SCHEMA: "Track.1";
  name: string;
  kind: "Video" | "Audio";
  children: (OtioClipItem | OtioGapItem)[];
}

export interface OtioTimeline {
  OTIO_SCHEMA: "Timeline.1";
  name: string;
  metadata: Record<string, unknown>;
  tracks: {
    OTIO_SCHEMA: "Stack.1";
    name: "tracks";
    children: OtioTrackItem[];
  };
}

/**
 * REQ-023: Universal OpenTimelineIO (OTIO v1) Exporter.
 * Compiles the Editorial IR into standard OpenTimelineIO JSON format
 * for DaVinci Resolve, Blender VSE, Maya, RV and Nuke Studio.
 */
export class OtioExporter {
  public static exportToOtioJson(ir: EditorialIR, prettyPrint = true): string {
    const timeline = this.compileTimeline(ir);
    return JSON.stringify(timeline, null, prettyPrint ? 2 : undefined);
  }

  public static compileTimeline(ir: EditorialIR): OtioTimeline {
    const frameRate = ir.metadata.frameRate;

    const otioTracks: OtioTrackItem[] = ir.tracks.map((track) => {
      const isVideo = track.type.startsWith("VIDEO") || track.type === "SUBTITLE";
      const kind: "Video" | "Audio" = isVideo ? "Video" : "Audio";

      const children: (OtioClipItem | OtioGapItem)[] = [];
      let currentTimelineCursor = 0.0;

      for (const clip of track.clips) {
        // Insert gap if there is empty space before this clip
        const gapDuration = clip.timelineRange.startSeconds - currentTimelineCursor;
        if (gapDuration > 0.001) {
          children.push({
            OTIO_SCHEMA: "Gap.1",
            source_range: this.createTimeRange(0, gapDuration, frameRate),
          });
        }

        // Insert clip
        children.push({
          OTIO_SCHEMA: "Clip.1",
          name: clip.label,
          source_range: this.createTimeRange(
            clip.sourceRange.startSeconds,
            clip.sourceRange.durationSeconds,
            frameRate
          ),
          media_reference: {
            OTIO_SCHEMA: "ExternalReference.1",
            target_url: clip.assetId,
            available_range: this.createTimeRange(
              0,
              clip.sourceRange.startSeconds + clip.sourceRange.durationSeconds,
              frameRate
            ),
          },
          metadata: {
            speed: clip.speed,
            volumeDb: clip.volumeDb,
            pan: clip.pan,
            editorialTrackType: track.type,
          },
        });

        currentTimelineCursor = clip.timelineRange.startSeconds + clip.timelineRange.durationSeconds;
      }

      return {
        OTIO_SCHEMA: "Track.1",
        name: track.name,
        kind,
        children,
      };
    });

    return {
      OTIO_SCHEMA: "Timeline.1",
      name: ir.metadata.title,
      metadata: {
        projectId: ir.projectId,
        profile: ir.metadata.profile,
        checksum: ir.checksum,
        createdAt: ir.createdAt,
        frameRate,
        width: ir.metadata.width,
        height: ir.metadata.height,
      },
      tracks: {
        OTIO_SCHEMA: "Stack.1",
        name: "tracks",
        children: otioTracks,
      },
    };
  }

  private static createTimeRange(
    startSeconds: number,
    durationSeconds: number,
    rate: number
  ): OtioTimeRange {
    return {
      OTIO_SCHEMA: "TimeRange.1",
      start_time: {
        OTIO_SCHEMA: "RationalTime.1",
        rate,
        value: Math.round(startSeconds * rate),
      },
      duration: {
        OTIO_SCHEMA: "RationalTime.1",
        rate,
        value: Math.max(1, Math.round(durationSeconds * rate)),
      },
    };
  }
}
