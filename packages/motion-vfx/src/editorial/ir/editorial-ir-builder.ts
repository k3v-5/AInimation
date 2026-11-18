import crypto from "crypto";
import {
  EditorialClip,
  EditorialClipInput,
  EditorialClipSchema,
  EditorialIR,
  EditorialIRSchema,
  EditorialMarker,
  EditorialMarkerSchema,
  EditorialMetadata,
  EditorialMetadataSchema,
  EditorialTrack,
  EditorialTrackSchema,
  EditorialTrackType,
  EditorialTransition,
  EditorialTransitionSchema,
} from "./editorial-ir.types.js";

/**
 * REQ-021 & REQ-022: Fluent and deterministic builder for the Editorial IR.
 * Manages timeline tracks, clips, transitions and markers, and seals the document
 * with an immutable SHA-256 checksum.
 */
export class EditorialIRBuilder {
  private readonly projectId: string;
  private metadata: EditorialMetadata;
  private readonly tracks: Map<string, EditorialTrack> = new Map();
  private readonly transitions: EditorialTransition[] = [];
  private readonly markers: EditorialMarker[] = [];

  constructor(projectId: string, metadata: EditorialMetadata) {
    this.projectId = projectId;
    this.metadata = EditorialMetadataSchema.parse(metadata);
  }

  public setMetadata(metadata: Partial<EditorialMetadata>): this {
    this.metadata = EditorialMetadataSchema.parse({ ...this.metadata, ...metadata });
    return this;
  }

  public createTrack(params: {
    id: string;
    name: string;
    type: EditorialTrackType;
    index: number;
    isMuted?: boolean;
    isLocked?: boolean;
  }): this {
    const track = EditorialTrackSchema.parse({
      id: params.id,
      name: params.name,
      type: params.type,
      index: params.index,
      isMuted: params.isMuted ?? false,
      isLocked: params.isLocked ?? false,
      clips: [],
    });
    this.tracks.set(track.id, track);
    return this;
  }

  public addClip(trackId: string, clip: EditorialClipInput): this {
    const track = this.tracks.get(trackId);
    if (!track) {
      throw new Error(`Track '${trackId}' not found in Editorial IR.`);
    }
    const validatedClip = EditorialClipSchema.parse(clip);
    track.clips.push(validatedClip);
    return this;
  }

  public addTransition(transition: EditorialTransition): this {
    const validated = EditorialTransitionSchema.parse(transition);
    this.transitions.push(validated);
    return this;
  }

  public addMarker(marker: EditorialMarker): this {
    const validated = EditorialMarkerSchema.parse(marker);
    this.markers.push(validated);
    return this;
  }

  /**
   * Seals and compiles the complete Editorial IR with a deterministic SHA-256 checksum.
   */
  public build(deterministicTimestamp?: string): EditorialIR {
    // Sort tracks by index ascending
    const sortedTracks = Array.from(this.tracks.values())
      .sort((a, b) => a.index - b.index)
      .map((t) => ({
        ...t,
        clips: [...t.clips].sort((a, b) => a.timelineRange.startSeconds - b.timelineRange.startSeconds),
      }));

    // Sort transitions and markers temporally
    const sortedTransitions = [...this.transitions].sort((a, b) => a.timestampSeconds - b.timestampSeconds);
    const sortedMarkers = [...this.markers].sort((a, b) => a.timestampSeconds - b.timestampSeconds);

    const createdAt = deterministicTimestamp ?? "2026-09-02T00:00:00.000Z";

    const contentForHash = JSON.stringify({
      schemaVersion: "4.0.0",
      projectId: this.projectId,
      metadata: this.metadata,
      tracks: sortedTracks,
      transitions: sortedTransitions,
      markers: sortedMarkers,
      createdAt,
    });

    const checksum = crypto.createHash("sha256").update(contentForHash).digest("hex");

    const ir: EditorialIR = {
      schemaVersion: "4.0.0",
      projectId: this.projectId,
      metadata: this.metadata,
      tracks: sortedTracks,
      transitions: sortedTransitions,
      markers: sortedMarkers,
      checksum,
      createdAt,
    };

    return EditorialIRSchema.parse(ir);
  }
}
