# 📐 Especificación de la Representación Intermedia Canónica (Project IR)

**Estándar:** `Autonomous After Effects MCP — Project IR Specification`  
**Referencia:** `REQ-001`, `REQ-002`, `REQ-003`, `REQ-004`  

---

## 1. Modelo de Datos Formal

La Representación Intermedia Canónica (`ProjectIR`) es una estructura serializable en JSON validada estrictamente por esquemas Zod en tiempo de ejecución.

### Esquema Canónico Principal:
```typescript
export interface CanonicalProjectIR {
  schemaVersion: "3.0.0";
  projectId: string; // UUID v4 inmutable
  version: number; // Contador de versión monótono
  hash: string; // Hash SHA-256 canónico del estado
  metadata: {
    title: string;
    author: string;
    createdAt: string;
    engineVersion: string;
    compilerVersion: string;
  };
  compositions: CompositionIR[];
  assets: AssetManifestIR[];
  colorProfile: "sRGB" | "Rec709" | "DisplayP3";
}

export interface CompositionIR {
  id: string; // UUID inmutable
  name: string;
  width: number;
  height: number;
  fps: number;
  duration: number;
  backgroundColor: [number, number, number, number]; // RGBA [0, 1]
  tracks: TrackIR[];
  markers?: MarkerIR[];
}
```

---

## 2. Invariante de Hashes Deterministas

El hash de un proyecto se calcula como el digest SHA-256 de su serialización JSON normalizada (claves ordenadas alfabéticamente y flotantes redondeados con precisión determinista $\epsilon = 10^{-6}$):

$$\text{ProjectHash} = \text{SHA256}(\text{CanonicalCanonicalStringify}(\text{ProjectIR}))$$
