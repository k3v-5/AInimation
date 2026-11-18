import assert from "node:assert/strict";
import { describe, it } from "node:test";
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import { MediaMetadataProbe } from "../../assets/core/MediaMetadataProbe.js";
import { AssetImporter } from "../../assets/importer/AssetImporter.js";

describe("Fase 5A / 5B — MediaMetadataProbe Duration & Binary Header Extraction Tests", () => {
  it("probes non-existent files gracefully without throwing", () => {
    const res = MediaMetadataProbe.probe("non_existent_file.mp4");
    assert.deepEqual(res, {});
  });

  it("extracts real WAV duration from binary header", () => {
    const tmpWav = path.join(os.tmpdir(), `test_probe_${Date.now()}.wav`);
    
    // Generate valid 1-second 44.1kHz 16-bit stereo WAV file
    const sampleRate = 44100;
    const numChannels = 2;
    const bitsPerSample = 16;
    const byteRate = sampleRate * numChannels * (bitsPerSample / 8); // 176400 B/s
    const blockAlign = numChannels * (bitsPerSample / 8);
    const dataSize = byteRate * 2; // 2 seconds of audio = 352800 bytes
    const totalSize = 44 + dataSize;

    const buf = Buffer.alloc(totalSize);
    buf.write("RIFF", 0);
    buf.writeUInt32LE(totalSize - 8, 4);
    buf.write("WAVE", 8);
    buf.write("fmt ", 12);
    buf.writeUInt32LE(16, 16); // Subchunk1Size
    buf.writeUInt16LE(1, 20);  // PCM format
    buf.writeUInt16LE(numChannels, 22);
    buf.writeUInt32LE(sampleRate, 24);
    buf.writeUInt32LE(byteRate, 28);
    buf.writeUInt16LE(blockAlign, 32);
    buf.writeUInt16LE(bitsPerSample, 34);
    buf.write("data", 36);
    buf.writeUInt32LE(dataSize, 40);

    fs.writeFileSync(tmpWav, buf);

    try {
      const probe = MediaMetadataProbe.probe(tmpWav);
      assert.equal(probe.sampleRate, 44100);
      assert.equal(probe.channels, 2);
      assert.ok(Math.abs((probe.duration ?? 0) - 2.0) < 0.05, `Expected ~2.0s, got ${probe.duration}`);

      const imported = AssetImporter.importFromPath(tmpWav);
      assert.equal(imported.type, "audio");
      assert.ok(imported.metadata !== undefined && Math.abs(Number(imported.metadata.duration) - 2.0) < 0.05);
    } finally {
      if (fs.existsSync(tmpWav)) fs.unlinkSync(tmpWav);
    }
  });

  it("extracts PNG image dimensions accurately", () => {
    const tmpPng = path.join(os.tmpdir(), `test_probe_${Date.now()}.png`);
    const buf = Buffer.alloc(32);
    buf.write("\x89PNG\r\n\x1a\n", 0);
    buf.writeUInt32BE(13, 8); // IHDR length
    buf.write("IHDR", 12);
    buf.writeUInt32BE(1080, 16); // Width: 1080
    buf.writeUInt32BE(1920, 20); // Height: 1920

    fs.writeFileSync(tmpPng, buf);

    try {
      const probe = MediaMetadataProbe.probe(tmpPng);
      assert.equal(probe.width, 1080);
      assert.equal(probe.height, 1920);
      assert.equal(probe.format, "png");

      const imported = AssetImporter.importFromPath(tmpPng);
      assert.ok(imported.metadata !== undefined);
      assert.equal(imported.metadata.width, 1080);
      assert.equal(imported.metadata.height, 1920);
    } finally {
      if (fs.existsSync(tmpPng)) fs.unlinkSync(tmpPng);
    }
  });
});
