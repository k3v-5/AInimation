import * as crypto from 'crypto';
import * as fs from 'fs';

/**
 * Computes a SHA-256 hash of a physical file.
 * Returns null if the file does not exist or an error occurs.
 */
export function calculateFileHash(filePath: string): string | null {
  if (!fs.existsSync(filePath)) {
    return null;
  }

  try {
    const fileBuffer = fs.readFileSync(filePath);
    const hashSum = crypto.createHash('sha256');
    hashSum.update(fileBuffer);
    return hashSum.digest('hex');
  } catch (err) {
    console.error(`Error calculating hash for file ${filePath}:`, err);
    return null;
  }
}
