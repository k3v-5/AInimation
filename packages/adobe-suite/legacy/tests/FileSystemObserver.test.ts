import { test, expect, describe } from 'vitest';
import { FileSystemObserver } from '../src/core/FileSystemObserver.js';
import fs from 'fs';
import path from 'path';
import os from 'os';

describe('FileSystemObserver (Real Perception)', () => {
  test('Returns false if file never stabilizes or never appears', async () => {
    const observer = new FileSystemObserver();
    const mockFilePath = path.join(os.tmpdir(), "fake_file_" + Date.now() + ".mp4");

    const result = await observer.waitForFileStabilization(mockFilePath, 100, 500, 2);
    expect(result).toBe(false);
  });

  test('Returns true when a file exists and stabilizes', async () => {
    const observer = new FileSystemObserver();
    const mockFilePath = path.join(os.tmpdir(), "real_file_" + Date.now() + ".mp4");

    // Create the file so it exists and has a size
    fs.writeFileSync(mockFilePath, 'mock data');

    const result = await observer.waitForFileStabilization(mockFilePath, 100, 1000, 2);
    expect(result).toBe(true);

    // Cleanup
    if (fs.existsSync(mockFilePath)) {
      fs.unlinkSync(mockFilePath);
    }
  });
});