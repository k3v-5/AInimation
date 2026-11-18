# Esquema de Serialización JSON: Fase 2 (v0.2.0)

**Documento:** `spec/serialization-schema-v0.2.0.md`  
**Estado:** VIGENTE / CONGELADO  
**Versión de Esquema:** `0.2.0`

---

## 1. Estructura Raíz del JSON v0.2.0

```json
{
  "schemaVersion": "0.2.0",
  "composition": {
    "id": "comp_1",
    "name": "Full Motion Scene",
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "duration": 10.0
  },
  "assets": [
    {
      "id": "logo_asset",
      "type": "image",
      "path": "assets/logo.png",
      "metadata": { "width": 512, "height": 512 }
    },
    {
      "id": "bg_music",
      "type": "audio",
      "path": "assets/music.mp3",
      "metadata": { "duration": 120 }
    }
  ],
  "elements": [
    {
      "id": "title_main",
      "name": "Main Title",
      "type": "text",
      "timing": { "startTime": 0.0, "endTime": 5.0, "enabled": true },
      "transform": {
        "position": {
          "type": "vector2",
          "baseValue": { "x": 540, "y": 960 },
          "keyframes": []
        },
        "scale": {
          "type": "vector2",
          "baseValue": { "x": 1.0, "y": 1.0 },
          "keyframes": []
        },
        "rotation": { "type": "number", "baseValue": 0, "keyframes": [] },
        "opacity": { "type": "number", "baseValue": 1.0, "keyframes": [] },
        "anchorPoint": { "type": "vector2", "baseValue": { "x": 0.5, "y": 0.5 }, "keyframes": [] }
      },
      "text": {
        "content": { "type": "string", "baseValue": "Hola Motion Engine", "keyframes": [] },
        "fontFamily": "Inter",
        "fontSize": { "type": "number", "baseValue": 96, "keyframes": [] },
        "fontWeight": 700,
        "color": {
          "type": "color",
          "baseValue": { "r": 1, "g": 1, "b": 1, "a": 1 },
          "keyframes": []
        },
        "alignment": "center",
        "lineHeight": { "type": "number", "baseValue": 1.2, "keyframes": [] },
        "letterSpacing": { "type": "number", "baseValue": 0, "keyframes": [] }
      }
    }
  ]
}
```

---

## 2. Invariantes y Reglas de Compatibilidad

1. **Schema Versioning:**
   - Proyectos serializados en `v0.2.0` especifican `"schemaVersion": "0.2.0"`.
   - El deserializador acepta tanto `"0.2.0"` como `"0.1.0"` (retrocompatibilidad).
2. **Validación de Assets:**
   - Cualquier elemento de tipo `image`, `video` o `audio` debe referenciar un `assetId` registrado en `assets: [...]`. Si no existe, se lanza `ValidationError`.
3. **Serialización Determinista:**
   - Las listas de assets y elementos preservan el orden exacto.
   - Las propiedades dentro de los objetos se serializan con orden de claves determinista.
