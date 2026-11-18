# Especificación Técnica: Fase 2C — Integration, Serialization & Validation

**Documento:** `spec/phase-2c.md`  
**Estado:** VIGENTE / CONGELADO  
**Versión de Arquitectura:** `0.2.0-2C` (Core V1 Checkpoint)

---

## 0. Propósito y Alcance

La **Fase 2C** consolida el Core del motor de Motion Graphics como un sistema unificado, determinista y seguro ante fallos, antes de comenzar el desarrollo de primitivas de animación (Fase 3).

```
                 CORE V1
                  │
       ┌──────────┴──────────┐
       │                     │
    Timeline             Elements
       │                     │
 Properties            ┌─────┴─────┐
       │               │           │
 Keyframes          Transform    Assets
       │               │           │
 Easing            Matrix2D    Registry
                  │
                  ▼
        ┌───────────────────┐
        │ ProjectValidator  │
        │   Serialization   │
        │ Migration System  │
        │  Snapshot Engine  │
        └───────────────────┘
```

---

## 1. Reglas e Invariantes Arquitectónicos

1. **Separación de Responsabilidades:**
   $$\text{Project} \longrightarrow \text{Evaluator} \longrightarrow \text{Snapshot} \longrightarrow (\text{Renderer})$$
   El renderer futuro sólo consumirá snapshots inmutables; nunca accederá a propiedades, timelines ni activos físicos.
2. **Determinismo Estricto:**
   $$\forall t, \quad \text{Project}.\text{evaluate}(t) \equiv \text{Project}.\text{evaluate}(t)$$
   La evaluación temporal es idempotente y no depende de reloj del sistema, aleatoriedad, ni estado mutable global.
3. **Reporte Estructurado de Validación (`ValidationIssue`):**
   Los errores no sólo lanzan excepciones en tiempo de ejecución, sino que el sistema provee diagnósticos estructurados legibles por IA con códigos de error canónicos.
4. **Aislamiento de Clonado Profundo (Zero-Aliasing):**
   $$\text{clone}.\text{transform} \neq \text{original}.\text{transform}$$
   Modificar cualquier propiedad en un clon no muta el elemento original.
5. **Arquitectura de Migraciones:**
   El formato serializado soporta `schemaVersion` con pipeline de migración extensible `migrate(data, fromVersion, toVersion)`.

---

## 2. Códigos de Error Canónicos (`ValidationIssueCode`)

| Código | Descripción |
|---|---|
| `INVALID_SETTINGS` | Dimensiones, framerate o duración de composición no positivos. |
| `INVALID_DURATION` | Duración de elemento no positiva ($< 0$ o $\le 0$). |
| `INVALID_TIME` | `startTime` o timestamp inválido (negativo, `NaN` o infinito). |
| `DUPLICATE_ELEMENT_ID` | Identificador de elemento duplicado en la composición o grupo. |
| `DUPLICATE_ASSET_ID` | Identificador de recurso duplicado en el `AssetRegistry`. |
| `MISSING_ASSET` | Elemento referencia un `assetId` inexistente en el registro. |
| `MISSING_PARENT` | `parentId` declarado apunta a un elemento que no existe. |
| `PARENT_CYCLE` | Referencia circular o ciclo en la jerarquía de emparentamiento. |
| `INVALID_TRANSFORM` | Escala, posición, rotación u opacidad con valores no numéricos (`NaN`, `Infinity`). |
| `INVALID_PROPERTY` | Formato o keyframes de propiedad corruptos o desordenados. |
| `UNSUPPORTED_ELEMENT_TYPE` | Tipo de elemento no registrado o desconocido. |
| `INVALID_SCHEMA` | Versión de esquema JSON incompatible o no migrable. |

---

## 3. Interfaces del Validador y Migrador

```typescript
export interface ValidationIssue {
  severity: "error" | "warning";
  code: string;
  message: string;
  path?: string;
  elementId?: string;
  assetId?: string;
}

export interface ValidationReport {
  isValid: boolean;
  issues: ValidationIssue[];
}

export class ProjectValidator {
  static validate(composition: Composition): ValidationReport;
  static assertValid(composition: Composition): void;
}
```
