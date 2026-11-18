import * as path from 'path';
import * as fs from 'fs';
import * as os from 'os';
import { Artifact, ArtifactType } from './abstractions.js';
import { ProjectManager } from './ProjectManager.js';
import { calculateFileHash } from './utils/hash.js';

export class ArtifactManager {
  private baseDir: string;
  private artifacts: Map<string, Artifact> = new Map();
  private projectManager: ProjectManager;
  public activeProjectId: string | null = null;

  constructor() {
    this.baseDir = path.join(os.homedir(), 'Documents', 'AnimationEngine', 'Artifacts');
    this.ensureBaseDirectory();
    this.projectManager = new ProjectManager();
  }

  private ensureBaseDirectory() {
    if (!fs.existsSync(this.baseDir)) {
      fs.mkdirSync(this.baseDir, { recursive: true });
    }
  }

  public registerArtifact(type: ArtifactType, operationId: string, metadata: Record<string, unknown> = {}): Artifact {
    const artifactId = `art_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
    const fileName = `${artifactId}.${this.getExtensionForType(type)}`;
    const localPath = path.join(this.baseDir, fileName);

    const artifact: Artifact = {
      id: artifactId,
      type,
      version: 1,
      createdBy: operationId,
      dependencies: [],
      metadata: {
        ...metadata,
        local_path: localPath
      }
    };

    this.artifacts.set(artifactId, artifact);
    fs.writeFileSync(localPath, `// Mock artifact for ${type}\n${JSON.stringify(artifact, null, 2)}`);

    // Persist to DB if part of an active project
    if (this.activeProjectId) {
      this.projectManager.saveAsset({
         id: artifactId,
         project_id: this.activeProjectId,
         type: type,
         local_path: localPath,
         hash: calculateFileHash(localPath),
         created_at: new Date().toISOString()
      });
    }

    return artifact;
  }

  public getArtifactPath(artifactId: string): string | null {
    const art = this.artifacts.get(artifactId);
    if (art && typeof art.metadata.local_path === 'string') {
      return art.metadata.local_path;
    }
    return null;
  }

  private getExtensionForType(type: ArtifactType): string {
    const extMap: Record<ArtifactType, string> = {
      'scene': 'json',
      'timeline': 'json',
      'asset': 'png',
      'render': 'mp4',
      'puppet': 'puppet',
      'audio': 'wav'
    };
    return extMap[type] || 'tmp';
  }
}