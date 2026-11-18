# Especificación Técnica: Fase 10 — Asset Intelligence & Media Library

**Documento:** `spec/phase-10-asset-intelligence-library.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulo:** `src/asset-library/`

---

## 0. Propósito y Principio Arquitectónico

La **Fase 10** construye la biblioteca de medios inteligente (*Semantic Media Library*), transformando archivos multimedia en crudo en entidades indexadas semánticamente, con detección automática de tomas (*shots*), análisis de composición y rostros, clasificación de licencias y recuperación vectorial de B-roll guiada por lenguaje natural:

$$\text{Raw Files} \longrightarrow \text{Ingestion Pipeline} \longrightarrow \text{Shot Segmentation \& Vision} \longrightarrow \text{Vector Index} \longrightarrow \text{Semantic Media API}$$

```
                           RAW ASSET (Video/Audio/Image)
                                        │
                                        ↓
                               ASSET INGESTION
                    (Metadata, SHA-256, Type, Proxies)
                                        │
                                        ↓
                            SHOT SEGMENTATION & VISION
                   (Shots [start, end], Objects, Actions, Camera)
                                        │
                                        ↓
                           COMPOSITION & FACE ANALYSIS
                    (Subject Box, Face Avoidance, Safe Areas)
                                        │
                                        ↓
                            SEMANTIC EMBEDDING STORE
                         (Vector Index & Cosine Distance)
                                        │
                                        ↓
                         LICENSE & PROVENANCE MANAGEMENT
                       (Royalty-Free, Personal, Restricted)
                                        │
                                        ↓
                           ASSET INTELLIGENCE SERVICE
                     (findBestVisual, semanticSearch, ranking)
```

---

## 1. Tipos y Esquema de Datos (`Asset`, `Shot`, `CompositionAnalysis`)

### 1.1. Toma de Video (*Shot*)
Cada archivo de video se subdivide en tomas continuas:
$$\text{Shot} = \{ \text{id}, \text{assetId}, \text{start}, \text{end}, \text{objects}, \text{environment}, \text{action}, \text{camera}, \text{qualityScore} \}$$

### 1.2. Análisis de Composición (*CompositionAnalysis*)
- Detección de rostros y posición de sujetos para evitar solapamiento de subtítulos.
- Cálculo de espacio negativo (*negative space*) y colores predominantes.

### 1.3. Búsqueda Semántica Multicriterio (*SemanticSearch*)
Puntuación de candidatos calculada mediante:
$$S_{\text{total}} = 0.45 \cdot S_{\text{vector}} + 0.20 \cdot S_{\text{quality}} + 0.20 \cdot S_{\text{duration}} + 0.15 \cdot S_{\text{composition}}$$
Filtrado estricto por licencias permitidas para exportación comercial.
