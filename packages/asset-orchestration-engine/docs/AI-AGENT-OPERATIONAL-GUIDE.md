# Guía de Operación para Agentes de IA (AI Agent Operational Guide)
**Asset Orchestration Engine (AOE) — Optimización de Tokens, Ejecución Atómica y Cero Retrabajo**

---

## 🎯 1. Objetivo para la IA

Este documento instruye a cualquier Agente de Inteligencia Artificial (Claude, ChatGPT, Cursor Agent, Antigravity, Windsurf, Copilot, etc.) sobre cómo operar el **Asset Orchestration Engine (AOE)** para:
1. **Minimizar el Consumo de Tokens (hasta un 80% de ahorro)** mediante ejecución por lotes (*Batch Execution*).
2. **Eliminar el Retrabajo y Suposiciones** gracias a la validación empírica en tiempo real.
3. **Garantizar Modelos 3D Listos para Motores (UE5/Unity)** con topología limpia, colisiones seguras y materiales PBR estandarizados.

---

## ⚡ 2. Las 5 Leyes Inflexibles de Eficiencia para la IA

### Ley 1: Prohibición de Acciones Repetitivas Fragmentadas
- **Regla**: Si una tarea requiere 2 o más operaciones de modelado, shader o exportación, **NUNCA ejecutes llamadas a herramientas una a una** (ej. llamar a `execute_blender_code` 15 veces para crear 15 primitivas).
- **Acción Obligatoria**: Escribe un script Python autocontenido en `scripts/` y ejecútalo en un único paso atómico mediante:
  ```powershell
  blender.exe -b base.blend --python scripts/tu_generador.py -- --preview-output render.png
  ```

### Ley 2: Diagnóstico Empírico Inmediato (Prohibido Adivinar)
- **Regla**: Ante cualquier error de renderizado, malla vacía, fallo de animación o problemas de shader, **está estrictamente prohibido intentar corregir el código mediante adivinanzas teóricas sucesivas**.
- **Acción Obligatoria**: Inyecta un script de inspección de datos (`bpy.data.objects`, `depsgraph`, `vertex_groups`, etc.) en Blender o ejecuta `tests/` para consultar el estado real del motor antes de proponer cambios.

### Ley 3: Previsualización Obligatoria de 4 Vistas antes de Exportar
- **Regla**: Todo asset de personaje o arma debe renderizarse en una cuadrícula compuesta de 4 cuadrantes ($1920\times1080$) antes de exportar FBX o importar en el motor:
  1. **Vista de Acción (3/4 Frontal)**: Captura la silueta dinámica y volumen.
  2. **Vista Frontal**: Validación de proporciones anatómicas y simetría.
  3. **Vista Trasera**: Flujo dorsal, espina y accesorios posteriores.
  4. **Vista en Primera Persona (FPS)**: Manos, empuñadura y detalles de cámara de jugador.

### Ley 4: Regla de Cero-Colisión y Buffer Frontal
- **Regla**: Todo accesorio, escudo o arma debe contar con un offset de seguridad $\ge 30\text{ cm}$ respecto al torso y emparentarse rígidamente al hueso correspondiente (`hand_r`, `chest`) para prevenir *clipping* en animaciones.
- Los proyectiles deben ignorar a su emisor mediante `IgnoreActorWhenMoving(Owner, true)`.

### Ley 5: Preservación de Workspaces
- **Regla**: Nunca sobreescribir el archivo maestro de producción de manera destructiva. Crear siempre un archivo `.blend` de trabajo en un workspace temporal o aislado, y solo fusionar al validar al 100%.

---

## 🏗️ 3. Flujo de Trabajo Típico de la IA en 3 Pasos

```
┌─────────────────────────────────────────────────────────────┐
│ 1. COMPILACIÓN DE INTENCIÓN                                │
│ Parsear descripción del usuario a especificación geométrica │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. GENERACIÓN POR SCRIPT EN LOTE (BATCH PYTHON)            │
│ Ejecutar en Blender background: Geometría + Shaders + 4-View │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. EVALUACIÓN Y VALIDACIÓN QA                              │
│ Validar que cumple manifold, UVs y aprobación del usuario   │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 4. Plantilla de Script Python para la IA (`scripts/template_asset.py`)

Copia y adapta esta plantilla estándar para crear cualquier nuevo asset en 1 solo paso:

```python
import bpy
import bmesh
import math
from mathutils import Matrix, Vector
import os
import sys
import argparse

def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend-file", type=str, default="")
    parser.add_argument("--preview-output", type=str, default="")
    return parser.parse_args(argv)

def create_pbr_material(name, base_color=(0.05, 0.05, 0.05, 1.0), metallic=0.9, roughness=0.05, emission_color=None, emission_strength=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = 1.0
        if emission_color and emission_strength > 0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission_color
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

def build_asset_geometry(col):
    mesh = bpy.data.meshes.new("SM_CustomAsset_Mesh")
    obj = bpy.data.objects.new("SM_CustomAsset", mesh)
    col.objects.link(obj)

    bm = bmesh.new()
    # Construir geometría limpia aquí
    mat_core = Matrix.Translation((0, 0, 1.0)) @ Matrix.Diagonal((0.5, 0.5, 0.5, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_core)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def main():
    args = parse_args()
    col = bpy.data.collections.get("AOE_Assets") or bpy.data.collections.new("AOE_Assets")
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)

    # 1. Geometría
    obj = build_asset_geometry(col)

    # 2. Materiales
    mat = create_pbr_material("M_AssetPBR", (0.005, 0.005, 0.008, 1.0), 0.94, 0.03, (0.85, 0.02, 1.0, 1.0), 30.0)
    obj.data.materials.clear()
    obj.data.materials.append(mat)

    # 3. Guardar
    if args.blend_file:
        bpy.ops.wm.save_as_mainfile(filepath=args.blend_file)
        print(f"[OK] Asset guardado en: {args.blend_file}")

if __name__ == "__main__":
    main()
```

---

## 🧪 5. Comandos de Verificación Inmediata para la IA

Para validar que todo el pipeline y la base de código están intactos y operativos:

```powershell
# 1. Ejecutar la suite completa de 1382 pruebas
python -m unittest discover -s tests -p "test_*.py"

# 2. Validar generación de un asset específico
blender.exe -b workspace.blend --python scripts/tu_script.py -- --preview-output render.png
```

---

## 📊 6. Matriz de Fases para Referencia Rápida de la IA

| Fase | Subsistema | Cuándo Utilizarlo |
| :--- | :--- | :--- |
| **F51 / F71** | `intent_compiler` | Convertir un prompt libre a especificación geométrica determinista. |
| **F75** | `automated_visual_eval` | Evaluar calidad de shaders PBR y geometría contra restricciones QA. |
| **F76** | `autonomous_correction` | Corregir automáticamente normales invertidas, no-manifold o UVs rotas. |
| **F77** | `failure_analysis` | Diagnosticar causa raíz de fallos en Blender o Unreal. |
| **F78** | `strategy_learning` | Consultar la mejor estrategia histórica para una categoría de asset. |
| **F79** | `cost_performance` | Optimizar polycount, tiempo de render y memoria sin perder calidad visual. |
| **F80** | `production_orchestration` | Ejecutar el pipeline maestro completo de 19 etapas (Intent $\to$ Entrega). |

Siguiendo esta guía, cualquier Agente de IA logrará resultados de grado estudio con el mínimo consumo computacional y cero errores en producción.
