import { WavGenerator } from '../core/WavGenerator.js';
import { NeuralSpeechEngine, EmotionPreset } from '../core/NeuralSpeechEngine.js';
import path from 'path';
import fs from 'fs';

export const audioTools = [
  {
    name: 'audio_generate_speech',
    description: 'Generates a clean 48kHz 16-bit PCM WAV audio file from text for character dialogue. This format is natively optimal for Adobe Character Animator to compute accurate lip-sync.',
    inputSchema: {
      type: 'object',
      properties: {
        text: {
          type: 'string',
          description: 'The dialogue or speech text for the character to speak'
        },
        output_path: {
          type: 'string',
          description: 'Path where the .wav file should be saved (e.g. "F:/Projects/Audio/voice_01.wav")'
        },
        voice_name: {
          type: 'string',
          description: 'Optional voice name (e.g. "David", "Zira", "Sabina", "Dalia")'
        }
      },
      required: ['text', 'output_path']
    },
    handler: async (args: any) => {
      const generatedPath = await WavGenerator.generateSpeechWav(args.text, args.output_path, args.voice_name);
      const stats = fs.statSync(generatedPath);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            message: 'Audio speech file generated successfully',
            file_path: generatedPath,
            file_size_bytes: stats.size,
            sample_rate: '48,000 Hz',
            channels: 'Mono',
            bit_depth: '16-bit PCM',
            ready_for_lip_sync: true
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'audio_calculate_viseme_cues',
    description: 'Calculates expected phoneme/viseme timing cues for a given text or script, providing a timeline map of which mouth shapes (Ah, Ee, Oh, M, etc.) should appear.',
    inputSchema: {
      type: 'object',
      properties: {
        text: {
          type: 'string',
          description: 'Script or dialogue to analyze'
        },
        words_per_minute: {
          type: 'number',
          description: 'Pacing in words per minute (default: 140)'
        }
      },
      required: ['text']
    },
    handler: async (args: any) => {
      const cues = WavGenerator.estimateVisemeCues(args.text, args.words_per_minute || 140);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            total_cues: cues.length,
            cues
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'audio_generate_expressive_speech',
    description: 'Synthesizes neural broadcast-quality dialogue using Microsoft Edge-TTS with multi-lingual support (Spanish, English, Japanese, etc.), emotional nuances (cheerful, whispering, angry, sad, excited, dramatic), rate/pitch controls, and automatic 48kHz 16-bit PCM resampling with -1.0 dBFS peak normalization for Adobe Character Animator and After Effects.',
    inputSchema: {
      type: 'object',
      properties: {
        text: {
          type: 'string',
          description: 'Dialogue or speech script for the character'
        },
        output_path: {
          type: 'string',
          description: 'Output file path where the .wav file will be saved (e.g. "F:/Projects/Audio/dialogue_01.wav")'
        },
        voice: {
          type: 'string',
          description: 'Voice name or alias (e.g. "es-MX-DaliaNeural", "es-ES-AlvaroNeural", "mexico_female", "mexico_male", "spain_female", "spain_male", "argentina_female", "colombia_male", "us_female", "us_male", "uk_female")'
        },
        emotion_preset: {
          type: 'string',
          enum: ['neutral', 'cheerful', 'whispering', 'angry', 'sad', 'excited', 'dramatic'],
          description: 'Emotional modulation preset adjusting speed, pitch and dynamics'
        },
        rate: {
          type: 'string',
          description: 'Custom speed adjustment (e.g. "+10%", "-15%", "+0%")'
        },
        pitch: {
          type: 'string',
          description: 'Custom pitch adjustment (e.g. "+5Hz", "-10Hz", "+0Hz")'
        },
        volume: {
          type: 'string',
          description: 'Custom volume adjustment (e.g. "+10%", "-5%", "+0%")'
        }
      },
      required: ['text', 'output_path']
    },
    handler: async (args: any) => {
      const result = await NeuralSpeechEngine.synthesizeSpeech({
        text: args.text,
        outputPath: args.output_path,
        voice: args.voice,
        emotionPreset: args.emotion_preset as EmotionPreset,
        rate: args.rate,
        pitch: args.pitch,
        volume: args.volume
      });

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: result.status,
            message: `Neural audio synthesized (${result.engineUsed})`,
            file_path: result.filePath,
            duration_seconds: result.durationSeconds,
            sample_rate: `${result.sampleRate.toLocaleString()} Hz`,
            channels: result.channels === 1 ? 'Mono' : 'Stereo',
            bit_depth: result.bitDepth,
            normalization: result.normalization,
            voice_used: result.voiceUsed,
            engine_used: result.engineUsed,
            ready_for_character_animator: result.readyForLipSync
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'audio_export_lip_sync_markers',
    description: 'Generates timeline marker tracks matching Character Animator mouth visemes (Ah, Ee, Oh, W-Oo, F, L, M, D, S, etc.) exported as After Effects ExtendScript (.jsx), JSON Cue Sheet, or Premiere/Audition CSV marker list.',
    inputSchema: {
      type: 'object',
      properties: {
        text: {
          type: 'string',
          description: 'Dialogue or script corresponding to the audio'
        },
        output_path: {
          type: 'string',
          description: 'Target base output path (e.g. "F:/Projects/Markers/character_dialogue_cues")'
        },
        audio_path: {
          type: 'string',
          description: 'Optional path to existing .wav audio file to calibrate viseme durations precisely against actual audio length'
        },
        fps: {
          type: 'number',
          description: 'Composition frame rate for frame-accurate alignment (default: 24)'
        },
        format: {
          type: 'string',
          enum: ['json', 'after_effects_jsx', 'csv_markers', 'all'],
          description: 'Export format: "after_effects_jsx" (creates markers via JSX), "json" (data cue sheet), "csv_markers" (Premiere/Audition format), or "all" (default: "all")'
        }
      },
      required: ['text', 'output_path']
    },
    handler: async (args: any) => {
      const result = NeuralSpeechEngine.exportLipSyncMarkers(args.text, args.output_path, {
        audioPath: args.audio_path,
        fps: args.fps || 24,
        format: args.format || 'all'
      });

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: result.status,
            message: 'Lip-sync timeline markers generated successfully',
            fps: result.fps,
            duration_seconds: result.durationSeconds,
            total_cues: result.totalCues,
            exported_files: {
              json: result.jsonPath || null,
              after_effects_jsx: result.jsxPath || null,
              csv_markers: result.csvPath || null
            },
            sample_cues: result.cues.slice(0, 5)
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'audio_list_available_voices',
    description: 'Lists available high-quality neural voices from Microsoft Edge-TTS with regional accents (Mexico, Spain, Colombia, Argentina, US, UK, Japan, etc.) and friendly aliases.',
    inputSchema: {
      type: 'object',
      properties: {
        language_filter: {
          type: 'string',
          description: 'Filter by language code (e.g. "es" for Spanish, "en" for English, "ja" for Japanese, or "all")'
        }
      }
    },
    handler: async (args: any) => {
      const voices = await NeuralSpeechEngine.listVoices(args.language_filter || 'es');
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            filter: args.language_filter || 'es',
            total_found: voices.length,
            built_in_aliases: NeuralSpeechEngine.VOICE_ALIASES,
            voices: voices.slice(0, 30) // Cap sample listing for readable response
          }, null, 2)
        }]
      };
    }
  }
];
