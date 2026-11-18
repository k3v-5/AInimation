# Esquema de Serialización JSON: Fase 1

**Documento:** `spec/serialization-schema.md`  
**Estado:** VIGENTE / CONGELADO  
**Versión de Esquema:** `0.1.0`

---

## 1. Estructura Raíz del JSON

```json
{
  "schemaVersion": "0.1.0",
  "composition": {
    "id": "comp_1",
    "name": "Main Composition",
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "duration": 5.0,
    "layers": [
      {
        "id": "layer_title",
        "name": "Title Layer",
        "startTime": 0.0,
        "endTime": 5.0,
        "properties": {
          "position": {
            "type": "vector2",
            "baseValue": { "x": 960, "y": 540 },
            "keyframes": [
              {
                "time": 0.0,
                "value": { "x": 960, "y": 1080 },
                "easing": "easeOut"
              },
              {
                "time": 1.0,
                "value": { "x": 960, "y": 540 }
              }
            ]
          },
          "opacity": {
            "type": "number",
            "baseValue": 1.0,
            "keyframes": [
              { "time": 0.0, "value": 0.0, "easing": "linear" },
              { "time": 0.5, "value": 1.0 }
            ]
          },
          "rotation": {
            "type": "number",
            "baseValue": 0.0,
            "keyframes": []
          },
          "scale": {
            "type": "vector2",
            "baseValue": { "x": 1.0, "y": 1.0 },
            "keyframes": []
          }
        }
      }
    ]
  }
}
```

---

## 2. Definición Formal de Esquema

### 2.1. Tipos de Propiedad Permitidos en `type`:
- `"number"`: Valor numérico escalar.
- `"vector2"`: Objeto `{ "x": number, "y": number }`.
- `"vector3"`: Objeto `{ "x": number, "y": number, "z": number }`.
- `"color"`: Objeto `{ "r": number, "g": number, "b": number, "a": number }`.

### 2.2. Invariantes de Serialización:
1. `schemaVersion` es obligatorio y debe coincidir con `"0.1.0"`.
2. Las listas de `keyframes` deben estar ordenadas cronológicamente por `time`.
3. Todos los valores numéricos deben ser finitos (no `NaN`, no `Infinity`).
4. Si un valor no tiene keyframes, `keyframes` es un array vacío `[]`.
5. La serialización debe ser determinista (las claves de propiedades ordenadas alfabéticamente al serializar).
6. Los `keyframes` pueden incluir opcionalmente metadatos espaciales (`spatialIn`, `spatialOut`, `spatialInterpolation`) que son preservados transparentemente.

---

## 3. Métodos del Contrato

```typescript
export interface SerializedComposition {
  schemaVersion: "0.1.0";
  composition: {
    id: string;
    name: string;
    width: number;
    height: number;
    fps: number;
    duration: number;
    layers: SerializedLayer[];
  };
}

export function serializeComposition(comp: Composition): SerializedComposition;
export function deserializeComposition(data: unknown): Composition;
```
