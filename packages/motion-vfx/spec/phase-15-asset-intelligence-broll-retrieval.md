# Especificación Técnica: Fase 15 — Asset Intelligence & B-Roll Retrieval Engine

**Documento:** `spec/phase-15-asset-intelligence-broll-retrieval.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulo:** `src/broll-retrieval/`

---

## 0. Propósito y Principio Arquitectónico

La **Fase 15** construye el motor de inteligencia de medios y recuperación de B-Roll (*B-Roll Retrieval & Asset Intelligence Engine*), permitiendo que las solicitudes abstractas del *AI Director* se resuelvan en clips precisos, seguros para texto/rostros, optimizados en sub-intervalos temporales y ordenados mediante ranking multicriterio:

$$\text{B-Roll Request} \longrightarrow \text{Hybrid Search} \longrightarrow \text{Multicriteria Ranking} \longrightarrow \text{Subclip Optimization} \longrightarrow \text{Explainable Recommendations}$$

```
                           B-ROLL REQUEST
                 (Intent, Duration, Style, TextSafe)
                                │
                                ↓
                          HYBRID SEARCH
                 (Semantic, Tags, Objects, OCR)
                                │
                                ↓
                      MULTICRITERIA RANKING
        (Semantic + Visual + Quality + TextSafe - ReusePenalty)
                                │
                                ↓
                       SUBCLIP OPTIMIZER
              (Optimal [tStart, tEnd] Time Window)
                                │
                                ↓
                      B-ROLL RESOLVER
              (Best Clip + Explainable Alternatives)
```

---

## 1. Módulos y Capacidades Clave

### 1.1. Metadatos Multimodales e Indexación de Assets (`AssetCatalogIndex`)
- Huellas digitales perceptuales (*Perceptual Hash*) y detección de duplicados / cuasi-duplicados.
- Indexación de tomas (*shots*), objetos, rostros, texto OCR y regiones seguras (*text-safe* en `left`, `center`, `right`).

### 1.2. Motor de Ranking Multicriterio (`AssetRankingEngine`)
- Puntuación ponderada combinando relevancia semántica, similitud visual, calidad técnica, compatibilidad estilística, espacio negativo y penalización por reutilización (*reuse penalty*).
- Desglose explicativo de puntuaciones (*Explainable Retrieval*).

### 1.3. Optimizador de Subclips Temporales (`SubclipOptimizer`)
- Extracción de la mejor ventana temporal $[t_{\text{start}}, t_{\text{end}}]$ dentro de un clip largo para satisfacer la duración exacta demandada por el *AI Director*.

### 1.4. Resolvedor de B-Roll y Alternativas (`BRollResolver`)
- Integración directa con el *AI Director*: resolución de `BRollRequest` en candidatos principales y lista ordenada de alternativas para reemplazo interactivo.
