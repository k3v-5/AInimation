import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  InvalidWavError,
  WavValidator,
} from "../../../vlog/index.js";

describe("Milestone 4 — WAV Validator & Binary Header Suite", () => {
  it("validates canonical PCM 16-bit 44.1kHz mono WAV buffers", () => {
    // 1 segundo de audio = 44100 muestras
    const samples = new Int16Array(44100);
    for (let i = 0; i < samples.length; i++) {
      samples[i] = Math.floor(Math.sin((2 * Math.PI * 440 * i) / 44100) * 10000);
    }

    const wavBuf = WavValidator.createCanonicalWav(samples);
    const meta = WavValidator.validateBuffer(wavBuf, true);

    assert.equal(meta.sampleRate, 44100);
    assert.equal(meta.channels, 1);
    assert.equal(meta.bitDepth, 16);
    assert.equal(meta.isCanonical, true);
    assert.equal(meta.durationSeconds, 1.0);
    assert.equal(meta.dataSizeBytes, 44100 * 2);
  });

  it("rejects truncated buffer smaller than 44 bytes with InvalidWavError", () => {
    const tinyBuffer = Buffer.alloc(30);
    assert.throws(() => WavValidator.validateBuffer(tinyBuffer), InvalidWavError);
  });

  it("rejects buffer with corrupted RIFF header", () => {
    const fakeBuf = Buffer.alloc(100);
    fakeBuf.write("NOPE", 0, "ascii");
    assert.throws(() => WavValidator.validateBuffer(fakeBuf), InvalidWavError);
  });

  it("rejects non-canonical sample rate when enforceCanonical is true", () => {
    // Crear WAV con 48000 Hz manipulando el header
    const samples = new Int16Array(1000);
    const wavBuf = WavValidator.createCanonicalWav(samples);
    wavBuf.writeUInt32LE(48000, 24); // Alterar sampleRate en fmt subchunk

    assert.throws(
      () => WavValidator.validateBuffer(wavBuf, true),
      InvalidWavError
    );

    // Con enforceCanonical=false debe permitir leer los metadatos reales
    const meta = WavValidator.validateBuffer(wavBuf, false);
    assert.equal(meta.sampleRate, 48000);
    assert.equal(meta.isCanonical, false);
  });

  it("PBT: canonical WAV duration matches exactly (sampleCount / 44100)", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 100, max: 44100 * 3 }),
        (sampleCount) => {
          const samples = new Int16Array(sampleCount);
          const wavBuf = WavValidator.createCanonicalWav(samples);
          const meta = WavValidator.validateBuffer(wavBuf, true);

          const expectedDuration = Number((sampleCount / 44100).toFixed(4));
          assert.equal(meta.durationSeconds, expectedDuration);
        }
      )
    );
  });
});
