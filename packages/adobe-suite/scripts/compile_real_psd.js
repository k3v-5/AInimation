import fs from 'fs';
import path from 'path';
import { writePsd } from 'ag-psd';

function convertManifestLayer(item) {
  const layer = {
    name: item.name,
    hidden: item.hidden || false,
    opened: item.opened !== undefined ? item.opened : true
  };

  if (item.rawPath && fs.existsSync(item.rawPath)) {
    const rawBuffer = fs.readFileSync(item.rawPath);
    layer.top = item.top;
    layer.left = item.left;
    layer.bottom = item.top + item.height;
    layer.right = item.left + item.width;
    layer.imageData = {
      width: item.width,
      height: item.height,
      data: new Uint8Array(rawBuffer)
    };
  }

  if (item.children && Array.isArray(item.children)) {
    layer.children = item.children.map(convertManifestLayer);
  }

  return layer;
}

async function main() {
  console.log('=== COMPILING ILLUSTRATED CHARACTER ANIMATOR PSD ===\n');

  const baseDir = path.resolve('f:/Dev/AdobeEngineSuit/showcase_animation');
  const manifestPath = path.join(baseDir, 'puppet_manifest_v2.json');
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));

  const headGroup = convertManifestLayer(manifest.head);
  const bodyGroup = convertManifestLayer(manifest.body);

  const rootCharacter = {
    name: manifest.characterName,
    children: [headGroup, bodyGroup],
    opened: true
  };

  const psdDoc = {
    width: manifest.canvasWidth,
    height: manifest.canvasHeight,
    channels: 4,
    bitsPerChannel: 8,
    colorMode: 3, // RGB
    children: [rootCharacter]
  };

  console.log('Writing PSD with ag-psd...');
  const buffer = writePsd(psdDoc);
  const heroPath = path.join(baseDir, 'Aero_Hero.psd');
  fs.writeFileSync(heroPath, Buffer.from(buffer));
  console.log(`Psd successfully created at: ${heroPath}`);
  console.log(`File size: ${fs.statSync(heroPath).size} bytes`);

  try {
    const starPath = path.join(baseDir, 'Aero_Star.psd');
    fs.writeFileSync(starPath, Buffer.from(buffer));
    console.log(`Also updated Aero_Star.psd`);
  } catch (err) {
    console.log(`Note: Aero_Star.psd is currently locked by Character Animator. Use Aero_Hero.psd!`);
  }
}

main().catch(err => {
  console.error('Failed to compile PSD:', err);
  process.exit(1);
});
