import { PuppetBuilder } from '../core/PuppetBuilder.js';
import { CharacterAnimatorDeepEngine } from '../core/CharacterAnimatorDeepEngine.js';
import { AdobeDetector } from '../core/AdobeDetector.js';
import { PhaseTracker } from '../core/PhaseTracker.js';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

export const characterTools = [
  {
    name: 'ch_scaffold_puppet',
    description: 'Generates a fully rigged, production-ready PSD puppet file structured according to Adobe Character Animator standards (includes +Head, Eyes, Pupils, Body, Limbs, 14 custom visual Mouth visemes, Dangle/Draggable/Fixed physics tags, and Hand swap triggers).',
    inputSchema: {
      type: 'object',
      properties: {
        character_name: {
          type: 'string',
          description: 'Name of the character (e.g. "Hero", "Robot", "Wizard")'
        },
        output_path: {
          type: 'string',
          description: 'Path where the .psd file will be written (e.g. "F:/Projects/Puppets/Hero.psd")'
        },
        width: {
          type: 'number',
          description: 'Width in pixels (default: 2000)'
        },
        height: {
          type: 'number',
          description: 'Height in pixels (default: 2000)'
        },
        include_limbs: {
          type: 'boolean',
          description: 'Whether to include arms and legs (+Left Arm, +Right Arm, etc.) (default: true)'
        },
        include_physics_tags: {
          type: 'boolean',
          description: 'Whether to include Dangle (hair), Draggable (hand), and Fixed (feet) tags (default: true)'
        },
        include_hand_triggers: {
          type: 'boolean',
          description: 'Whether to include keyboard-triggered hand swap sets [Open (1), Fist (2), Point (3), ThumbsUp (4)] (default: true)'
        },
        include_face_parallax: {
          type: 'boolean',
          description: 'Whether to structure front hair, ears, and back hair for 2.5D head parallax (default: true)'
        }
      },
      required: ['character_name', 'output_path']
    },
    handler: async (args: any) => {
      const out = PuppetBuilder.scaffoldPuppet({
        characterName: args.character_name,
        outPath: args.output_path,
        width: args.width,
        height: args.height,
        includeLimbs: args.include_limbs ?? true,
        includePhysicsTags: args.include_physics_tags ?? true,
        includeHandTriggers: args.include_hand_triggers ?? true,
        includeFaceParallax: args.include_face_parallax ?? true
      });

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            message: `Deep puppet PSD scaffolded for Character Animator at: ${out}`,
            character_name: args.character_name,
            file_path: out,
            file_size_bytes: fs.statSync(out).size,
            features_included: {
              custom_graphic_visemes: 14,
              physics_tags: args.include_physics_tags ?? true,
              hand_swap_triggers: args.include_hand_triggers ?? true,
              face_parallax_layers: args.include_face_parallax ?? true
            },
            ready_for_import: true
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ch_scaffold_multi_angle_puppet',
    description: 'Generates a production-ready Multi-Angle Head Turner PSD puppet for Adobe Character Animator (3-view: Frontal, Left Quarter, Right Quarter, or 5-view: including Left Profile and Right Profile). Each view contains properly perspective-shifted Eyes, Pupils, Nose, and all 14 visual Mouth visemes.',
    inputSchema: {
      type: 'object',
      properties: {
        character_name: {
          type: 'string',
          description: 'Name of the character'
        },
        output_path: {
          type: 'string',
          description: 'Target .psd file path'
        },
        views: {
          type: 'string',
          enum: ['3-view', '5-view'],
          description: '"3-view" (Frontal, Left Quarter, Right Quarter) or "5-view" (+ Profiles) (default: "3-view")'
        },
        width: {
          type: 'number',
          description: 'Canvas width in pixels (default: 2000)'
        },
        height: {
          type: 'number',
          description: 'Canvas height in pixels (default: 2000)'
        },
        include_limbs: {
          type: 'boolean',
          description: 'Whether to include arms and legs (default: true)'
        },
        include_physics: {
          type: 'boolean',
          description: 'Whether to include Dangle, Draggable, and Fixed physics tags (default: true)'
        }
      },
      required: ['character_name', 'output_path']
    },
    handler: async (args: any) => {
      const out = CharacterAnimatorDeepEngine.scaffoldMultiAnglePuppet({
        characterName: args.character_name,
        outPath: args.output_path,
        views: args.views || '3-view',
        width: args.width,
        height: args.height,
        includeLimbs: args.include_limbs !== false,
        includePhysics: args.include_physics !== false
      });

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            message: `Multi-angle Head Turner puppet created at: ${out}`,
            character_name: args.character_name,
            views_mode: args.views || '3-view',
            file_path: out,
            file_size_bytes: fs.statSync(out).size,
            ready_for_head_turner: true
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ch_scaffold_walk_puppet',
    description: 'Generates a puppet specifically rigged for Adobe Character Animator Walk behavior, structured with Frontal, Left Profile, and Right Profile views with standard joint tags (Left/Right Hip, Knee, Ankle, Heel, Toe, Waist, Neck).',
    inputSchema: {
      type: 'object',
      properties: {
        character_name: {
          type: 'string',
          description: 'Name of the character'
        },
        output_path: {
          type: 'string',
          description: 'Target .psd file path'
        },
        width: {
          type: 'number',
          description: 'Canvas width in pixels (default: 2000)'
        },
        height: {
          type: 'number',
          description: 'Canvas height in pixels (default: 2200)'
        }
      },
      required: ['character_name', 'output_path']
    },
    handler: async (args: any) => {
      const out = CharacterAnimatorDeepEngine.scaffoldWalkPuppet({
        characterName: args.character_name,
        outPath: args.output_path,
        width: args.width,
        height: args.height
      });

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            message: `Walk-cycle rigged puppet created at: ${out}`,
            character_name: args.character_name,
            file_path: out,
            file_size_bytes: fs.statSync(out).size,
            walk_views: ['Frontal', 'Left Profile', 'Right Profile'],
            ready_for_walk_behavior: true
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ch_slice_artwork_to_puppet',
    description: 'Converts 2D flat character artwork or illustration parameters into an anatomically sliced, fully rigged Character Animator PSD with Head, Eyes, Eyeballs, Pupils, Torso, Limbs, and 14 custom visual Mouth visemes.',
    inputSchema: {
      type: 'object',
      properties: {
        character_name: {
          type: 'string',
          description: 'Name of the character'
        },
        output_path: {
          type: 'string',
          description: 'Target .psd file path'
        },
        image_path: {
          type: 'string',
          description: 'Optional path to existing illustration image (PNG, JPG)'
        },
        primary_color_rgb: {
          type: 'array',
          items: { type: 'number' },
          description: 'RGB array [r, g, b] for character clothes/accent'
        },
        skin_color_rgb: {
          type: 'array',
          items: { type: 'number' },
          description: 'RGB array [r, g, b] for skin tone'
        },
        width: {
          type: 'number',
          description: 'Canvas width (default: 2000)'
        },
        height: {
          type: 'number',
          description: 'Canvas height (default: 2000)'
        }
      },
      required: ['character_name', 'output_path']
    },
    handler: async (args: any) => {
      const out = CharacterAnimatorDeepEngine.sliceArtworkToPuppet({
        characterName: args.character_name,
        outPath: args.output_path,
        imagePath: args.image_path,
        primaryColor: args.primary_color_rgb,
        skinColor: args.skin_color_rgb,
        width: args.width,
        height: args.height
      });

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            message: `Artwork sliced and rigged into Character Animator PSD at: ${out}`,
            character_name: args.character_name,
            file_path: out,
            visemes_synthesized: 14,
            ready_for_import: true
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ch_add_puppet_triggers_and_physics',
    description: 'Enriches any existing puppet PSD with emotional swap sets [Blush (b), Sweatdrop (w), AnimeVein (v)], frame-by-frame crying tears cycle [Tears (t)], hand swap sets [6 gestures (1..6)], breathing behavior (+Chest Breather), and Dangle hair physics.',
    inputSchema: {
      type: 'object',
      properties: {
        psd_path: {
          type: 'string',
          description: 'Path to existing puppet .psd file'
        },
        output_path: {
          type: 'string',
          description: 'Optional target .psd path (overwrites original if omitted)'
        },
        include_emotions: {
          type: 'boolean',
          description: 'Include Blush, Sweatdrop, AnimeVein triggers (default: true)'
        },
        include_hand_gestures: {
          type: 'boolean',
          description: 'Include 6-gesture hand swap set [Open, Fist, Point, Peace, ThumbsUp, Wave] (default: true)'
        },
        include_cycle_layers: {
          type: 'boolean',
          description: 'Include frame-by-frame tears cycle (default: true)'
        },
        include_breathing: {
          type: 'boolean',
          description: 'Include +Chest Breather layer (default: true)'
        }
      },
      required: ['psd_path']
    },
    handler: async (args: any) => {
      const result = CharacterAnimatorDeepEngine.addPuppetTriggersAndPhysics({
        psdPath: args.psd_path,
        outPath: args.output_path,
        includeEmotions: args.include_emotions !== false,
        includeHandGestures: args.include_hand_gestures !== false,
        includeCycleLayers: args.include_cycle_layers !== false,
        includeBreathing: args.include_breathing !== false
      });

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            message: `Puppet triggers and physics injected successfully into: ${result.outPath}`,
            file_path: result.outPath,
            added_features: result.addedFeatures
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ch_audit_puppet_deep',
    description: 'Puppet Doctor tool that performs an exhaustive multi-criteria audit of any Character Animator PSD or AI file. Calculates a 0-100 health score, breakdown across independence (+), visemes, eyes, limbs/walk joints, physics, and triggers, plus remediation recommendations.',
    inputSchema: {
      type: 'object',
      properties: {
        file_path: {
          type: 'string',
          description: 'Path to the .psd puppet file to audit'
        }
      },
      required: ['file_path']
    },
    handler: async (args: any) => {
      const report = CharacterAnimatorDeepEngine.auditPuppetDeep(args.file_path);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: report.isReadyForCharacterAnimator ? 'HEALTHY' : 'NEEDS_REPAIR',
            ...report
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ch_auto_repair_puppet',
    description: 'Puppet Doctor auto-repair tool that scans a broken or unstructured character PSD, fixes missing layer independence ("+"), synthesizes missing mouth visemes using distinct graphics, repairs eye/pupil naming, and wraps loose layers in a root character group.',
    inputSchema: {
      type: 'object',
      properties: {
        input_psd_path: {
          type: 'string',
          description: 'Path to the broken or unorganized .psd file'
        },
        output_psd_path: {
          type: 'string',
          description: 'Optional path to write the repaired .psd file (overwrites original if omitted)'
        }
      },
      required: ['input_psd_path']
    },
    handler: async (args: any) => {
      const result = CharacterAnimatorDeepEngine.autoRepairPuppet(args.input_psd_path, args.output_psd_path);
      const audit = CharacterAnimatorDeepEngine.auditPuppetDeep(result.repairedPath);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            message: `Puppet auto-repaired successfully. New health score: ${audit.healthScore}/100`,
            repaired_file_path: result.repairedPath,
            changes_applied: result.changes,
            post_repair_audit: {
              healthScore: audit.healthScore,
              isReady: audit.isReadyForCharacterAnimator,
              visemesFound: audit.details.foundVisemes.length
            }
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ch_prepare_recording_take',
    description: 'Prepares a complete performance recording take package: synthesizes high-def neural speech audio WAV, frame-accurate viseme cues timeline (.json), trigger cue sheet (.txt & .json), and an After Effects Dynamic Link JSX import script.',
    inputSchema: {
      type: 'object',
      properties: {
        character_name: {
          type: 'string',
          description: 'Name of the character'
        },
        puppet_psd_path: {
          type: 'string',
          description: 'Path to the rigged puppet .psd file'
        },
        output_dir: {
          type: 'string',
          description: 'Directory where take package files will be saved'
        },
        speech_text: {
          type: 'string',
          description: 'Text for neural speech synthesis (optional if audio_path is provided)'
        },
        audio_path: {
          type: 'string',
          description: 'Path to existing audio file (optional if speech_text is provided)'
        },
        voice: {
          type: 'string',
          description: 'Edge-TTS voice identifier (e.g. "es-ES-AlvaroNeural", "en-US-GuyNeural")'
        },
        fps: {
          type: 'number',
          description: 'Animation frame rate (default: 30)'
        },
        triggers_timeline: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              timeSec: { type: 'number' },
              triggerKey: { type: 'string' },
              triggerName: { type: 'string' }
            }
          },
          description: 'List of trigger actions with timestamps'
        }
      },
      required: ['character_name', 'puppet_psd_path', 'output_dir']
    },
    handler: async (args: any) => {
      const result = await CharacterAnimatorDeepEngine.prepareRecordingTake({
        characterName: args.character_name,
        puppetPsdPath: args.puppet_psd_path,
        outputDir: args.output_dir,
        speechText: args.speech_text,
        audioPath: args.audio_path,
        voice: args.voice,
        fps: args.fps,
        triggersTimeline: args.triggers_timeline
      });

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            message: `Performance recording take prepared for ${args.character_name}`,
            ...result
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ch_validate_puppet',
    description: 'Deeply inspects an existing PSD file and verifies its compliance with Adobe Character Animator rigging rules. Reports missing visemes, head independence (+) tags, pupil tracking readiness, physics tags (Dangle, Draggable, Fixed), and hand swap triggers.',
    inputSchema: {
      type: 'object',
      properties: {
        file_path: {
          type: 'string',
          description: 'Path to the .psd file to validate'
        }
      },
      required: ['file_path']
    },
    handler: async (args: any) => {
      const report = PuppetBuilder.validatePuppet(args.file_path);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: report.isValid ? 'VALID' : 'NEEDS_ATTENTION',
            ...report
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ch_launch_character_animator',
    description: 'Launches Adobe Character Animator on the host machine, optionally opening a puppet file (.psd, .ai) or existing project.',
    inputSchema: {
      type: 'object',
      properties: {
        file_to_open: {
          type: 'string',
          description: 'Optional path to a .psd, .ai, or .chproj file to open directly'
        }
      }
    },
    handler: async (args: any) => {
      const chExe = AdobeDetector.getCharacterAnimatorPath();
      if (!chExe) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'ERROR',
              message: 'Adobe Character Animator executable was not found on this machine.'
            }, null, 2)
          }],
          isError: true
        };
      }

      const launchArgs = args.file_to_open ? [path.resolve(args.file_to_open)] : [];
      const child = spawn(chExe, launchArgs, { detached: true, stdio: 'ignore' });
      child.unref();

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            message: `Adobe Character Animator launched (${chExe})${args.file_to_open ? ` with ${args.file_to_open}` : ''}`
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ch_inspect_environment',
    description: 'Inspects and reports the installation status and paths of Adobe Character Animator, Illustrator, After Effects, and Blender on the local workstation.',
    inputSchema: {
      type: 'object',
      properties: {}
    },
    handler: async () => {
      const status = AdobeDetector.getStatus();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            environment: status
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ch_get_roadmap_status',
    description: 'Returns the current progress hook of the Master Animation Roadmap, showing completed phases, the active phase, and pending phases.',
    inputSchema: {
      type: 'object',
      properties: {}
    },
    handler: async () => {
      const state = PhaseTracker.getState();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            roadmap: state
          }, null, 2)
        }]
      };
    }
  }
];
