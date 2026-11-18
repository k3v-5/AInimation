/**
 * History tools: undo and redo the changes the other tools made.
 */
import { z } from 'zod/v4';
import { project, result } from './shared.js';

const projectField = z
  .string()
  .optional()
  .describe('The id of an open project, from project_open. Defaults to the project used most recently.');

export function registerHistoryTools(server, { store }) {
  server.registerTool(
    'history_undo',
    {
      title: 'Undo',
      description:
        'Undo the last change to the open project. Every tool that changes a project makes one undoable step, so ' +
        'one call reverses one tool call. Repeat the call to undo further changes.',
      inputSchema: z.object({ project: projectField }),
      annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      const label = current.editor.undoLabel;
      const undone = await current.editor.undo();
      return result(undone ? `Undid "${label}".` : 'There is nothing left to undo.', {
        undone: Boolean(undone),
        label: label || null,
        canUndo: current.editor.canUndo,
        canRedo: current.editor.canRedo,
        project: current.id,
      });
    },
  );

  server.registerTool(
    'history_redo',
    {
      title: 'Redo',
      description: 'Redo the change that was last undone in the open project.',
      inputSchema: z.object({ project: projectField }),
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      const label = current.editor.redoLabel;
      const redone = await current.editor.redo();
      return result(redone ? `Redid "${label}".` : 'There is nothing left to redo.', {
        redone: Boolean(redone),
        label: label || null,
        canUndo: current.editor.canUndo,
        canRedo: current.editor.canRedo,
        project: current.id,
      });
    },
  );
}
