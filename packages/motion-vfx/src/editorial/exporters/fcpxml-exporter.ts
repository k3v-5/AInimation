import { EditorialIR } from "../ir/editorial-ir.types.js";

/**
 * REQ-024: Universal Final Cut Pro XML (FCPXML v1.9) Exporter.
 * Compiles the Editorial IR into standard FCPXML format
 * for Apple Final Cut Pro, DaVinci Resolve, and Adobe Premiere Pro.
 */
export class FcpxmlExporter {
  public static exportToFcpxml(ir: EditorialIR): string {
    const { metadata, tracks, markers } = ir;
    const frameRate = metadata.frameRate;
    const formatDuration = `1/${frameRate}s`;

    // 1. Collect unique assets for <resources>
    const uniqueAssetMap = new Map<string, { id: string; name: string }>();
    let assetCounter = 1;

    for (const track of tracks) {
      for (const clip of track.clips) {
        if (!uniqueAssetMap.has(clip.assetId)) {
          uniqueAssetMap.set(clip.assetId, {
            id: `r_asset_${assetCounter++}`,
            name: clip.label,
          });
        }
      }
    }

    // 2. Build <resources> section
    let resourcesXml = `    <format id="r_fmt" name="FFVideoFormat_${metadata.width}x${metadata.height}p${frameRate}" frameDuration="${formatDuration}" width="${metadata.width}" height="${metadata.height}"/>\n`;

    for (const [assetId, assetInfo] of uniqueAssetMap.entries()) {
      resourcesXml += `    <asset id="${assetInfo.id}" name="${this.escapeXml(assetInfo.name)}" src="${this.escapeXml(assetId)}" start="0s" duration="3600s" hasVideo="1" hasAudio="1" format="r_fmt"/>\n`;
    }

    // 3. Build <spine> elements from primary video track (or first available track)
    const primaryTrack =
      tracks.find((t) => t.type === "VIDEO_PRIMARY") ??
      tracks.find((t) => t.type.startsWith("VIDEO")) ??
      tracks[0];

    let spineXml = "";
    let timelineCursor = 0.0;

    if (primaryTrack) {
      for (const clip of primaryTrack.clips) {
        const gapDuration = clip.timelineRange.startSeconds - timelineCursor;
        if (gapDuration > 0.001) {
          spineXml += `          <gap offset="${this.formatTime(timelineCursor, frameRate)}" name="Gap" duration="${this.formatTime(gapDuration, frameRate)}"/>\n`;
        }

        const assetInfo = uniqueAssetMap.get(clip.assetId);
        const refId = assetInfo ? assetInfo.id : "r_asset_1";

        // Find markers that fall within this clip's timeline range
        const clipStart = clip.timelineRange.startSeconds;
        const clipEnd = clipStart + clip.timelineRange.durationSeconds;
        const clipMarkers = markers.filter((m) => m.timestampSeconds >= clipStart && m.timestampSeconds < clipEnd);

        let markerXml = "";
        for (const m of clipMarkers) {
          const markerOffsetInClip = m.timestampSeconds - clipStart;
          markerXml += `\n            <marker start="${this.formatTime(markerOffsetInClip, frameRate)}" duration="0s" value="${this.escapeXml(m.name)}"/>`;
        }

        spineXml += `          <asset-clip ref="${refId}" offset="${this.formatTime(clip.timelineRange.startSeconds, frameRate)}" name="${this.escapeXml(clip.label)}" start="${this.formatTime(clip.sourceRange.startSeconds, frameRate)}" duration="${this.formatTime(clip.sourceRange.durationSeconds, frameRate)}" format="r_fmt">${markerXml}\n          </asset-clip>\n`;

        timelineCursor = clip.timelineRange.startSeconds + clip.timelineRange.durationSeconds;
      }
    }

    const totalSequenceDuration = Math.max(1.0, timelineCursor);

    return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.9">
  <resources>
${resourcesXml}  </resources>
  <library>
    <event name="Event_${this.escapeXml(metadata.title)}">
      <project name="${this.escapeXml(metadata.title)}">
        <sequence format="r_fmt" duration="${this.formatTime(totalSequenceDuration, frameRate)}" tcStart="0s" tcFormat="NDF">
          <spine>
${spineXml}          </spine>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
`;
  }

  private static formatTime(seconds: number, rate: number): string {
    const frames = Math.round(seconds * rate);
    return `${frames}/${rate}s`;
  }

  private static escapeXml(text: string): string {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&apos;");
  }
}
