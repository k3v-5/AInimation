# Especificación Técnica: Fase 3E — Animation Authoring / Declarative DSL

**Documento:** `spec/phase-3e-animation-dsl.md`  
**Estado:** VIGENTE / CONGELADO  
**Módulos:** `src/animation/dsl/`

---

## 0. Propósito y Filosofía Arquitectónica

La **Fase 3E** establece una capa declarativa estructurada (*Domain-Specific Language* y *Intermediate Representation*) sobre el motor de animación.

Permite a agentes de IA y herramientas externas generar, consultar, validar y modificar animaciones complejas mediante objetos JSON puros sin ejecutar código arbitrario ni depender de la API interna del motor:

```
[LLM / Intent Layer]
         │ (JSON declarativo estructurado)
         ▼
[DSL Parser & Variable Resolver] ($duration, $distance)
         │
         ▼
[DSL Diagnostic Validator] (Errores con path canónico: animations[0].children[1].direction)
         │
         ▼
[DSL Compiler]
         │
         ▼
[Animation IR] (Representación Intermedia agnóstica de backend)
         │
         ├───> [Internal Animation Tree: AnimationNode (Fases 1-3D)]
         ├───> [After Effects JSX Exporter] (Futuro)
         └───> [Remotion / WebGL Exporter] (Futuro)
```

---

## 1. Esquema del DSL v1

### 1.1. Estructura Raíz (`DSLDocument`)
```typescript
export interface DSLDocument {
  version: 1;
  variables?: Record<string, number | string>;
  animations: DSLNode[];
}
```

### 1.2. Nodos de Movimiento Atómico (`DSLBasicAnimationNode`)
- `type`: `"fadeIn" | "fadeOut" | "slideIn" | "slideOut" | "scaleIn" | "scaleOut" | "rotateIn" | "rotateOut"`
- `target`: `string` (ej. `"hero_title"`, `"#hero_title"`)
- `duration?`: `number | string` (admite variables como `"$entranceDuration"`)
- `delay?`: `number | string`
- `easing?`: `EasingName`
- `motion?`: `string | DSLMotionConfig` (ej. `"spring"`, `"overshoot"`, o `{ "type": "spring", "preset": "snappy" }`)
- `direction?`: `"left" | "right" | "up" | "down"` (para `slideIn` / `slideOut`)
- `distance?`: `number | string` (para `slideIn` / `slideOut`)
- `from?` / `to?`: valores numéricos, vectoriales o variables

### 1.3. Nodos de Composición (`DSLCompositionNode`)
- `type`: `"parallel" | "sequence" | "delay" | "hold" | "repeat" | "offset" | "stagger"`
- `children?`: `DSLNode[]`
- `count?`: `number` (para `repeat`)
- `offsetTime?`: `number | string` (para `offset`)
- `staggerDelay?`: `number | string` (para `stagger`)
- `staggerMode?`: `"forward" | "reverse"` (para `stagger`)

---

## 2. Invariantes y Reglas de Validación

1. **Diagnóstico con Rutas Precisas (Path-Based Error Reporting):**
   Cualquier error de validación incluye la ruta exacta del campo infractor (ej. `animations[0].children[1].direction: Expected 'left' | 'right' | 'up' | 'down', got 'banana'`).
2. **Sustitución Estricta de Variables:**
   Las referencias a variables `$varName` deben existir en el bloque `variables`. De lo contrario, se genera el error diagnóstico `UNDEFINED_VARIABLE`.
3. **Paridad Numérica Determinista 100%:**
   $$\forall t, \quad \text{compileDSL(doc)}.\text{evaluate}(t) \equiv \text{HandCraftedEngineNode}.\text{evaluate}(t)$$
4. **Backend Independence:**
   El compilador genera `AnimationIR`, permitiendo reutilizar la misma especificación para el motor interno o generadores de After Effects/Remotion.
