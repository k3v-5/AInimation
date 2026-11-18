# Spike Técnico: Conexión Real con Adobe Character Animator (P0)

## 1. Análisis de la Integración Actual (`adobe-mcp`)
Revisando el código fuente de `adobe-mcp` (específicamente `server/adobe_mcp.py`), encontramos cómo se integran las distintas aplicaciones de Adobe en Windows:

```python
    "characteranimator": {
        "com_id": None,
        "process": "Character Animator.exe",
        "extendscript": False,
        "jsx_target": None,
        "display": "Adobe Character Animator",
    },
```

### Limitaciones Identificadas:
1. **No COM Object (`com_id: None`):** Character Animator no expone un objeto de automatización COM en Windows (a diferencia de Photoshop, Premiere, etc., que exponen `Photoshop.Application`).
2. **No ExtendScript (`extendscript: False`):** Character Animator no tiene soporte oficial de scripting .jsx mediante el motor clásico de Adobe (ExtendScript Toolkit).

Debido a esto, la herramienta original `adobe-mcp` solo puede realizar un monitoreo básico de si el proceso `Character Animator.exe` está corriendo vía PowerShell, pero **no expone APIs internas de manipulación de puppets, timelines o exportación.**

## 2. Estrategias de Control Profundo (Deep Integration)

Dado que las vías tradicionales de Adobe (COM y JSX) están bloqueadas, tenemos que evaluar vías alternativas para cumplir con la Fase 2 / Milestone 2 de la arquitectura Agentic Animation.

### Estrategia A: OS UI Automation (PyAutoGUI / RPA)
* **Descripción:** Usar bibliotecas de automatización del sistema operativo (ej. PyAutoGUI o PyWinAuto) para inyectar clics y atajos de teclado directamente en la interfaz de usuario de Character Animator.
* **Pros:** Permite controlar casi cualquier flujo que un humano pueda hacer.
* **Contras:** Muy frágil. Depende de resoluciones de pantalla, idiomas de la interfaz y tiempos de carga impredecibles. Rompe fácilmente la capa de "Perception" (es difícil validar el Observed State si solo mandas clics a ciegas).
* **Veredicto:** Evitar en un producto *Agentic* robusto, usar solo como último recurso.

### Estrategia B: Manipulación directa de archivos (.chproj)
* **Descripción:** Los proyectos de Character Animator se guardan en carpetas con un archivo `.chproj`. Este archivo podría ser internamente SQLite, XML o JSON. Si entendemos su estructura, podemos inyectar assets y escenas antes de que el usuario lo abra.
* **Pros:** Completamente "headless", 100% determinista.
* **Contras:** Si el formato es propietario y ofuscado, modificarlo corromperá el proyecto. Requiere ingeniería inversa profunda del formato de archivo de Adobe.

### Estrategia C: Dynamic Link / Integración vía After Effects (Estrategia Recomendada)
* **Descripción:** Adobe Character Animator soporta "Dynamic Link" con After Effects y Premiere Pro. Además, podemos exportar escenas y puppets usando scripts desde *otras* aplicaciones. Dado que After Effects SÍ tiene una integración COM y ExtendScript profunda (`com_id: AfterEffects.Application`), la IA puede construir la escena en AE y vincular el puppet de CH.
* **Pros:** Altamente estable. Aprovecha el ecosistema Adobe.
* **Contras:** Requiere que After Effects actúe como un intermediario o puente.

## 3. Implementación Propuesta para Iteración 2

Dado que no podemos modificar el código C++ cerrado de Character Animator, para lograr `AC-04 (Conexión Real)` de forma resiliente, el **Animation Engine** implementará una combinación de técnicas en el `CharacterAnimatorProvider`:

1. **Gestión de Proyectos vía File System:** El provider puede crear copias de plantillas pre-armadas (`.chproj`) copiando carpetas lógicas.
2. **OS Automation Controlado (CLI Hooks):** Iniciar Character Animator pasándole por línea de comandos el proyecto objetivo: `Character Animator.exe "ruta\al\proyecto.chproj"`.
3. **Perception vía OCR / Lectura de Logs:** Para la validación del "Observed State" sin acceso a API, el motor puede monitorear las carpetas de exportación (ej. ver si apareció un archivo `.png` o `.mp4` tras enviar el atajo de render) o leer los logs locales de sesión de Adobe ubicados en `%AppData%\Adobe\Character Animator`.

## 4. Modificaciones en el Código
Para reflejar esta investigación y cumplir la Iteración 2 temporalmente sin romper la arquitectura:
Añadiremos capacidades simuladas de OS Automation dentro del `CharacterAnimatorProvider` que representen estos flujos de archivo y CLI.
