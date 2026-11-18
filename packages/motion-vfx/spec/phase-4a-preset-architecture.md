# Especificación Técnica: Fase 4A — Preset & Effect Architecture

**Documento:** `spec/phase-4a-preset-architecture.md`  
**Estado:** VIGENTE / CONGELADO  
**Módulos:** `src/presets/`

---

## 0. Propósito y Filosofía Arquitectónica

La **Fase 4A** establece la infraestructura de **Presets de Movimiento**.

Un preset no es una animación opaca ni un caso especial en el motor, sino una **receta declarativa transparente** que traduce intenciones semánticas de alto nivel hacia composiciones de árboles `AnimationNode` existentes:

```
[Intención del Usuario / LLM]
         │ "Haz que el título entre con un pop suave"
         ▼
[Preset: popIn (Categoría: entrance, tags: [smooth, modern])]
         │
         ▼
[PresetResolver] (Validación de parámetros, defaults y overrides estrictos)
         │
         ▼
[Expanded AnimationNode Tree]
         │
    Parallel
    ├── FadeIn (transform.opacity: 0 -> base)
    └── ScaleIn (transform.scale: 0.8 -> 1.0 + Overshoot)
         │
         ▼
[Animation Engine Evaluator / IR Exporter]
```

---

## 1. Interfaces y Esquemas de Parámetros

### 1.1. Categorías Canónicas (`PresetCategory`)
- `entrance`: Aparición y entrada en escena.
- `exit`: Desaparición y salida.
- `emphasis`: Llamado de atención y pulsos.
- `transition`: Paso entre tomas o estados.
- `text`: Tipografía y dinámicas de texto.
- `camera`: Movimiento y encuadre virtual.
- `utility`: Utilidades de layout y sincronización.

### 1.2. Tipos de Parámetros (`PresetParameterType`)
- `"number" | "boolean" | "string" | "enum" | "duration" | "distance" | "color"`

```typescript
export interface PresetParameterSchema {
  name: string;
  type: PresetParameterType;
  default: unknown;
  description: string;
  min?: number;
  max?: number;
  values?: string[]; // para type === "enum"
}
```

### 1.3. Definición de Preset (`PresetDefinition`)
```typescript
export interface PresetDefinition {
  id: string;
  name: string;
  category: PresetCategory;
  version: number;
  description: string;
  tags: string[];
  parameters: PresetParameterSchema[];
  compatibleWith?: ElementType[];
  requires?: string[];
  dependencies?: string[];
  build(context: PresetContext): AnimationNode;
}
```

---

## 2. Invariantes y Reglas de Resolución

1. **Rechazo Estricto de Parámetros Desconocidos:**
   Cualquier propiedad en `overrides` no declarada en el esquema lanza `ValidationError("UNKNOWN_PRESET_PARAMETER")`.
2. **Transparencia Total de Expansión:**
   El resultado de `resolve(presetId)` es un árbol de `AnimationNode` estándar inspeccionable, editable y serializable.
3. **Detección de Ciclos en Dependencias:**
   Si un preset compuesto depende de otros presets, el grafo de dependencias se valida como DAG acíclico (`CIRCULAR_PRESET_DEPENDENCY`).
4. **Compatibilidad Estricta:**
   El resolver verifica que el elemento de destino pertenezca a `compatibleWith` (ej. no aplicar un preset tipográfico a un elemento de audio).
5. **Determinismo:**
   Mismos parámetros y mismo elemento destino producen un árbol de animación idéntico.
