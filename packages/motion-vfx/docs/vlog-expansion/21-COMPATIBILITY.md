# 🌐 MATRIZ DE COMPATIBILIDAD Y ENTORNO
## VLOG INTELLIGENCE ENGINE (v3.5.x)
**Documento:** `docs/vlog-expansion/21-COMPATIBILITY.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Definir la matriz de compatibilidad con versiones de software anfitrión (Adobe After Effects), sistemas operativos, entornos de ejecución Node.js y formatos de contenedor audiovisual.

## 2. Alcance
- Compatibilidad con Adobe After Effects CC 2021, 2022, 2023, 2024 y 2025.
- Compatibilidad bilingüe completa con After Effects en **Español** (`es_ES` / `es_LA`) e **Inglés** (`en_US`).
- Soporte para Windows 10/11, macOS 12+ y Ubuntu 20.04+.
- Soporte para Node.js 18 LTS, 20 LTS y 22+.

## 3. No Alcance
- No soporta versiones obsoletas de After Effects anteriores a CC 2020 (v17.0).

## 4. Entradas
- Detección del entorno de ejecución y lenguaje del host.

## 5. Salidas
- Código ExtendScript universal que se ejecuta limpiamente sin importar el idioma de After Effects.

## 6. Interfaces
```typescript
export interface EnvironmentCompatibilityMatrix {
  readonly supportedNodeVersions: string[];
  readonly supportedAEVersions: string[];
  readonly supportedAELanguages: string[];
  readonly supportedOS: string[];
}
```

## 7. Configuración
```typescript
export const COMPATIBILITY_MATRIX: EnvironmentCompatibilityMatrix = {
  supportedNodeVersions: ["18.x", "20.x", "22.x"],
  supportedAEVersions: ["2021", "2022", "2023", "2024", "2025"],
  supportedAELanguages: ["es_ES", "es_LA", "en_US", "en_GB", "fr_FR", "de_DE"],
  supportedOS: ["win32", "darwin", "linux"],
};
```

## 8. Algoritmo
- Uso de Universal Match Names en ExtendScript:
  - `property("ADBE Root Vectors Group")` con fallback a `property("Contents")` y `property("Contenido")`.
  - `property("ADBE Text Properties").property("ADBE Text Document")` con fallback a `layer.text.sourceText`.

## 9. Reglas de Negocio
- **RN-COMP01:** Prohibido el uso de strings de nombres de propiedades localizadas sin Match Name universal.

## 10. Invariantes
- **INV-COMP01:** Todo script JSX generado debe ejecutarse sin errores en una instalación de After Effects en Español puro.

## 11. Casos Normales
- Ejecución en After Effects 2024 en Español de México: Se crean las formas, textos y efectos sin errores de objeto nulo.

## 12. Casos Límite
- Versiones antiguas de After Effects sin soporte de ciertas expresiones: El compilador genera sintaxis compatible con el motor JavaScript legado y moderno.

## 13. Errores
- `CompatibilityViolationError`.

## 14. Recuperación
- Encapsulamiento con bloques `try { ... } catch(e) { ... }` para propiedades opcionales.

## 15. Determinismo
- Mismo script generado es compatible universalmente.

## 16. Rendimiento
- Sin sobrecarga en tiempo de ejecución.

## 17. Dependencias
- Node.js `process.platform`.

## 18. Compatibilidad
- Núcleo temático de este documento.

## 19. Seguridad
- Compatibilidad probada sin requerir permisos de administrador.

## 20. Tests
- Tests de compatibilidad en `src/tests/automation/vlog/compatibility/CompatibilityMatrix.test.ts`.

## 21. Fixtures
- Scripts de validación de sintaxis ExtendScript.

## 22. Golden Tests
- Validación de scripts JSX en entornos bilingües.

## 23. Integración
- Aplicado en `AfterEffectsJSXCompiler`.

## 24. Definition of Done
- Scripts JSX certificados para After Effects en Español e Inglés.
