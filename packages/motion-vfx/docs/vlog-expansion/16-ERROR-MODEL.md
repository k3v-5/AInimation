# 🛡️ MODELO DE ERRORES Y DIAGNÓSTICO
## VLOG INTELLIGENCE ENGINE (v3.5.x)
**Documento:** `docs/vlog-expansion/16-ERROR-MODEL.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Definir la jerarquía completa de errores tipados, códigos de fallo estandarizados y protocolos de diagnóstico para la capa Vlog Intelligence, asegurando que ningún fallo produzca excepciones genéricas o estados corruptos sin contexto.

## 2. Alcance
- Jerarquía de clases que heredan de `MotionEngineError`.
- Códigos de error unificados: `INVALID_MEDIA_REFERENCE`, `INVALID_TIME_RANGE`, `CROSSFADE_OVERLAP`, `TRANSCRIPT_ALIGNMENT_ERROR`, `UNSUPPORTED_LANGUAGE`, `PACING_VIOLATION`.
- Contexto diagnóstico serializable en cada excepción.

## 3. No Alcance
- No reemplaza los errores base del Core v3.4.0 (`ValidationError`, `HierarchyCycleError`, etc.).

## 4. Entradas
- Condiciones de error detectadas en runtime.

## 5. Salidas
- Instancias de excepción estructuradas con `name`, `message`, `code` y `context`.

## 6. Interfaces
```typescript
export class VlogIntelligenceError extends MotionEngineError {
  constructor(message: string, public readonly code: string, public readonly context?: Record<string, any>) {
    super(`[VlogIntelligence:${code}] ${message}`);
  }
}
```

## 7. Configuración
- Políticas de severidad (Fatal vs Advertencia).

## 8. Algoritmo
1. Al detectar una violación de invariante, instanciar la subclase de error específica.
2. Adjuntar los datos diagnósticos (timestamps, duraciones, IDs).
3. Lanzar la excepción o registrar advertencia según la política del módulo.

## 9. Reglas de Negocio
- **RN-ERR01:** Prohibido `throw new Error(...)` genérico en todo el código de la expansión.

## 10. Invariantes
- **INV-ERR01:** Todo error lanzado contiene una propiedad `code` en mayúsculas con formato `SNAKE_CASE`.

## 11. Casos Normales
- Detección de timestamp inválido: Lanza `InvalidTimeRangeError` con `{ start: 10, end: 5 }`.

## 12. Casos Límite
- Errores anidados: El contexto incluye la causa original (`cause`).

## 13. Errores
- Catálogo completo de clases de error documentado.

## 14. Recuperación
- Mecanismos de degradación elegante cuando el error no compromete la integridad del proyecto.

## 15. Determinismo
- Mismo fallo produce exactamente el mismo código y mensaje de error.

## 16. Rendimiento
- Sobrecarga de instanciación de error despreciable ($< 0.1\text{ms}$).

## 17. Dependencias
- `src/errors/index.ts` del Core v3.4.0.

## 18. Compatibilidad
- Compatible con el formateador de errores JSON-RPC del servidor MCP.

## 19. Seguridad
- Sanitización de rutas en mensajes de error para no exponer información sensible del sistema de archivos.

## 20. Tests
- Tests unitarios verificando la captura y códigos de error en `src/tests/automation/vlog/errors/ErrorModel.test.ts`.

## 21. Fixtures
- Entradas inválidas controladas para provocar cada clase de error.

## 22. Golden Tests
- Verificación de estructura JSON de error.

## 23. Integración
- Utilizado transversalmente por todos los submódulos de la capa vlog.

## 24. Definition of Done
- Jerarquía de errores implementada y probada al 100%.
