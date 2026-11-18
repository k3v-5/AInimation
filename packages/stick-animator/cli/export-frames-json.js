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

export async function exportFramesJson(stykPath, outputPath) {
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

  const output = {
    canvas_width: canvasWidth,
    canvas_height: canvasHeight,
    fps: fps,
    total_frames: totalFrames,
    frames: framesData
  };

  await writeFile(outputPath, JSON.stringify(output), 'utf-8');
  console.log(`Exported ${totalFrames} frames to ${outputPath}`);
}

const input = process.argv[2] || path.join(__dirname, 'cyber_samurai.styk');
const out = process.argv[3] || path.join(__dirname, 'frames.json');
exportFramesJson(input, out).catch(console.error);
