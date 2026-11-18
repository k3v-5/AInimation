# 🔒 Especificación de Seguridad, Sandbox y Control de Recursos

**Estándar:** `Autonomous After Effects MCP — Security & Sandbox Specification`  
**Referencia:** `REQ-029`, `REQ-030`, `REQ-031`  

---

## 1. Vector de Seguridad y Prevención de Explotación

El servidor MCP opera bajo un modelo de privilegios mínimos (*Principle of Least Privilege*):

1. **Sandboxing de Sistema de Archivos:**
   - Toda lectura y escritura de archivos se valida contra `PathSanitizer.sanitize(filePath, safeBaseDir)`.
   - Bloqueo total de Path Traversal (`../`, `..\\`, rutas absolutas no autorizadas).
2. **Prohibición de Ejecución Arbitraria:**
   - La IA nunca puede ejecutar comandos de consola (`shell`), scripts binarios o código ExtendScript no generado por el compilador formal.
3. **Límites de Recursos (Resource Exhaustion Prevention):**
   - `max_layers_per_comp`: 500
   - `max_keyframes_per_property`: 5,000
   - `max_duration_sec`: 3,600 (1 hora)
   - `max_operations_per_transaction`: 100
