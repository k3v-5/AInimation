# Iteration 17: Abstracción de Audio (TTS) y Mundo 3D (Blender)

## Objetivo
Robustecer el sistema Swarm Intelligence integrando agentes capaces de gestionar flujos de trabajo fuera del ecosistema puro de Adobe 2D. Específicamente, incorporar capacidades de Text-To-Speech (TTS) nativas para el `AudioAgent`, y abrir el entorno hacia la animación tridimensional usando **Blender** (`BlenderAgent` y `BlenderProvider`) de forma automatizada ("headless").

## Acceptance Criteria (Criterios de Aceptación)

### 1. Integración de Generación de Audio
*   **AC-57: Audio Provider:** Crear `AudioProvider.ts` que implemente el contrato `IAnimationProvider` y exponga la capacidad `audio.generate_tts`.
*   **AC-58: Audio Agent Routing:** Crear `AudioAgent.ts` en la arquitectura Swarm. Si el `SwarmDirector` detecta intenciones de generación de voz, debe delegar al `AudioAgent` para llamar al proveedor de audio.

### 2. Integración 3D Headless (Blender)
*   **AC-59: Blender Provider:** Crear `BlenderProvider.ts` que exponga la capacidad `blender.execute_python`.
*   **AC-60: Python (bpy) Execution:** El `BlenderProvider` debe poder recibir un script de Python (`bpy`) y ejecutarlo dinámicamente usando la CLI de Blender en modo de fondo: `blender -b -P script.py`. En modo `test`, debe simular (mockear) la ejecución.
*   **AC-61: Blender Agent Routing:** Crear `BlenderAgent.ts`. Si el `SwarmDirector` detecta una orden de renderizado o modelado 3D, debe delegar al `BlenderAgent` para generar el script de Python adecuado y pasárselo al DAG.

### 3. Orquestación Continua
*   **AC-62:** El `AnimationEngine` debe poder manejar de forma nativa estos nuevos proveedores en conjunto con los existentes sin requerir cambios en el bucle principal de ejecución de nodos (`processNode`).
