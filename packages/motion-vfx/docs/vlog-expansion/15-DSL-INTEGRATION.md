# 📝 DECLARATIVE PRODUCTION DSL INTEGRATION
## ESPECIFICACIÓN TÉCNICA DEL MÓDULO (v3.5.x)
**Documento:** `docs/vlog-expansion/15-DSL-INTEGRATION.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Extender el Declarative Production DSL (`ProductionDSL`) de v3.4.0 para permitir definir producciones completas de vlog mediante bloques declarativos concisos en JSON/TypeScript, incluyendo directivas de jump cut automático, emparejamiento de B-Roll y generación multi-idioma en una sola invocación declarativa.

## 2. Alcance
- Definición de nuevas directivas DSL: `vlogMode: true`, `autoJumpCut: true`, `targetLanguages: ["es", "en"]`, `travelOverlays: [...]`.
- Compilación de 1 paso desde el DSL hacia el `FinalVlogEditPlan` y `ProjectIR`.
- Preservación del 100% de compatibilidad con las directivas DSL existentes de v3.4.0.

## 3. No Alcance
- No modifica la gramática de bajo nivel de las capas primitivas de `ProjectIR`.

## 4. Entradas
- Declaración `ProductionDSLScript` con bloques de vlog.

## 5. Salidas
- `ProjectIR` compilado y validado mediante `ProjectValidator`.

## 6. Interfaces
```typescript
export interface VlogProductionDSLConfig {
  readonly aRollSource: string;
  readonly bRollDirectory?: string;
  readonly transcriptText?: string;
  readonly targetLanguages?: SupportedLanguage[];
  readonly autoJumpCut?: boolean;
  readonly punchInScale?: number;
  readonly travelOverlays?: TravelOverlayInstance[];
}
```

## 7. Configuración
- Hereda valores por defecto de los módulos subyacentes.

## 8. Algoritmo
1. Parsear el bloque DSL.
2. Si `vlogMode === true`, invocar `VlogJumpCutEngine` y `SemanticBrollMatcher`.
3. Si `targetLanguages` está presente, orquestar `LocalizationPipeline`.
4. Compilar los resultados a elementos de pista estándar en `ProjectIR`.

## 9. Reglas de Negocio
- **RN-DSL01:** La sintaxis declarativa debe ser legible para humanos e inteligible para modelos LLM.

## 10. Invariantes
- **INV-DSL01:** Todo script DSL válido compila a un `ProjectIR` que pasa `ProjectValidator.assertValid()`.

## 11. Casos Normales
- Definición de un vlog con 3 líneas de configuración declarativa que produce un proyecto completo de After Effects.

## 12. Casos Límite
- DSL con parámetros omitidos: Aplica valores por defecto inteligentes.

## 13. Errores
- `DSLCompilationError`: Declaración malformada o tipos incompatibles.

## 14. Recuperación
- Mensajes de error claros señalando la línea y propiedad defectuosa.

## 15. Determinismo
- 100% determinista.

## 16. Rendimiento
- Compilación del DSL en $< 10\text{ms}$.

## 17. Dependencias
- `ProductionDSL` de v3.4.0.

## 18. Compatibilidad
- Totalmente compatible con el parser existente.

## 19. Seguridad
- Validación previa mediante Zod Schema.

## 20. Tests
- Tests unitarios en `src/tests/automation/vlog/dsl/VlogDSLIntegration.test.ts`.

## 21. Fixtures
- Ejemplos de scripts DSL de vlog.

## 22. Golden Tests
- Snapshot de `ProjectIR` compilado.

## 23. Integración
- Integrado en `src/workflows/ProductionDSL.ts`.

## 24. Definition of Done
- Compilador DSL actualizado y probado con 100% de éxito.
