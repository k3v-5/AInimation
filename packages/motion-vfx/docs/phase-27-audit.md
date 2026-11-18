# Auditoría de Arquitectura e Integración: Fase 27 — Standalone CLI, Public TypeScript SDK & Gold Master Certification (v3.0.0)

## 1. Existing Systems & Architecture
- **Motor Audiovisual Determinista (Fases 1–16)**
- **Control Plane MCP & Exportadores (Fases 17–19)**
- **Producción Autónoma & QA de 7 Familias (Fase 20)**
- **Persistencia CAS, Optimización A/B & Percepción (Fases 21–23)**
- **Orquestación Distribuida & Enjambre (Fase 24)**
- **Multi-Aspect Ratio & Social Delivery (Fase 25)**
- **Deep AE JSX Compiler & Bidirectional Bridge (Fase 26)**

## 2. Baseline de Pruebas
- **Total:** 597 tests.
- **Estado:** 100% pasando en verde en 4.91s.

## 3. Invariantes de la Fase 27
- **Determinismo en CLI y SDK:** Cualquier llamada vía CLI (`npx motion-engine ...`) o vía SDK (`MotionEngineSDK`) produce exactamente el mismo resultado y el mismo hash canónico que la ejecución interna.
- **Códigos de Salida UNIX Estándar:** 0 = Éxito, 1 = Error de validación/configuración, 2 = Error de ejecución de pipeline.
- **Cero Efectos Secundarios:** El CLI y SDK nunca mutan archivos sin instrucción explícita de salida.

## 4. Files to Create
- `src/cli/`: `CLIArgs.ts`, `CLIOutput.ts`, `CLIRunner.ts`, `index.ts`.
- `src/cli/commands/`: `RenderCommand.ts`, `ExportAECommand.ts`, `ExportSocialCommand.ts`, `QACommand.ts`, `ValidateCommand.ts`.
- `bin/motion-engine.js`.
- `src/sdk/`: `MotionEngineSDK.ts`, `index.ts`.
- `spec/phase-27-cli-sdk-gold-master.md`.
- `docs/milestone-30-gold-master.md`.
- Tests en `src/tests/cli/` y `src/tests/sdk/`.

## 5. Files to Modify
- `package.json` (actualizar versión a `3.0.0`, registrar campo `"bin"`).
- `src/index.ts` (exportar SDK y CLI).
- `docs/ROADMAP.md` y `README.md`.
