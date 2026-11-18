import crypto from "crypto";
import {
  ClaimEntity,
  ClaimEntityInput,
  ClaimEntitySchema,
  LocationEntity,
  LocationEntitySchema,
  PersonEntity,
  PersonEntitySchema,
  ProjectKnowledgeGraph,
  ProjectKnowledgeGraphSchema,
  SceneEntity,
  SceneEntityInput,
  SceneEntitySchema,
  ShotEntity,
  ShotEntityInput,
  ShotEntitySchema,
} from "../contracts/knowledge-graph.types.js";

/**
 * REQ-041: Project Knowledge Graph Engine.
 * Manages relationships between people, locations, claims, scenes, and shots,
 * providing deterministic query capabilities and state checksumming.
 */
export class ProjectKnowledgeGraphEngine {
  private readonly projectId: string;
  private readonly people: Map<string, PersonEntity> = new Map();
  private readonly locations: Map<string, LocationEntity> = new Map();
  private readonly claims: Map<string, ClaimEntity> = new Map();
  private readonly scenes: Map<string, SceneEntity> = new Map();
  private readonly shots: Map<string, ShotEntity> = new Map();

  constructor(projectId: string) {
    this.projectId = projectId;
  }

  public addPerson(person: PersonEntity): void {
    const validated = PersonEntitySchema.parse(person);
    this.people.set(validated.id, validated);
  }

  public getPerson(id: string): PersonEntity | undefined {
    return this.people.get(id);
  }

  public addLocation(location: LocationEntity): void {
    const validated = LocationEntitySchema.parse(location);
    this.locations.set(validated.id, validated);
  }

  public getLocation(id: string): LocationEntity | undefined {
    return this.locations.get(id);
  }

  public addClaim(claim: ClaimEntityInput): void {
    const validated = ClaimEntitySchema.parse(claim);
    this.claims.set(validated.id, validated);
  }

  public getClaim(id: string): ClaimEntity | undefined {
    return this.claims.get(id);
  }

  public getClaimsBySpeaker(speakerId: string): ClaimEntity[] {
    return Array.from(this.claims.values()).filter((c) => c.speakerId === speakerId);
  }

  public addScene(scene: SceneEntityInput): void {
    const validated = SceneEntitySchema.parse(scene);
    this.scenes.set(validated.id, validated);
  }

  public getScene(id: string): SceneEntity | undefined {
    return this.scenes.get(id);
  }

  public getScenesByLocation(locationId: string): SceneEntity[] {
    return Array.from(this.scenes.values()).filter((s) => s.locationId === locationId);
  }

  public addShot(shot: ShotEntityInput): void {
    const validated = ShotEntitySchema.parse(shot);
    this.shots.set(validated.id, validated);
  }

  public getShotsForScene(sceneId: string): ShotEntity[] {
    return Array.from(this.shots.values()).filter((s) => s.sceneId === sceneId);
  }

  /**
   * Produces an immutable, validated snapshot with a deterministic SHA-256 checksum.
   */
  public toSnapshot(): ProjectKnowledgeGraph {
    const sortedPeople = Array.from(this.people.values()).sort((a, b) => a.id.localeCompare(b.id));
    const sortedLocations = Array.from(this.locations.values()).sort((a, b) => a.id.localeCompare(b.id));
    const sortedClaims = Array.from(this.claims.values()).sort((a, b) => a.id.localeCompare(b.id));
    const sortedScenes = Array.from(this.scenes.values()).sort((a, b) => a.id.localeCompare(b.id));
    const sortedShots = Array.from(this.shots.values()).sort((a, b) => a.id.localeCompare(b.id));

    const contentForHash = JSON.stringify({
      projectId: this.projectId,
      people: sortedPeople,
      locations: sortedLocations,
      claims: sortedClaims,
      scenes: sortedScenes,
      shots: sortedShots,
    });

    const checksum = crypto.createHash("sha256").update(contentForHash).digest("hex");

    const snapshot: ProjectKnowledgeGraph = {
      projectId: this.projectId,
      people: sortedPeople,
      locations: sortedLocations,
      claims: sortedClaims,
      scenes: sortedScenes,
      shots: sortedShots,
      checksum,
    };

    return ProjectKnowledgeGraphSchema.parse(snapshot);
  }
}
