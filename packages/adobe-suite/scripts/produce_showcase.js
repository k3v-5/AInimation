import fs from 'fs';
import path from 'path';
import { CharacterAnimatorDeepEngine } from '../dist/core/CharacterAnimatorDeepEngine.js';
import { NeuralSpeechEngine } from '../dist/core/NeuralSpeechEngine.js';
import { BlenderEngine } from '../dist/core/BlenderEngine.js';
import { SceneManifestBuilder } from '../dist/core/SceneManifestBuilder.js';
import { PipelineManager } from '../dist/core/PipelineManager.js';

async function main() {
  console.log('=== INICIANDO PRODUCCION COMPLETA DE ANIMACION (SHOWCASE MCP) ===\n');

  const projectDir = path.resolve('f:/Dev/AdobeEngineSuit/showcase_animation');
  fs.mkdirSync(projectDir, { recursive: true });

  const characterName = 'Aero_Star';

  // -------------------------------------------------------------
  // PASO 1: RIGGING DE MARIONETA MULTI-ÁNGULO CON HEAD TURNER & FÍSICAS
  // -------------------------------------------------------------
  console.log('1. Generando marioneta multi-ángulo con Head Turner y 14 visemas...');
  const puppetPath = path.join(projectDir, `${characterName}.psd`);

  CharacterAnimatorDeepEngine.scaffoldMultiAnglePuppet({
    characterName,
    outPath: puppetPath,
    views: '3-view',
    width: 2000,
    height: 2000,
    includeLimbs: true,
    includePhysics: true
  });

  console.log('   Inyectando swap sets emocionales, ciclo de lágrimas, manos y respiración...');
  const triggerResult = CharacterAnimatorDeepEngine.addPuppetTriggersAndPhysics({
    psdPath: puppetPath,
    includeEmotions: true,
    includeHandGestures: true,
    includeCycleLayers: true,
    includeBreathing: true
  });

  // Auditoría médica del puppet
  const audit = CharacterAnimatorDeepEngine.auditPuppetDeep(puppetPath);
  console.log(`   Auditoría de marioneta: Health Score ${audit.healthScore}/100 [${audit.isReadyForCharacterAnimator ? 'LISTO PARA CHARACTER ANIMATOR' : 'REVISAR'}]`);
  console.log(`   Visemas encontrados: ${audit.details.foundVisemes.length}/14`);
  console.log(`   Vistas Head Turner: ${audit.details.headTurnerViewsFound.join(', ')}`);
  console.log(`   Triggers detectados: ${audit.details.triggersFound.length}`);

  // -------------------------------------------------------------
  // PASO 2: SÍNTESIS DE VOZ NEURONAL CINEMATOGRÁFICA 48kHz (-1 dBFS)
  // -------------------------------------------------------------
  console.log('\n2. Sintetizando voz neuronal cinematográfica HD (48,000 Hz, 16-bit Mono)...');
  const dialogueText = '¡Hola! Bienvenidos a Adobe Character Animator. Gracias a nuestro nuevo motor MCP, este personaje cuenta con rigging multi-ángulo de Head Turner, catorce visemas anatómicos sincronizados a cuarenta y ocho kilohercios, swap sets de expresiones emocionales y físicas elásticas en tiempo real. ¡Todo listo para animar!';

  const wavPath = path.join(projectDir, `${characterName}_Dialogue.wav`);
  const audioResult = await NeuralSpeechEngine.synthesizeSpeech({
    text: dialogueText,
    voice: 'mexico_female', // es-MX-DaliaNeural
    outputPath: wavPath,
    emotionPreset: 'cheerful'
  });

  console.log(`   Audio generado en: ${wavPath}`);
  console.log(`   Duración: ${audioResult.durationSeconds.toFixed(2)}s | Frecuencia: ${audioResult.sampleRate}Hz | Normalización: ${audioResult.normalization}`);

  // -------------------------------------------------------------
  // PASO 3: EXPORTACIÓN DE MARCADORES DE LIP-SYNC Y CUE SHEETS
  // -------------------------------------------------------------
  console.log('\n3. Generando marcadores de lip-sync para After Effects, Premiere y Character Animator...');
  const markersDir = path.join(projectDir, 'markers');
  fs.mkdirSync(markersDir, { recursive: true });
  const markersResult = NeuralSpeechEngine.exportLipSyncMarkers(
    dialogueText,
    path.join(markersDir, `${characterName}_markers`),
    {
      audioPath: wavPath,
      fps: 30,
      format: 'all'
    }
  );

  console.log(`   Total de fonemas/visemas calculados: ${markersResult.totalCues}`);
  console.log(`   Marcadores JSX para After Effects: ${markersResult.jsxPath}`);
  console.log(`   Cue Sheet JSON: ${markersResult.jsonPath}`);
  console.log(`   Tabla CSV para Premiere/Audition: ${markersResult.csvPath}`);

  // -------------------------------------------------------------
  // PASO 4: ESCENOGRAFÍA 3D PROCEDURAL CON BLENDER 5.2
  // -------------------------------------------------------------
  console.log('\n4. Creando escenografía 3D procedural en Blender 5.2 con iluminación cinematográfica...');
  const blendPath = path.join(projectDir, 'StudioStage_3D.blend');
  const blenderScaffold = await BlenderEngine.scaffold3dRoom({
    roomType: 'studio_stage',
    outputPath: blendPath,
    addProps: true,
    lightingPreset: 'cinematic_three_point',
    cameraFocalLength: 50
  });
  console.log(`   Escenario 3D creado en: ${blenderScaffold.blendFile}`);

  console.log('   Renderizando pase de fondo Beauty Pass en Blender...');
  const backgroundPassesDir = path.join(projectDir, 'background_passes');
  const renderPasses = await BlenderEngine.renderParallaxPasses({
    blendFile: blendPath,
    outputDir: backgroundPassesDir,
    baseName: 'studio_stage',
    frameNumber: 1,
    width: 1920,
    height: 1080
  });
  console.log(`   Fondo renderizado: ${renderPasses.beautyPass}`);

  // -------------------------------------------------------------
  // PASO 5: TAKE CONSOLIDADO PARA CHARACTER ANIMATOR & AFTER EFFECTS DYNAMIC LINK
  // -------------------------------------------------------------
  console.log('\n5. Empaquetando take de producción y script Dynamic Link...');
  const takeDir = path.join(projectDir, 'ch_performance_take');
  const take = await CharacterAnimatorDeepEngine.prepareRecordingTake({
    characterName,
    puppetPsdPath: puppetPath,
    outputDir: takeDir,
    audioPath: wavPath,
    fps: 30,
    triggersTimeline: [
      { timeSec: 0.0, triggerKey: '1', triggerName: 'Mano Abierta (Open)' },
      { timeSec: 1.5, triggerKey: 'b', triggerName: 'Rubor Emocional (Blush)' },
      { timeSec: 3.2, triggerKey: '5', triggerName: 'Pulgar Arriba (ThumbsUp)' },
      { timeSec: 5.0, triggerKey: '6', triggerName: 'Saludando (Wave)' },
      { timeSec: 7.0, triggerKey: '1', triggerName: 'Postura Neutra' }
    ]
  });

  // -------------------------------------------------------------
  // PASO 6: CREACIÓN DE GUÍA DE INTERACCIÓN EN VIVO
  // -------------------------------------------------------------
  const readmeContent = `# ${characterName} - Proyecto de Animación en Vivo para Character Animator

Este proyecto fue generado de manera autónoma y nativa mediante el servidor **Adobe Animation MCP**.

## 📁 Archivos en esta Carpeta:
1. **\`${characterName}.psd\`**: Marioneta multicapa lista para Character Animator con Head Turner (3 vistas: Frontal, Cuarto Izquierdo, Cuarto Derecho), 14 visemas labiales, ojos con pupila independiente, y extremidades articuladas.
2. **\`${characterName}_Dialogue.wav\`**: Audio neuronal HD de diálogo en español (48,000 Hz, 16-bit Mono, -1.0 dBFS).
3. **\`background_passes/studio_stage_beauty.png\`**: Fondo 3D de estudio cinematográfico renderizado en Blender 5.2.
4. **\`ch_performance_take/import_${characterName}_take_into_ae.jsx\`**: Script de After Effects para sincronizar marioneta, audio y marcadores mediante Dynamic Link.
5. **\`ch_performance_take/${characterName}_trigger_cue_sheet.txt\`**: Hoja de atajos de teclado para actuar en vivo.

## 🚀 Cómo Usarlo en Character Animator (Ya que lo tienes abierto):
1. **Arrastra el archivo \`${characterName}.psd\`** al panel **Proyecto** de Adobe Character Animator.
2. Haz doble clic en el puppet para abrirlo en el espacio de trabajo **Rig (Armadura)** y comprueba:
   - En la jerarquía verás \`+Head\` con sus vistas \`Frontal\`, \`Left Quarter\` y \`Right Quarter\`.
   - Cada ángulo contiene su boca con los **14 visemas**.
   - En el panel de **Triggers (Disparadores)** verás los atajos configurados.
3. Arrastra el puppet a una **Nueva Escena** (o presiona \`Ctrl+N\`).
4. **Arrastra el archivo \`${characterName}_Dialogue.wav\`** directamente a la línea de tiempo de la escena.
5. Selecciona el audio y la capa del personaje en la línea de tiempo, y en el menú superior ve a:
   👉 **Línea de tiempo > Calcular toma de sincronización labial a partir de audio de escena** (Timeline > Compute Lip Sync Take from Scene Audio).
   ¡El personaje hablará inmediatamente con sincronía fonética perfecta!
6. **Controles en Vivo por Teclado:**
   - Tecla **1**: Mano abierta (Open)
   - Tecla **2**: Puño cerrado (Fist)
   - Tecla **3**: Apuntar (Point)
   - Tecla **4**: Señal de paz (Peace)
   - Tecla **5**: Pulgar arriba (ThumbsUp)
   - Tecla **6**: Saludo con la mano (Wave)
   - Tecla **b**: Ruborizarse (Blush)
   - Tecla **w**: Gota de sudor (Sweatdrop)
   - Tecla **v**: Vena de ira anime (AnimeVein)
   - Tecla **t**: Lágrimas animadas en ciclo continuo (Tears Cycle)
   - Mueve tu cabeza frente a la cámara web para activar el **Head Turner** multi-ángulo.
   - Arrastra la mano derecha con el ratón gracias a la física **Draggable**.

---
`;

  fs.writeFileSync(path.join(projectDir, 'INSTRUCCIONES_ANIMACION.md'), readmeContent, 'utf-8');

  console.log('\n=== PRODUCCION FINALIZADA CON EXITO ===');
  console.log(`Proyecto generado en: ${projectDir}`);
  console.log(`Guía generada en: ${path.join(projectDir, 'INSTRUCCIONES_ANIMACION.md')}`);
}

main().catch(err => {
  console.error('Error durante la producción:', err);
  process.exit(1);
});
