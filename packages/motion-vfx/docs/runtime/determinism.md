# Determinismo Temporal y Cross-Process (Fase 18)

## Principios
- Dos ejecuciones independientes del mismo proyecto producen exactamente los mismos bytes serializados y el mismo hash SHA-256.
- `verifyDeterminism()` evalúa `comp.evaluate(t)` repetidas veces garantizando coincidencia exacta de hashes de frame.
- Libre de contaminación por `Date.now()`, `Math.random()`, locale, timezone o PID dentro de la IR canónica.
