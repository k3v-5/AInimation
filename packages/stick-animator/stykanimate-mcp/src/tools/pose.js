/**
 * Pose tools: read the rig at a point in time and change it.
 *
 * The rig is the interesting part of a stick figure: joints carry absolute
 * angles, lengths and bends, and hands and feet may be driven by inverse
 * kinematics. These tools work in those terms, and report the solved world
 * positions so a model can see what a pose actually looks like.
 */
import { z } from 'zod/v4';
import { poseReport } from '../summary.js';
import { ToolError } from '../errors.js';
import { degrees, goToKeyframe, keyframeIndex, project, rangeOptions, result, selectJoint, selectObject } from './shared.js';

const projectField = z
  .string()
  .optional()
  .describe('The id of an open project, from project_open. Defaults to the project used most recently.');
const frameField = z.number().int().optional().describe('The place on the timeline to work on. Defaults to the playhead.');
const uidField = z.number().int().describe('The id of the figure instance.');

export function registerPoseTools(server, { store }) {
  server.registerTool(
    'pose_evaluate',
    {
      title: 'Evaluate the rig',
      description:
        'Read the solved rig at a point in the animation: where every joint sits in canvas pixels, where each ' +
        'segment starts and ends, and what the inverse kinematics controllers are doing. ' +
        'Use this to find out where a hand or foot is before changing it, and to check a pose after changing it. ' +
        'Give a tick for sub-keyframe precision, or a keyframe number.',
      inputSchema: z.object({
        project: projectField,
        frame: frameField,
        tick: z.number().int().optional().describe('The absolute tick to evaluate. Overrides the keyframe number.'),
        uids: z.array(z.number().int()).optional().describe('Only report these figure instances.'),
        includeSegments: z
          .boolean()
          .optional()
          .describe('Include the per-segment endpoints. Defaults to true.'),
      }),
      annotations: { readOnlyHint: true, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      const editor = current.editor;
      const index = keyframeIndex(editor, input);
      const report = poseReport(editor, { keyframe: index, tick: input.tick, uids: input.uids ?? null });
      if (input.includeSegments === false) {
        for (const figure of report.figures) figure.segments = [];
      }
      const summary = report.figures
        .map(figure => {
          return `${figure.name ?? `Figure ${figure.uid}`}: ${figure.joints.length} joints, root (${figure.root?.x}, ${figure.root?.y})`;
        })
        .join('; ');
      return result(`Keyframe ${report.keyframe} (tick ${report.tick}, ${report.seconds}s): ${summary || 'no figures'}.`, report);
    },
  );

  server.registerTool(
    'pose_set',
    {
      title: 'Set a pose',
      description:
        'Change a figure\'s pose in one keyframe: move its root, scale it, and set the angle, length or world ' +
        'position of any of its joints. ' +
        'A joint is named by its handle id (from figure_describe) or by its index in the segment list. ' +
        'An angle is absolute, measured from the parent joint, in radians or degrees. ' +
        'Give a world x and y to place a joint at a point instead; that respects inverse kinematics. ' +
        'Everything in one call is a single undo step.',
      inputSchema: z.object({
        project: projectField,
        uid: uidField,
        frame: frameField,
        root: z
          .object({ x: z.number(), y: z.number() })
          .optional()
          .describe('The new root position of the figure, in canvas pixels.'),
        scale: z.number().optional().describe('The new size factor of the figure. 2 doubles it.'),
        joints: z
          .array(
            z.object({
              handleId: z.number().int().optional().describe('The native joint identity.'),
              index: z.number().int().optional().describe('The position of the joint in the segment list.'),
              angleDeg: z.number().optional().describe('The absolute joint angle in degrees.'),
              angleRad: z.number().optional().describe('The absolute joint angle in radians.'),
              length: z.number().optional().describe('The length of the segment this joint starts.'),
              x: z.number().optional().describe('The world x to place the joint at, in canvas pixels.'),
              y: z.number().optional().describe('The world y to place the joint at, in canvas pixels.'),
            }),
          )
          .optional()
          .describe('The joints to change.'),
      }),
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false },
    },
    async input => {
      const current = project(store, input);
      const editor = current.editor;
      const index = keyframeIndex(editor, input);
      goToKeyframe(editor, index);
      const object = selectObject(editor, input.uid);
      const figure = editor.report.figure_types.find(entry => entry.figure_type_id === object.figure_type_id);
      const changes = [];
      const notes = [];
      if (input.root && object.join) {
        // A joined figure takes its position from the figure it is joined to,
        // so a root change on it has no visible effect.
        notes.push('This figure is joined to another one, so its root position comes from that figure.');
      }

      editor.beginDrag('Set pose');
      try {
        if (input.root) {
          editor.updateObject({ root_x: input.root.x, root_y: input.root.y });
          changes.push(`root to (${input.root.x}, ${input.root.y})`);
        }
        if (input.scale !== undefined) {
          editor.updateObject({ scale: input.scale });
          changes.push(`scale to ${input.scale}`);
        }
        for (const joint of input.joints ?? []) {
          const index_ = resolveJointIndex(figure, joint);
          editor.select(object.unique_id, index_);
          if (joint.angleDeg !== undefined || joint.angleRad !== undefined) {
            const angle = joint.angleRad ?? degrees(joint.angleDeg);
            editor.updateSegment({ angle_rad: angle });
            changes.push(`joint ${index_} angle to ${angle.toFixed(4)} rad`);
          }
          if (joint.length !== undefined) {
            editor.updateSegment({ length: joint.length });
            changes.push(`joint ${index_} length to ${joint.length}`);
          }
          if (joint.x !== undefined || joint.y !== undefined) {
            if (joint.x === undefined || joint.y === undefined) {
              throw new ToolError('Placing a joint needs both x and y.', { code: 'missing_value' });
            }
            const moved = editor.poseJoint(joint.x, joint.y, { snap: false });
            if (!moved) {
              throw new ToolError(
                `Joint ${index_} could not be moved to (${joint.x}, ${joint.y}). ` +
                  'It may be a static part, a connector, or a joint without inverse kinematics.',
                { code: 'joint_not_movable' },
              );
            }
            changes.push(`joint ${index_} to (${joint.x}, ${joint.y})`);
          }
        }
        editor.commitDrag();
      } catch (error) {
        editor.cancelDrag();
        throw error;
      }
      return result(
        `Set the pose of figure ${input.uid} in keyframe ${index}: ${changes.join(', ') || 'no changes'}.` +
          (notes.length ? ` ${notes.join(' ')}` : ''),
        { uid: input.uid, keyframe: index, changes, notes, project: current.id },
      );
    },
  );

  server.registerTool(
    'pose_ik_set',
    {
      title: 'Move an IK target',
      description:
        'Move the inverse kinematics target of a joint, placing a hand or foot at a point on the canvas. ' +
        'The controller must already be enabled on that joint; use figure_describe to see which joints have ' +
        'controllers. A pinned controller keeps the target when the figure moves; an unpinned one bakes the pose.',
      inputSchema: z.object({
        project: projectField,
        uid: uidField,
        handleId: z.number().int().describe('The joint whose controller to move.'),
        x: z.number().describe('The world x of the target, in canvas pixels.'),
        y: z.number().describe('The world y of the target, in canvas pixels.'),
        frame: frameField,
      }),
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false },
    },
    async input => {
      const current = project(store, input);
      const editor = current.editor;
      const index = keyframeIndex(editor, input);
      goToKeyframe(editor, index);
      selectObject(editor, input.uid);
      const jointIndex = selectJoint(editor, input.handleId);
      const handleId = editor.figure.segments[jointIndex].segment_id;
      const controller = editor.object?._stykIK?.[handleId];
      if (!controller || controller.enabled === false) {
        throw new ToolError(
          `Joint ${handleId} has no enabled inverse kinematics controller. ` +
            'Enable one with set_ik before moving its target.',
          { code: 'no_ik_controller' },
        );
      }
      const moved = editor.poseIKTarget(input.x, input.y);
      if (!moved) {
        throw new ToolError(`The target of joint ${handleId} could not be moved.`, { code: 'ik_not_movable' });
      }
      return result(
        `Moved the IK target of joint ${handleId} on figure ${input.uid} to (${input.x}, ${input.y}).`,
        { uid: input.uid, handleId, x: input.x, y: input.y, pinned: Boolean(controller.pinned), keyframe: index },
      );
    },
  );

  server.registerTool(
    'pose_set_ik',
    {
      title: 'Configure an IK controller',
      description:
        'Turn the inverse kinematics controller of a joint on or off, pin or unpin its target, allow it to ' +
        'stretch, or change how many bones its chain covers. Enabling a controller creates it at the joint\'s ' +
        'current position, so the pose does not jump.',
      inputSchema: z.object({
        project: projectField,
        uid: uidField,
        handleId: z.number().int().describe('The joint whose controller to configure.'),
        enabled: z.boolean().optional().describe('Whether the controller drives the joint.'),
        pinned: z.boolean().optional().describe('Whether the target stays where it is when the figure moves.'),
        allowStretch: z.boolean().optional().describe('Whether the limb may stretch to reach the target.'),
        chainLength: z.number().int().min(1).max(8).optional().describe('How many bones the chain covers.'),
        bendDirection: z.number().int().min(-1).max(1).optional().describe('-1, 0 or 1: which way the knee bends.'),
        frame: frameField,
      }),
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false },
    },
    async input => {
      const current = project(store, input);
      const editor = current.editor;
      const index = keyframeIndex(editor, input);
      goToKeyframe(editor, index);
      selectObject(editor, input.uid);
      const jointIndex = selectJoint(editor, input.handleId);
      const patch = {};
      for (const key of ['enabled', 'pinned', 'allowStretch', 'chainLength', 'bendDirection']) {
        if (input[key] !== undefined) patch[key] = input[key];
      }
      if (!Object.keys(patch).length) {
        throw new ToolError('Give at least one setting to change.', { code: 'missing_value' });
      }
      editor.setNodeIK(patch);
      const handleId = editor.figure.segments[jointIndex].segment_id;
      const controller = editor.object?._stykIK?.[handleId] ?? null;
      return result(
        `Updated the IK controller of joint ${handleId}: ${Object.entries(patch)
          .map(([key, value]) => `${key}=${value}`)
          .join(', ')}.`,
        {
          uid: input.uid,
          handleId,
          settings: controller
            ? {
                enabled: controller.enabled !== false,
                pinned: Boolean(controller.pinned),
                allowStretch: Boolean(controller.allowStretch),
                chainLength: controller.chainLength ?? null,
                target: controller.target ? { x: controller.target.x, y: controller.target.y } : null,
              }
            : null,
          keyframe: index,
        },
      );
    },
  );

  server.registerTool(
    'pose_reset',
    {
      title: 'Reset a pose',
      description:
        'Return a figure to the rest pose of its definition, dropping the angles, lengths and bends it had. ' +
        'The figure keeps its position, size and colour.',
      inputSchema: z.object({
        project: projectField,
        uid: uidField,
        frame: frameField,
        frames: z.array(z.number().int()).optional().describe('Several keyframes to reset the figure in.'),
      }),
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      const editor = current.editor;
      const positions = input.frames ?? [keyframeIndex(editor, input)];
      for (const position of positions) {
        if (position < 0 || position >= editor.timeline.length) {
          throw new ToolError(
            `There is no keyframe ${position}. The animation has ${editor.timeline.length} keyframes ` +
              `(0 to ${editor.timeline.length - 1}).`,
            { code: 'bad_frame' },
          );
        }
      }
      const range = rangeOptions(editor, positions);
      const outcome = editor.applyFigureRange({ kind: 'reset' }, {
        uids: [input.uid],
        ...range,
        label: 'Reset pose',
      });
      return result(`Reset the pose of figure ${input.uid} in ${outcome.changedFrames} keyframe(s).`, {
        uid: input.uid,
        changedFrames: outcome.changedFrames,
        project: current.id,
      });
    },
  );
}

/** Find a joint by handle id, or by its position in the segment list. */
function resolveJointIndex(figure, joint) {
  if (joint.handleId !== undefined) {
    const index = figure.segments.findIndex(segment => segment.segment_id === joint.handleId);
    if (index < 0) {
      const handles = figure.segments.map(segment => segment.segment_id);
      throw new ToolError(
        `This figure has no joint with the handle id ${joint.handleId}. Its handles: ${handles.join(', ') || 'none'}.`,
        { code: 'unknown_joint' },
      );
    }
    return index;
  }
  if (joint.index !== undefined) {
    if (joint.index < 0 || joint.index >= figure.segments.length) {
      throw new ToolError(
        `This figure has ${figure.segments.length} joints, so the index ${joint.index} is out of range.`,
        { code: 'unknown_joint' },
      );
    }
    return joint.index;
  }
  throw new ToolError('Name the joint with a handleId or an index.', { code: 'missing_target' });
}
