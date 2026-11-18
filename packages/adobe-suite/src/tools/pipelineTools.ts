import { PipelineManager } from '../core/PipelineManager.js';
import { BlenderEngine } from '../core/BlenderEngine.js';
import { EmotionPreset } from '../core/NeuralSpeechEngine.js';
import path from 'path';
import fs from 'fs';
import os from 'os';

export const pipelineTools = [
  {
    name: 'render_preview_frame_to_base64',
    description: 'Extracts and encodes an image or rendered animation frame into Base64 (PNG/JPEG) within the MCP response. This provides direct "eyes" for multimodal models (Claude, GPT-4o, Gemini) to visually inspect character anatomy, mouth visemes, lighting, and composition.',
    inputSchema: {
      type: 'object',
      properties: {
        file_path: {
          type: 'string',
          description: 'Path to an existing image file (.png, .jpg, .webp, .svg)'
        },
        blend_file: {
          type: 'string',
          description: 'Optional .blend file path to render a frame directly on the fly if an image does not already exist'
        },
        frame_number: {
          type: 'number',
          description: 'Frame number to render if blend_file is provided (default: 1)'
        }
      }
    },
    handler: async (args: any) => {
      let targetPath = args.file_path;

      // If a blend file is provided and targetPath is missing, render a quick frame with Blender
      if (args.blend_file && (!targetPath || !fs.existsSync(targetPath))) {
        const tempPng = path.join(os.tmpdir(), `preview_render_${Date.now()}.png`);
        const passes = await BlenderEngine.renderParallaxPasses({
          blendFile: args.blend_file,
          outputDir: path.dirname(tempPng),
          baseName: `temp_frame_${Date.now()}`,
          frameNumber: args.frame_number || 1,
          width: 960,
          height: 540
        });
        targetPath = passes.beautyPass;
      }

      if (!targetPath || !fs.existsSync(targetPath)) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'ERROR',
              error: `Target image file not found: ${targetPath || 'None specified'}`
            }, null, 2)
          }],
          isError: true
        };
      }

      try {
        const info = await PipelineManager.getFrameBase64(targetPath);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                status: 'SUCCESS',
                file_path: info.resolvedPath,
                mime_type: info.mimeType,
                file_size_kb: Math.round(info.fileSizeBytes / 1024),
                resolution: info.resolution || null,
                visual_inspection_ready: true
              }, null, 2)
            },
            {
              type: 'image',
              data: info.base64Data,
              mimeType: info.mimeType
            }
          ]
        };
      } catch (err: any) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'ERROR',
              error: err.message
            }, null, 2)
          }],
          isError: true
        };
      }
    }
  },

  {
    name: 'pipeline_create_talking_character',
    description: 'One-Click Autonomous Pipeline: Simultaneously generates an anatomically rigged Character Animator puppet (.psd) with 14 mouth visemes and physics tags, synthesizes emotional 48kHz neural dialogue (.wav), exports timeline lip-sync cue sheets (.jsx, .json, .csv), and optionally opens Character Animator.',
    inputSchema: {
      type: 'object',
      properties: {
        character_name: {
          type: 'string',
          description: 'Name of the character (e.g. "Sophia", "CyberWarrior")'
        },
        dialogue_text: {
          type: 'string',
          description: 'Dialogue or speech script for the character to speak'
        },
        output_dir: {
          type: 'string',
          description: 'Destination directory for all project assets'
        },
        voice: {
          type: 'string',
          description: 'Voice name or alias (e.g. "mexico_female", "spain_male", "es-MX-DaliaNeural", "us_female")'
        },
        emotion_preset: {
          type: 'string',
          enum: ['neutral', 'cheerful', 'whispering', 'angry', 'sad', 'excited', 'dramatic'],
          description: 'Emotional style and dynamic inflection (default: "cheerful")'
        },
        launch_character_animator: {
          type: 'boolean',
          description: 'Automatically launch Adobe Character Animator with the created puppet (default: false)'
        }
      },
      required: ['character_name', 'dialogue_text', 'output_dir']
    },
    handler: async (args: any) => {
      try {
        const result = await PipelineManager.createTalkingCharacter({
          characterName: args.character_name,
          dialogueText: args.dialogue_text,
          outputDir: args.output_dir,
          voice: args.voice,
          emotionPreset: args.emotion_preset as EmotionPreset,
          launchCharacterAnimator: args.launch_character_animator === true
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }]
        };
      } catch (err: any) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'ERROR',
              message: `Pipeline failed: ${err.message}`
            }, null, 2)
          }],
          isError: true
        };
      }
    }
  },

  {
    name: 'pipeline_render_social_clip',
    description: 'One-Click Social Video Pipeline: Assembles a complete vertical (9:16 for TikTok/Shorts/Reels) or horizontal (16:9) scene combining 2D character, 2.5D background, dialogue audio, lip-sync markers, and secondary bounce physics ready for After Effects composition or batch rendering.',
    inputSchema: {
      type: 'object',
      properties: {
        project_name: {
          type: 'string',
          description: 'Project or episode name'
        },
        output_dir: {
          type: 'string',
          description: 'Destination folder for manifests and scripts'
        },
        character_file: {
          type: 'string',
          description: 'Path to rigged puppet (.psd/.ai) or character render'
        },
        aspect_ratio: {
          type: 'string',
          enum: ['9:16', '16:9', '1:1'],
          description: 'Target video aspect ratio (default: "9:16" vertical)'
        },
        background_file: {
          type: 'string',
          description: 'Optional path to 2D background image or 3D rendered pass'
        },
        dialogue_audio_file: {
          type: 'string',
          description: 'Optional path to character dialogue .wav'
        },
        lip_sync_markers_file: {
          type: 'string',
          description: 'Optional path to lip-sync markers .jsx file'
        },
        duration_seconds: {
          type: 'number',
          description: 'Composition duration in seconds (default: 10)'
        },
        enable_secondary_bounce: {
          type: 'boolean',
          description: 'Inject squash & stretch bounce expressions on character (default: true)'
        }
      },
      required: ['project_name', 'output_dir', 'character_file']
    },
    handler: async (args: any) => {
      try {
        const result = await PipelineManager.createSocialClip({
          projectName: args.project_name,
          outputDir: args.output_dir,
          characterFile: args.character_file,
          aspectRatio: (args.aspect_ratio as any) || '9:16',
          backgroundFile: args.background_file,
          dialogueAudioFile: args.dialogue_audio_file,
          lipSyncMarkersFile: args.lip_sync_markers_file,
          durationSeconds: args.duration_seconds,
          enableSecondaryBounce: args.enable_secondary_bounce !== false
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }]
        };
      } catch (err: any) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'ERROR',
              message: `Social clip pipeline failed: ${err.message}`
            }, null, 2)
          }],
          isError: true
        };
      }
    }
  }
];
