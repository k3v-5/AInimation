# Directrices de Desarrollo, Calidad y Continuidad del Proyecto

Este proyecto se rige por estándares estrictos de ingeniería de software para garantizar robustez, mantenibilidad y colaboración fluida entre múltiples sesiones y agentes de IA.

---

## 1. Principios de Diseño y Arquitectura (SOLID)
- **Single Responsibility (SRP)**: Cada módulo, clase o componente de UI debe tener una única razón para cambiar. Los adaptadores de UE5, pipelines de IA y herramientas FastMCP deben estar completamente desacoplados.
- **Open/Closed (OCP)**: Nuevos backends de IA (ej. nuevos proveedores de Image-to-3D o motores de render) deben añadirse mediante plugins/adaptadores sin modificar la lógica central del orquestador.
- **Liskov Substitution (LSP)**: Todos los proveedores de inferencia (Cloud o Local) deben implementar la misma interfaz abstracta de forma intercambiable.
- **Interface Segregation (ISP)**: Interfaces pequeñas y orientadas a propósitos específicos en lugar de monolitos.
- **Dependency Inversion (DIP)**: Los módulos de alto nivel dependen de abstracciones, no de detalles de bajo nivel.

---

## 2. Tipado Estricto al 100% (Zero-Any Policy)
- **Python**: Tipado estricto con `typing` (`Optional`, `Union`, `Dict`, `List`, `Callable`) y modelos validados con **Pydantic v2**. Ninguna función debe carecer de firmas de tipos en parámetros y retornos.
- **TypeScript**: `strict: true` activado en `tsconfig.json`. Prohibido el uso de `any`; utilizar tipos discriminated unions y esquemas `zod` para validación en runtime.

---

## 3. Documentación e Indexación Continua
- Cada paquete o módulo debe incluir un archivo `README.md` o docstrings completos describiendo su rol, entradas, salidas y contratos.
- Mantener un índice de herramientas MCP con sus esquemas JSON Schema y ejemplos de llamadas.
- No asumir conocimiento implícito; documentar cualquier variable de entorno, puerto o dependencia nativa.

---

## 4. Memoria y Continuidad entre Sesiones de LLM (`PROJECT_STATUS.md`)
- Se mantiene un archivo raíz `PROJECT_STATUS.md` actualizado en cada sesión con:
  - **Avances consolidados**: Lo que ya está implementado, verificado y funcionando.
  - **Decisiones arquitectónicas**: Qué se eligió y por qué.
  - **Backlog y Tareas Pendientes**: Próximos pasos detallados con suficiente contexto para que cualquier LLM subsiguiente tome el relevo de inmediato.

---

## 5. Testeabilidad y Verificación Visual Rigurosa
- **Pruebas Automatizadas**: Cada componente backend, adaptador MCP y función utilitaria debe tener pruebas unitarias con `pytest` y tests de componentes en frontend.
- **Verificación Visual**: Durante la implementación de la UI o generación de escenas:
  - Verificar visualmente mediante capturas, inspección de render o previsualizaciones que cada elemento gráfico (timeline, controles, botones, dropzones, sliders) esté correctamente alineado, legible y en su posición exacta.
  - No dar por completada una tarea visual sin validar su apariencia e interactividad real.

---

## 6. Pipeline Obligatorio de Imagen a Objeto 3D Articulable (Mandatory 3D-First Policy)
- **Principio 3D-First Inviolable**: Toda imagen o arte conceptual provisto por el usuario para animar DEBE transformarse SIEMPRE en un **objeto 3D con profundidad volumétrica real** ($Z(x, y)$), normales tangenciales PBR y malla poligonal estándar (**Khronos glTF 2.0 / GLB** y **Wavefront OBJ**).
- **Prohibición Estricta de Filtros Planos y Recortes con Tijera**:
  - Queda terminantemente prohibido animar imágenes como recortes planos 2D o aplicar filtros de ondulación/deformación en cuadrícula 2D (efecto de filtro falso).
  - Queda prohibido recortar partes anatómicas con polígonos planos que provoquen hendiduras, cortes rectos o vacíos en la piel/cuello.
- **Articulación de Partes Específicas (Rigging y Deformers Continuos $C^\infty$)**:
  - Cada parte que deba moverse (mandíbula, cables, orejas, pelaje, extremidades, ojos) debe gobernarse mediante **rigging esquelético o campos de deformación continua $C^\infty$**.
  - La articulación debe preservar la integridad de la malla sin rupturas de superficie.
  - La animación debe contar siempre con **paralaje tridimensional volumétrico en Yaw y Pitch** (los elementos frontales sobresalen y rotan en perspectiva real), sombreado dinámico PBR Blinn-Phong con cálculo de normales y sombras de contacto proyectadas.
