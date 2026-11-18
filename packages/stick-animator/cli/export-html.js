import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const mcpRoot = path.join(__dirname, 'stykanimate-mcp');

const { readSourceFile, readDocument } = await import(
  pathToFileURL(path.join(mcpRoot, 'src', 'documents.js')).href
);
const { Editor } = await import(
  pathToFileURL(path.join(mcpRoot, 'src', 'core.js')).href
);

export async function exportToHtml(stykPath, outputPath) {
  const file = await readSourceFile(stykPath);
  const doc = await readDocument({ bytes: file.bytes, filename: file.path });

  const editor = new Editor({ demo: false });
  editor.load(doc.document);

  const totalFrames = Math.max(1, editor.totalTicks || doc.document.total_output_frames || (doc.document.keyframes?.length ?? 1));
  const fps = doc.document.fps || 24;
  const canvasWidth = doc.document.canvas_width || 960;
  const canvasHeight = doc.document.canvas_height || 540;

  const framesData = [];
  for (let t = 0; t < totalFrames; t++) {
    editor.seek(t);
    const drawables = (editor.geometry.drawables || []).map(d => ({
      type: d.type,
      points: d.points ? d.points.map(p => ({ x: Math.round(p.x * 10) / 10, y: Math.round(p.y * 10) / 10 })) : null,
      start: d.start ? { x: Math.round(d.start.x * 10) / 10, y: Math.round(d.start.y * 10) / 10 } : null,
      end: d.end ? { x: Math.round(d.end.x * 10) / 10, y: Math.round(d.end.y * 10) / 10 } : null,
      length: d.length ? Math.round(d.length * 10) / 10 : 0,
      thickness: d.thickness ? Math.round(d.thickness * 10) / 10 : 6,
      rgb: d.rgb || [200, 200, 200],
      alpha: d.alpha ?? 1,
      z: d.z || 0,
      code: d.seg?.primitive_code ?? 0,
    }));
    drawables.sort((a, b) => a.z - b.z);
    framesData.push(drawables);
  }

  const html = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>StykAnimate Pro Player - ${path.basename(stykPath)}</title>
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
      padding: 24px;
      box-sizing: border-box;
    }
    .player-card {
      background: #1a1e2d;
      border: 1px solid #2d3748;
      border-radius: 16px;
      box-shadow: 0 12px 40px rgba(0,0,0,0.6);
      padding: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      max-width: 1000px;
      width: 100%;
    }
    canvas {
      background: #141622;
      border-radius: 10px;
      box-shadow: inset 0 2px 12px rgba(0,0,0,0.7);
      max-width: 100%;
      height: auto;
    }
    .controls {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-top: 18px;
      width: 100%;
    }
    button {
      background: #3b82f6;
      color: #ffffff;
      border: none;
      border-radius: 8px;
      padding: 10px 20px;
      font-weight: 600;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.2s;
    }
    button:hover {
      background: #60a5fa;
      transform: translateY(-1px);
    }
    .timeline {
      flex: 1;
      height: 6px;
      accent-color: #3b82f6;
      cursor: pointer;
    }
    .meta-info {
      font-size: 13px;
      color: #94a3b8;
      display: flex;
      justify-content: space-between;
      width: 100%;
      margin-top: 12px;
      padding-top: 8px;
      border-top: 1px solid #262f40;
    }
    .badge {
      background: #2563eb33;
      color: #60a5fa;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <div class="player-card">
    <canvas id="c" width="${canvasWidth}" height="${canvasHeight}"></canvas>
    <div class="controls">
      <button id="playBtn">Pause</button>
      <input type="range" id="seek" class="timeline" min="0" max="${totalFrames - 1}" value="0">
      <span id="frameCounter" style="font-family: monospace; font-size: 14px;">0 / ${totalFrames - 1}</span>
    </div>
    <div class="meta-info">
      <span>Animación: <b>${path.basename(stykPath)}</b> (${canvasWidth}x${canvasHeight} @ ${fps} FPS)</span>
      <span class="badge">StykAnimate Advanced Rig & Polyfills</span>
    </div>
  </div>

  <script>
    const frames = ${JSON.stringify(framesData)};
    const fps = ${fps};
    const totalFrames = ${totalFrames};
    const canvas = document.getElementById('c');
    const ctx = canvas.getContext('2d');
    const playBtn = document.getElementById('playBtn');
    const seek = document.getElementById('seek');
    const frameCounter = document.getElementById('frameCounter');

    let currentFrame = 0;
    let playing = true;
    let lastTime = performance.now();
    const frameInterval = 1000 / fps;

    function renderFrame(index) {
      const drawables = frames[index];
      if (!drawables) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (const d of drawables) {
        const col = 'rgba(' + d.rgb[0] + ',' + d.rgb[1] + ',' + d.rgb[2] + ',' + (d.alpha ?? 1) + ')';
        ctx.fillStyle = col;
        ctx.strokeStyle = col;
        ctx.lineWidth = d.thickness || 6;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        if (d.type === 'poly' && d.points && d.points.length >= 3) {
          ctx.beginPath();
          ctx.moveTo(d.points[0].x, d.points[0].y);
          for (let i = 1; i < d.points.length; i++) ctx.lineTo(d.points[i].x, d.points[i].y);
          ctx.closePath();
          ctx.fill();
        } else if (d.type === 'circle') {
          const r = (d.length || d.thickness || 20) / 2;
          const center = d.end || (d.points && d.points[1]) || d.start;
          if (center) {
            ctx.beginPath();
            ctx.arc(center.x, center.y, Math.max(1, r), 0, Math.PI * 2);
            if (d.code === 3) { // circleFill
              ctx.fill();
            } else { // circle line
              ctx.stroke();
            }
          }
        } else if (d.type === 'line') {
          ctx.beginPath();
          if (d.points && d.points.length > 2) {
            ctx.moveTo(d.points[0].x, d.points[0].y);
            for (let i = 1; i < d.points.length; i++) ctx.lineTo(d.points[i].x, d.points[i].y);
          } else if (d.start && d.end) {
            ctx.moveTo(d.start.x, d.start.y);
            ctx.lineTo(d.end.x, d.end.y);
          }
          ctx.stroke();
        }
      }

      seek.value = index;
      frameCounter.innerText = index + ' / ' + (totalFrames - 1);
    }

    function loop(time) {
      if (playing) {
        const delta = time - lastTime;
        if (delta >= frameInterval) {
          lastTime = time - (delta % frameInterval);
          currentFrame = (currentFrame + 1) % totalFrames;
          renderFrame(currentFrame);
        }
      }
      requestAnimationFrame(loop);
    }

    playBtn.addEventListener('click', () => {
      playing = !playing;
      playBtn.innerText = playing ? 'Pause' : 'Play';
    });

    seek.addEventListener('input', (e) => {
      currentFrame = parseInt(e.target.value, 10);
      renderFrame(currentFrame);
    });

    renderFrame(0);
    requestAnimationFrame(loop);
  </script>
</body>
</html>`;

  await writeFile(outputPath, html, 'utf-8');
  console.log(`Exported player HTML to ${outputPath}`);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  const input = process.argv[2] || path.join(mcpRoot, 'assets', 'python-vs-java.styk');
  const output = process.argv[3] || path.join(__dirname, 'preview.html');
  exportToHtml(input, output);
}
