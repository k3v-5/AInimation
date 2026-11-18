# 🎬 Especificación de Pipeline de Renderizado y Manifiestos de Entrega

**Estándar:** `Autonomous After Effects MCP — Rendering & Export Pipeline Specification`  
**Referencia:** `REQ-008`, `REQ-028`  

---

## 1. Manifiesto de Renderizado Canónico (`RenderManifest`)

Cada proceso de renderizado produce un artefacto criptográfico con la firma completa de producción:

```json
{
  "manifestVersion": "1.0.0",
  "projectHash": "a1b2c3d4...",
  "compositionId": "comp_main_9x16",
  "engineVersion": "v3.0.0-gold-master",
  "compilerVersion": "v3.0.0",
  "renderSettings": {
    "resolution": [1080, 1920],
    "fps": 60.0,
    "codec": "H.264 / NVENC",
    "audioCodec": "AAC 320kbps 48kHz"
  },
  "qaScore": 96.5,
  "outputFile": "F:/Dev/after-effects-mcp/dist/render/final_output.mp4"
}
```

---

## 2. Aceleración por Hardware y GPU

El pipeline utiliza el decodificador y codificador por hardware **NVIDIA GeForce RTX 5070 (NVENC / CUDA)** con bitrate optimizado para redes sociales ($8-10\text{ Mbps}$ en vertical $9:16$ a $60\text{ fps}$) para garantizar archivos ultralivianos y renderizado en tiempo real.
