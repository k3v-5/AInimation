import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { ProjectManager } from '../src/core/ProjectManager.js';
import { db } from '../src/core/Database.js';

describe('ProjectManager', () => {
  let projectManager: ProjectManager;

  beforeEach(() => {
    db.exec('DELETE FROM assets');
    db.exec('DELETE FROM projects');
    projectManager = new ProjectManager();
  });

  afterEach(() => {
    db.exec('DELETE FROM assets');
    db.exec('DELETE FROM projects');
  });

  it('should create and retrieve a project', () => {
    const proj = projectManager.createProject('Test Project');
    expect(proj).toBeDefined();
    expect(proj.name).toBe('Test Project');
    expect(proj.id).toMatch(/^proj_\d+_\d+$/);

    const retrieved = projectManager.getProject(proj.id);
    expect(retrieved).toBeDefined();
    expect(retrieved?.name).toBe('Test Project');
  });

  it('should list projects in order of last_modified', () => {
    const proj1 = projectManager.createProject('Proj 1');
    db.prepare("UPDATE projects SET last_modified = '2020-01-01 00:00:00' WHERE id = ?").run(proj1.id);

    const proj2 = projectManager.createProject('Proj 2');
    db.prepare("UPDATE projects SET last_modified = '2021-01-01 00:00:00' WHERE id = ?").run(proj2.id);

    const projects = projectManager.listProjects();
    expect(projects.length).toBe(2);
    expect(projects[0].id).toBe(proj2.id); // More recent first
    expect(projects[1].id).toBe(proj1.id);
  });

  it('should save and retrieve assets for a project', () => {
    const proj = projectManager.createProject('Test Project 2');

    projectManager.saveAsset({
      id: 'asset_1',
      project_id: proj.id,
      type: 'puppet',
      local_path: '/some/path/puppet.psd',
      hash: null,
      created_at: new Date().toISOString()
    });

    const assets = projectManager.getAssetsForProject(proj.id);
    expect(assets.length).toBe(1);
    expect(assets[0].id).toBe('asset_1');
    expect(assets[0].local_path).toBe('/some/path/puppet.psd');
  });
});
