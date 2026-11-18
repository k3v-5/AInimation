import { VisemeName } from './PuppetBuilder.js';

export interface PixelData {
  width: number;
  height: number;
  data: Uint8Array;
}

export class VisemeDrawer {
  /**
   * Generates custom, visually distinct RGBA pixel graphics for each of the 14 Character Animator visemes.
   * Dimensions: 140px width x 80px height per viseme.
   */
  public static drawViseme(viseme: VisemeName, width: number = 140, height: number = 80): PixelData {
    const data = new Uint8Array(width * height * 4);

    const setPixel = (x: number, y: number, r: number, g: number, b: number, a: number = 255) => {
      if (x < 0 || x >= width || y < 0 || y >= height) return;
      const idx = (y * width + x) * 4;
      data[idx] = r;
      data[idx + 1] = g;
      data[idx + 2] = b;
      data[idx + 3] = a;
    };

    const fillEllipse = (cx: number, cy: number, rx: number, ry: number, r: number, g: number, b: number, a: number = 255) => {
      for (let y = Math.max(0, Math.floor(cy - ry)); y <= Math.min(height - 1, Math.ceil(cy + ry)); y++) {
        for (let x = Math.max(0, Math.floor(cx - rx)); x <= Math.min(width - 1, Math.ceil(cx + rx)); x++) {
          const dx = (x - cx) / rx;
          const dy = (y - cy) / ry;
          if (dx * dx + dy * dy <= 1) {
            setPixel(x, y, r, g, b, a);
          }
        }
      }
    };

    const fillRect = (x0: number, y0: number, w: number, h: number, r: number, g: number, b: number, a: number = 255) => {
      for (let y = y0; y < y0 + h && y < height; y++) {
        for (let x = x0; x < x0 + w && x < width; x++) {
          setPixel(x, y, r, g, b, a);
        }
      }
    };

    const cx = Math.floor(width / 2);
    const cy = Math.floor(height / 2);

    const lipColor: [number, number, number] = [210, 60, 80];
    const mouthDark: [number, number, number] = [45, 15, 20];
    const teethColor: [number, number, number] = [245, 245, 250];
    const tongueColor: [number, number, number] = [235, 110, 130];

    switch (viseme) {
      case 'Neutral':
        // Closed relaxed mouth with slight smile curve
        fillEllipse(cx, cy, 35, 6, lipColor[0], lipColor[1], lipColor[2]);
        fillRect(cx - 30, cy - 1, 60, 2, mouthDark[0], mouthDark[1], mouthDark[2]);
        break;

      case 'Ah':
        // Large open vertical oval, visible teeth row on top, tongue at bottom
        fillEllipse(cx, cy, 30, 32, lipColor[0], lipColor[1], lipColor[2]);
        fillEllipse(cx, cy, 26, 28, mouthDark[0], mouthDark[1], mouthDark[2]);
        fillRect(cx - 20, cy - 24, 40, 10, teethColor[0], teethColor[1], teethColor[2]);
        fillEllipse(cx, cy + 18, 20, 12, tongueColor[0], tongueColor[1], tongueColor[2]);
        break;

      case 'Ee':
        // Wide smiling mouth showing upper & lower teeth rows
        fillEllipse(cx, cy, 50, 18, lipColor[0], lipColor[1], lipColor[2]);
        fillEllipse(cx, cy, 45, 14, mouthDark[0], mouthDark[1], mouthDark[2]);
        fillRect(cx - 35, cy - 12, 70, 9, teethColor[0], teethColor[1], teethColor[2]);
        fillRect(cx - 30, cy + 3, 60, 8, teethColor[0], teethColor[1], teethColor[2]);
        break;

      case 'Oh':
        // Deep round circle
        fillEllipse(cx, cy, 24, 24, lipColor[0], lipColor[1], lipColor[2]);
        fillEllipse(cx, cy, 18, 18, mouthDark[0], mouthDark[1], mouthDark[2]);
        fillEllipse(cx, cy + 10, 12, 6, tongueColor[0], tongueColor[1], tongueColor[2]);
        break;

      case 'W-Oo':
        // Tight pursed small circle
        fillEllipse(cx, cy, 14, 14, lipColor[0], lipColor[1], lipColor[2]);
        fillEllipse(cx, cy, 9, 9, mouthDark[0], mouthDark[1], mouthDark[2]);
        break;

      case 'F':
        // Upper teeth visibly resting on lower lip
        fillEllipse(cx, cy, 38, 14, lipColor[0], lipColor[1], lipColor[2]);
        fillEllipse(cx, cy, 34, 10, mouthDark[0], mouthDark[1], mouthDark[2]);
        fillRect(cx - 22, cy - 8, 44, 12, teethColor[0], teethColor[1], teethColor[2]);
        fillRect(cx - 26, cy + 3, 52, 6, lipColor[0], lipColor[1], lipColor[2]);
        break;

      case 'D':
        // Half-open mouth with tongue touching roof behind top teeth
        fillEllipse(cx, cy, 36, 20, lipColor[0], lipColor[1], lipColor[2]);
        fillEllipse(cx, cy, 32, 16, mouthDark[0], mouthDark[1], mouthDark[2]);
        fillRect(cx - 22, cy - 12, 44, 8, teethColor[0], teethColor[1], teethColor[2]);
        fillEllipse(cx, cy - 2, 16, 8, tongueColor[0], tongueColor[1], tongueColor[2]);
        break;

      case 'L':
        // Tongue clearly elevated in center
        fillEllipse(cx, cy, 34, 22, lipColor[0], lipColor[1], lipColor[2]);
        fillEllipse(cx, cy, 30, 18, mouthDark[0], mouthDark[1], mouthDark[2]);
        fillRect(cx - 24, cy - 14, 48, 8, teethColor[0], teethColor[1], teethColor[2]);
        fillEllipse(cx, cy - 2, 14, 14, tongueColor[0], tongueColor[1], tongueColor[2]);
        break;

      case 'M':
        // Pressed tight lips (solid line with thickness)
        fillEllipse(cx, cy, 32, 7, lipColor[0], lipColor[1], lipColor[2]);
        fillRect(cx - 28, cy - 1, 56, 2, mouthDark[0], mouthDark[1], mouthDark[2]);
        break;

      case 'R':
        // Moderately rounded mouth, subtle tooth bar
        fillEllipse(cx, cy, 28, 18, lipColor[0], lipColor[1], lipColor[2]);
        fillEllipse(cx, cy, 23, 14, mouthDark[0], mouthDark[1], mouthDark[2]);
        fillRect(cx - 16, cy - 10, 32, 6, teethColor[0], teethColor[1], teethColor[2]);
        break;

      case 'S':
        // Gritted teeth with narrow opening
        fillEllipse(cx, cy, 42, 14, lipColor[0], lipColor[1], lipColor[2]);
        fillEllipse(cx, cy, 38, 10, mouthDark[0], mouthDark[1], mouthDark[2]);
        fillRect(cx - 30, cy - 8, 60, 7, teethColor[0], teethColor[1], teethColor[2]);
        fillRect(cx - 28, cy, 56, 7, teethColor[0], teethColor[1], teethColor[2]);
        break;

      case 'Uh':
        // Relaxed open mouth
        fillEllipse(cx, cy, 32, 22, lipColor[0], lipColor[1], lipColor[2]);
        fillEllipse(cx, cy, 27, 17, mouthDark[0], mouthDark[1], mouthDark[2]);
        fillEllipse(cx, cy + 8, 18, 9, tongueColor[0], tongueColor[1], tongueColor[2]);
        break;

      case 'Smile':
        // Big open happy grin with curved bottom
        fillEllipse(cx, cy + 2, 46, 22, lipColor[0], lipColor[1], lipColor[2]);
        fillEllipse(cx, cy, 42, 18, mouthDark[0], mouthDark[1], mouthDark[2]);
        fillRect(cx - 32, cy - 14, 64, 10, teethColor[0], teethColor[1], teethColor[2]);
        fillEllipse(cx, cy + 10, 24, 10, tongueColor[0], tongueColor[1], tongueColor[2]);
        break;

      case 'Surprised':
        // Tall exaggerated vertical mouth
        fillEllipse(cx, cy, 22, 34, lipColor[0], lipColor[1], lipColor[2]);
        fillEllipse(cx, cy, 17, 29, mouthDark[0], mouthDark[1], mouthDark[2]);
        fillRect(cx - 12, cy - 22, 24, 8, teethColor[0], teethColor[1], teethColor[2]);
        break;
    }

    return { width, height, data };
  }
}
