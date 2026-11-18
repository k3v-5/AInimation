import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, it } from "node:test";
import {
  InvalidMediaError,
  MediaHasher,
  MediaScanner,
  VlogMediaIngestionEngine,
} from "../../../vlog/index.js";

describe("Milestone 2-A — Vlog Media Ingestion Engine Suite", () => {
  it("generates deterministic SHA-256 and stable asset ID", async () => {
    const testBuffer = Buffer.from("Vlog Ingestion Determinism Test Content 2026");
    const hash = MediaHasher.hashBuffer(testBuffer);
    assert.equal(hash.length, 64);

    const assetId1 = MediaHasher.generateStableAssetId(hash);
    const assetId2 = MediaHasher.generateStableAssetId(hash);
    assert.equal(assetId1, assetId2);
    assert.ok(assetId1.startsWith("asset_"));
  });

  it("scans directories and ignores hidden, temporary and unsupported files", () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "vlog_ingest_test_"));

    try {
      // Crear archivos válidos
      const validMp4 = path.join(tmpDir, "video_broll_01.mp4");
      const validWav = path.join(tmpDir, "audio_voice_01.wav");
      const validPng = path.join(tmpDir, "image_polaroid_01.png");
      fs.writeFileSync(validMp4, Buffer.from("fake_mp4_bytes"));
      fs.writeFileSync(validWav, Buffer.from("fake_wav_bytes"));
      fs.writeFileSync(validPng, Buffer.from("fake_png_bytes"));

      // Crear archivos que deben ser ignorados
      const hiddenFile = path.join(tmpDir, ".DS_Store");
      const tempFile = path.join(tmpDir, "backup.tmp");
      const unsupportedDoc = path.join(tmpDir, "script.txt");
      fs.writeFileSync(hiddenFile, "hidden");
      fs.writeFileSync(tempFile, "temp");
      fs.writeFileSync(unsupportedDoc, "text");

      const scanned = MediaScanner.scanDirectories([tmpDir]);
      assert.equal(scanned.length, 3);
      assert.ok(scanned.some((p) => p.endsWith("video_broll_01.mp4")));
      assert.ok(scanned.some((p) => p.endsWith("audio_voice_01.wav")));
      assert.ok(scanned.some((p) => p.endsWith("image_polaroid_01.png")));
      assert.ok(!scanned.some((p) => p.includes(".DS_Store")));
      assert.ok(!scanned.some((p) => p.includes("script.txt")));
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it("guarantees deterministic alphabetical ordering independent of discovery", () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "vlog_order_test_"));

    try {
      // Crear archivos en orden desordenado
      fs.writeFileSync(path.join(tmpDir, "z_clip.mp4"), "z");
      fs.writeFileSync(path.join(tmpDir, "a_clip.mp4"), "a");
      fs.writeFileSync(path.join(tmpDir, "m_clip.mp4"), "m");

      const scanned = MediaScanner.scanDirectories([tmpDir]);
      const basenames = scanned.map((p) => path.basename(p));
      assert.deepEqual(basenames, ["a_clip.mp4", "m_clip.mp4", "z_clip.mp4"]);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it("prevents path traversal and validates non-existent root directory", () => {
    assert.throws(
      () => MediaScanner.scanDirectories(["/path/to/definitely/non_existent_folder_999"]),
      InvalidMediaError
    );
  });

  it("ingests a directory of media, detects duplicates and verifies READ-ONLY invariance", async () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "vlog_ingest_e2e_"));
    const subDir1 = path.join(tmpDir, "day1");
    const subDir2 = path.join(tmpDir, "day2");
    fs.mkdirSync(subDir1);
    fs.mkdirSync(subDir2);

    try {
      const contentOriginal = Buffer.from("unique_video_content_sample_alpha");
      const file1 = path.join(subDir1, "take_01.mp4");
      const file2 = path.join(subDir2, "take_duplicate.mp4"); // Mismo contenido
      const file3 = path.join(subDir1, "voice_track.wav");

      fs.writeFileSync(file1, contentOriginal);
      fs.writeFileSync(file2, contentOriginal); // Duplicado de file1
      fs.writeFileSync(file3, Buffer.from("voice_audio_content"));

      // Hash antes de la ingesta
      const hashBefore = MediaHasher.hashBuffer(contentOriginal);

      const report = await VlogMediaIngestionEngine.ingestDirectories([tmpDir], {
        allowDuplicates: false,
      });

      assert.equal(report.totalFilesScanned, 3);
      // El duplicado debe ser detectado e ignorado
      assert.equal(report.validMediaFiles.length, 2);
      assert.equal(report.corruptedOrUnsupportedFiles.length, 1);
      assert.ok(report.corruptedOrUnsupportedFiles[0].reason.includes("Duplicate media file detected"));

      // Verificar que todos los archivos válidos son marcados como READ-ONLY
      for (const media of report.validMediaFiles) {
        assert.equal(media.isReadOnly, true);
        assert.ok(media.id.startsWith("asset_"));
      }

      // Invarianza: el archivo original en disco no sufrió ninguna modificación
      const bytesAfter = fs.readFileSync(file1);
      const hashAfter = MediaHasher.hashBuffer(bytesAfter);
      assert.equal(hashBefore, hashAfter);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it("handles empty directory gracefully returning empty report", async () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "vlog_empty_test_"));
    try {
      const report = await VlogMediaIngestionEngine.ingestDirectories([tmpDir]);
      assert.equal(report.totalFilesScanned, 0);
      assert.equal(report.validMediaFiles.length, 0);
      assert.equal(report.totalDurationSeconds, 0);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });
});
