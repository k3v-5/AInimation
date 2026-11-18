# Ficha Técnica: Pipeline de Generación de Assets, Rigging y Renders
## Módulos: `Art/Blender/generar_testdummy_fiel_referencia.py`, `Art/Blender/generar_personaje_riggeado_oficial.py`, `Art/Blender/generar_personaje_fiel_referencia_v11.py` y `Art/Blender/generar_lote3_personajes.py`

### 1. Propósito
Automatizar la creación procedural, topología deformable de 3 bucles en articulaciones, asignación de pesos de piel (Skinning) determinista mediante BMesh Deform Layers, esqueleto bipedal compatible con retargeting de Unreal Engine 5, equipamiento modular desacoplado por sockets (`weapon_socket_r`), materiales PBR calibrados, modelado orgánico textil (arpillera y sudadera) para muñecos de pruebas y bomberos, renderizado de validación de flexión de articulaciones y exportación técnica a formatos FBX y .blend para el proyecto *Astra Hazard: Rescue Squad*.

---

### 2. Contratos y Salidas
- **Motor Ejecutor:** Blender 5.2.0 LTS (modo *headless* por CLI `blender.exe -b --python`).
- **Assets Producidos Oficiales:**
  - `Art/FBX/Characters/SK_TestDummy_Ragdoll.fbx`: Malla esquelética 1:1 del muñeco de pruebas / superviviente civil basada fielmente en el concept sheet `media_1791137482814.png`. Cabeza y manos en arpillera beige con microtrama textural procedural (`#C6B79D`), costura sagital central en relieve, ojos bordados en 'X' grandes (`XX`) y sonrisa de puntadas discontinuas. Sudadera y pantalón cargo en verde salvia / olive drab (`#64826B`) con cremallera frontal, cordones blancos con punteras metálicas, bolsillo canguro, dianas de choque de 4 cuadrantes (amarillo/negro) en hombros, codos, muñecas y rodillas, cinturón táctico de cuero con mini-respirador y cuerda colgante, gauntlet con pantalla LED verde emisiva, y mochila de expedición completa con estera enrollada (bedroll) y parches "MAS" / "MAS CORP.". Riggeado con esqueleto estándar bipedal para simulación de Ragdoll físico en UE5.
  - `Art/Blender/SK_TestDummy_Ragdoll.blend`: Escena Blender maestra con esqueleto, modificadores de piel, materiales procedurales y luces de hangar.
  - `Art/Renders/SK_TestDummy_Fiel_4views.png`: Model Sheet técnico oficial de 4 vistas (Frontal, Trasera con mochila, Perspectiva de acción 3/4 y Perfil lateral).
  - `Art/Renders/comparativa_testdummy_fiel.png`: Hoja de verificación visual lado a lado contrastando el arte conceptual del usuario con el render 3D generado.
  - `Art/FBX/Characters/SK_Firefighter_Official_Rigged.fbx`: Malla esquelética en **Rest A-Pose estándar de UE5** (brazos en ángulo de 35° descendente, piernas en A-stance simétrica).
  - `Art/FBX/Equipment/SM_ExtinguisherCannon.fbx`: Malla estática modular del cañón extintor táctico con punto de pivote en la empuñadura.
  - `Art/Blender/SK_Firefighter_Official_Rigged.blend`: Archivo fuente de escena con el armature de bombero.
  - `Art/Renders/SK_Firefighter_Rig_Validation_4views.png`: Model Sheet de validación de flexión de articulaciones a 90° y 115°.
- **Convenciones de Exportación:**
  - Ejes: `-Y Forward`, `Z Up` (estándar nativo de Unreal Engine).
  - Unidades: Métrica 1:1 (altura estilizada chunky ~1.50m para el dummy, ~1.58m para el bombero).
  - Materiales: PBR calibrados con paleta extraída directamente de la referencia del artista conceptual.

---

### 3. Razón de Diseño (Rationale) y Resolución de Iteraciones
- **Eliminación del aspecto 'Robot / LEGO' en el Muñeco de Pruebas:**
  - El diseño inicial utilizaba cubos rígidos naranjas con aspecto de robot automotriz genérico.
  - Se rediseñó totalmente a una figura humanoide orgánica y estilizada: cabeza y manoplas de arpillera acolchada (saco de tela con costura perimetral), sudadera de tela suave verde salvia con capucha caída, cordones visibles y bolsillo canguro.
  - Las dianas de choque se calibraron geométricamente mediante división radial de 24 sectores (`cap_tris=True`) para garantizar cuadrantes amarillos y negros perfectamente alternados sin deformación UV.
  - La mochila incorpora una estera de acampada enrollada con espirales laterales, hebillas metálicas y parches de la corporación MAS.
- **Topología de Deformación y Skinning BMesh:**
  - Para evitar fallos de difusión de calor (*Bone Heat failed*), la asignación de pesos de vértices se realiza a nivel de datos internos de BMesh (`bmesh.types.BDeformTableLayer`).
  - La cabeza, mochila y accesorios rígidos mantienen peso $1.0$ a sus huesos estructurales, mientras que las articulaciones de codos y rodillas presentan pesos interpolados $50\% / 50\%$.
- **Calibración de Color e Iluminación de Hangar:**
  - Se calibró la iluminación con key lights suaves (120W-140W), luz cálida de lámpara industrial amarilla y fondo reflectante oscuro de hangar, evitando cualquier sobreexposición o lavado de blancos.
