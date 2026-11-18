/**
 * The server: tool registration, resources and the session it holds.
 */
import { McpServer, ResourceTemplate } from '@modelcontextprotocol/server';
import { z } from 'zod/v4';
import { CodecService } from './codec.js';
import { ProjectStore } from './session.js';
import { projectSummary, poseReport } from './summary.js';
import { registerProjectTools } from './tools/project.js';
import { registerFigureTools } from './tools/figure.js';
import { registerPoseTools } from './tools/pose.js';
import { registerTimelineTools } from './tools/timeline.js';
import { registerLayerTools } from './tools/layer.js';
import { registerHistoryTools } from './tools/history.js';
import { guard } from './errors.js';

const VERSION = '0.1.0';

/**
 * Build the MCP server.
 *
 * The session (the open projects and the Python codec) is created once and
 * shared, so it survives the per-request server instances the HTTP transport
 * builds.
 *
 * @param {object} [options]
 * @param {ProjectStore} [options.store] The session to work on.
 * @param {CodecService|null} [options.codec] The Python codec, for Pivot files.
 */
export function createServer({ store, codec = null, log = () => {} } = {}) {
  if (!store) {
    throw new Error('createServer needs a session. Build one with createSession().');
  }
  const server = new McpServer({ name: 'stykanimate', version: VERSION });
  const context = { store, codec, log };
  // Every tool answers with a tool result rather than a protocol fault, so a
  // mistake in a request comes back as something the model can read and fix.
  const tools = {
    registerTool(name, config, handler) {
      return server.registerTool(name, config, (args, extra) => guard(() => handler(args, extra)));
    },
  };

  registerCapabilityTools(tools, context);
  registerProjectTools(tools, context);
  registerFigureTools(tools, context);
  registerPoseTools(tools, context);
  registerTimelineTools(tools, context);
  registerLayerTools(tools, context);
  registerHistoryTools(tools, context);
  registerResources(server, context);

  return server;
}

/** Create the session the tools work on: open projects and the codec. */
export function createSession({ pivot = true, log = () => {} } = {}) {
  const codec = pivot ? new CodecService({ log }) : null;
  const store = new ProjectStore({ codec });
  return { store, codec };
}

function registerCapabilityTools(server, { store, codec }) {
  server.registerTool(
    'capabilities',
    {
      title: 'What this server can do',
      description:
        'Report what this server supports: the file formats it can read and write, whether the Python codec for ' +
        'Pivot files is available, and the projects that are currently open. ' +
        'Call this first when you do not know what the project looks like yet.',
      inputSchema: z.object({}),
      annotations: { readOnlyHint: true, idempotentHint: true },
    },
    async () => {
      const projects = store.list().map(project => ({
        id: project.id,
        name: project.name,
        path: project.path,
        format: project.kind,
        dirty: project.dirty,
        keyframes: project.editor.report.keyframes.length,
        figureDefinitions: project.editor.report.figure_types.length,
      }));
      return {
        content: [
          {
            type: 'text',
            text:
              `StykAnimate MCP ${VERSION}. Reads .styk, .stkz and .stykmov directly; ` +
              `${codec ? 'reads and writes .piv and .stk through the bundled Python codec' : 'cannot read Pivot files in this build'}. ` +
              `Writes .styk, .stkz, .stykmov${codec ? ', .piv and .stk' : ''}. ` +
              `${projects.length} project(s) open.`,
          },
        ],
        structuredContent: {
          version: VERSION,
          reads: ['styk', 'stkz', 'stykmov', 'json', ...(codec ? ['piv', 'stk'] : [])],
          writes: ['styk', 'stkz', 'stykmov', ...(codec ? ['piv', 'stk'] : [])],
          pivotCodec: Boolean(codec),
          pythonCodecRunning: Boolean(codec?.running),
          openProjects: projects,
        },      };
    },
  );
}

function registerResources(server, { store }) {
  server.registerResource(
    'project-summary',
    'stykanimate://projects',
    {
      title: 'Open projects',
      description: 'A summary of every project this session holds open.',
      mimeType: 'application/json',
    },
    async uri => ({
      contents: [
        {
          uri: uri.href,
          mimeType: 'application/json',
          text: JSON.stringify(store.list().map(projectSummary), null, 2),
        },
      ],
    }),
  );

  server.registerResource(
    'project-document',
    new ResourceTemplate('stykanimate://projects/{project}/document', {
      list: async () => ({
        resources: store.list().map(project => ({
          uri: `stykanimate://projects/${project.id}/document`,
          name: `${project.name} document`,
          title: `${project.name} document`,
          description: 'The editable document of the project.',
          mimeType: 'application/json',
        })),
      }),
    }),
    {
      title: 'Project document',
      description:
        'The whole editable document of a project, in the native StykAnimate schema. ' +
        'Use it to read the project exactly; change it through the tools, not by editing this text.',
      mimeType: 'application/json',
    },
    async (uri, { project } = {}) => {
      const target = store.require(project);
      return {
        contents: [
          {
            uri: uri.href,
            mimeType: 'application/json',
            text: JSON.stringify(target.editor.serialize(), null, 2),
          },
        ],
      };
    },
  );

  server.registerResource(
    'project-pose',
    new ResourceTemplate('stykanimate://projects/{project}/pose', {
      list: async () => ({
        resources: store.list().map(project => ({
          uri: `stykanimate://projects/${project.id}/pose`,
          name: `${project.name} rig`,
          title: `${project.name} rig`,
          description: 'The solved rig of the project at the playhead.',
          mimeType: 'application/json',
        })),
      }),
    }),
    {
      title: 'Solved rig',
      description: 'The solved rig of a project at one tick: joint positions, segment endpoints and IK state.',
      mimeType: 'application/json',
    },
    async (uri, { project, tick } = {}) => {
      const target = store.require(project);
      const report = poseReport(target.editor, {
        keyframe: target.editor.frameIndex,
        tick: tick === undefined ? undefined : Number(tick),
      });
      return {
        contents: [{ uri: uri.href, mimeType: 'application/json', text: JSON.stringify(report, null, 2) }],
      };
    },
  );
}

export { guard };
