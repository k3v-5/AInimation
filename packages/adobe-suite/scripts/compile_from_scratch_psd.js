import fs from 'fs';
import path from 'path';
import { writePsd } from 'ag-psd';
import { CharacterAnimatorDeepEngine } from '../dist/core/CharacterAnimatorDeepEngine.js';

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
  console.log('=== COMPILANDO CYBERGIRL_FROMSCRATCH CHARACTER ANIMATOR PSD ===\n');

  const baseDir = path.resolve('f:/Dev/AdobeEngineSuit/showcase_animation');
  const manifestPath = path.join(baseDir, 'cybergirl_from_scratch_manifest.json');
  
  if (!fs.existsSync(manifestPath)) {
    throw new Error(`Manifiesto no encontrado en: ${manifestPath}`);
  }

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

  console.log('Escribiendo CyberGirl_FromScratch.psd con ag-psd...');
  const buffer = writePsd(psdDoc);
  const outPsdPath = path.join(baseDir, 'CyberGirl_FromScratch.psd');
  fs.writeFileSync(outPsdPath, Buffer.from(buffer));
  console.log(`PSD creado exitosamente en: ${outPsdPath}`);
  console.log(`Tamaño de archivo: ${fs.statSync(outPsdPath).size} bytes`);

  // Auditoría médica de Character Animator
  console.log('\n=== AUDITORÍA MÉDICA DEL RIGGING (CharacterAnimatorDeepEngine) ===');
  const audit = CharacterAnimatorDeepEngine.auditPuppetDeep(outPsdPath);
  console.log(`Puppet Health Score: ${audit.healthScore}/100 [${audit.isReadyForCharacterAnimator ? 'LISTO PARA CHARACTER ANIMATOR' : 'REVISAR'}]`);
  console.log(`Visemas anatómicos encontrados: ${audit.details.foundVisemes.length}/14 (${audit.details.foundVisemes.join(', ')})`);
  console.log(`Ojos y Pupil Tracking: Left Eye: ${audit.details.eyes.leftEye}, Right Eye: ${audit.details.eyes.rightEye}`);
  console.log(`Físicas detectadas: Dangle=${audit.details.physicsTags.dangleCount}`);
  console.log(`Triggers configurados: ${audit.details.triggersFound.length} (${audit.details.triggersFound.join(', ')})`);

  if (audit.issues.length > 0) {
    console.log('Notas de auditoría:', audit.issues);
  }
}

main().catch(err => {
  console.error('Fallo al compilar CyberGirl_FromScratch PSD:', err);
  process.exit(1);
});
