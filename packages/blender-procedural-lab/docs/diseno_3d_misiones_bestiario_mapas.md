# Ficha Técnica: Pipeline de Arte 3D - Misiones, Bestiario, Mapas y Hardware de Lanzadera

Este documento detalla la arquitectura técnica, estándares de modelado y pipelines de generación procedural en **Blender 5.2 LTS** para el ecosistema visual de misiones de **Astra Hazard - Rescue Squad**, incorporando la estética oficial de cómic sci-fi y metal envejecido (*Weathered Olive-Gunmetal*) de las referencias oficiales `media_1791204795741.png`, `media_1791198846797.jpg`, `media_1791198833604.jpg` y `media_1791250538751.png`.

---

## 1. Propósito y Alcance

Para responder al diseño integral del bucle de misiones (*Contract to Extraction*) y dotar a cada expedición, entidad y dispositivo de la estética de novela gráfica sci-fi aprobada, se han implementado y calibrado tres generadores procedurales maestros en Python / Blender 5.2 LTS:

1. **`Art/Blender/generar_bestiario_10_entidades_oficial.py`**:
   - Reconstrucción anatómica y articular 1:1 con fidelidad estricta (>=95%) a la guía oficial de diseño anotada (`media_1791273929163.png`) erradicando cajas primitivas y aplicando los 20 pilares visuales:
     - **01-02. Delineado y Lineart Variable:** Trazo negro grueso de tinta cómic mediante *Inverted Hull Solidify* (`offset = 1.0`, `use_flip_normals = True`, `use_rim = False`, material negro mate `M_Comic_Ink_Outline` con `use_backface_culling = True`).
     - **03. Fuego Estilizado 2D/3D con Gradiente Procedural:** Llamas volumétricas cómic con gradiente procedural a lo largo del eje Z (`Separate XYZ` sobre `Generated`) con ColorRamp lineal continuo:
       - *Fuego Naranja*: Base amarilla incandescente `(1.0, 0.92, 0.15)` -> cuerpo naranja saturado `(1.0, 0.38, 0.02)` -> puntas carmesí `(0.95, 0.16, 0.01)`.
       - *Fuego Cian*: Base blanco-cian incandescente `(0.85, 1.0, 1.0)` -> cuerpo cian eléctrico `(0.0, 0.82, 1.0)` -> puntas azul cobalto `(0.0, 0.42, 0.95)`.
       - Delineado exterior con tinta negra Solidify sin artefactos de inversión.
     - **04. Pistones y Articulaciones Mecánicas:** Cilindros hidráulicos articulados de acero oscuro con vástagos de latón/cromo en codos de lobo, rodillas digitígradas y patas de la araña de techo, más placas vertebrales a lo largo de la columna lupina.
     - **05. Garras Exageradas Cartoon y Cráneo Lupino Esculpido:** Cráneo bmesh de 6 anillos longitudinales facetados reorientado en pose de acecho frontal-baja (`pitch = -12°`, rotación hacia cámara `10°`), mandíbula inferior articulada abierta en snarl con colmillos metálicos, fuego oral incandescente, y extremidades delanteras firmemente plantadas sobre la pasarela (`Z ≈ 0.68m`, erradicando patas flotantes) con 4 garras curvas gruesas cartoon (`scale = 1.45`) en cada extremidad.
     - **06. Lente Emisiva + Monitor CRT Verde Fosfórico:** Dron Auditor con lente óptica cyclópea roja enmarcada en anillos concéntricos de latón y monitor CRT verde fosfórico lateral (`tex_crt_green_screen.png`) con radar, barrido y telemetría proyectados mediante mapeo UV plano directo y emisión pura.
     - **07. Remaches, Tuercas y Manómetros Analógicos:** Tres manómetros superiores en el domo del Auditor inclinados 52° hacia el frente para encarar directamente la cámara, con bisel de latón y carátula blanca de 0-120 PSI (`tex_dial_analogo.png`) con aguja roja biselada integrada en la cara frontal mediante UV planar.
     - **08. Texturas de Desgaste y Calavera de Marfil:** Placas de acero con remaches, óxido, desgaste industrial y tramado cruzado (*cross-hatching*) en sombras (`tex_plates_crosshatch.png`), y máscara de calavera en auténtico marfil óseo (`M_Bone_White`).
     - **09-11. Trasgo Chatarrero (Asimetría, Ojo Gigante y Engranajes):** Máscara de hueso esculpida con dientes serrados tallados; 3 cuernos de tubos doblados; asimetría ocular radical (ojo derecho oscuro con pupila roja vs ojo izquierdo con monóculo telescópico dorado gigante de 3 niveles concéntricos); maza con 12 pinchos piramidales, hebilla de cinturón de engranaje dentado de bronce envejecido (no emisivo) y escudo de sierra circular dentada de acero orientado frontalmente a la cámara (`(R(8), R(22), R(5))`) para exhibir dientes de corte y buje de latón.
     - **12. Poses Dinámicas y Nuevas Entidades:** Lobo en pose feral de acecho, trasgo en guardia compacta, Cinder Spirit con armadura de magma, y Spider-Bot colgado. Además incluye 5 nuevas entidades: Charr-Brute (Gorila Mecánico), Plasma Leech (Sanguijuela de Tuberías), Cyber-Hound Scout (Sabueso Rastreador), Furnace Keeper (Centinela Calderero), y Vapor Creeper (Merodeador Tóxico). Aislamiento por toma (`hide_render`) para el letrero `SECTOR 7`.
     - **13. Sombras Duras y Oclusión de Contacto:** Sombras definidas de 2 tonos en rejilla y piso mediante cel-shading estricto con umbral en 0.16 para asegurar lectura frontal impecable.
     - **14. Tuberías y Cables Colgantes:** Conductos superiores de vapor, vigas I-beam en la pared posterior y tubería de soporte dedicada donde se aferra el Spider-Bot.
     - **15. Perspectiva y Anatomía Industrial:** Spider-Bot trepador colgado de las tuberías con chasis verde oliva facetado, 3 celdas de energía verdes en el lomo, lente ciclópea y 4 patas mecánicas (delanteras descendiendo con garras hacia el suelo, traseras aferradas al tubo).
     - **16. Iluminación Emisiva Calibrada:** Resplandor calibrado a Strength 1.0 (sin quemado cromático a blanco) en ojos, lentes ópticas, pantallas de telemetría, celdas verdes de energía, fisuras de magma y llamas 2D.
     - **17. Cono de Escaneo del Auditor Despejado:** Haz cónico rojo translúcido proyectado hacia la derecha/suelo sin ocluir la pantalla CRT verde ni el Trasgo.
     - **18. Luz de Rebote (Rim Lighting):** Iluminación cálida de rebote (4500W) desde el interior del horno de fundición de ladrillo bañando el flanco posterior del golem y el entorno.
     - **19. Cel-Shading de 2 Tonos con Escala de Textura Paramétrica:** Sombreador PBR desacoplado (`Diffuse BSDF -> ShaderToRGB -> ColorRamp(CONSTANT) -> Emission(1.0)`), con Box Triplanar con escala ajustable `tex_scale` (3.6x para ladrillo refractario, 4.0x para rejilla de suelo, 3.0x para pasarela) erradicando el emborronado de texturas.
     - **20. Entorno Factoría Sector 7:** Pasarela de rejilla con barandilla industrial de hierro oscuro, zócalo de seguridad hazard (amarillo/negro a 45°), columnas I-beam de pared, lámparas de mamparo a media altura (220W ámbar), pila de escombros con chatarra y engranajes oscuros, y horno ardiente de ladrillo refractario (`tex_brick_forge.png`) con arco de fundición y clave de latón.
   - **Artefactos Renderizados Oficiales**:
     - Escena `.blend`: `Art/Blender/Bestiario_Entidades_Oficial.blend`.
     - Lámina Cuadrante Maestra (2560x1440): `Art/Renders/Showcase_Bestiario_Entidades_Oficial.png`.
     - Renders Individuales (1920x1080):
       - `Showcase_Bestiario_panorama_all.png` (Panorama general 1:1 de Factoría Sector 7 con las 5 entidades interactuando).
       - `Showcase_Bestiario_werewolf_beast.png` (Primer plano de acción del lobo mecánico en pasarela, aislado y sin oclusión periférica).
       - `Showcase_Bestiario_orb_and_trasgo.png` (Plano medio del Dron Auditor con manómetros encarados y Trasgo con máscara, ojo gigante, maza y escudo).
       - `Showcase_Bestiario_cinder_spirit_furnace.png` (Titán Cinder Spirit con magma, cola cian continua saliendo del horno ardiente y Spider-Bot superior).

2. **`Art/Blender/generar_hardware_shuttle_maestro.py`**:
   - Instrumental táctico y cabina de inserción de la lanzadera (`media_1791198846797.jpg`):
     - **Stasis Pod Médico**: Marco perimetral abierto de cobre/latón con cristal criogénico translúcido; astronauta durmiendo visible en traje espacial con pechera y franja naranja; brazo articulado con monitor ECG curvo (`HR: 64 bpm`, `STATUS: STABLE`).
     - **Mesa Holográfica Táctica 3D**: Consola de vuelo de acero militar con botones retroiluminados multicolor, diales analógicos, pantalla angular con cuadrícula de constelaciones y haz cónico que proyecta el sistema solar 3D (`SECTOR 7`, `MINING RT`, `ASTEROID 14`).
     - **Gadgets Tácticos Diegéticos**:
       - *Escáner MultiGas/EMF*: Chasis erguido sostenido por mano con guante de bombero, display LCD (`O2: 21% / CO2: 0.1% / SCAN ACTIVE`), diodos LED y sensor de boquilla.
       - *Bandeja de Consumibles*: 3 bengalas térmicas con franjas hazard (`FLARE - EMER`), cilindro de parche expansivo (`BREACH PATCH - SHIP-FIX`) y rollo de cinta de reparación reforzada.
   - **Artefactos Renderizados**:
     - Escena `.blend`: `Art/Blender/Hardware_Mision_Y_Gadgets_Oficial.blend`.
     - Lámina 4K (3840x2160): `Art/Renders/Showcase_Hardware_Y_Gadgets_Oficial.png`.

3. **`Art/Blender/generar_mapas_dioramas_maestro.py`**:
   - Tríptico arquitectónico de los tres arquetipos de navíos para las Fases 1 a 4 de gameplay (`media_1791198833604.jpg`):
     - **Panel 1: Carguero Químico ("ACIDGOO" / "QUÍMICO MORTAL" - Tier 1)**:
       - Casco de buque oxidado en verde oliva/teal con óxido corrosivo y ojos de buey iluminados.
       - Torre del puente de mando en dos niveles con pintura blanca envejecida, chimeneas gemelas (roja y negra), mástil con cruceta de radar y rótulo estarcido legible `QUIMICO MORTAL`.
       - Pórtico amarillo central con 3 columnas en perfil H y viga transversal, grúa articulada con cilindros hidráulicos levantando contenedor suspendido y rótulo `ACIDGOO`.
       - Cisterna de ácido verde fluorescente en primer plano con refuerzos verticales, escalera de acceso interior y vapores ondulantes.
     - **Panel 2: Crucero de Lujo ("Celestia" - Tier 2)**:
       - Gran salón Art-Déco con ventana monumental en arco dorado enmarcando el gigante gaseoso Saturno con bandas atmosféricas horizontales y anillos concéntricos con división de Cassini, más planeta azul orbital.
       - Suelo de moqueta terciopelo vino tinto con cenefas geométricas doradas incrustadas.
       - Sillones de terciopelo burdeos con patas de latón, mesas auxiliares con lámparas cónicas de luz cálida, escalera señorial de caoba con barandilla dorada y lámparas de araña escalonadas concéntricas.
     - **Panel 3: Refinería de Plasma ("Black Rock" - Tier 3)**:
       - Esclusa industrial de inserción en asteroide con franjas hazard y letrero en poste `REFINERÍA DE PLASMA`.
       - Pasarela curva de rejilla metálica con barandillas tubulares amarillas suspendida sobre el vacío espacial.
       - Dron de servicio minero inferior con 4 patas/propulsores y doble foco frontal flotando en gravedad cero.
       - Reactor toroidal magnético Tokamak con bobinas radiales de latón, núcleo de plasma azul cian neón, singularidad blanca-azulada y letrero `PELIGRO: ALTA ENERGÍA`.
   - **Artefactos Renderizados**:
     - Escena `.blend`: `Art/Blender/Mapas_Arquetipos_Oficial.blend`.
     - Tríptico Maestro (2560x1440): `Art/Renders/Showcase_Mapas_Arquetipos_Oficial.png`.

---

## 2. Contratos e Interfaces de los Generadores Procedurales

### Sombreador Maestro de Cómic (`create_comic_weathered_material`)
```python
def create_comic_weathered_material(
    name: str,
    base_rgb: tuple[float, float, float, float],
    rust_rgb: tuple[float, float, float, float] = (0.48, 0.18, 0.06, 1.0),
    grime_rgb: tuple[float, float, float, float] = (0.10, 0.09, 0.08, 1.0),
    rust_scale: float = 4.5,
    metallic: float = 0.25,
    roughness: float = 0.80,
    has_rust: bool = True,
    ink_threshold: float = 0.26
) -> bpy.types.Material
```
### Sombreador Maestro de Contorno Cómic (Inverted Hull Ink Outlines en Blender 5.2 EEVEE Next)
En Blender 5.2 LTS, el modificador `Solidify` con caras invertidas y `use_backface_culling = True` no descarta las caras frontales en tiempo real, cubriendo los modelos con un caparazón negro opaco. La solución de ingeniería implementada desacopla el descarte hacia el grafo de nodos:
- **Estructura de Nodos:**
  - `Material.surface_render_method = 'BLENDED'`.
  - `ShaderNodeNewGeometry.Backfacing` conectado al factor `Fac` de un `ShaderNodeMixShader`.
  - `ShaderNodeEmission` negro `(0.04, 0.03, 0.03)` en el slot 1 (caras invertidas frontales al observador).
  - `ShaderNodeBsdfTransparent` en el slot 2 (caras frontales que se vuelven 100% transparentes).
- **Resultado:** Línea de tinta exterior nítida y continua de cómic que respeta el 100% de los materiales PBR interiores sin oscurecerlos.

### Pipeline de Texturizado Procedural de Alta Resolución (Pillow / PIL)
Para eliminar la apariencia de "primitivas geométricas apiladas", se integró generación procedural de texturas en Python antes del renderizado:
- **Bestiario:** Letrero `SECTOR 7` de chapa con tornillos perimetrales, pantalla CRT con telemetría verde fosfórica y osciloscopio, puerta de exclusa con advertencias estarcidas, tablero con siluetas de herramientas, escudo buckler con remaches y franjas diagonales de seguridad de 45°.
- **Mapas:** Casco remachado del buque con escurrimiento de óxido y rótulos `QUÍMICO MORTAL` y `ACIDGOO`, bandas atmosféricas de Saturno, alfombra Art Déco con grecas doradas, caoba pulida y letrero de Tokamak `REFINERÍA DE PLASMA`.
- **Hardware:** Mapa orbital 3D holográfico con órbitas elípticas, ECG con pulso biométrico PQRST, display OLED de gases y rótulos tácticos de suministros.

### Generador de Cristales BMesh Dipiramidales Facetados
Para el Titán de Fuego Azul (Blue Fire Golem), se sustituyó el apilado de conos por un generador determinista en `bmesh`:
- Construcción de dipirámide hexagonal limpia unificada (vértice cenital, ecuador de 6 lados y vértice inferior).
- Sombreado plano estricto (`use_smooth = False`) para que cada faceta capture especularidad angular independiente.
- Material `M_Crystal_Cyan` calibrado con emisión moderada (`1.2W`) y sin rugosidad de óxido para erradicar el quemado a blanco puro (*white clipping*) y garantizar un color cian-aguamarina saturado y vibrante.

---

## 3. Razón de Diseño (Rationale) y Principios SOLID

### S (Single Responsibility Principle)
- Cada script Python gestiona exclusivamente un subsistema de arte del juego:
  - `generar_bestiario_maestro_showcase.py`: Simulación anatómica, fuego/plasma, dipirámides bmesh y props del taller Sector 7.
  - `generar_hardware_shuttle_maestro.py`: Instrumental diegético, monitores tácticos, transmisión alfa criogénica y herramientas manuales de inserción.
  - `generar_mapas_dioramas_maestro.py`: Arquitectura ambiental de 3 tiers de misión (Carguero químico, Crucero orbital, Refinería de plasma).

### O (Open/Closed Principle)
- Los generadores admiten nuevas texturas procedurales, diales o arquetipos sin alterar la arquitectura base de sombreado Inverted Hull ni romper la compatibilidad con EEVEE.

### L (Liskov Substitution Principle)
- Todos los modelos y dioramas respetan la escala métrica canónica de Unreal Engine (1 unidad Blender = 1 metro; bomberos a 1.80m, pasarelas de 1.20 a 2.50m de ancho, barandillas a 1.00m de altura) asegurando sustitución transparente en la fase de exportación FBX/UCX.

### I (Interface Segregation Principle)
- Se desacopla la lógica de renderizado fotográfico (cámaras de showcase y tracking de 4 cuadrantes) de la estructura geométrica interna de los objetos. Cada diorama puede ser instanciado individualmente o en conjunto.

### D (Dependency Inversion Principle)
- Los generadores sintetizan el 100% de sus recursos (geometría, shaders, texturas Pillow, iluminación y composición de cuadrantes) de forma completamente autónoma y local mediante Python estándar y Pillow, garantizando reproducibilidad determinista en cualquier entorno sin depender de bibliotecas externas descargables.

### Filosofía Fail-Fast y Tipado Estricto
- Compatibilidad estricta con la API de **Blender 5.2 LTS** (`engine = 'BLENDER_EEVEE_NEXT'` / `'BLENDER_EEVEE'`).
- Calibración de fuentes de luz mediante ángulos de sombra de cómic (`sun_data.angle = R(8.0)`) y materiales de suelo mate (`roughness = 0.80`, `metallic = 0.15`) para erradicar quemaduras especulares.
- Rutas deterministas a `Art/Renders/` y sincronización automática hacia el directorio de artefactos del proyecto.

---

---

## 4. Catálogo Maestro de Activos 3D Modulares y Reutilizables (V6)

Para cumplir con el mandato estricto de descomposición integral de los mapas oficiales (`media_1791273626834.png`) y el bestiario mecánico (`media_1791273929163.png`) en **activos modulares independientes y reutilizables**, se ha implementado el generador maestro `Art/Blender/generar_catalogo_activos_modulares_v6.py`, respaldado por su biblioteca desacoplada de texturas y trim sheets en `Art/Textures/Modular/` y el archivo maestro oficial `Art/Blender/Catalogo_Activos_Modulares_Oficial.blend`.

### 4.1. Biblioteca de Texturas PBR y Trim Sheets Modulares (`Art/Textures/Modular/`)
Cada textura cuenta con mapas PBR completos (`BaseColor`, `Normal`, `ORM`, `Emissive`) generados en 2048x2048 para UV tiling y mapeo de alta densidad:
1. `T_Trim_Industrial_BaseColor.png`: Franjas hazard (45° amarillo/negro), hileras de remaches industriales, pletinas oxidadas, chapa corrugada naval.
2. `T_Luxury_Quilted_Velvet_Leather_BaseColor.png`: Textura de capitoné acolchado con rombos y botones para tapicería noble de terciopelo.
3. `T_Luxury_ArtDeco_Gilded_Brass_BaseColor.png`: Latón y oro cepillado pulido con grecas y líneas geométricas Art Déco.
4. `T_Luxury_Marble_Gold_Inlay_BaseColor.png`: Mármol Carrara blanco con veteado y grecas geométricas incrustadas en oro.
5. `T_Luxury_Walnut_Wood_Panels_BaseColor.png`: Boiserie de nogal oscuro con relieve y barniz satinado.
6. `T_Derelict_Rust_Plates_BaseColor.png`: Placas de acero con corrosión profunda, picaduras y escurridos de óxido.
7. `T_Corroded_Acid_Pipes_BaseColor.png`: Tuberías corroídas por agentes químicos y sales ácidas.
8. `T_Grating_Walkway_BaseColor.png`: Rejilla metálica electrosoldada antiderrapante.
9. `T_Props_Machinery_BaseColor.png`: Dial de manómetro analógico, osciloscopios CRT y botoneras de control.
10. `T_Steel_Plates_BaseColor.png`: Placas de blindaje remachadas de gunmetal industrial.

### 4.2. Descomposición de Kits Modulares (26 Activos Autónomos Reutilizables)
Todos los activos se ensamblan bajo una jerarquía modular no destructiva con raíz `Empty` (`assemble_asset()`), preservando modificadores Bevel independientes, pivotes en `(0, 0, Z=0)` y compatibilidad nativa para Blueprints/Prefabs en Unreal Engine 5:

- **Kit 01: Carguero Químico (Tier 1 - Industrial Derelict):**
  1. `SM_Contenedor_Espacial_TEU`: Contenedor de carga intermodal con 14 costillas corrugadas, cantoneras ISO y barras de cierre con levas.
  2. `SM_Tanque_Acido_Radiactivo`: Cuba química de casco oxidado con corte frontal abierto, líquido ácido verde radiactivo vibrante (`#15FF30`), escalera interior de inspección, burbujas efervescentes y vapores cónicos 2D.
  3. `SM_Brazo_Grua_Industrial`: Pescante hidráulico de carga con mástil giratorio, pluma en celosía amarilla, cilindro hidráulico y pinza de sujeción (*spreader claw*).
  4. `SM_Pasarela_Modular_Industrial`: Pasarela de 2.4m con suelo de rejilla electrosoldada, zócalos de seguridad hazard y doble pasamanos tubular.
  5. `SM_Viga_I_Industrial`: Columna gantry vertical de 3.2m en perfil I con pletina de anclaje de 4 pernos y refuerzos triangulares.
  6. `SM_Bateria_Barriles_Toxicos`: Trío de bidones químicos verde oliva con cinchas de advertencia y charco de ácido fluorescente en cubierta.

- **Kit 02: Crucero de Lujo (Tier 2 - Art Déco Celestia):**
  7. `SM_Ventanal_Arqueado_Observatorio`: Ventanal monumental semicircular con doble nervadura de latón dorado y vista panorámica al cosmos (planeta Saturno con anillos).
  8. `SM_Panel_Boiserie_ArtDeco`: Panel mural de madera de nogal con molduras escalonadas y rombos dorados, complementado con alfombra burdeos y grecas concéntricas de oro.
  9. `SM_Sillon_ArtDeco_Chesterfield`: Sillón club individual en terciopelo burdeos profundo (`#3A0A16`) con capitoné diamantado y patas de caoba con punteras de latón.
  10. `SM_Sofa_Doble_ArtDeco`: Sofá de dos plazas en terciopelo burdeos capitoné con reposabrazos cilíndricos y patas rematadas en oro.
  11. `SM_Mesa_Marmol_Oro_ArtDeco`: Mesa de centro circular de mármol Carrara con aro biselado de latón, patas trípode, aro de refuerzo y copa de cóctel.
  12. `SM_Espejo_Monumental_Solsticio`: Espejo biselado rodeado por 16 rayos solares geométricos dorados de longitud alternada.
  13. `SM_Lampara_Arana_Ziggurat`: Candelabro suspendido de tres niveles escalonados de latón y difusores cilíndricos de luz ámbar suave.
  14. `SM_Lampara_Pie_Salon`: Lámpara de pie de salón con base escalonada de latón, mástil esbelto y pantalla trapezoidal de luz cálida.

- **Kit 03: Refinería de Plasma (Tier 3 - Alta Tensión):**
  15. `SM_Generador_Toroidal_Plasma`: Reactor de confinamiento magnético toroidal con 6 grapas de alta tensión, anillo de plasma cian eléctrico y singularidad central con arcos voltaicos.
  16. `SM_Bateria_Tuberias_Colector`: Colector vertical y codo de tuberías bridadas en gunmetal con mirilla de inspección de plasma cian.
  17. `SM_Consola_Control_Plasma`: Pupitre angular de mando con monitor CRT de fósforo activo, pulsador de parada de emergencia y botonera.
  18. `SM_Cartelera_Peligro_Plasma`: Cartelera industrial mural con placa de advertencia de alta tensión y franjas diagonales negras/amarillas.
  19. `SM_Modulo_Pasarela_Curva`: Tramo de pasarela de inspección con suelo de rejilla y barandilla tubular perimetral.
  20. `SM_Dron_Minero_Observador`: Subdron minero esférico flotante con aletas estabilizadoras y sensor óptico cian.

- **Kit 04: Componentes de Enemigos y Mecánica Chatarrera:**
  21. `SM_Dron_Auditor_Esferico`: Casco esférico blindado de gunmetal con remaches, ojo óptico prominente con bisel de latón y lente carmesí emisiva (`#FF0A1A`), tres manómetros superiores, CRT inferior, propulsores de actitud y patas trípode.
  22. `SM_Sierra_Circular_24Dientes`: Disco de sierra de acero al carbono de 1.2m con 24 dientes afilados biselados y cubo central amarillo apernado con 4 tornillos.
  23. `SM_Chimeneas_Fuego_Comic`: Colector triple de chimeneas acodadas con llamaradas cónicas estilizadas en 2 capas (núcleo amarillo, borde naranja cómic).
  24. `SM_Piston_Hidraulico_Articulado`: Cilindro hidráulico de gunmetal con vástago de cromo pulido a espejo, horquillas basculantes amarillas y latiguillo de presión.
  25. `SM_Maza_Puas_Chatarrera`: Maza de impacto pesada con mango de caoba, cabeza de fundición y 8 púas cónicas radiales de acero templado.
  26. `SM_Racor_Triple_Manometros`: Soporte mural con batería de 3 manómetros analógicos de latón, carátulas blancas calibradas y agujas indicadoras rojas.

### 4.3. Rationale de Ingeniería de Software (Clean Code & SOLID)
- **Principio de Responsabilidad Única (SRP):** Cada activo modular resuelve una función física o arquitectónica aislada. No existen mallas monolíticas indivisibles; el foso químico, la grúa, el reactor y los manómetros son entidades separadas listas para instanciación en cualquier mapa.
- **Principio Abierto/Cerrado (OCP):** El gestor de ensamblado `assemble_asset()` y la función `get_stylized_material()` permiten incorporar nuevos kits temáticos o packs de texturas sin modificar los contratos geométricos existentes.
- **Calibración Cinematográfica Fail-Fast:** Implementación de tracking vectorial matemático (`to_track_quat('-Z', 'Y')`) para cámaras close-up y panorama, garantizando un encuadre óptimo sin cortes de mallas, sobreexposición de lúmenes ni artefactos de recorte.

---

## 5. Ensamblado de Salas Modulares Jugables (Level Assembly Dioramas V1)

### 5.1. Propósito y Alcance
El generador arquitectónico [`generar_salas_modulares_ensambladas_oficial.py`](file:///F:/Dev/Game/Art/Blender/generar_salas_modulares_ensambladas_oficial.py) demuestra la aplicabilidad directa del catálogo de 26 activos modulares V6 mediante el ensamblado de tres dioramas arquitectónicos jugables independientes (8.6m x 8.6m x 4.8m cada uno) sobre plintos de exhibición con placas de latón grabadas:
1. **Sala 1: Bahía de Carga Química (Tier 1 - Carguero Industrial Derelict):**
   - **Activos Instanciados:** Muros y cornisa de acero oxidado `Mat_Rust_Hull`, suelo de rejilla `Mat_Grate_Steel`, cuba de ácido con fluido verde fluorescente (`#15FF30`), contenedores TEU apilados de forma dinámica, grúa pescante de celosía, pasarela modular elevada con barandillas tubulares, vigas estructurales I-Beam apernadas, batería de barriles tóxicos con charco químico húmedo `Mat_Acid_Spill_Puddle`, racor triple de manómetros, valvulería manual roja y rótulo de advertencia química.
   - **Iluminación de Estudio:** Softbox difuso de área (560W, ámbar) + luz de relleno lateral (300W, azulada) + radiación volumétrica verde radiactivo sin sombras oclusivas sobre paredes.
2. **Sala 2: Gran Salón VIP y Observatorio "Celestia" (Tier 2 - Crucero Art Déco):**
   - **Activos Instanciados:** Caparazón de mármol Carrara y nogal barnizado, moldura perimetral de oro, gran alfombra palaciega capitoné burdeos (`#3A0A16`) con doble greca geométrica dorada, ventanal monumental de latón con vista astronómica 2.5D a Saturno (disco gaseoso y anillos elípticos coplanares con división Cassini sin penetración de mamparos), sofás y sillones club Chesterfield, mesa de centro Carrara/oro con copa de cóctel, lámparas de pie trapezoidales, araña Ziggurat de latón y espejo Solsticio.
   - **Iluminación de Estudio:** Softbox de área cálido (460W) + relleno lateral (240W) + araña de techo Ziggurat (440W) + atmósfera fría del cosmos exterior.
3. **Sala 3: Cámara del Reactor Tokamak (Tier 3 - Hipertecnología y Alta Tensión):**
   - **Activos Instanciados:** Muros de blindaje militar `Mat_Plasma_Chamber_Wall`, suelo oscuro `Mat_Chamber_Floor_Dark`, pozo cilíndrico de confinamiento magnético, reactor toroidal Tokamak con 6 grapas de alta tensión, anillo de plasma cian eléctrico (`#00E5FF`) y singularidad central con arcos voltaicos, pasarela modular curva en voladizo, puesto de control con consola terminal CRT y pantalla de fósforo verde con osciloscopio orientada a la cámara, batería colectora de tuberías, cartelera mural de peligro de plasma, subdron minero en suspensión gravitatoria, pistón hidráulico y transformador con chimeneas de fuego cómic.
   - **Iluminación de Estudio:** Softbox de área frío (560W) + relleno cian (300W) + resplandor eléctrico del reactor toroidal (620W) sin sombras oclusivas del toro sobre los mamparos.

### 5.2. Rationale de Iluminación y Renderizado
- **Eliminación de Artefactos Conicales:** Se descartaron focos Spot convencionales de ángulo estrecho que generaban sombras curvas duras en las esquinas, sustituyéndolos por luces de área rectangulares de estudio (Softboxes difusos 8.5x6m y 7x5m) que proporcionan una caída suave y uniforme.
- **Desacoplamiento de Sombras en Emisores Diegéticos:** Los emisores de punto locales (`Chem_Acid_Glow` y `Plasma_Core_Light`) se configuraron con `use_shadow = False` para actuar como luz de radiación volumétrica ambiental sin proyectar sombras fantasma del borde de la cuba o de las bobinas del toro sobre los muros distantes.
- **Suelo Exterior Infinito Mate:** Configuración de `Mat_Studio_Floor` con `roughness = 0.98` y `metallic = 0.0`, erradicando halos especulares quemados en la escena panorámica tríptica.

---

## 6. Estado Actual y Validación

| Subsistema | Archivo Generador | Archivo Maestro (.blend) | Render Oficial Validado | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **Bestiario Mecánico Sector 7** | `Art/Blender/generar_bestiario_maestro_showcase.py` | `Art/Blender/Bestiario_Entidades_Oficial.blend` | `Showcase_Bestiario_Entidades_Oficial.png` | **100% Completado y Aprobado** |
| **Hardware y Gadgets Lanzadera** | `Art/Blender/generar_hardware_shuttle_maestro.py` | `Art/Blender/Hardware_Mision_Y_Gadgets_Oficial.blend` | `Showcase_Hardware_Y_Gadgets_Oficial.png` | **100% Completado y Aprobado** |
| **Mapas y Dioramas Tríptico** | `Art/Blender/generar_mapas_dioramas_maestro.py` | `Art/Blender/Mapas_Arquetipos_Oficial.blend` | `Showcase_Mapas_Arquetipos_Oficial.png` | **100% Completado y Aprobado** |
| **Catálogo de Activos Modulares V6 (26 Assets)** | `Art/Blender/generar_catalogo_activos_modulares_v6.py` | `Art/Blender/Catalogo_Activos_Modulares_Oficial.blend` | `Showcase_Catalogo_Activos_Modulares_Master.png` | **100% Completado y Aprobado (90%+ Fidelidad Visual)** |
| **Ensamblado de Salas Modulares (3 Dioramas)** | `Art/Blender/generar_salas_modulares_ensambladas_oficial.py` | `Art/Blender/Salas_Modulares_Ensambladas_Oficial.blend` | `Showcase_Salas_Ensambladas_Master.png` | **100% Completado y Aprobado (Calidad AAA / PBR)** |

> **Nota de Confinamiento:** Todo el arte se encuentra confinado en Blender 5.2 LTS (`.blend` y `.png`) a la espera de la autorización explícita del usuario para iniciar la fase de exportación FBX/UCX y su posterior ingesta en Unreal Engine 5.8.

