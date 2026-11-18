import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

export interface AppInfo {
  installed: boolean;
  path: string | null;
  version?: string;
}

export interface EnvironmentStatus {
  characterAnimator: AppInfo;
  illustrator: AppInfo;
  afterEffects: AppInfo;
  aerender: AppInfo;
  mediaEncoder: AppInfo;
  blender: AppInfo;
}

export class AdobeDetector {
  private static findFirstExisting(candidates: string[]): string | null {
    for (const candidate of candidates) {
      try {
        if (candidate.includes('*')) {
          // Glob matching on parent directory
          const dir = path.dirname(candidate);
          const basePattern = path.basename(candidate);
          if (fs.existsSync(dir)) {
            const files = fs.readdirSync(dir);
            const regex = new RegExp('^' + basePattern.replace(/\*/g, '.*') + '$', 'i');
            const match = files.find(f => regex.test(f));
            if (match) {
              const fullMatch = path.join(dir, match);
              if (fs.existsSync(fullMatch)) return fullMatch;
            }
          }
        } else if (fs.existsSync(candidate)) {
          return candidate;
        }
      } catch {
        // Ignore permission or stat errors
      }
    }
    return null;
  }

  public static getCharacterAnimatorPath(): string | null {
    const searchPaths = [
      'F:/Adobe/Adobe Character Animator 2026/Support Files/Character Animator.exe',
      'F:/Adobe/Adobe Character Animator 2025/Support Files/Character Animator.exe',
      'F:/Adobe/Adobe Character Animator 2024/Support Files/Character Animator.exe',
      'C:/Program Files/Adobe/Adobe Character Animator 2026/Support Files/Character Animator.exe',
      'C:/Program Files/Adobe/Adobe Character Animator 2025/Support Files/Character Animator.exe',
      'C:/Program Files/Adobe/Adobe Character Animator 2024/Support Files/Character Animator.exe',
      'D:/Adobe/Adobe Character Animator 2026/Support Files/Character Animator.exe',
      'E:/Adobe/Adobe Character Animator 2026/Support Files/Character Animator.exe'
    ];
    return this.findFirstExisting(searchPaths);
  }

  public static getIllustratorPath(): string | null {
    const searchPaths = [
      'F:/Adobe/Adobe Illustrator 2026/Support Files/Contents/Windows/Illustrator.exe',
      'C:/Program Files/Adobe/Adobe Illustrator 2026/Support Files/Contents/Windows/Illustrator.exe',
      'C:/Program Files/Adobe/Adobe Illustrator 2025/Support Files/Contents/Windows/Illustrator.exe',
      'C:/Program Files/Adobe/Adobe Illustrator 2024/Support Files/Contents/Windows/Illustrator.exe',
      'D:/Adobe/Adobe Illustrator 2026/Support Files/Contents/Windows/Illustrator.exe'
    ];
    return this.findFirstExisting(searchPaths);
  }

  public static getAfterEffectsPath(): string | null {
    const searchPaths = [
      'F:/Adobe/Adobe After Effects 2026/Support Files/AfterFX.exe',
      'C:/Program Files/Adobe/Adobe After Effects 2026/Support Files/AfterFX.exe',
      'C:/Program Files/Adobe/Adobe After Effects 2025/Support Files/AfterFX.exe',
      'C:/Program Files/Adobe/Adobe After Effects 2024/Support Files/AfterFX.exe',
      'D:/Adobe/Adobe After Effects 2026/Support Files/AfterFX.exe'
    ];
    return this.findFirstExisting(searchPaths);
  }

  public static getAerenderPath(): string | null {
    const searchPaths = [
      'F:/Adobe/Adobe After Effects 2026/Support Files/aerender.exe',
      'C:/Program Files/Adobe/Adobe After Effects 2026/Support Files/aerender.exe',
      'C:/Program Files/Adobe/Adobe After Effects 2025/Support Files/aerender.exe',
      'C:/Program Files/Adobe/Adobe After Effects 2024/Support Files/aerender.exe',
      'D:/Adobe/Adobe After Effects 2026/Support Files/aerender.exe'
    ];
    return this.findFirstExisting(searchPaths);
  }

  public static getMediaEncoderPath(): string | null {
    const searchPaths = [
      'F:/Adobe/Adobe Media Encoder 2026/Adobe Media Encoder.exe',
      'C:/Program Files/Adobe/Adobe Media Encoder 2026/Adobe Media Encoder.exe',
      'C:/Program Files/Adobe/Adobe Media Encoder 2025/Adobe Media Encoder.exe',
      'C:/Program Files/Adobe/Adobe Media Encoder 2024/Adobe Media Encoder.exe'
    ];
    return this.findFirstExisting(searchPaths);
  }

  public static getBlenderPath(): string | null {
    const searchPaths = [
      'E:/Blender/blender.exe',
      'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe',
      'C:/Program Files/Blender Foundation/Blender 4.3/blender.exe',
      'C:/Program Files/Blender Foundation/Blender 4.2/blender.exe',
      'D:/Blender/blender.exe'
    ];
    const directPath = this.findFirstExisting(searchPaths);
    if (directPath) return directPath;

    // Check PATH
    try {
      const output = execSync('where blender', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
      if (output && fs.existsSync(output.split('\n')[0].trim())) {
        return output.split('\n')[0].trim();
      }
    } catch {
      // not in PATH
    }
    return null;
  }

  public static getStatus(): EnvironmentStatus {
    const chPath = this.getCharacterAnimatorPath();
    const aiPath = this.getIllustratorPath();
    const aePath = this.getAfterEffectsPath();
    const aerenderPath = this.getAerenderPath();
    const amePath = this.getMediaEncoderPath();
    const blenderPath = this.getBlenderPath();

    return {
      characterAnimator: { installed: !!chPath, path: chPath },
      illustrator: { installed: !!aiPath, path: aiPath },
      afterEffects: { installed: !!aePath, path: aePath },
      aerender: { installed: !!aerenderPath, path: aerenderPath },
      mediaEncoder: { installed: !!amePath, path: amePath },
      blender: { installed: !!blenderPath, path: blenderPath }
    };
  }
}
