/**
 * Project tools: open, inspect, validate and save a project.
 */
import path from 'node:path';
import { z } from 'zod/v4';
import { projectSummary, keyframeRows, layerRows, figureRows, paginate, playbackRows, DEFAULT_LIMIT } from '../summary.js';
import { writeDocument, writeFileAtomic } from '../documents.js';
import { ToolError } from '../errors.js';
import { goToKeyframe, keyframeIndex, project, result } from './shared.js';

const projectField = z
  .string()
  .optional()
  .describe('The id of an open project, from project_open. Defaults to the project used most recently.');

const limitField = z
  .number()
  .int()
  .min(1)
  .max(500)
  .optional()
  .describe(`How many rows to return (1-500, default ${DEFAULT_LIMIT}).`);

/** Give a path the extension of the format it is written in. */
function withExtension(target, format) {
  const extension = path.extname(target);
  return extension ? `${target.slice(0, -extension.length)}.${format}` : `${target}.${format}`;
}

export function registerProjectTools(server, { store }) {
  server.registerTool(
    'project_open',
    {
      title: 'Open a project',
      description:
        'Open a StykAnimate or Pivot project file and make it the active project. ' +
        'Accepts .styk, .stkz and .stykmov (StykAnimate native files, read directly in JavaScript) and ' +
        '.piv and .stk (Pivot files, read through the bundled Python codec). ' +
        'Returns a project id that later tools accept, plus a summary of the project. ' +
        'Opening a file does not change it.',
      inputSchema: z.object({
        path: z.string().describe('Absolute or relative path of the project file to open.'),
      }),
      annotations: { readOnlyHint: true, openWorldHint: true, idempotentHint: true },
    },
    async ({ path }) => {
      const opened = await store.openFile(path);
      const summary = projectSummary(opened);
      return result(
        `Opened ${summary.name} (${summary.path}). ${summary.frames.keyframes} keyframes, ` +
          `${summary.figures.instances} figures, ${summary.figures.definitions} definitions, ` +
          `${summary.layers} layers, ${summary.fps} fps, ${summary.canvas.width}×${summary.canvas.height}.`,
        { project: summary },
      );
    },
  );

  server.registerTool(
    'project_close',
    {
      title: 'Close a project',
      description:
        'Close an open project and release its editor. Unsaved changes are discarded; save first with project_save.',
      inputSchema: z.object({ project: projectField }),
      annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      store.close(current.id);
      return result(`Closed ${current.name}.`, { closed: current.id, name: current.name });
    },
  );

  server.registerTool(
    'project_describe',
    {
      title: 'Describe the project',
      description:
        'Report the structure of the open project: canvas, frame rate, keyframes, figure definitions and ' +
        'instances, layers, backgrounds, effects, movieclips and audio. ' +
        'Ask for the parts you need with the "include" list; without it the tool returns the summary alone.',
      inputSchema: z.object({
        project: projectField,
        include: z
          .array(z.enum(['layers', 'figures', 'keyframes', 'definitions']))
          .optional()
          .describe('Extra sections to include: layers, figures, keyframes, definitions.'),
        limit: limitField,
      }),
      annotations: { readOnlyHint: true, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      const summary = projectSummary(current);
      const data = { project: summary };
      const include = new Set(input.include ?? []);
      if (include.has('layers')) data.layers = layerRows(current.editor);
      if (include.has('figures')) {
        const page = paginate(figureRows(current.editor), { limit: input.limit });
        data.figures = page;
      }
      if (include.has('keyframes')) {
        const page = paginate(keyframeRows(current.editor), { limit: input.limit });
        data.keyframes = page;
      }
      if (include.has('definitions')) {
        data.definitions = current.editor.report.figure_types.map(figure => ({
          figureTypeId: figure.figure_type_id,
          name: figure.name ?? null,
          segmentCount: figure.segments?.length ?? 0,
          isMovieclip: Boolean(figure._styk?.movieclip),
        }));
      }
      return result(
        `${summary.name}: ${summary.frames.keyframes} keyframes, ${summary.figures.instances} figures, ` +
          `${summary.figures.definitions} definitions, ${summary.layers} layers, ${summary.fps} fps, ` +
          `${summary.canvas.width}×${summary.canvas.height}, ${summary.frames.durationSeconds}s.`,
        data,
      );
    },
  );

  server.registerTool(
    'project_validate',
    {
      title: 'Validate the project',
      description:
        'Run the editor\'s own document validation over the open project and report the first problem it finds, ' +
        'or confirm that the project is valid. Use this after edits that a client rejected, and before saving.',
      inputSchema: z.object({ project: projectField }),
      annotations: { readOnlyHint: true, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      try {
        current.editor.serialize();
        return result(`${current.name} is valid.`, { valid: true, project: current.id });
      } catch (error) {
        return {
          isError: true,
          content: [{ type: 'text', text: `${current.name} is not valid: ${error.message}` }],
          structuredContent: {
            valid: false,
            project: current.id,
            error: { message: error.message, messageKey: error.messageKey ?? null },
          },
        };
      }
    },
  );

  server.registerTool(
    'project_save',
    {
      title: 'Save the project',
      description:
        'Write the open project to a file. Use "styk" for a StykAnimate project, "stkz" for a single figure, ' +
        '"stykmov" for a movieclip, and "piv" or "stk" for Pivot files (these need the Python codec). ' +
        'A figure file holds one figure: name it with "figureTypeId" or "figureUid", or leave both out to take ' +
        'the first figure in the project. ' +
        'The file is written in full before it replaces the destination, so a failure leaves the previous file intact. ' +
        'Give a path to choose where it goes, or leave it out to save beside the file it was opened from.',
      inputSchema: z.object({
        project: projectField,
        path: z.string().optional().describe('Where to write the file. Defaults to the path it was opened from.'),
        format: z
          .enum(['styk', 'stkz', 'stykmov', 'piv', 'stk'])
          .optional()
          .describe('The file format. Defaults to the format it was opened from, or styk.'),
        figureTypeId: z.number().int().optional().describe('The figure definition to export as stkz or stk.'),
        figureUid: z.number().int().optional().describe('The figure instance to export as stkz.'),
      }),
      annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: false },
    },
    async input => {
      const current = project(store, input);
      const format = input.format ?? (current.kind && current.kind !== 'json' ? current.kind : 'styk');
      const target = input.path ?? current.path;
      if (!target) {
        throw new ToolError('Give a path to save the project to.', { code: 'missing_path' });
      }
      const document = current.editor.serialize();
      const written = await writeDocument({
        document,
        format,
        name: current.name,
        figureTypeId: input.figureTypeId,
        figureUid: input.figureUid,
        sourceId: current.sourceId,
        codec: store.codec,
      });
      const destination = withExtension(target, format);
      const saved = await writeFileAtomic(destination, written.bytes);
      current.editor.markSaved();
      return result(`Saved ${current.name} to ${saved.path} (${saved.bytes} bytes, ${format}).`, {
        path: saved.path,
        bytes: saved.bytes,
        format,
        project: current.id,
      });
    },
  );

  server.registerTool(
    'project_timeline',
    {
      title: 'Show the timeline',
      description:
        'List the timeline of the open project. The "playback" section is the list of places the playhead moves ' +
        'through: their number is the frame number the pose and figure tools take. The "keyframes" section is the ' +
        'list of stored poses, with the place each one is shown at. ' +
        'Give "fromTick" and "toTick" to narrow the playback list.',
      inputSchema: z.object({
        project: projectField,
        fromTick: z.number().int().optional().describe('Only places starting at or after this tick.'),
        toTick: z.number().int().optional().describe('Only places starting at or before this tick.'),
        limit: limitField,
      }),
      annotations: { readOnlyHint: true, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      const rows = keyframeRows(current.editor);
      const page = paginate(rows, { limit: input.limit });
      const playback = paginate(playbackRows(current.editor, { from: input.fromTick ?? 0, to: input.toTick ?? Infinity }), {
        limit: input.limit,
      });
      return result(
        `${playback.returned} of ${playback.total} places on the timeline, ${page.total} stored poses · ` +
          `${current.editor.report.fps} fps · ${current.editor.totalTicks} ticks total.`,
        {
          playback,
          keyframes: page,
          fps: current.editor.report.fps,
          totalTicks: current.editor.totalTicks,
        },
      );
    },
  );

  server.registerTool(
    'project_seek',
    {
      title: 'Move the playhead',
      description:
        'Move the editor\'s playhead to a keyframe or an absolute tick. The playhead decides which keyframe later ' +
        'tools edit when no frame is named.',
      inputSchema: z.object({
        project: projectField,
        frame: z.number().int().optional().describe('The keyframe number to go to.'),
        tick: z.number().int().optional().describe('The absolute tick to go to.'),
      }),
      annotations: { readOnlyHint: true, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      if (input.frame === undefined && input.tick === undefined) {
        throw new ToolError('Give a keyframe number or a tick to move to.', { code: 'missing_target' });
      }
      if (input.tick !== undefined && input.tick !== null) {
        // A tick request lands between keyframes, so the playhead goes there
        // rather than to the start of the keyframe it falls in.
        const tick = Math.trunc(input.tick);
        if (!Number.isInteger(tick) || tick < 0 || tick >= Math.max(1, current.editor.totalTicks)) {
          throw new ToolError(
            `Tick ${tick} is outside the animation (0 to ${Math.max(0, current.editor.totalTicks - 1)}).`,
            { code: 'bad_tick' },
          );
        }
        current.editor.seek(tick);
        return result(`Playhead at tick ${current.editor.tick}.`, {
          tick: current.editor.tick,
          keyframe: current.editor.frameIndex,
          project: current.id,
        });
      }
      const index = keyframeIndex(current.editor, input);
      goToKeyframe(current.editor, index);
      return result(`Playhead at keyframe ${index} (tick ${current.editor.tick}).`, {
        keyframe: index,
        tick: current.editor.tick,
        project: current.id,
      });
    },
  );
}
