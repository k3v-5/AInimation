/**
 * The open projects a session holds.
 *
 * The editor's own model allows several projects open at once, with one live
 * in the editor and the others resting beside it. The server keeps the same
 * shape: every tool may name a project, and the most recently used one is
 * the default, so a short conversation never has to repeat an identifier.
 */
import { Editor } from './core.js';
import { ToolError } from './errors.js';
import { detectKind, readDocument } from './documents.js';

let counter = 0;

export class Project {
  constructor({ id, editor, path, kind, sourceId, filename }) {
    this.id = id;
    this.editor = editor;
    this.path = path;
    this.kind = kind;
    this.sourceId = sourceId;
    this.filename = filename;
    this.openedAt = Date.now();
  }

  get name() {
    return this.editor.name || this.filename || 'Untitled animation';
  }

  get dirty() {
    return this.editor.dirty;
  }

  get revision() {
    return this.editor.revision;
  }
}

export class ProjectStore {
  #projects = new Map();
  #activeId = null;

  constructor({ codec = null } = {}) {
    this.codec = codec;
  }

  get active() {
    return this.#activeId ? this.#projects.get(this.#activeId) ?? null : null;
  }

  list() {
    return [...this.#projects.values()];
  }

  /** The named project, or the active one. Throws when nothing is open. */
  require(id) {
    if (id === undefined || id === null || id === '') {
      const active = this.active;
      if (!active) {
        throw new ToolError('No project is open. Call project_open with a file path first.', { code: 'no_project' });
      }
      return active;
    }
    const project = this.#projects.get(String(id));
    if (!project) {
      const open = [...this.#projects.keys()];
      throw new ToolError(
        `No open project has the id "${id}". ${open.length ? `Open projects: ${open.join(', ')}.` : 'No projects are open.'}`,
        { code: 'unknown_project' },
      );
    }
    return project;
  }

  /** Open a decoded document as a new project. */
  adopt({ document, path, kind, sourceId, filename }) {
    const id = `p${++counter}`;
    const editor = new Editor({ demo: false, historyLimit: 200 });
    editor.load(document, filename);
    const project = new Project({ id, editor, path, kind, sourceId, filename });
    this.#projects.set(id, project);
    this.#activeId = id;
    return project;
  }

  /** Read a file and open it. */
  async openFile(filePath) {
    const { readSourceFile } = await import('./documents.js');
    const source = await readSourceFile(filePath);
    const kind = detectKind(source.path);
    if (!kind) {
      throw new ToolError(
        `${source.path} is not a StykAnimate or Pivot project. Open a .styk, .stkz, .stykmov, .piv, .stk or .json file.`,
        { code: 'unsupported_file' },
      );
    }
    const read = await readDocument({
      bytes: source.bytes,
      filename: source.path,
      codec: this.codec,
    });
    return this.adopt({
      document: read.document,
      path: source.path,
      kind: read.kind,
      sourceId: read.sourceId,
      filename: read.document?._styk?.name || baseName(source.path),
    });
  }

  /** Close a project and release its editor. */
  close(id) {
    const project = this.require(id);
    this.#projects.delete(project.id);
    if (this.#activeId === project.id) {
      const remaining = [...this.#projects.keys()];
      this.#activeId = remaining.at(-1) ?? null;
    }
    return project;
  }

  /** Mark a project as the default for later calls. */
  activate(id) {
    const project = this.require(id);
    this.#activeId = project.id;
    return project;
  }
}

function baseName(filePath) {
  const name = String(filePath).split(/[\\/]/).at(-1) ?? 'Untitled animation';
  return name.replace(/\.(piv|stk|styk|stkz|stykmov|json)$/i, '');
}
