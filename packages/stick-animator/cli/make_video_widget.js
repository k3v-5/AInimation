import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

async function main() {
  const videoBuffer = await readFile(path.join('F:', 'Dev', 'StictAnimator', 'cyber_samurai.mp4'));
  const b64 = videoBuffer.toString('base64');
  const html = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Cyber Samurai MP4 Video</title>
  <style>
    body {
      margin: 0;
      background: #0f111a;
      color: #e2e8f0;
      font-family: system-ui, -apple-system, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 16px;
      box-sizing: border-box;
    }
    .video-card {
      background: #1a1e2d;
      border: 1px solid #2d3748;
      border-radius: 14px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.6);
      padding: 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
      max-width: 980px;
      width: 100%;
    }
    video {
      border-radius: 8px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.5);
      max-width: 100%;
      height: auto;
      background: #000;
    }
    .footer {
      display: flex;
      justify-content: space-between;
      width: 100%;
      margin-top: 12px;
      font-size: 13px;
      color: #94a3b8;
    }
    .badge {
      background: #10b98122;
      color: #34d399;
      padding: 3px 10px;
      border-radius: 6px;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="video-card">
    <video controls autoplay loop playsinline>
      <source src="data:video/mp4;base64,${b64}" type="video/mp4">
      Tu navegador no soporta reproducción de video MP4.
    </video>
    <div class="footer">
      <span>Archivo: <b>cyber_samurai.mp4</b> (960x540 @ 24 FPS • 211 KB)</span>
      <span class="badge">MP4 Renderizado Nativo</span>
    </div>
  </div>
</body>
</html>`;

  const dest = 'C:/Users/sasuk/.gemini/antigravity/brain/1349b18c-0fb4-45d4-8dc6-e1fd918fd7c3/video_player_widget.html';
  await writeFile(dest, html, 'utf-8');
  console.log(`Video widget written to ${dest}`);
}

main().catch(console.error);
