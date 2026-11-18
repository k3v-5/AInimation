# Plan de UV y texturas — fase preliminar

Qué lleva cada asset, cuánto cuesta y por qué. Manda
[ARTE-BIBLIA.md](ARTE-BIBLIA.md); esto es su aplicación concreta.

---

## Lo que la biblia permite, y lo que no

Hay un malentendido fácil de cometer aquí, así que primero se aclara:

> **La regla no es «sin textura», es «sin suciedad».** Lo que rompe el
> laboratorio aséptico es el desgaste, no el dibujo.

| Prohibido | Permitido |
|---|---|
| Desgaste, óxido, porosidad, suciedad fotorrealista | Trazos de circuito grabados |
| Cualquier mapa que simule uso o deterioro | Patrones geométricos, paneles de fibra |
| Color base con variación «sucia» | Líneas finas |

Y la frase que ordena todo el plan: **«un trazo de circuito es el equivalente en
material de una línea de panel en geometría»**. La textura aquí no decora —
sustituye geometría que sería demasiado cara de modelar.

**El color base sigue siendo plano.** Eso significa que el mapa que más falta
hace **no es un albedo**, sino una **máscara de detalle** que module *roughness*
y *emisivo* sobre un color liso. Un albedo pintado rompería la regla del bloque
de color puro.

---

## Estado de partida

Las 15 mallas tenían **cero capas UV**. Unreal avisaba —«la malla no tiene
conjunto UV, creación de un conjunto predeterminado»— y se dio por inofensivo
porque no había texturas. El conjunto que Unreal inventa no sirve para nada.

Ya están todas desenvueltas: `darx_lib.desenvolver()`, Smart UV Project a **66°**
y no al 89 por defecto — con geometría facetada, 89 mete en la misma isla caras
que forman esquina viva y la textura cruza el canto.

El desenvuelto se rehace en cada reconstrucción desde `rehacer_todo.py`, porque
`MB.build()` crea las mallas desde cero y los UV se perderían **sin dar ningún
error**.

---

## Densidad de texel: va por distancia de visión, no por tamaño

Ésta es la decisión que había que tomar ahora y no después, porque cambiarla
obliga a rehacer los UV de todo.

> **Primer intento equivocado:** una sola densidad calculada por área. Con eso
> los brazos de primera persona pedían 1024 y el jugador de tercera 2048 — al
> revés de lo que hace falta. Los brazos tienen poca superficie pero **se miran a
> 30 cm llenando la pantalla**; el de tercera se ve a metros.
>
> Lo que manda es **cuánto se amplía en pantalla**, no cuánto mide.

| Clase | px/m | Qué entra |
|---|---|---|
| `fps` | **1024** | Brazos y arma en primera persona. Lo más ampliado del juego |
| `personaje` | **512** | Jugador, enemigos y terminales. De 2 a 20 m |
| `objeto` | **256** | Recogibles y proyectiles. Pequeños y emisivos |
| `mundo` | **128** | Los cubos. Blanco plano y el 98% de lo instanciado |

---

## Qué lleva cada cosa

| Asset | Área | Textura | Qué llevaría |
|---|---|---|---|
| `SK_FPS_Arms` | 1,21 m² | **2048** | **Máxima prioridad.** Trazos de circuito en el antebrazo, líneas de panel finas en el chasis del arma |
| `SK_Robot_Grab` | 15,27 m² | 2048 | Paneles y rejillas de la carcasa; ahorra geometría en el tren de rodaje |
| `SK_Gunner_Static` | 8,87 m² | 2048 | Igual que el robot |
| `SK_Player` | 5,93 m² | 2048 | Trazos de circuito en traje y mochila |
| `SM_Terminal_Data` | 4,44 m² | 2048 | **El único caso donde la textura lleva información**, no adorno: la pantalla |
| `SM_Terminal_Upgrade` | 6,35 m² | 2048 | Ídem |
| `SM_Pickup_*` | ~0,3 m² | 256 | Marca de tipo, si acaso |
| `SM_Projectile_*` | 0,04 m² | **ninguna** | Emisivo puro, visible una fracción de segundo y en movimiento |
| `SM_Bolt_Trail_*` | 0,10 m² | **ninguna** | Ídem |
| `SM_Cube_*` | ~7 m² | **ninguna** | Ver abajo |

### Los cubos NO se texturizan

Es la decisión de presupuesto más importante del plan, y va en contra del
instinto de «texturizar todo».

1. Son **blanco plano por doctrina**. No hay nada que dibujar.
2. Son el **98% de lo instanciado**. Cada texel se paga decenas de miles de veces.
3. El trabajo de legibilidad **ya está hecho en geometría**: bisel de 1,8 cm con
   material de arista propio, y las marcas direccionales que distinguen muro,
   cobertura y refugio.

Texturizarlos es donde más cuesta y menos se gana. Tienen UV por si algún día
hace falta una máscara, pero el plan es no usarla.

---

## Presupuesto

**100 MB en RGBA8 sin comprimir** si todo llevara textura. Con compresión BC
ronda los 25 MB, y añadir mapas de normales lo duplica.

Quitando cubos y proyectiles —que no la llevan— baja a **~12 MB comprimido**,
que para un vertical slice es razonable.

---

## Orden sugerido

1. **`SK_FPS_Arms`** — lo que se ve el 100% del tiempo y más ampliado.
2. **Las dos terminales** — es donde la textura *informa* en vez de decorar.
3. **Los tres personajes** — trazos de circuito, ganancia por unidad de trabajo alta.
4. **Recogibles** — opcional.
5. **Cubos y proyectiles** — no.

---

## Prueba hecha: qué sobrevive a un UV automático y qué no

Se generó la hoja de detalle (`darx_textura.py`, procedural como todo lo demás) y
se probó sobre `SK_FPS_Arms` con sus UV de Smart UV Project. Resultado, medido en
render y no supuesto:

| Canal | Qué es | Veredicto |
|---|---|---|
| **R** rugosidad | Líneas de panel, dos escalas | **Funciona.** El negro plano gana rotura de placa, y sale gratis |
| **B** cavidad | Junta en la rejilla gruesa | **Funciona**, por lo mismo |
| **G** emisivo | Trazos de circuito | **No funciona** sobre UV automático |

**Por qué la diferencia:** las líneas de panel son *ruido* —da igual dónde caigan,
cualquier trozo se lee igual—, así que sobreviven a islas arbitrarias. Los trazos
de circuito son *figurativos*: se cortan a mitad en el borde de isla, se enroscan
por los nudillos de forma incidental y aparecen guiones sueltos que leen como
error.

### Decisión

- **La máscara de detalle se queda en rugosidad y cavidad.** Es lo que aporta sin
  pedir trabajo manual.
- **El emisivo sigue en geometría**, con su propio *slot* de material
  (`M_Arm_Accent`, `M_Gun_Accent`). Ya está resuelto ahí y colocado a mano, que
  es justo lo que los trazos necesitan y el UV automático no da.

El canal G se sigue generando por si algún asset recibe UV hechos a mano, pero no
se usa por defecto.

### La triplanar GANA — probado en el motor

Se montó `Art/prueba_triplanar.py`: material con la función
`WorldAlignedTexture` del motor y cuatro cubos **pegados** en el mundo, tres en
fila y uno encima. Pegados a propósito: separados, cualquier proyección parece
correcta.

**Resultado: el patrón cruza la unión entre cubos contiguos sin salto**, con las
líneas horizontales a la misma altura en ambas piezas y el mismo paso en las
verticales. La escala se ve idéntica. Es justo lo que un desenvuelto por islas
no puede dar.

**Lo que eso decide:**

- El detalle de superficie —líneas de panel, rejilla— va por **triplanar**, no
  por textura por asset. Densidad uniforme en todo el juego, **cero texels por
  pieza**, e inmune a que el desenvuelto cambie al rehacer un modelo.
- **Se cae la columna «2048» de la tabla de arriba** para todo lo que solo
  necesitaba rotura de superficie: personajes, enemigos, recogibles.
- La textura por asset queda **solo donde lleva información**: las pantallas de
  las dos terminales.
- Los UV **no se tiran**: siguen haciendo falta el día que algo necesite un mapa
  colocado, y no estorban.

**Presupuesto revisado:** de ~12 MB comprimidos a **prácticamente cero** para el
detalle de superficie — una sola hoja compartida para todo el juego.

**Pendiente de ajuste, que no de decisión:** con `ESCALA_MUNDO = 100` entra la
textura entera en cada cubo de 1 m —16 celdas por metro— y lee como baldosa en
vez de como línea de panel. Con 200–400 las líneas se separan. Es un número.

> **Y una cosa observada que no afecta al veredicto:** los cubos de prueba salen
> azul claro cuando el color base del material es casi negro (0.055). Sin mirar
> no se sabe por qué, y para la pregunta que se estaba respondiendo da igual —
> pero conviene comprobarlo antes de dar el material por bueno para producción.

---

### La alternativa que se barajaba antes de probarla

Las líneas de panel funcionan porque son ruido — y a un ruido **no le hace falta
UV**. Una proyección **triplanar en el material de Unreal** daría el mismo efecto
con densidad perfectamente uniforme entre piezas, sin depender del desenvuelto y
sin gastar un solo texel por asset.

Merece probarse antes de comprometerse a una textura por pieza. Los UV ya están
hechos y no estorban: sirven igual si la triplanar no convence.

---

## Lo que queda sin decidir

- ~~Triplanar contra textura por pieza~~ — **decidido: gana la triplanar.**
  Probado en el motor, ver arriba.
- ~~El azul de los cubos de prueba~~ — **explicado.** Un material oscuro y poco
  rugoso es un **espejo oscuro**, y en un nivel de pruebas lo que domina es el
  Sky Sphere. Estaba reflejando el cielo. Comprobado con la predicción que hacía
  la hipótesis: el mismo material en un cuarto cerrado se ve negro.

  **Y tiene consecuencia de diseño:** el entorno de DarX es un laboratorio
  blanco. Un cuerpo negro muy pulido ahí reflejará **blanco** y perderá su
  silueta. Los acentos morados dejan de ser adorno: son lo que le devuelve el
  color y lo recorta del fondo.
- ~~Afinar `ESCALA_MUNDO`~~ — **hecho**, 300 en `fase9_material_y_luz.py`.
- **UV1 para lightmaps.** Hoy no hace falta: el proyecto usa Lumen y el
  importador tiene `generate_lightmap_u_vs = False`.
