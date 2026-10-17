# Directrices de Desarrollo, Calidad, Seguridad y Continuidad del Proyecto

Este proyecto se rige por estándares estrictos de ingeniería de software para garantizar robustez, mantenibilidad, alto rendimiento y una colaboración fluida y continua entre múltiples sesiones, desarrolladores y agentes de IA.

---

## 1. Principios de Diseño, Arquitectura (SOLID) y Escalabilidad
- **Single Responsibility (SRP)**: Cada módulo, clase o componente de UI debe tener una única razón para cambiar. Los adaptadores de UE5/Blender, pipelines de IA y herramientas FastMCP deben estar completamente desacoplados.
- **Open/Closed (OCP)**: Nuevos backends de IA y nuevos motores 3D (Unreal Engine 5, Blender, etc.) deben integrarse mediante plugins/adaptadores desacoplados sin modificar la lógica central del orquestador.
- **Liskov Substitution (LSP)**: Todos los adaptadores de motores 3D e inferencia (Cloud o Local) deben implementar la misma interfaz abstracta de forma intercambiable.
- **Interface Segregation (ISP)**: Interfaces pequeñas y orientadas a propósitos específicos en lugar de contratos monolíticos.
- **Dependency Inversion (DIP)**: Los módulos de alto nivel dependen de abstracciones (`Base3DEngineAdapter`, `BaseAIProvider`), no de detalles de implementación de bajo nivel.
- **Escalabilidad y Optimización**:
  - Toda operación de cómputo intensivo o E/S de red debe ser asíncrona y no bloqueante (`asyncio`, streaming de eventos, background tasks).
  - Reutilización inteligente de activos mediante almacenamiento direccionable por contenido (CAS con SHA-256) para evitar cálculos o descargas redundantes.
  - Gestión rigurosa del uso de memoria RAM y VRAM (descarga oportuna de tensores y modelos pesados).

---

## 2. Seguridad y Robustez Operacional
- **Validación en Fronteras**: Todos los datos que ingresan a través de la CLI, FastMCP o la interfaz gráfica deben ser validados estrictamente mediante modelos Pydantic v2 (Python) o esquemas Zod (TypeScript).
- **Sanitización de Rutas**: Mitigación proactiva de ataques de *path traversal*; las rutas de archivos deben ser resueltas y confinadas a directorios permitidos antes de cualquier operación en disco.
- **Manejo Estructurado de Errores**: Prohibidos los bloques `try/except` silenciosos o capturas genéricas que oculten el origen de un error. Todo fallo debe propagar contexto estructurado a través del bus de telemetría y generar registros legibles.

---

## 3. Tipado Estricto al 100% (Zero-Any Policy)
- **Python**: Tipado estricto con `typing` (`Optional`, `Union`, `Dict`, `List`, `Callable`) y modelos validados con **Pydantic v2**. Ninguna función debe carecer de firmas de tipos en parámetros y retornos.
- **TypeScript**: `strict: true` activado en `tsconfig.json`. Prohibido el uso de `any`; utilizar tipos discriminated unions y esquemas `zod` para validación en runtime.

---

## 4. Documentación e Indexación Continua
- Cada paquete o módulo debe incluir un archivo `README.md` o docstrings exhaustivos describiendo su rol, entradas, salidas y contratos.
- Mantener un índice actualizado de herramientas MCP con sus esquemas JSON Schema y ejemplos de llamadas.
- No asumir conocimiento implícito; indexar cualquier variable de entorno, puerto, dependencia nativa o comando de ejecución.

---

## 5. Memoria, Continuidad y Protocolo de Handover entre Agentes/LLMs (`PROJECT_STATUS.md`)
- Se mantiene el archivo raíz `PROJECT_STATUS.md` permanentemente sincronizado en cada sesión.
- **Protocolo de Relevo Continuo (Handover Protocol)**: Antes de concluir una interacción o tras completar una tarea clave, el agente debe actualizar `PROJECT_STATUS.md` asegurando que cualquier LLM o agente posterior cuente con el contexto exacto:
  - **Avances Consolidados**: Lista detallada de lo implementado, probado y verificado, citando rutas de archivos y métricas.
  - **Estado Actual y Decisiones**: Contexto claro sobre qué se está implementando en este momento, alternativas evaluadas y la justificación técnica de la solución elegida.
  - **Backlog y Tareas Pendientes**: Próximos pasos desglosados en tareas atómicas con rutas de archivos, comandos directos listos para ejecutar y dependencias previas.

---

## 6. Testeabilidad y Verificación Visual Rigurosa
- **Pruebas Automatizadas**: Cada componente backend, adaptador MCP, adaptador de motor 3D y función utilitaria debe tener pruebas unitarias con `pytest` y tests de componentes en frontend con Vitest.
- **Verificación Visual**: Durante la implementación de la UI o generación de escenas:
  - Verificar visualmente mediante capturas, inspección de render o previsualizaciones que cada elemento gráfico (timeline, controles, botones, dropzones, sliders) esté correctamente alineado, legible y en su posición exacta.
  - No dar por completada una tarea visual sin validar su apariencia e interactividad real.

---

## 7. Pipeline Obligatorio de Imagen a Objeto 3D Articulable (Mandatory 3D-First Policy)
- **Principio 3D-First Inviolable**: Toda imagen o arte conceptual provisto por el usuario para animar DEBE transformarse SIEMPRE en un **objeto 3D con profundidad volumétrica real** ($Z(x, y)$), normales tangenciales PBR y malla poligonal estándar (**Khronos glTF 2.0 / GLB** y **Wavefront OBJ**).
- **Prohibición Estricta de Filtros Planos y Recortes con Tijera**:
  - Queda terminantemente prohibido animar imágenes como recortes planos 2D o aplicar filtros de ondulación/deformación en cuadrícula 2D (efecto de filtro falso).
  - Queda prohibido recortar partes anatómicas con polígonos planos que provoquen hendiduras, cortes rectos o vacíos en la piel/cuello.
- **Articulación de Partes Específicas (Rigging y Deformers Continuos $C^\infty$)**:
  - Cada parte que deba moverse (mandíbula, cables, orejas, pelaje, extremidades, ojos) debe gobernarse mediante **rigging esquelético o campos de deformación continua $C^\infty$**.
  - La articulación debe preservar la integridad de la malla sin rupturas de superficie.
  - La animación debe contar siempre con **paralaje tridimensional volumétrico en Yaw y Pitch** (los elementos frontales sobresalen y rotan en perspectiva real), sombreado dinámico PBR Blinn-Phong con cálculo de normales y sombras de contacto proyectadas.
