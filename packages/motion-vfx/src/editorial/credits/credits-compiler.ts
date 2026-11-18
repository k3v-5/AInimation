import crypto from "crypto";
import {
  CreditSection,
  CreditsPlan,
  CreditsPlanSchema,
  SpeakerLowerThird,
  SpeakerLowerThirdSchema,
} from "../contracts/credits.types.js";
import { PersonEntity } from "../contracts/knowledge-graph.types.js";
import { ArchivalAsset } from "../contracts/archive.types.js";

/**
 * REQ-088 & REQ-089: Credits & Attribution Compiler.
 * Generates lower-thirds, archival on-screen attributions, and end credit sequences
 * conforming strictly to the project knowledge graph and design standards.
 */
export class CreditsCompiler {
  /**
   * Compiles lower third overlays for speaking characters.
   */
  public static compileSpeakerLowerThirds(params: {
    people: PersonEntity[];
    speakerAppearances: { speakerId: string; startSeconds: number; durationSeconds?: number }[];
    defaultDurationSeconds?: number;
  }): SpeakerLowerThird[] {
    const { people, speakerAppearances } = params;
    const defaultDuration = params.defaultDurationSeconds ?? 5.0;

    const personMap = new Map<string, PersonEntity>();
    for (const p of people) {
      personMap.set(p.id, p);
    }

    const lowerThirds: SpeakerLowerThird[] = [];

    speakerAppearances.forEach((app, index) => {
      const person = personMap.get(app.speakerId);
      if (!person) return;

      const duration = app.durationSeconds ?? defaultDuration;
      const start = app.startSeconds;
      const end = start + duration;

      const roleText = person.title
        ? person.title.toUpperCase()
        : person.role.replace(/_/g, " ").toUpperCase();

      lowerThirds.push(
        SpeakerLowerThirdSchema.parse({
          id: `lt_${person.id}_${index + 1}`,
          speakerId: person.id,
          fullName: person.name.toUpperCase(),
          roleOrTitle: roleText,
          affiliation: person.affiliation?.toUpperCase(),
          timelineStartSeconds: start,
          timelineEndSeconds: end,
          style: "TIME_INSIGNIA",
        })
      );
    });

    return lowerThirds;
  }

  /**
   * Compiles complete project credits from knowledge graph entities and archival sources.
   */
  public static compileFullCredits(params: {
    projectId: string;
    people: PersonEntity[];
    archivalAssets?: ArchivalAsset[];
    directorName?: string;
    producerName?: string;
    musicCredits?: string[];
    mode?: "CARDS" | "CRAWL" | "STATIC_SLATE";
    speakerAppearances?: { speakerId: string; startSeconds: number; durationSeconds?: number }[];
  }): CreditsPlan {
    const { projectId, people } = params;
    const archivalAssets = params.archivalAssets ?? [];
    const mode = params.mode ?? "CARDS";

    const sections: CreditSection[] = [];

    // 1. Leadership / Production
    const leadershipEntries = [];
    if (params.directorName) {
      leadershipEntries.push({ role: "DIRECTED BY", names: [params.directorName] });
    }
    if (params.producerName) {
      leadershipEntries.push({ role: "PRODUCED BY", names: [params.producerName] });
    }
    if (leadershipEntries.length > 0) {
      sections.push({
        sectionTitle: "CREATIVE & PRODUCTION",
        entries: leadershipEntries,
      });
    }

    // 2. Featured Interviewees & Participants
    const interviewees = people.filter((p) => p.role === "EXPERT" || p.role === "WITNESS" || p.role === "GUEST");
    if (interviewees.length > 0) {
      sections.push({
        sectionTitle: "FEATURED VOICES",
        entries: interviewees.map((p) => ({
          role: p.title ? p.title : p.role.replace(/_/g, " "),
          names: [p.name],
          notes: p.affiliation,
        })),
      });
    }

    // 3. Archival Sources
    if (archivalAssets.length > 0) {
      const sourceMap = new Map<string, string[]>();
      for (const asset of archivalAssets) {
        const list = sourceMap.get(asset.sourceArchive) ?? [];
        list.push(asset.title);
        sourceMap.set(asset.sourceArchive, list);
      }

      sections.push({
        sectionTitle: "ARCHIVAL FOOTAGE & PHOTOGRAPHY",
        entries: Array.from(sourceMap.entries()).map(([archiveName, titles]) => ({
          role: "ARCHIVE REPOSITORY",
          names: [archiveName],
          notes: `${titles.length} historical item(s)`,
        })),
      });
    }

    // 4. Music & Audio
    if (params.musicCredits && params.musicCredits.length > 0) {
      sections.push({
        sectionTitle: "MUSIC & SOUND DESIGN",
        entries: [{ role: "SCORE & SOUNDTRACK", names: params.musicCredits }],
      });
    }

    // Lower thirds
    const speakerLowerThirds = params.speakerAppearances
      ? this.compileSpeakerLowerThirds({
          people,
          speakerAppearances: params.speakerAppearances,
        })
      : [];

    // Archival on-screen attributions
    const archivalAttributions = archivalAssets.map((a, i) => ({
      text: `Archival material courtesy of ${a.sourceArchive}`,
      timelineStartSeconds: i * 10.0,
      timelineEndSeconds: i * 10.0 + 4.0,
    }));

    // Estimated duration calculation (5 seconds per card, or 15s for crawl)
    const cardDuration = 4.0;
    const estimatedDuration = mode === "CRAWL" ? Math.max(12.0, sections.length * 3.5) : Math.max(4.0, sections.length * cardDuration);

    const payloadForHash = JSON.stringify({
      projectId,
      sections,
      mode,
      speakerCount: people.length,
      archiveCount: archivalAssets.length,
    });

    const checksumSha256 = crypto
      .createHash("sha256")
      .update(payloadForHash)
      .digest("hex");

    return CreditsPlanSchema.parse({
      projectId,
      speakerLowerThirds,
      archivalAttributions,
      endCredits: sections,
      endCreditsMode: mode,
      estimatedEndCreditsDurationSeconds: Number(estimatedDuration.toFixed(2)),
      checksumSha256,
    });
  }
}
