# Diseño del arma — pistola láser

Decisiones tomadas por dirección. Este documento manda sobre lo que haya en el
código o en los modelos: si algo no coincide, se cambia lo otro.

Sustituye a `DISENO-REVOLVER.md`. El arma pasó de revólver a **pistola de
energía** el 19 de agosto de 2026. Lo que sigue distingue en cada punto qué se
conservó del revólver y por qué, porque casi nada de aquel diseño era sobre
pólvora: era sobre **contar disparos mirando el arma**, y eso sobrevive entero.

---

## Las cinco decisiones

| | |
|---|---|
| **Recarga** | Celda de energía intercambiable |
| **Estilo** | Chasis limpio de polímero claro, acentos emisivos cian |
| **Munición visible** | Seis segmentos encendidos, vistos por la ventana del armazón |
| **Cuerpo a cuerpo** | Culatazo con la propia arma |
| **Carga sobrante** | Se pierde: la celda se sustituye, no se rellena |

---

## 1 · La celda como módulo

No se cargan disparos: **se cambia la celda completa**. Lo que suelta el
Artillero al caer no es munición suelta, es **una celda cargada**.

**El objeto que cae.** `SM_Pickup_AmmoClip` conserva el nombre —`DarxModuloSuelto
.cpp` lo referencia por ruta fija— pero ya no es un cargador: es un prisma
hexagonal con seis nervios cian encendidos y seis segmentos en la cara superior.
Es literalmente la misma pieza que lleva el arma, a escala 2,6. Si el jugador no
reconoce la pieza, no entiende la mecánica.

**La animación.** `A_FPS_SwapCylinder` pasó a `A_FPS_SwapCell`: expulsar, encajar,
cerrar. 36 f = 1,2 s. Los seis huesos `charge1..6` cuelgan de la celda y se mueven
con ella como bloque; no se vacían de uno en uno.

**La celda descartada.** Al cambiarla cae al suelo. Es información gratis: ves
dónde has recargado y cuántas veces.

### Sustituir, no rellenar

La carga que quede en la celda puesta **se va con ella**. No se suma. Si el
Artillero suelta una celda de 5 y te quedan 2, te quedas con 5, no con 6.

De ahí sale una regla de recogida que no es cosmética: **una celda solo se coge
si trae más carga de la que llevas**. Si no, se queda en el suelo y sigue ahí.
Sin esa condición, cruzar por encima de una celda a medias con la tuya llena te
costaría munición sin haber decidido nada — el peor tipo de castigo, el que no
avisa.

Con ella, la decisión existe pero es de **cuándo volver**: sabes que hay una
celda de 5 tres salas atrás, y el momento de ir a por ella depende de cuánto te
quede.

> **Esta sección no cambió al pasar a láser.** Estaba escrita sobre un tambor y
> vale igual sobre una celda, porque nunca dependió de que hubiera pólvora: el
> mecanismo es *sustituir un módulo entero*, y eso encaja mejor en un arma de
> energía que en un revólver. En código sigue siendo `SustituirCelda`, antes
> `SustituirTambor`; solo cambió el nombre.

## 2 · Silueta

Sigue la [biblia de arte](ARTE-BIBLIA.md) sin excepción: chasis limpio en
polímero claro dentro del lienzo blanco y gris, geometría precisa sin greeble, y
todo el interés visual confiado a los acentos emisivos y al diseño diegético.

Lo que se conservó del revólver, y por qué:

- **El armazón partido.** Bloque trasero y bloque emisor unidos solo por el riel
  superior. Existía para que se viera el tambor; ahora deja ver la celda. La
  razón no era el tambor, era la ventana.
- **Los 22° de canteo.** Con el arma alineada con la vista se mira por detrás del
  cuerpo y no se ve la cara de la celda, que es justo lo que hay que ver.
- **El eje.** La celda ocupa el eje exacto del viejo tambor. Mantenerlo dejó
  intactos el encuadre de cámara y el agarre de la mano, que costaron su ajuste.

Lo que se fue con el revólver: el latón, las recámaras, el cañón con ánima, la
varilla eyectora y el martillo. En su lugar hay bloque emisor facetado, tres
aletas de disipación y una **boca ensanchada con ranura emisiva**.

La boca es la pieza más ancha del morro, no la más fina. En un arma sin cañón es
el único sitio del que puede salir el disparo, y afilada no se leía.

## 3 · Indicador en el armazón

Una **ventana en el armazón que deja ver la cara trasera de la celda**. No es un
contador abstracto: son los seis segmentos de carga directamente, y como la celda
es la pieza que cambias, el indicador refleja siempre el módulo puesto sin ningún
mecanismo intermedio.

**Aquí el láser mejora al revólver.** Un culote de latón gastado y uno lleno se
parecen; un segmento **encendido** y uno **apagado** no. La limitación que el
diseño anterior daba por asumida —«a distancia no se lee»— deja de serlo, porque
el contraste ya no es de color sino de emisión.

Además la celda lleva seis nervios encendidos en las caras del hexágono, que dan
la lectura de «llena» desde fuera sin mirar por la ventana.

## 4 · Culatazo

El melee se hace **con el arma**, no con la mano libre: `A_FPS_Bash`, 13 f =
0,43 s, justo por debajo de la cadencia de 0,45 s.

Los números del combate no cambian: 20 de daño, 160 de alcance. Tres golpes
tumban a un robot, dos al Artillero.

## 5 · Color

**Todo lo tuyo es morado.** Arma, celda, proyectil, estela y los brillos del
cuerpo. Es la regla dura de [ARTE-BIBLIA.md](ARTE-BIBLIA.md):

> **TÚ — morado/violeta.** Reservado al jugador: sus armas, su proyectil, los
> brillos de su cuerpo. **El morado es del jugador y de nadie más.**

- **Morado** — arma, celda, proyectil, estela, acentos del brazo. Una sola señal.
- **Rojo** — amenaza. Estrictamente enemigos y daño, nunca lo tuyo.
- **Verde, azul, cian, ámbar** — botín, terminales y objetos del mundo.

> **Hubo una versión en cian**, con el argumento de que ataba el arma a tus
> propias balas. El argumento era bueno y la decisión estaba mal: con el arma en
> un tono y el cuerpo en otro, el jugador dejaba de tener **una** señal y pasaba
> a tener dos, y ninguna significaba «tú». La biblia asigna el morado a las armas
> *y* al proyectil por esa razón exacta.
>
> Morado contra rojo separa igual de bien que cian contra rojo —son opuestos en
> el círculo— así que no se perdió nada en legibilidad de combate.

El acento del arma (`COL_GUN_ACCENT`) es un pelo más frío que el del cuerpo para
que la pistola no desaparezca contra el brazo, pero sigue siendo morado.

---

## Estado en código

| Decisión | Estado |
|---|---|
| Sustituir en vez de rellenar | **Hecho** — `UDarxArmaComponent::SustituirCelda` |
| Malla de la pistola láser | **Hecho** — `darx_fps.py`, huesos `cell` / `charge1..6` / `emitter` |
| Malla de la celda suelta | **Hecho** — `darx_props.py`, `SM_Pickup_AmmoClip` |
| Animación de cambio de celda | **Hecho** — `A_FPS_SwapCell` |
| Culatazo | **Hecho** — `A_FPS_Bash` |
| Ventana del armazón | **Hecho** |
| Estela del disparo | **Hecho** — `ADarxProyectil::Estela`, `SM_Bolt_Trail_*` |

**Nota sobre `Balas`.** El código sigue llamando `Balas` a los disparos y
`ADarxProyectil` al proyectil, y así se queda: el arma **no dispara un haz**.

## 6 · El disparo: como el de SUPERHOT

El disparo es un **proyectil visible y lento** (14 m/s, sin gravedad, línea
recta), no hitscan y no un rayo instantáneo. Un láser que llega antes de verse
haría el juego imposible de leer, y toda la Fase 5 está construida sobre lo
contrario: que la bala se vea venir y el posicionamiento decida el intercambio,
no el reflejo.

A eso se le añadió lo que faltaba para que se lea como SUPERHOT: **la estela**.

Ver el proyectil te dice **dónde** está. Ver la estela te dice **de dónde
viene** — y esa es la única información con la que decides hacia qué lado
esquivar. Con la bala sola, a 14 m/s, sabes que algo se acerca pero no desde
dónde hasta que la tienes encima.

- Cinta emisiva de 1 m (`SM_Bolt_Trail_Player` / `_Enemy`) que el actor tiende
  entre la boca del arma y la posición actual de la bala, escalándola cada frame.
- Morada como el proyectil, y **más apagada que él** a propósito: si la estela brilla igual que la
  bala, el ojo se va al trazo entero y pierdes el punto que de verdad te puede
  dar.
- `LargoMaximoEstela` = 0 dibuja la trayectoria completa, que es lo de SUPERHOT.
  Es ajustable porque en una sala con seis enemigos disparando son seis líneas
  cruzando la pantalla, y ahí puede convenir recortarlas.

Encaja además con la **dilatación temporal** que ya existe (Fase 7,
`UDarxHabilidadesComponent`): al ralentizar a los enemigos, las balas quedan casi
suspendidas y las estelas dibujan el mapa entero del tiroteo. Es exactamente el
momento SUPERHOT, y sale gratis de dos sistemas que ya estaban.

---

## Tercera persona: lo que falta

**No existe un modelo de jugador.** Solo hay `SK_FPS_Arms`, brazos y arma para
primera persona.

El GDD §1 dice que el jugador es, junto a los enemigos, lo único que rompe la
regla del entorno blanco. Ese personaje no está diseñado, y dos requisitos salen
del código y condicionan su silueta:

- Debe caber en la cápsula de **radio 34 y media altura 96** — el mismo volumen
  1×2×1 que valida el QA. Un personaje más ancho no pasaría por corredores que el
  validador dio por buenos.
- El culatazo y el disparo tienen que **leerse desde fuera**, porque en tercera
  persona la silueta es lo único que comunica qué estás haciendo.
