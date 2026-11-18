# 🔒 SEGURIDAD, SANITIZACIÓN Y BLINDAJE
## VLOG INTELLIGENCE ENGINE (v3.5.x)
**Documento:** `docs/vlog-expansion/19-SECURITY-AND-SAFETY.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Establecer las directivas de seguridad para prevenir vulnerabilidades de inyección de código ExtendScript, inyección de comandos en terminales de audio (FFmpeg/Whisper/Piper), desbordamientos de memoria (*OOM*) y accesos indebidos a rutas del sistema de archivos (*Path Traversal*).

## 2. Alcance
- Sanitización y escape riguroso de cadenas de texto y metadatos inyectados en scripts `.jsx`.
- Normalización y validación de rutas de archivo con `path.resolve` impidiendo accesos fuera del workspace del usuario.
- Límites de tamaño en buffers y duración máxima de transcripciones.

## 3. No Alcance
- No gestiona autenticación de red (el servidor MCP opera localmente vía `stdio`).

## 4. Entradas
- Cadenas de texto no confiables (transcripciones, nombres de archivo de usuario, parámetros de MCP).

## 5. Salidas
- Cadenas sanitizadas y rutas normalizadas seguras.

## 6. Interfaces
```typescript
export interface PathSecurityPolicy {
  readonly allowedBaseDirectories: string[];
}
```

## 7. Configuración
- Límite máximo de texto: 50,000 caracteres por lote.

## 8. Algoritmo
- Escape de caracteres `\`, `"`, `'`, saltos de línea y bytes nulos `\0` antes de interpolar en scripts JSX.
- Validación de que toda ruta pertenezca a los directorios permitidos del usuario.

## 9. Reglas de Negocio
- **RN-SEC01:** Prohibida la interpolación directa de variables sin sanitizar en plantillas JSX o comandos de terminal.

## 10. Invariantes
- **INV-SEC01:** Ningún script JSX generado puede ejecutar código fuera del bloque `app.beginUndoGroup()` / `app.endUndoGroup()`.

## 11. Casos Normales
- Texto con comillas y barras invertidas `El vlogger dijo "¡Hola \ Guadalajara!"`: Escapado correctamente sin romper el parser ExtendScript.

## 12. Casos Límite
- Ruta maliciosa `../../../../Windows/System32`: Rechazada con `PathTraversalError`.

## 13. Errores
- `SecurityViolationError`, `PathTraversalError`.

## 14. Recuperación
- Rechazo inmediato de la operación insegura.

## 15. Determinismo
- La función de sanitización es puramente determinista.

## 16. Rendimiento
- Sobrecarga de sanitización $< 0.05\text{ms}$.

## 17. Dependencias
- `path` de Node.js nativo.

## 18. Compatibilidad
- Compatible con sintaxis ExtendScript de After Effects.

## 19. Seguridad
- Núcleo temático de este documento.

## 20. Tests
- Tests de sanitización en `src/tests/automation/vlog/security/SecuritySanitization.test.ts`.

## 21. Fixtures
- Payloads de prueba con intentos de escape e inyección.

## 22. Golden Tests
- Verificación de salidas escapadas.

## 23. Integración
- Aplicado en `AfterEffectsJSXCompiler` y generadores de comandos CLI.

## 24. Definition of Done
- Tests de seguridad pasando al 100%.
