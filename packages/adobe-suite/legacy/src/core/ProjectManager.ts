import { db } from './Database.js';

export interface ProjectData {
  id: string;
  name: string;
  created_at: string;
  last_modified: string;
}

export interface AssetData {
  id: string;
  project_id: string;
  type: string;
  local_path: string;
  hash: string | null;
  created_at: string;
}

export interface ExecutionData {
  id: string;
  project_id: string;
  status: string;
  intent_json: string;
  context_json: string | null;
  created_at: string;
}

export interface OperationData {
  id: string;
  execution_id: string;
  capability: string;
  status: string;
  result_json: string | null;
  error_text: string | null;
  created_at: string;
}

export class ProjectManager {
  public createProject(name: string): ProjectData {
    const id = "proj_" + Date.now() + "_" + Math.floor(Math.random() * 1000);
    const stmt = db.prepare('INSERT INTO projects (id, name) VALUES (?, ?)');
    stmt.run(id, name);
    return this.getProject(id)!;
  }

  public getProject(id: string): ProjectData | undefined {
    return db.prepare('SELECT * FROM projects WHERE id = ?').get(id) as ProjectData | undefined;
  }

  public listProjects(): ProjectData[] {
    return db.prepare('SELECT * FROM projects ORDER BY last_modified DESC LIMIT 20').all() as ProjectData[];
  }

  public saveAsset(asset: AssetData): void {
    const stmt = db.prepare('INSERT OR REPLACE INTO assets (id, project_id, type, local_path, hash) VALUES (?, ?, ?, ?, ?)');
    stmt.run(asset.id, asset.project_id, asset.type, asset.local_path, asset.hash);

    // Update project modification time
    db.prepare('UPDATE projects SET last_modified = CURRENT_TIMESTAMP WHERE id = ?').run(asset.project_id);
  }

  public getAssetsForProject(projectId: string): AssetData[] {
    return db.prepare('SELECT * FROM assets WHERE project_id = ?').all(projectId) as AssetData[];
  }

  public saveExecution(data: Omit<ExecutionData, 'created_at'>): void {
    const stmt = db.prepare('INSERT OR REPLACE INTO executions (id, project_id, status, intent_json, context_json) VALUES (?, ?, ?, ?, ?)');
    stmt.run(data.id, data.project_id, data.status, data.intent_json, data.context_json);
  }

  public getExecution(id: string): ExecutionData | undefined {
    return db.prepare('SELECT * FROM executions WHERE id = ?').get(id) as ExecutionData | undefined;
  }

  public updateExecutionStatus(id: string, status: string, context_json?: string): void {
    if (context_json) {
      db.prepare('UPDATE executions SET status = ?, context_json = ? WHERE id = ?').run(status, context_json, id);
    } else {
      db.prepare('UPDATE executions SET status = ? WHERE id = ?').run(status, id);
    }
  }

  public saveOperation(data: Omit<OperationData, 'created_at'>): void {
    const stmt = db.prepare('INSERT OR REPLACE INTO operations (id, execution_id, capability, status, result_json, error_text) VALUES (?, ?, ?, ?, ?, ?)');
    stmt.run(data.id, data.execution_id, data.capability, data.status, data.result_json, data.error_text);
  }

  public getOperationsForExecution(executionId: string): OperationData[] {
    return db.prepare('SELECT * FROM operations WHERE execution_id = ?').all(executionId) as OperationData[];
  }

  public updateAssetHash(localPath: string, hash: string): void {
    db.prepare('UPDATE assets SET hash = ? WHERE local_path = ?').run(hash, localPath);
  }

  public getAssetByPath(localPath: string): AssetData | undefined {
    return db.prepare('SELECT * FROM assets WHERE local_path = ?').get(localPath) as AssetData | undefined;
  }

  public addAssetDependency(sourcePath: string, targetPath: string): void {
    const stmt = db.prepare('INSERT OR IGNORE INTO asset_dependencies (source_path, target_path) VALUES (?, ?)');
    stmt.run(sourcePath, targetPath);
  }

  public getDependentAssets(sourcePath: string): string[] {
    const rows = db.prepare('SELECT target_path FROM asset_dependencies WHERE source_path = ?').all(sourcePath) as { target_path: string }[];
    return rows.map(r => r.target_path);
  }
}