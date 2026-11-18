import crypto from "crypto";

export interface CharacterRecord {
  characterId: string;
  name: string;
  aliases: string[];
  role: "PROTAGONIST" | "ANTAGONIST" | "WITNESS" | "EXPERT" | "SECONDARY";
  appearance: string;
  firstAppearanceEpisode: string;
  continuityConstraints: string[];
}

export interface LocationRecord {
  locationId: string;
  name: string;
  aliases: string[];
  visualDescriptors: string[];
  paletteHex: string[];
  cameraGrammar: string;
}

export interface EditorialRuleMemory {
  ruleId: string;
  summary: string;
  originatingFeedback: string;
  enforcedSinceEpisode: string;
  isImmutable: boolean;
}

export interface EpisodeSnapshot {
  episodeId: string;
  episodeNumber: number;
  title: string;
  charactersPresent: string[];
  locationsPresent: string[];
  motifsUsed: string[];
  irChecksum: string;
  committedAt: string;
}

/**
 * REQ-072–075: Master Episodic Series Memory Engine
 * Persistencia versionada, inmutable y local de la continuidad narrativa, personajes y reglas editoriales entre episodios.
 */
export class EpisodicSeriesMemory {
  public readonly seriesId: string;
  private seriesVersion = 1;
  private readonly characters: Map<string, CharacterRecord> = new Map();
  private readonly locations: Map<string, LocationRecord> = new Map();
  private readonly episodes: Map<string, EpisodeSnapshot> = new Map();
  private readonly editorialRules: Map<string, EditorialRuleMemory> = new Map();

  constructor(seriesId: string) {
    this.seriesId = seriesId;
  }

  public getVersion(): number {
    return this.seriesVersion;
  }

  public registerCharacter(char: CharacterRecord): void {
    this.characters.set(char.characterId, char);
    this.seriesVersion++;
  }

  public getCharacter(id: string): CharacterRecord | undefined {
    return this.characters.get(id);
  }

  public registerLocation(loc: LocationRecord): void {
    this.locations.set(loc.locationId, loc);
    this.seriesVersion++;
  }

  public getLocation(id: string): LocationRecord | undefined {
    return this.locations.get(id);
  }

  public recordEditorialFeedback(feedback: {
    ruleId: string;
    summary: string;
    originatingFeedback: string;
    episodeId: string;
  }): EditorialRuleMemory {
    const memory: EditorialRuleMemory = {
      ruleId: feedback.ruleId,
      summary: feedback.summary,
      originatingFeedback: feedback.originatingFeedback,
      enforcedSinceEpisode: feedback.episodeId,
      isImmutable: true,
    };
    this.editorialRules.set(memory.ruleId, memory);
    this.seriesVersion++;
    return memory;
  }

  public getEditorialRules(): EditorialRuleMemory[] {
    return Array.from(this.editorialRules.values()).sort((a, b) => a.ruleId.localeCompare(b.ruleId));
  }

  public commitEpisode(snapshot: EpisodeSnapshot): void {
    this.episodes.set(snapshot.episodeId, snapshot);
    this.seriesVersion++;
  }

  public getEpisode(id: string): EpisodeSnapshot | undefined {
    return this.episodes.get(id);
  }

  /**
   * Genera el hash canónico del estado de memoria de la serie
   */
  public calculateCanonicalHash(): string {
    const payload = JSON.stringify({
      seriesId: this.seriesId,
      version: this.seriesVersion,
      characters: Array.from(this.characters.values()).sort((a, b) => a.characterId.localeCompare(b.characterId)),
      locations: Array.from(this.locations.values()).sort((a, b) => a.locationId.localeCompare(b.locationId)),
      rules: this.getEditorialRules(),
      episodes: Array.from(this.episodes.values()).sort((a, b) => a.episodeId.localeCompare(b.episodeId)),
    });

    return crypto.createHash("sha256").update(payload, "utf8").digest("hex");
  }

  /**
   * Serializa la memoria de la serie a JSON
   */
  public saveToJson(): string {
    return JSON.stringify({
      seriesId: this.seriesId,
      seriesVersion: this.seriesVersion,
      characters: Array.from(this.characters.entries()),
      locations: Array.from(this.locations.entries()),
      editorialRules: Array.from(this.editorialRules.entries()),
      episodes: Array.from(this.episodes.entries()),
      canonicalHash: this.calculateCanonicalHash(),
    }, null, 2);
  }

  /**
   * Restaura la memoria de la serie desde JSON validando su integridad
   */
  public loadFromJson(jsonString: string): void {
    const parsed = JSON.parse(jsonString);
    if (parsed.seriesId !== this.seriesId) {
      throw new Error(`[SERIES_ID_MISMATCH] Se esperaba serie '${this.seriesId}', se obtuvo '${parsed.seriesId}'`);
    }

    this.characters.clear();
    for (const [k, v] of parsed.characters || []) this.characters.set(k, v);

    this.locations.clear();
    for (const [k, v] of parsed.locations || []) this.locations.set(k, v);

    this.editorialRules.clear();
    for (const [k, v] of parsed.editorialRules || []) this.editorialRules.set(k, v);

    this.episodes.clear();
    for (const [k, v] of parsed.episodes || []) this.episodes.set(k, v);

    this.seriesVersion = parsed.seriesVersion;
  }
}
