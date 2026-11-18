# Reglas de trabajo en DarX

Cada regla de aquí salió de un fallo **real** de este proyecto, con fecha. No hay
consejos genéricos: si algo está escrito es porque costó tiempo descubrirlo.

La mayoría de los errores los cometí yo. Están incluidos con el mismo detalle que
los demás, porque una regla sin la cicatriz que la produjo no convence a nadie y
se acaba saltando.

---

> **¿Vienes de cero?** [INDICE-CONOCIMIENTO.md](INDICE-CONOCIMIENTO.md) es el
> mapa de todo: memoria, skill y documentación, y en qué orden leerlo.

## Regla 0 · La que resume todas las demás

> **Medir, no deducir. Y antes de fiarte de la medida, comprobar el instrumento.**

En un solo día, razonar en vez de medir salió mal **cuatro veces**: el convenio
de ejes, la rotación de los enemigos, la distancia del dash y la densidad de
texel. Y **tres veces** el instrumento de medida estaba roto y decía «todo bien».

Cuando una comprobación no se queja, hay dos posibilidades —que esté bien, o que
la comprobación no sirva— y **no son distinguibles sin probarla contra un fallo
conocido**.

### Diagnóstico Empírico Inmediato ante Fallos (Prohibido Adivinar)

**Qué pasó (23-ago):** Al fallar la visualización de mallas en runtime y quedar el personaje inmóvil, se intentaron resolver los problemas asumiendo hipótesis teóricas sucesivas. Un script de diagnóstico de 50 líneas (`Art/diagnostico_profundo.py`) reveló en 3 segundos la causa real: los assets estaban 100% correctos y compilados, pero el proceso de Unreal Editor abierto en memoria retenía los CDOs anteriores a la compilación.

**La regla:** Ante el primer fallo de carga, render o comportamiento, **crear y ejecutar de inmediato un script local de diagnóstico (.py/.ps1) o volcado de logs**. Medir el estado de la memoria y del motor antes de cambiar código a ciegas.

---

## Exportar e importar

### 1 · El `.blend` es una CACHÉ, no la fuente

La fuente son los `.py`. El `.blend` es el resultado de ejecutarlos.

**Qué pasó (20-ago, 21:01):** se exportaron los FBX y **después** se siguieron
editando `darx_player.py` (21:09) y `darx_fps.py` (21:13). Los FBX en disco no
tenían los dos últimos cambios —el arma blanca y los circuitos— y **nada avisó**.
Importar habría traído un modelo viejo con aspecto de estar al día.

Antes había pasado la versión grave: el `.blend` guardado era de dos días atrás y
le faltaba **todo** el trabajo de arte reciente.

**La regla:** no exportar a mano. Ejecutar siempre:

```
blender.exe --background DarX_Assets.blend --python rehacer_todo.py
```

Reconstruye desde los `.py`, valida, exporta y **guarda el `.blend`**. No hace
falta tener Blender abierto.

**Cómo se comprueba:** ningún `.py` de `Art/Blender/` puede ser más nuevo que el
FBX más antiguo. Si lo es, el export está caducado.

### 2 · Nunca digas «ya está exportado» sin mirar la fecha

Es la afirmación más fácil de verificar y la que más veces ha sido falsa. Cuesta
un `ls`. Decirlo sin comprobarlo hace que el siguiente paso se construya sobre
arena.

### 3 · Una animación de UN frame dura CERO, y Unreal la rechaza

**Qué pasó:** las cinco poses del AimOffset se hicieron de 1 frame porque un
AimOffset solo usa la pose. Sin rango de animación el FBX sale sin datos, el
importador no lo reconoce, **cae al factory de StaticMesh** y falla con «no se
pudo crear el recurso». El pipeline dijo «importando 28» y en disco aparecieron
**23**. Nadie cuenta 28 uassets a mano.

**La regla:** mínimo dos claves. Dos frames idénticos dan 1/30 s y el AimOffset
sigue leyendo el instante 0.

### 4 · Una esquelética exportada sin su armadura falla igual

Misma firma —`FactoryCreateFile: StaticMesh`— y síntomas que parecen tres bugs
distintos. `export_fbx` ya selecciona la armadura sola; no tocarlo.

### 5 · Después de importar, REINICIA el editor

Reimportar invalida los punteros de las clases C++. Sin reiniciar, los enemigos
salen **invisibles** y `verificar_assets.py` lo dirá con `skinned_asset = None`.
No es un bug nuevo cada vez: es siempre el mismo.

---

## Modelado

### 6 · Suavizar sin añadir segmentos no redondea nada

**Qué pasó (bien):** al pasar el cuerpo a liso se subió `seg` de **6 a 12**
además de poner `smooth=True`. Correcto, y es la parte que se hace mal casi
siempre: sombrear suave una sección de 6 lados no da un tubo redondo, da un
hexágono con sombreado raro y se ve peor que facetado.

**La regla:** `smooth=True` y `seg` alto van juntos, siempre.

### 7 · La cápsula NO es negociable

Radio **34**, media altura **96**. El validador de QA aprueba corredores contando
con ese volumen; un personaje más ancho no pasaría por pasillos que el QA dio por
buenos, y el bug aparecería como «me quedo atascado aquí» en un sitio que el
validador jura que es transitable.

**Y ojo con la cuenta:** `X_HOMBRO` es la posición del **hueso**, no el borde. El
radio del miembro se suma encima. Con 0.300 y una clavícula de radio 0.078 el
modelo salió de **0.758 m**, un 22% por encima del límite. La cuenta correcta es
`X_HOMBRO + radio <= 0.31`.

El guardián de exportación lo comprueba en cada reconstrucción. **Si falla, no se
exporta** — no se negocia con él.

### 8 · Mide en REPOSO, no en pose

Medir la malla con una pose aplicada da anchos que no son reales. Una vez dio un
robot de 0.730 m que en reposo medía 0.672 — dentro de su cápsula. Falsa alarma
que casi provoca un rediseño.

### 9 · Un solo convenio de ejes: se modela mirando a −Y

Las tres esqueléticas se modelan a **−Y** y se corrigen en el actor con
`RotacionMalla`. Podría modelarse ya mirando a +X y ahorrarse la corrección, pero
entonces habría **dos convenios** y recordar cuál es cuál es exactamente como se
generó la confusión que costó el día 19-ago.

**Y el motivo de fondo, medido:** el exportador **NO** intercambia ejes. Las cotas
de Blender salen 1:1 en Unreal.

---

## Materiales y color

### 10 · El morado es del jugador. El rojo solo amenaza

Es la regla de identidad del juego. Nada del jugador es rojo, nada enemigo es
morado.

### 11 · Subir el emisivo NO hace que se note más — lava el color

Por encima de ~2.5 el morado se va a **rosa salmón** y pierde justo lo que lo
identifica. El brillo se gana con bloom y contraste, no subiendo el número.

Pasó con los proyectiles, con el visor y con los ojos de los enemigos.

### 12 · El color base es PLANO. No se pinta

`ARTE-BIBLIA.md` manda bloque de color puro. Lo que se modula es **rugosidad y
emisivo**, nunca el albedo. Un albedo pintado es más fácil, rompe la regla y
encima queda peor.

### 13 · «Sin textura» no es la regla — la regla es «sin suciedad»

Cita literal de la biblia. Están **prohibidos** desgaste, óxido, porosidad y
suciedad. Están **permitidos** trazos de circuito grabados, patrones
geométricos, paneles de fibra y líneas finas.

Yo mismo le dije al usuario que la biblia prohibía texturas. **Era falso.** Leer
el documento antes de citarlo.

### 14 · Una máscara gris NO se conecta a Normal

Una entrada de Normal espera un **vector tangencial**. Meterle un gris directo da
basura. Hace falta un `NormalFromHeightmap` de por medio.

Y más de fondo: la máscara de detalle son **líneas rectas en rejilla**, no ondas
orgánicas. Aunque se conectara bien, daría una cuadrícula, no pliegues líquidos.
Para eso hace falta ruido orgánico, que es otra textura.

### 15 · Un cuerpo mojado no se ve mojado si no hay nada que reflejar

El brillo especular es un espejo. En una sala blanca vacía devuelve blanco liso y
vuelves a tener una mancha. **El material perfecto seguirá viéndose plano, y se
culpará al material.**

El acabado del concepto necesita fuentes de luz **con forma** en el entorno. Es
tan parte del trabajo como el material.

---

## Verificación

### 16 · Un guardián nuevo se prueba contra un fallo REAL

**Qué pasó, dos veces seguidas y con el mismo guardián:**

Primero escribí uno que buscaba `AnimationStack` dentro del FBX para detectar
animaciones vacías. **No servía:** los ficheros rotos lo tienen, dos veces, igual
que los sanos, y pesan lo mismo (140 KB). Ni el tamaño ni el contenido los
delatan.

Lo reescribí para medir la duración… y puse el umbral en 2 cuando
`export_actions` devuelve el **span** (`frame_range[1] - frame_range[0]`), no el
número de claves. Una acción válida con claves en 0 y 1 devuelve **1**. El
guardián marcaba como rotas justo las cinco que acababa de arreglar.

Antes había pasado con `grep -a` sobre FBX binarios: devolvía 0 para los cuatro
ficheros, **incluido el que funcionaba**.

**La regla:** un guardián que no se queja no demuestra nada hasta que se le pone
delante un caso roto de verdad y lo caza.

### 17 · Dos guardianes no pueden contradecirse

`arreglar_colisiones.py` excluía las estelas de disparo a propósito y
`verificar_assets.py` les exigía colisión. Resultado: **dos FALLOS en cada
pasada** por algo correcto, y un cierre de «no juegues hasta arreglarlos».

Un verificador que grita por lo correcto **se deja de leer**, y entonces deja de
servir para lo que sí importa.

### 18 · Comprueba los NÚMEROS, no los mensajes

«importando 28 animaciones» y 23 uassets en disco conviven sin ninguna
contradicción visible. El log dice lo que **intentó**, no lo que **consiguió**.

Comprobaciones que valen: cuántos ficheros hay, qué fecha tienen, cuánto pesan.

---

## Rutas y comandos

### 19 · El proyecto es `E:\Darx_Proyect` — con GUION BAJO

Existió `E:\Darx Proyect` **con espacio**, con cuatro documentos viejos. Se borró
el 20-ago tras comprobar que su único contenido exclusivo estaba derogado.

Dolió de forma tonta: el directorio de trabajo era el del **espacio**, así que
los enlaces relativos resolvían contra la carpeta equivocada y «no cargaban». Los
ficheros estaban bien; lo roto era el camino.

**Usa rutas absolutas.** Y si algo «no carga», mira contra qué se resuelve la
ruta antes de mirar el fichero.

### 20 · La consola de Unreal no admite `&&`, y `py` ejecuta FICHEROS

`py "script.py" && py "montar()"` no hace nada: ni encadena, ni `py` acepta
instrucciones. Por eso los scripts del proyecto **se llaman a sí mismos** al
final (`main()`), y basta con un `py "ruta"`.

### 21 · Compilar: valida un fichero antes de gastar una build

```
compilar.ps1 -Archivo "ruta\al\fichero.cpp"    # 20-60 s, con el editor abierto
compilar.ps1 -Esperar                          # build entera, ~7 min
```

Requiere disciplina **IWYU**: cada `.cpp` incluye lo que usa. En build unity un
fichero puede compilar «de prestado» por lo que incluyó su vecino, y la
validación aislada lo destapa.

---

## Cómo informar del trabajo

### 22 · No des porcentajes de parecido

«90% de similitud con el concepto» no es medible y no ayuda a decidir nada. Di
**qué está hecho, qué falta y qué lo bloquea**.

En ese caso concreto el 90% era además engañoso: lo que quedaba fuera —material,
iluminación, animación— es la **mayor parte** del aspecto final, no un 10%.

### 23 · Separa lo hecho de lo propuesto

Un informe que mezcla «cambié X» con «tendrás que conectar Y» hace imposible
saber qué está en disco. Dos listas.

### 24 · Si te corriges, corrige y sigue

Este documento está lleno de errores míos porque **ocultarlos habría hecho que se
repitieran**. Decir «me equivoqué, era esto» y continuar vale más que defender
una versión que ya no se sostiene.

---

## Filosofía de Automatización

### 25 — Si se puede programar, se programa (Prioridad MCP / Código)
Antes de proponer ensamblar nodos a mano, importar archivos uno a uno o realizar tareas repetitivas en el Editor, **hay que preguntarse explícitamente si se puede automatizar por código o mediante MCP**. 
Este proyecto ya ha demostrado que generar modelos por código, materiales por script o MetaSounds vía `UMetaSoundBuilderSubsystem` es la única vía escalable. Hacer las cosas a mano es una oportunidad para cometer errores. El código garantiza reproducibilidad.

### 26 — Detección proactiva de patrones repetitivos y scripts para ahorro de tokens
Siempre que se detecte un patrón de acciones repetitivas (procesar lotes de audio, transformar múltiples mallas, orquestar decenas de clips/tracks en Ableton o verificar estados en bucle), **se debe crear inmediatamente un script local (`.py` o `.ps1`)**.
Ejecutar tareas en lote mediante scripts reduce drásticamente el consumo de tokens de contexto, evita la latencia de decenas de llamadas a herramientas individuales y garantiza ejecución atómica y reproducible.

### 27 — Documentación obligatoria de aprendizajes y de lo que NO funciona
Cada vez que se aprenda una nueva técnica, se descubra una limitación de una API o herramienta, o se confirme una forma en la que algo **falla o no funciona** (ejemplos: aislamiento de sesión de escritorio en subshells de Windows al lanzar GUIs, loops exportados de DAWs que contienen notas repetidas y requieren recorte a single-hit, retornos de `PlaySoundAtLocation` en Unreal), **se debe documentar de inmediato** en este archivo y en las reglas del workspace. Documentar el fallo evita que el agente o el equipo tropiecen dos veces con la misma piedra.

### 28 — Prohibición estricta de reutilizar o repetir diseños de personajes
Está terminantemente prohibido reutilizar, clonar o reciclar diseños de personajes, jefes o tropas (por ejemplo, asignar el modelo de un Boss a un enemigo normal, o pegar cubos/esferas genéricas sobre el maniquí base) a menos que el usuario lo solicite de manera explícita.
Cada enemigo, tropa o jefe debe contar con su propia silueta, proporciones, modelo y estética visual dedicada, coherente con sus mecánicas. Si no existe un asset adecuado, se debe generar un modelo o estructura dedicada mediante Blender MCP o scripts de modelado de assets.

### 29 — Previsualización obligatoria de diseños de personajes antes de importar a Unreal
**Qué pasó (23-ago)**: Se modelaron y exportaron directamente varios enemigos a Unreal Engine sin mostrar previamente las vistas previas de los modelos en Blender, descubriéndose desalineaciones de escudos y detalles de silueta recién en el motor de juego.
**La regla**: Antes de exportar FBX o importar mallas esqueletales/estáticas de personajes a Unreal Engine, **es obligatorio generar una captura o render del viewport de Blender y presentarla al usuario**. La importación y conexión en C++ solo se efectúa tras la confirmación visual del diseño.

### 30 — Protocolo de Cero Retrabajo (Ficha, Buffer de No-Clipping, 4-Vistas y Zero-Self-Collision)
**Qué pasó (23-ago)**: Se acumuló retrabajo en la fase de tropas al iterar a ciegas en Blender, sufrir clipping de brazos a través del escudo balístico y colisionar proyectiles/charcos ácidos con las cápsulas de los propios emisores.
**La regla**: Para cualquier nueva entidad o habilidad:
1. **Ficha de Diseño Previa**: Declarar silueta, 3 rasgos visuales únicos y animaciones antes de escribir código.
2. **Buffer de No-Clipping**: Mantener un offset de seguridad ($\ge 30\text{ cm}$) entre accesorios frontales/escudos y el torso, emparentando escudos rígidamente al hueso `chest`/`root`.
3. **Hoja 4-Vistas**: Renderizar Frontal, Trasera, Acción/Ataque y Vista FPS para aprobación del usuario antes de exportar FBX.
4. **Zero-Self-Collision**: Todo proyectil o efecto de área ignora por defecto a su emisor (`IgnoreActorWhenMoving(Owner, true)`) y clava su altura con raycast vertical estricto al suelo (`ECC_WorldStatic`).
5. **Lote Único**: Agrupar mallas, animaciones y clases en un único pipeline de exportación/importación sin pasos fragmentados.

### 31 — Estándar Integral de Audio: Sesión Única AbletonMCP + Ficha Vital + Contrato de Efectos
**Qué aprendimos**: Crear sonidos de forma fragmentada o con scripts aislados dificulta mantener la consistencia tímbrica y el balance de mezcla entre las armas, enemigos y el HUD.
**La regla**:
1. **Una Sola Sesión en Ableton**: Todo el universo sonoro de DarX vive en el proyecto central de Ableton Live operado vía AbletonMCP. Las pistas se organizan por grupos (Armas, Mobs, Bosses, HUD, Ambiente, Música).
2. **Contrato de Sonido Completo**: Ningún sonido se exporta sin contar con su ficha en el documento de análisis/contrato:
   - **Propósito**: Evento de activación en Unreal y duración estricta.
   - **Timbre**: Explicación perceptiva del sonido.
   - **Cadena AbletonMCP**: Instrumentos (`query:Synths#...`), efectos en serie (`query:AudioFx#...`), automatización de macros y clips en la línea de tiempo.
3. **Exportación y Normalización Atómica**: Al exportar lotes desde Ableton Live, seleccionar siempre *'Todas las pistas individuales'* con clips alineados en la línea de tiempo del Arrangement (compás 1.1.1). Cada preset independiente de Vital u otro sintetizador debe habitar en **su propia pista MIDI individual** para no compartir patches ni generar renders cruzados. El script de procesamiento posterior debe recortar silencios al transitorio en $0\text{ ms}$, preservar ciclos rítmicos exactos en loops y normalizar a $-3.0\text{ dBFS}$ Mono $48\text{ kHz}$.

### 32 — Documentación Obligatoria de Procesos Nuevos y Registro del «Por Qué»
**Qué aprendimos**: Ejecutar integraciones complejas sin documentar el proceso hace que futuras expansiones dependan de adivinar pasos o rediscutir decisiones tomadas.
**La regla**:
1. **Documentar al terminar**: Ningún proceso nuevo se da por cerrado hasta contar con su documento maestro en `docs/`.
2. **Explicar el porqué**: Registrar la justificación de cada parámetro técnico, de diseño y psicoacústico.
3. **Indexar en el mapa**: Registrar el enlace en `docs/INDICE-CONOCIMIENTO.md`.

### 33 — Ejecución Obligatoria del Sistema de Tests Automatizados (`.\ejecutar_tests.ps1`)
**Qué aprendimos**: Realizar cambios en C++, shaders, mallas o niveles sin una verificación automatizada unificada puede introducir regresiones silenciosas (flags de instancing desactivados, cubos de plantilla residuales, spawn penetrando colisiones).
**La regla**:
1. Antes de dar por concluida cualquier modificación de código o contenido, **se debe ejecutar obligatoriamente `.\ejecutar_tests.ps1`**.
2. Los 7 módulos de prueba (Compilación C++, 16 Shaders PBR, 14 Mallas Modulares, Limpieza de Nivel, Generación Incursión, Generación Sandbox y Spawn Seguro) deben arrojar `[PASS]` al $100\%$.

### 34 — Desacople Estricto entre el Generador Sandbox (AWorldGenActor) y el Generador de Incursión (ADarxGeneradorMundo)
**Qué aprendimos (23-ago)**: El juego poseía dos generadores: el generador antiguo `AWorldGenActor` (que generaba el pasillo de cubos blancos de prueba con gramática) y el generador real `ADarxGeneradorMundo` (que orquesta los 3 Biomas modulares PBR, esclusas de desinfección, arenas de Boss y escalas Chico/Mediano/Grande/Infinito). Al pulsar 'Crear Mundo Procedural', el código C++ seguía invocando `AWorldGenActor::Procedural` en lugar de `ADarxGeneradorMundo`, ignorando las opciones de bioma y escala elegidas por el usuario.
**La regla**:
1. **Separación de Responsabilidades**:
   - `AWorldGenActor`: Exclusivo para el **Modo Sandbox** (banco de pruebas de 15,759 instancias de movilidad).
   - `ADarxGeneradorMundo`: Exclusivo para el **Modo Incursión / Mundo Procedural**. Configura de forma estricta `TamanoMision`, `BiomaInicial` y `SemillaAleatoria`.
2. **Cero Coexistencia de Instancias**: Al cambiar de modo o volver al Menú Principal, se deben limpiar atómicamente tanto las salas modulares de `ADarxGeneradorMundo` como las instancias ISM de `AWorldGenActor`.

### 35 — Pausa Obligatoria del Juego en Opciones de Debug y Menús Tácticos
**Qué aprendimos (23-ago)**: Al abrir herramientas de depuración (como la Matriz de Muteo de audio o el Spawner de entidades), si el mundo continuaba en tiempo real, el jugador recibía daño de proyectiles o enemigos circundantes mientras manipulaba faders o botones de configuración.
**La regla**:
1. Toda pantalla, menú o herramienta de depuración en runtime (ej. `Matriz de Mute / Debug Mixer`, `Menú de Spawner`, `Menú de Audio`) **debe pausar el juego obligatoriamente** (`UGameplayStatics::SetGamePaused(World, true)`).
2. Los peones, IA, físicas y proyectiles deben permanecer congelados durante la interacción. Al cerrar la pantalla de debug, el juego se reanuda suavemente (`SetGamePaused(World, false)`).

### 36 — Espacialización 3D y Atenuación Obligatoria de Sonidos de Enemigos y Entorno
**Qué aprendimos (23-ago)**: Al instanciarse múltiples enemigos en distintas salas del mapa que emitían sonidos en bucle (*Hover* del Repulsor, *Hum* del Portador, *Loops* de ácido), la falta de atenuación espacial 3D causaba que todos los sonidos se reprodujeran en 2D global en los oídos del jugador a máximo volumen sin importar la distancia, generando un pitido/zumbido constante en toda la partida.
**La regla**:
1. **Espacialización Posicional Estricta**: Todo sonido emitido por un enemigo, jefe, trampa, proyectil o efecto de entorno debe reproducirse obligatoriamente como sonido 3D espacializado (`UDarxAudioSubsystem::ReproducirSFX` o `ReproducirSFXAdjunto`) con atenuación y origen físico definido.
2. **Prohibición de SFX Globales en 2D**: Prohibido reproducir sonidos de gameplay sin atenuación. A distancias superiores al radio de la sala/combate ($\ge 18-20\text{ m}$), el volumen debe caer al $0\%$ absoluto ($0\text{ dB}$).
3. **Control de Bucles Continuos**: Todo sonido ambiental o de estado en bucle (`bEnBucle = true`) debe contar con atenuación cerrada o activación por proximidad, impidiendo acumulación de ruidos en segundo plano.

### 37 — Geometría Continua y Hermética en Esclusas de Transición (Cero Caídas al Vacío)
**Qué aprendimos (24-ago)**: Al cruzar de un bioma a otro a través de la compuerta de desinfección, el jugador caía al vacío infinito porque el actor `ADarxEsclusaDesinfeccion` intentaba cargar una malla inexistente (`SM_Esclusa_Camara`) y hacía fallback a un cubo estándar centrado en $Z=0$ que dejaba un foso de 6 metros de hueco sin suelo.
**La regla**:
1. Las zonas de transición o esclusas entre salas modulares deben construirse con geometría modular continua dedicada: `MallaSuelo` con altura exacta al nivel de las salas ($Z=50\text{ cm}$), paredes laterales a $Y=\pm 250\text{ cm}$ y techo a $Z=450\text{ cm}$.
2. Toda superficie transitable debe contar con colisión `BlockAll` activa por defecto, garantizando cero huecos físicos en cualquier semilla o generación procedural.

### 38 — Normalización de Ratón y Manejo de Eventos de Clic en Canvas HUD de Unreal Engine
**Qué aprendimos (24-ago)**: Los botones del menú de pausa, spawner táctico y selector de mundo no respondían o requerían clics en zonas desfasadas. Esto ocurría porque `GetMousePosition` devolvía coordenadas del Viewport físico en pantalla, las cuales quedaban desfasadas con cualquier escala DPI de Windows (125%/150%) o resolución arbitraria respecto al `Canvas->SizeX/SizeY`. Además, `IsInputKeyDown` evaluaba el estado continuo y no el disparo del clic.
**La regla**:
1. Toda interfaz dibujada en Canvas AHUD debe normalizar las coordenadas del puntero mediante:
   $$\text{MouseX} = \text{ViewportMouseX} \cdot \left(\frac{\text{Canvas}\rightarrow\text{SizeX}}{\text{ViewportSizeX}}\right), \quad \text{MouseY} = \text{ViewportMouseY} \cdot \left(\frac{\text{Canvas}\rightarrow\text{SizeY}}{\text{ViewportSizeY}}\right)$$
2. El disparo de clics en menús pausados debe capturarse mediante `PC->WasInputKeyJustPressed(EKeys::LeftMouseButton)` con filtro de flanco (`bClickProcesado`) para evitar disparos accidentales en ráfaga.

### 39 — Integración Nativa y Asignación C++ de Efectos Niagara VFX en CDOs
**Qué aprendimos (24-ago)**: La creación de sistemas Niagara (.uasset) mediante scripts de automatización debe conectarse de forma nativa en los constructores C++ (`ConstructorHelpers::FObjectFinder<UNiagaraSystem>`) en los CDOs de las entidades (proyectiles, habilidades, enemigos) para garantizar que los efectos se disparen de forma determinista y optimizada en runtime (`UNiagaraFunctionLibrary::SpawnSystemAtLocation`).
**La regla**:
1. Todo efecto visual de partículas debe crearse como emisor nativo en `/Game/DarX/VFX/NS_...`.
2. Vincular los emisores directamente en los constructores C++ de los actores y componentes correspondientes, evitando cargas dinámicas tardías o comprobaciones nulas en gameplay crítico.

### 40 — Previsualización Visual y Calibración Cromática de Niagara VFX (Cero Retrabajo en Efectos)
**Qué aprendimos (24-ago)**: Los contenedores `.uasset` de Niagara creados mediante factorías básicas carecen de emisores activos. Al poblarlos con plantillas nativas de alta gama (`DirectionalBurst`, `RadialBurst`, `SimpleExplosion`), es fundamental renderizar capturas visuales en estudio oscuro aislando el suelo y calibrando las intensidades emisivas ($6-14\times$ para evitar saturación blanca de bloom) para que cada efecto muestre su paleta única (cian cinético, naranja fuego, rojo carmesí, ámbar PEM, magenta glitch).
**La regla**:
1. Todo sistema Niagara debe contar con emisores calibrados con curvas de vida, velocidad y materiales emisivos balanceados.
2. Todo lote de VFX debe contar con un script automatizado de renderizado de previsualización (`Art/VFX/render_all_vfx_previews.py`) que capture imágenes HD y las presente en la galería visual antes de su entrega al usuario.

### 41 — Reactividad Visual y No-Hardcodeo de Estados Activos en Botones de UI / Canvas HUD
**Qué aprendimos (24-ago)**: Los botones del menú de opciones gráficas (Presets, Escala de Resolución, Límite de FPS, Modo de Pantalla y Sombras) ejecutaban el comando en C++, pero el argumento `bDestacado` de `DibujarBotonMinecraft` tenía índices cableados estáticos (ej. `p == 2`, `r == 2`, `f == 3`), haciendo que los botones seleccionados visualmente parecieran no cambiar tras hacer clic.
**La regla**:
1. El flag `bDestacado` de todo botón de selección múltiple (radio button) debe compararse contra la variable de estado real y reactiva (`p == PresetGraficoActual`, `EscalaResActual`, `FpsLockActual`, `ModoPantallaActual`, `SombrasActual`).
2. Actualizar las variables de estado inmediatamente al procesar el evento de clic en el HUD y reflejar el feedback en tiempo de ejecución.

### 42 — Rangos de Detección Tácticos Escalonados (30m / 50m / 70m) y Apertura Total de Esclusas
**Qué aprendimos (24-ago)**:
1. Las puertas de la esclusa hermética (`ADarxEsclusaDesinfeccion`) tenían un offset de apertura insuficiente ($Z=220\text{ cm}$ en lugar de elevarse sobre el techo a $Z=650\text{ cm}$) manteniendo `BlockAll`, bloqueando físicamente el paso del jugador a la siguiente sala.
2. Los enemigos y drones fijaban al jugador sin importar la distancia (hasta 150 metros a través de múltiples salas), saturando el combate.
**La regla**:
1. Toda puerta de compuerta vertical debe retraerse completamente fuera del vano transitable ($Z \ge 650\text{ cm}$) y conmutar a `NoCollision` al estar abierta.
2. Los enemigos deben categorizarse en 3 tiers estrictos de detección/agresión:
   - **Tier 30m ($3000\text{ cm}$)**: Enemigos melee, fuerza bruta y kamikazes (`RobotAgarre`, `Detonador`, `RobotContencion`, `Amalgam`).
   - **Tier 50m ($5000\text{ cm}$)**: Enemigos de rango medio, soporte táctico e invocadores (`Bastion`, `Repulsor`, `Interferente`, `Fase`, `Portador`, `FloraCarnivora`, `StaticMatrix`).
   - **Tier 70m ($7000\text{ cm}$)**: Francotiradores y drones de reconocimiento con línea de vista estricta (`ArtilleroEstatico`, `Observador`, `BossError`, `Telekinetic`).

### 44 — Reaparición en Punto de Muerte, Atenuación de Alarma del Detonador y Cámaras Seguras de Descompresión
**Qué aprendimos (24-ago)**:
1. El sonido de sobrecarga del Detonador (`SFX_DETONADOR_Beep`) debe diseñarse como una turbina FM sci-fi con aceleración exponencial y atenuación espacial 3D cerrada ($18\text{ m}$), evitando pitidos estridentes u ondas cuadradas planas.
2. Al morir en combate durante pruebas/incursión, el jugador debe reaparecer en el punto exacto de la baja (`UltimaUbicacionMuerte + 25\text{ cm}`) con salud y munición restauradas al 100%, evitando perder el progreso o tener que recorrer de nuevo todo el nivel.
3. La sala de inicio absoluto ($32\times 32\text{ m}$) y la sala inmediatamente posterior a cada esclusa de desinfección deben ser **Zonas Seguras de Despliegue Táctico** ($s=0$), sin mobs hostiles pegados a la salida para evitar emboscadas injustas.
4. Las opciones de NVIDIA DLSS, DLSS 3 Frame Generation, DLSS 3.5 Ray Reconstruction y Reflex deben contar con selectores dedicados en el panel de opciones gráficas.
**La regla**:
1. Guardar la posición de muerte en `ADarxProyectGameMode::AlMorirJugador` y teletransportar al jugador a ese punto al revivir.
2. Todo sonido de alerta/detonación debe contar con atenuación física 3D $\le 18-30\text{ m}$.
3. Mantener la sala $s=0$ de cada sector libre de enemigos agresivos para dar un respiro táctico al operador.

### 45 — Apertura de Vanos entre Salas Conectadas, Calibración de Emisivos LED y Respuesta Táctil de Reinicio
**Qué aprendimos (24-ago)**:
1. `bCerrarOeste` en `ADarxSalaBase::ConstruirGeometriaSala` debe ser **estrictamente `bEsPrimera`**. Si se asocia a `TipoSala == ETipoSala::Entrada`, cualquier sala intermedia de tipo seguro o transición levantará un muro macizo bloqueando la puerta Oeste e impidiendo avanzar.
2. Los materiales PBR con emisión nunca deben superar valores de $0.80-0.90$. Valores desmedidos ($12.0-18.0$) en combinación con el Bloom por defecto de Unreal Engine saturan el búfer de brillo creando niebla blanca, destellos cegadores y pérdida de legibilidad en el arma y entorno.
3. La cámara en primera persona debe calibrar sus `PostProcessSettings` con Bloom suave ($0.18$), umbral estricto ($1.0$) y exposición manual ($0.0\text{ EV}$) para mantener la nitidez sci-fi.
4. En la pantalla de Game Over, el botón de reinicio debe procesar tanto el clic de ratón normalizado con DPI como las teclas de acción rápida (`[ R ]`, `[ Barra Espaciadora ]`, `[ Enter ]`, `[ E ]`), evitando clics no registrados.
**La regla**:
1. Solo la primera sala del nivel puede tener el muro posterior cerrado (`bEsPrimera = true`). Todas las demás salas deben mantener vanos pasantes en ambos extremos.
2. Todo material emisivo debe calibrarse a intensidades $\le 0.85$.
3. Mantener `BloomIntensity = 0.18f` en la cámara principal para evitar sobreexposición.

### 46 — Auto-Exposición Adaptativa, Iluminación del Traje y Menú de Calibración Visual en Modo Developer
**Qué aprendimos (24-ago)**:
1. `AutoExposureMethod = AEM_Manual` con `AutoExposureBias = 0.0f` apaga completamente la visibilidad en mapas de interiores si no hay luces físicas de miles de lúmenes, dejando la pantalla 100% en negro.
2. La cámara debe usar `AutoExposureMethod = AEM_Histogram` con límites adaptativos suaves (`MinBrightness = 0.05f`, `MaxBrightness = 4.0f`, `Bias = 1.2f`) y linterna/luz de relleno táctica en el exo-traje para garantizar visibilidad clara sin depender de focos artificiales en el mapa.
3. Se debe proporcionar un panel de calibración en vivo en el menú de Desarrollo (`ESubPantallaDesarrollo::Iluminacion`) para permitir al desarrollador y jugador regular el multiplicador de LEDs ($0.2\times$ a $5.0\times$), exposición ($ -1.0 $ a $ +6.0\text{ EV} $), bloom ($0.0$ a $2.0$) y potencia de la linterna con un solo clic.
**La regla**:
1. Siempre configurar `AEM_Histogram` en la cámara principal del jugador.
2. Todo ajuste visual de iluminación debe ser configurable en tiempo real desde la sub-pantalla de Iluminación del menú de Desarrollo.

### 47 — Anclaje de Charcos de Ácido al Suelo y Control de Concurrencia de Audio en Bucles
**Qué aprendimos (25-ago)**:
1. Si un proyectil genera charcos de área (`AFloraCharcoAcido`), el raycast de suelo debe ignorar estrictamente a todos los peones, jefes y proyectiles, y exigir que `ImpactNormal.Z > 0.65f`. Si no hay suelo horizontal válido, el charco se destruye de inmediato para evitar que quede flotando a media altura en el aire o sobre el cuerpo del jefe.
2. El espesor del disco de ácido debe ser plano ($\le 1.5\text{ cm}$) y rasante al suelo (`Z = 1.5f`).
3. Los efectos de sonido en bucle de charcos (`SFX_BOSS4_CharcoLoop.wav`) deben sintetizarse como siseo/burbujeo líquido orgánico sin frecuencias agudas ni armónicos sintéticos duros, a volumen tenue ($0.35$) con radio de atenuación espacial estrecho ($\le 6-8\text{ m}$), y detenerse inmediatamente al destruir el actor (`EndPlay`).

### 48 — Alineación Vertical Matemática de Jefes en Arenas y Menú Principal Vectorial HD
**Qué aprendimos (25-ago)**:
1. Las salas de jefe (`ADarxSalaBoss`) que generan plataformas centrales elevadas (ej. la base de raíces de 8x8 de la Flora Carnívora) no deben usar alturas de spawn hardcodeadas. Se debe realizar un raycast vertical hacia abajo (`ECC_WorldStatic`) desde el centro de la arena para situar la cápsula exactamente sobre la cota superior del terreno (`ImpactPoint.Z + HalfHeight`).
2. En el menú principal (`ADarxHUD::DibujarMenuPrincipal`), el texto del título no debe escalarse a $2.4\times$ raster para evitar pixelado de bitmap; debe representarse con tipografía nítida ($1.25\times$) enmarcada en una caja táctica vectorial con corchetes cian y badges seguros en ASCII (`[ > ]`, `[ + ]`, `[ # ]`, `[ * ]`, `[ X ]`) evitando glifos unicode no compatibles.

### 49 — Estructura de 5 Fases y Reglas Estrictas de Modelado 3D en Blender
**Qué aprendimos (27-ago)**:
1. La creación y modificación de modelos 3D sin una estructura por etapas conduce a retrabajo, detalles prematuros y reconstrucciones innecesarias de piezas existentes.
2. Los modelos para videojuegos requieren prioridad estricta de silueta y proporciones métricas reales sobre detalles finos, con compuertas obligatorias de aprobación visual antes de pasar a fases posteriores.
3. El centrado de pivote en $(0,0,0)$ es un invariante matemático: exportar objetos con desplazamientos mundiales de escena causa flotación al adjuntarse a sockets en el motor.

**La estructura obligatoria**:
- **Fase 1**: Silueta y proporciones (volúmenes generales y escala).
- **Fase 2**: Piezas principales (geometría base y articulaciones).
- **Fase 3**: Detalles (elementos secundarios solicitados).
- **Fase 4**: Materiales (shaders PBR y UVs).
- **Fase 5**: Optimización para Unreal (topología, pivote en $(0,0,0)$ y FBX).

**Las directivas inflexibles**:
1. **Compuerta de Silueta**: No añadir detalles (Fase 3) hasta que la silueta y las proporciones hayan sido aprobadas por el usuario.
2. **Prohibición de Reconstrucción**: Una vez creada una parte del modelo, no reconstruirla; modificar únicamente si existe un requisito explícito.
3. **Prioridad Absoluta**: Priorizar siempre silueta y proporciones sobre detalles.
4. **Cero Elementos No Solicitados**: No añadir elementos ni inventar detalles para "mejorar" el diseño.
5. **Dimensiones Reales**: Utilizar dimensiones métricas y proporciones explícitas.
6. **Simetría Controlada**: Mantener simetría cuando el diseño lo requiera.
7. **Verificación de Forma**: Comprobar que la forma general coincide con la descripción antes de detallar.
8. **Cambios Incrementales**: Realizar modificaciones pequeñas e inspeccionar el resultado.
9. **Criterio de Parada**: Detenerse en cuanto el modelo cumpla los requisitos.
10. **Cero Refactors Estéticos**: No realizar refactors cosméticos ni cambiar materiales/topología salvo necesidad estricta.
11. **Enfoque de Videojuego**: Simplicidad y control de geometría sobre detalles superfluos.
12. **Consulta ante la Duda**: Si no se está seguro de una característica, preguntar al usuario; no inventar.

---

## Asset Orchestration Engine (AOE) & Digital Twin

### 50 — Desacople Total de MCP mediante Capa de Abstracción de Capabilities
**Qué aprendimos**: Acoplar la lógica de generación a un servidor MCP específico (ej. Ahujasid) genera fragilidad, fallos silenciosos ante caídas de red y retrabajo innecesario.
**La regla**:
1. Las capas de planificación, compilación y crítica nunca invocan herramientas MCP directamente (`import ahujasid` prohibido en capas superiores).
2. Todo pasa por `BlenderCapabilityAPI` con contratos estables (`object.create`, `transform.set`, `material.assign`), circuit breakers y reconciliación de estado (`StateReconciler`) para evitar duplicación de objetos ante timeouts.

### 51 — Identidad Semántica Digital Twin y Peso Cuantitativo de Referencias Visuales
**Qué aprendimos**: Tratar un modelo como una lista de objetos efímeros de Blender (`Cube.001`, `Cylinder`) obliga a la IA a regenerar el activo completo ante pequeños defectos y a ignorar referencias visuales reales.
**La regla**:
1. Todo componente posee un `semantic_id` inmutable (ej. `asset_042.ring_01`) mantenido en el `SemanticAssetGraph`.
2. Las correcciones son quirúrgicas: si falla un componente, el `AssetImpactAnalyzer` aísla el límite mínimo de regeneración sin tocar el resto del activo.
3. Las imágenes de referencia se descomponen matemáticamente (silueta, aspect ratio, proporciones, partes, PBR y cámara) en `VisualRequirementItem`s obligatorios, con peso real sobre el generador.

### 52 — Desacople Estricto entre Validación Técnica y Aceptación Artística / Calidad Visual
**Qué aprendimos (Fase 70)**: Un trabajo largo puede pasar el 100% de los tests técnicos (checkpoints en disco, recuperación ante crash de proceso, persistencia, leases, reconciliación de Blender, cero duplicados y exportación FBX), pero el modelo 3D resultante ser artísticamente insuficiente (un blockout básico de cajas y cilindros sin biseles, tratamiento de superficie, micro-detalles, ergonomía creíble ni PBR contrastado).
**La regla**:
1. **Regla de Rechazo Visual Independiente**: *Un asset puede pasar todos los tests técnicos unitarios y de orquestación, y aun así ser rechazado rotundamente por calidad visual insuficiente*.
2. **Prohibición de Confundir Pipeline con Calidad Artística**: La resiliencia de la orquestación (F70) resuelve la persistencia y recuperación de tareas; la calidad artística depende de la percepción, el razonamiento compositivo, la biblioteca de patrones y la crítica visual estricta.
3. **Rúbrica Visual Obligatoria**: Ningún asset se considera aceptado para producción sin superar la evaluación de: (a) Silueta y proporciones; (b) Diseño funcional creíble; (c) Tratamiento de superficies y biseles; (d) Materiales PBR diferenciados; y (e) Coherencia con el lenguaje visual de DarX.
4. **Artefactos de Recuperación Técnica**: Los modelos generados únicamente para probar la infraestructura de ejecución/crash se etiquetan y archivan como *Technical Recovery Artifacts*, quedando terminantemente prohibido su uso como modelos finales de videojuego.

---

## Antes de decir «terminado»

1. ¿Ningún `.py` es más nuevo que el FBX más antiguo?
2. ¿`rehacer_todo.py` termina con «Todo correcto»?
3. ¿Coinciden los **conteos** de FBX y de uassets?
4. ¿El guardián de la cápsula pasa?
5. ¿Reiniciaste el editor después de importar?
6. ¿`test_suite_darx.py` arrojó `21/21 TESTS PASARON [PASS]` al 100%?
7. ¿Todo sonido de enemigo/efecto tiene atenuación espacial 3D con origen físico definido?
8. ¿La esclusa de desinfección tiene suelo transitable continuo a $Z=50\text{ cm}$ y compuertas retraídas a $Z=650\text{ cm}$?
9. ¿Los rangos de detección de los enemigos están limitados a sus tiers de 30m, 50m o 70m?
10. ¿El Bastión rota lentamente ($0.65$) para permitir flanqueo y no hay luces flotantes sin modelo físico?
11. ¿El Detonador cuenta con su nuevo audio sci-fi de turbina y atenuación espacial cerrada a 18m?
12. ¿Al morir se reaparece en el mismo punto con salud/munición restauradas?
13. ¿La sala de inicio y la antecámara tras la esclusa son amplias ($32\times 32\text{ m}$) y sin enemigos inmediatos?
14. ¿Las opciones de DLSS, Frame Gen, Ray Reconstruction y Reflex están disponibles en el menú?
15. ¿El Boss y los charcos de ácido están anclados con raycast al suelo sin clipping ni flotación?
16. ¿La suite completa del Asset Engine (`test_suite_*.py`) arroja 750/750 tests PASS?
17. Lo que afirmas, **¿lo has mirado, o lo supones?**


