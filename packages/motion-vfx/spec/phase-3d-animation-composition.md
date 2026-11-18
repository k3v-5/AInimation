# Especificación Técnica: Fase 3D — Animation Composition

**Documento:** `spec/phase-3d-animation-composition.md`  
**Estado:** VIGENTE / CONGELADO  
**Módulos:** `src/animation/composition/` y `src/animation/`

---

## 0. Propósito y Alcance

La **Fase 3D** completa la infraestructura de composición temporal avanzada del motor de animación, permitiendo orquestar árboles complejos de transformaciones simultáneas, secuenciales, solapadas, repetidas y escalonadas (stagger):

```
AnimationNode (Composite Pattern Extendido)
│
├── BasicAnimation (Atómico)
├── ParallelAnimation (Concurrente)
├── SequenceAnimation (Secuencial con Overlap)
├── DelayNode (Consumo de tiempo / Espera)
├── HoldNode (Mantenimiento de estado)
├── RepeatNode (Repetición N veces)
├── OffsetNode (Desplazamiento temporal relativo)
└── StaggerBuilder (Distribución escalonada para arrays de elementos)
```

---

## 1. Reglas e Invariantes Arquitectónicos

1. **Inmutabilidad y Pureza Temporal:**
   $$\forall t, \quad \text{Node}.\text{evaluate}(t) \equiv \text{Node}.\text{evaluate}(t)$$
   La composición no depende de reloj global, variables mutables ni llamadas a `Math.random()`.
2. **Duración de Nodos Compuestos:**
   - **Parallel:** $\text{duration} = \max_{i}(\text{child}_i.\text{totalDuration})$.
   - **Sequence:** $\text{duration} = \sum_{i}(\text{child}_i.\text{totalDuration} + \text{offset}_i)$.
   - **Repeat:** $\text{duration} = \text{count} \times \text{child}.\text{totalDuration}$.
   - **Hold / Delay:** $\text{duration} = \text{holdDuration}$.
3. **Staggering Determinista:**
   Dada una lista de $N$ elementos y un intervalo $\Delta t$:
   - Modo `"forward"`: $\text{delay}_i = i \cdot \Delta t$
   - Modo `"reverse"`: $\text{delay}_i = (N - 1 - i) \cdot \Delta t$
4. **Detección de Ciclos:**
   El árbol de animación es un Grafo Acíclico Dirigido (DAG). Cualquier referencia circular lanza `ValidationError("CYCLIC_ANIMATION")`.
5. **Lossless Round-Trip Declarativo:**
   Toda la jerarquía compuesta es 100% serializable a JSON y reconstruible sin pérdida semántica.

---

## 2. Definición de Nodos Especializados

### 2.1. `DelayNode`
Consume tiempo en una secuencia sin generar valores de propiedad:
- $\text{duration} = d > 0$.
- `evaluate(t) = new AnimationResult()` (vacío).

### 2.2. `HoldNode`
Idéntico en timing a `DelayNode`, pero expresa semánticamente una pausa / retención de estado en un pipeline secuencial de motion graphics:
- $\text{duration} = h > 0$.
- `label = "hold"` por defecto.

### 2.3. `RepeatNode`
Repite un nodo hijo $N$ veces ($N \ge 1$):
- $\text{duration} = N \times \text{child}.\text{totalDuration}$.
- En el instante local $t$, $t_{\text{rel}} = t \pmod{\text{child}.\text{totalDuration}}$.

### 2.4. `OffsetNode`
Aplica un desplazamiento temporal $\Delta t$ a la ejecución de su nodo hijo:
- $\text{totalDuration} = \max(0, \text{child}.\text{totalDuration} + \text{offset})$.
- `evaluate(t)` evalúa al hijo en $\max(0, t - \text{offset})$.

---

## 3. Tipos e Interfaces de Composición

```typescript
export type StaggerMode = "forward" | "reverse";

export interface StaggerOptions {
  delay: number; // Intervalo entre elementos sucesivos
  mode?: StaggerMode;
  seed?: number;
}
```
