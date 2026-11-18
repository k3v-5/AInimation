import { describe, it, expect, afterAll } from 'vitest';
import { WavGenerator } from '../src/core/WavGenerator.js';
import { NeuralSpeechEngine } from '../src/core/NeuralSpeechEngine.js';
import fs from 'fs';
import path from 'path';
import os from 'os';

describe('WavGenerator & NeuralSpeechEngine (Phase 4)', () => {
  const testWavPath = path.join(os.tmpdir(), `test_audio_${Date.now()}.wav`);
  const testNeuralPath = path.join(os.tmpdir(), `test_neural_${Date.now()}.wav`);
  const testMarkerDir = path.join(os.tmpdir(), `test_markers_${Date.now()}`);

  afterAll(() => {
    try { if (fs.existsSync(testWavPath)) fs.unlinkSync(testWavPath); } catch {}
    try { if (fs.existsSync(testNeuralPath)) fs.unlinkSync(testNeuralPath); } catch {}
    try { if (fs.existsSync(testMarkerDir)) fs.rmSync(testMarkerDir, { recursive: true, force: true }); } catch {}
  });

  it('generates a clean 48kHz 16-bit PCM WAV container with valid RIFF headers', () => {
    const filePath = WavGenerator.createCleanPcmWav(testWavPath, 0.5);

    expect(fs.existsSync(filePath)).toBe(true);
    const buffer = fs.readFileSync(filePath);

    // Verify RIFF header
    expect(buffer.toString('utf8', 0, 4)).toBe('RIFF');
    expect(buffer.toString('utf8', 8, 12)).toBe('WAVE');
    expect(buffer.toString('utf8', 12, 16)).toBe('fmt ');

    // Subchunk1Size = 16
    expect(buffer.readUInt32LE(16)).toBe(16);
    // AudioFormat = 1 (PCM)
    expect(buffer.readUInt16LE(20)).toBe(1);
    // NumChannels = 1 (Mono)
    expect(buffer.readUInt16LE(22)).toBe(1);
    // SampleRate = 48000 Hz
    expect(buffer.readUInt32LE(24)).toBe(48000);
    // BitsPerSample = 16
    expect(buffer.readUInt16LE(34)).toBe(16);

    // data chunk
    expect(buffer.toString('utf8', 36, 40)).toBe('data');
    expect(buffer.readUInt32LE(40)).toBeGreaterThan(0);
  });

  it('estimates viseme cues from dialogue text accurately', () => {
    const cues = WavGenerator.estimateVisemeCues('Hello world, animation engine online');

    expect(cues.length).toBeGreaterThan(0);
    expect(cues[0].viseme).toBeDefined();
    expect(cues[0].durationSeconds).toBeGreaterThan(0);
    expect(cues[cues.length - 1].timeSeconds).toBeGreaterThan(0);
  });

  it('resolves voice aliases correctly', () => {
    expect(NeuralSpeechEngine.resolveVoice('mexico_female')).toBe('es-MX-DaliaNeural');
    expect(NeuralSpeechEngine.resolveVoice('spain_male')).toBe('es-ES-AlvaroNeural');
    expect(NeuralSpeechEngine.resolveVoice('us_female')).toBe('en-US-JennyNeural');
    expect(NeuralSpeechEngine.resolveVoice('custom_voice')).toBe('custom_voice');
  });

  it('synthesizes neural 48kHz 16-bit mono speech via NeuralSpeechEngine', async () => {
    const res = await NeuralSpeechEngine.synthesizeSpeech({
      text: 'Animación en tiempo real con Adobe Character Animator.',
      outputPath: testNeuralPath,
      voice: 'mexico_female',
      emotionPreset: 'cheerful'
    });

    expect(res.status).toBe('SUCCESS');
    expect(res.sampleRate).toBe(48000);
    expect(res.channels).toBe(1);
    expect(res.bitDepth).toBe('16-bit PCM');
    expect(res.readyForLipSync).toBe(true);
    expect(fs.existsSync(testNeuralPath)).toBe(true);

    const buf = fs.readFileSync(testNeuralPath);
    expect(buf.toString('utf8', 0, 4)).toBe('RIFF');
    expect(buf.readUInt32LE(24)).toBe(48000); // 48kHz
    expect(buf.readUInt16LE(22)).toBe(1);     // Mono
  }, 15000);

  it('generates frame-accurate viseme cues and exports multi-format markers', () => {
    const markerBasePath = path.join(testMarkerDir, 'test_dialogue');
    const res = NeuralSpeechEngine.exportLipSyncMarkers(
      'Hola mundo! Bienvenidos al motor de animación.',
      markerBasePath,
      { fps: 24, format: 'all' }
    );

    expect(res.status).toBe('SUCCESS');
    expect(res.totalCues).toBeGreaterThan(0);
    expect(res.fps).toBe(24);
    expect(res.cues.some(c => c.viseme === 'Ah' || c.viseme === 'Ee' || c.viseme === 'Oh')).toBe(true);

    // Verify files created
    expect(fs.existsSync(res.jsonPath!)).toBe(true);
    expect(fs.existsSync(res.jsxPath!)).toBe(true);
    expect(fs.existsSync(res.csvPath!)).toBe(true);

    // Validate JSON structure
    const jsonContent = JSON.parse(fs.readFileSync(res.jsonPath!, 'utf-8'));
    expect(jsonContent.metadata.generator).toContain('AdobeEngineSuit');
    expect(jsonContent.cues.length).toBe(res.totalCues);

    // Validate JSX ExtendScript content
    const jsxContent = fs.readFileSync(res.jsxPath!, 'utf-8');
    expect(jsxContent).toContain('app.beginUndoGroup("Import Character Viseme Markers")');
    expect(jsxContent).toContain('new MarkerValue');

    // Validate CSV marker content
    const csvContent = fs.readFileSync(res.csvPath!, 'utf-8');
    expect(csvContent).toContain('Marker Name\tDescription\tIn\tOut\tDuration\tMarker Type');
  });

  it('lists available neural voices', async () => {
    const voices = await NeuralSpeechEngine.listVoices('es');
    expect(voices.length).toBeGreaterThan(0);
    expect(voices[0].name).toBeDefined();
    expect(voices[0].locale).toMatch(/^es/i);
  }, 15000);
});
