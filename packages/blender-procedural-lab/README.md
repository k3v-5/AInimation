# `@ianimation/blender-procedural-lab` — Laboratorio Procedural 3D y PBR en Blender 5.2 LTS

Colección de **123 generadores Python headless para Blender 5.2 LTS** (extraídos de `E:\Disco F\Dev\Game\Art`, excluyendo archivos `.blend`/`.fbx` binarios para mantener el repositorio liviano y reproducible por código).

> Todos los scripts fueron validados con **0 archivos corruptos** y se ejecutan de forma determinista con `E:\Blender\blender.exe --factory-startup -b -P <ruta_script.py>`.

---

## Clasificación de Módulos

| Directorio | Cantidad | Contenido Principal |
| :--- | :---: | :--- |
| [`generators/characters_and_rigs/`](generators/characters_and_rigs/) | **16** | Personajes riggeados 3D (`generar_personaje_riggeado_oficial.py`, `v11`), muñecos ragdoll de prueba (`generar_testdummy_fiel_referencia.py`), supervivientes y estilización Blender. |
| [`generators/animations_and_ik/`](generators/animations_and_ik/) | **15** | Locomoción y combate 3D (`generar_animaciones_locomocion_oficial.py`), solvers IK bimanuales (`solver_exacto_bimanual.py`), auditoría ósea y verificación de sockets. |
| [`generators/pbr_textures_and_benches/`](generators/pbr_textures_and_benches/) | **19** | Material Test Bench Shader Balls Pro V5, Trim Sheets 2048x2048, síntesis de 40 mapas PBR (BaseColor, Normal DirectX, ORM AO/Rough/Metal), shows de texturas oxidadas/lujo Art Déco y texturas HUD. |
| [`generators/modular_kits_and_props/`](generators/modular_kits_and_props/) | **64** | Kits modulares arquitectónicos (Industrial, Art Déco, Plasma, BioLab, Habitat — catálogo de 90 activos), 50 props maestros, bestiario 3D de 10 entidades, arsenal de 20 armas y 30 peligros ambientales. |
| [`exporters/`](exporters/) | **9** | Exportadores automatizados a FBX/GLB compatibles con Unreal Engine 5 (`exportar_90_activos_modulares_fbx.py`, `exportar_bestiario_fbx.py`, `exportar_20_armas_fbx.py`, etc.). |
| [`docs/`](docs/) | **10** | Especificaciones arquitectónicas completas (`pipeline_arte.md`, `animacion_locomocion.md`, `catalogo_texturas_modulares.md`, etc.). |

---

## Nota para Agentes de IA sobre Rutas de Salida

Varios scripts heredados de `Game/Art` utilizan rutas relativas o referencias hacia el workspace `Game` para depositar `.blend`/`.fbx` generados. Antes de invocar un generador desde este laboratorio:
1. Verifica los argumentos o variables `OUT_DIR` / `PROJECT_ROOT` dentro del script con `read_file`.
2. Ejecuta siempre en modo headless sin UI:
   ```powershell
   E:\Blender\blender.exe --factory-startup -b -P packages\blender-procedural-lab\generators\pbr_textures_and_benches\generar_material_test_bench_v5.py
   ```
