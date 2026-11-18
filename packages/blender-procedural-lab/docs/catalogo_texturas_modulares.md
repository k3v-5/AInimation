# Catálogo Maestro de Texturas y Materiales PBR Modulares (Fase Industrial & Fábrica)

## 1. Propósito y Alcance

Este documento especifica la arquitectura técnica, el pipeline de generación procedural y el catálogo oficial de **texturas modulares PBR y materiales estilizados** para los entornos de mapas, arquitectura estructural y objetos/props del juego *Astra Hazard*.

El objetivo principal es desacoplar completamente las superficies visuales de las geometrías tridimensionales fijas, proporcionando un conjunto de **Trim Sheets y Atlas PBR estándar** (2048x2048) con estética cómic-industrial (delineado de *inlines* de tinta, desgaste y óxido *hand-painted*, micro-relieve de remaches y sombreado *cel-shading* de alto contraste) listo para aplicarse a futuros mapas (Fábrica, Refinería, Carguero, Estación Orbital) y a todo el atrezo interactivo.

---

## 2. Contratos e Interfaces Técnicas de Texturas

### 2.1. Estándar de Canales PBR y Empaquetado ORM

Cada familia de materiales se compone de 4 mapas de textura optimizados según los estándares de la industria y la arquitectura de memoria de Unreal Engine 5:

| Canal / Mapa | Formato | Espacio de Color | Descripción y Contrato Funcional |
| :--- | :--- | :--- | :--- |
| **`BaseColor`** | PNG 24-bit sRGB | sRGB | Albedo estilizado que integra el color base, pátina de óxido, desgaste en aristas e *inlines* negros de tinta en juntas y remaches. |
| **`Normal`** | PNG 24-bit RGB | Non-Color / Linear | Mapa de normales en espacio tangente (*Tangent Space*). Ejes configurados para Unreal Engine (+X Derecha, -Y Abajo / Invertido, +Z Arriba) para remaches cónicos, biseles de ranuras a 45° y crestas corrugadas. |
| **`ORM`** | PNG 24-bit RGB | Non-Color / Linear | **Canal compuesto multi-canal:**<br>• **Canal R:** Oclusión Ambiental (*Ambient Occlusion*, hendiduras y juntas).<br>• **Canal G:** Rugosidad (*Roughness*, modulación entre pintura mate, óxido áspero y metal pulido).<br>• **Canal B:** Metalicidad (*Metallic*, 0.0 en dieléctricos como hormigón/óxido, 0.9–1.0 en aceros/pernos). |
| **`Emissive`** | PNG 24-bit sRGB | sRGB | Máscara de emisión luminosa para indicadores LED, pantallas CRT, señales de emergencia y filamentos calientes (multiplicado por intensidad HDR en el shader). |

---

## 3. Familias del Catálogo Oficial (Industrial & Fábrica)

### 3.1. `T_Trim_Industrial_PBR` (Trim Sheet Maestro Multi-Propósito)
Diseñado para cubrir verticalmente elementos estructurales mediante coordenadas UV normalizadas en franjas horizontales (Y: 0..2048):
1. **Franja Hazard Chevrons (Y: 0–256):** Rayas de seguridad a 45° en amarillo industrial (#F5BE14) y negro azabache (#161618), delimitadas por inlines gruesos y micro-arañazos.
2. **Placas de Acero Pesado (Y: 256–768):** Cuadrantes modulares cada 512 px con juntas biseladas, hileras dobles de pernos y remaches, y pátina de óxido naranja intenso (#A54416).
3. **Rejilla Perforada Diamond Mesh (Y: 768–1280):** Malla antideslizante con marco reforzado y profundidad oclusiva en los orificios calados.
4. **Paneles Estarcidos y Rótulos (Y: 1280–1664):** Fondo ocre con señalética estarcida de advertencia (*"FACTORÍA SECTOR 07"*, *"VAPOR // ALTA PRESIÓN"* y piloto luminoso emisivo de peligro).
5. **Chapa Corrugada Naval (Y: 1664–2048):** Ondulaciones sinusoidales con relieve normal calculado y rotulado corporativo (*"ASTRA HAZARD // REFINERÍA"*).

### 3.2. `T_Steel_Plates_PBR` (Blindaje y Vigas Estructurales)
- Cuatro grandes placas soldadas de 1024x1024 con biseles perimetrales de 16 px.
- Doble hilera de remaches de alta resistencia (altura normal = 240, AO profundo).
- Cordón diagonal de soldadura con micro-textura rugosa y ranuras centrales oscurecidas.

### 3.3. `T_Grating_Walkway_PBR` (Pasarelas Caladas y Suelos de Fábrica)
- Marco perimetral reforzado de vigas de 96 px con cabezas de perno hexagonales.
- Patrón geométrico de rombos metálicos expandidos con huecos calados ocluidos al 80% en el canal R del mapa ORM.
- Respuesta especular metálica alta (B = 0.90) con aristas contrastadas.

### 3.4. `T_Concrete_Factory_PBR` (Hormigón Armado y Cemento Estructural)
- Base grisácea desaturada con micro-grano generado proceduralmente.
- Grietas estructurales sinuosas con delineado entintado y hendidura profunda en el mapa de normales.
- Manchas de aceite y humedad industrial que reducen la rugosidad superficial (G = 0.55), simulando superficies resbaladizas y húmedas.
- Comportamiento puramente dieléctrico (B = 0.0).

### 3.5. `T_Props_Machinery_PBR` (Instrumentación, Consolas y Tuberías)
- **Cuadrante 1:** Manómetros y diales analógicos con bisel exterior de latón, carátula blanca envejecida, graduación radial a 360° y aguja indicadora roja.
- **Cuadrante 2:** Pantalla CRT retro-industrial de fósforo verde con retícula de osciloscopio, curva senoidal de telemetría y texto emisivo en alta definición.
- **Cuadrante 3:** Panel de pulsadores con botón tipo hongo de parada de emergencia en rojo intenso y balizas piloto LED (rojo, amarillo, verde) con máscara de emisión pura.
- **Cuadrante 4:** Tubería de fluidos pesados con acabado de bronce/cobre corrugado y bridas de acople reforzadas con pernos de sujeción.

---

### 3.6. `T_Derelict_Rust_Plates` (Chapa Descascarillada, Desprendimiento y Picaduras)
- **Tier / Contexto:** Tier 1 Carguero Químico & Tier 3 Derelict Industrial.
- **BaseColor:** Placas rectangulares gruesas de aleación de acero naval pintadas originalmente en verde-oliva/teal militar. Descascarillado severo con bordes de tinta oscura (*inlines*), revelando metal crudo profundamente oxidado en tonos naranja óxido (#9C3E14) y marrón umbrío (#4A210D). Soldaduras de cordón con rebaba física y pernos hexagonales con escurrimientos verticales de herrumbre.
- **Normal:** Normales tangentes profundas calculadas con relieve físico para el salto de la película de pintura (desnivel de 350 μm), cordones de soldadura con micro-burbujas y cráteres de corrosión.
- **ORM:** Oclusión ambiental profunda en ranuras de unión inter-placa (R = 0.22); rugosidad elevada en zonas de herrumbre áspera (G = 0.88–0.95) y pulida en bordes de fricción (G = 0.40); metalicidad en placas de acero desnudas (B = 0.85) y nula en óxido (B = 0.05).
- **Emissive:** Nulo (0, 0, 0).

### 3.7. `T_Battered_Armor_Impacts` (Mamparo Blindado con Impactos Balísticos y Metralla)
- **Tier / Contexto:** Zonas de combate, brechas de casco y sectores de catástrofe pesada.
- **BaseColor:** Mamparo naval blindado de gunmetal oscuro percutido por artillería pesada y proyectiles cinéticos. Cráteres cónicos profundos con rebabas elevadas de metal desgarrado, esquirlas de metralla, grietas de tensión radiales con delineado entintado y marcas circulares de quemadura y hollín.
- **Normal:** Fuerte deformación perpendicular en los labios de impacto elevados (+Z), fracturas de cizallamiento con biseles abruptos y micro-arañazos balísticos multidireccionales.
- **ORM:** AO profundo en el núcleo del cráter (R = 0.15); rugosidad ultra-baja en el acero recién cizallado de las rebabas (G = 0.18) y alta en depósitos de carbonilla/hollín (G = 0.78); metalicidad pura en el cuerpo del blindaje (B = 0.95).
- **Emissive:** Nulo (0, 0, 0).

### 3.8. `T_Corroded_Acid_Pipes` (Haz de Tuberías con Pátina Verdigris y Fugas Químicas)
- **Tier / Contexto:** Tier 1 Carguero Químico & Refinerías de Procesamiento Químico.
- **BaseColor:** Red densa de tuberías de cuproníquel y bronce envejecido con bridas y pernos de acople. Corrosión extrema por reactivos con pátina turquesa verdigris (#1CB89C), costras de azufre amarillo y roturas de conducto con escurrimientos y charcos de ácido verde fosforescente (#26F53D).
- **Normal:** Perfil cilíndrico marcado con costuras de fundición, escamas de corrosión en relieve y relieve invertido en los puntos de fractura del conducto.
- **ORM:** AO en intersecciones de tuberías (R = 0.20); rugosidad ultra-brillante en fluidos químicos líquidos (G = 0.08) y áspera en costras minerales (G = 0.82); metalicidad alta en bridas de bronce (B = 0.90) y nula en el fluido (B = 0.05).
- **Emissive:** Máscara HDR sRGB intensa en las fugas y gotas de ácido verde reactivo (intensidad 4.0 en shader).

### 3.9. `T_Decayed_Rusted_Grating` (Pasarela de Acero Romboide Carcomida y Rota)
- **Tier / Contexto:** Pasarelas elevadas abandonadas, conductos de mantenimiento y salas de máquinas.
- **BaseColor:** Trama romboidal pesada de barras de acero de 18 mm. Desgaste pulido en la huella de tránsito central, óxido escamoso en los laterales y una gran rotura irregular con barras retorcidas y rotas que dejan ver el vacío oscuro subyacente.
- **Normal:** Biseles tangentes a 45° en las barras transversales, puntas de corte irregulares y micro-picado en caras superiores.
- **ORM:** Oclusión total en los orificios calados (R = 0.05); rugosidad baja en la zona de desgaste por pisadas (G = 0.22) y áspera en herrumbre (G = 0.85); metalicidad en acero estructural (B = 0.95).
- **Emissive:** Nulo (0, 0, 0).

### 3.10. `T_Scorched_Plasma_Slag` (Mamparo Perforado por Plasma, Flujo Térmico y Escoria)
- **Tier / Contexto:** Tier 3 Refinería de Plasma 'Black Rock' & Sectores de Sobrecarga de Reactores.
- **BaseColor:** Blindaje de titanio oscurecido cortado por un haz de plasma concentrado. Brecha central incandescente con núcleo ardiente naranja-amarillo (#FF9419 / #FFF266), rodeada de escoria negra coagulada y halos continuos de temple térmico físico (gradiente de titanio anodizado: bronce, púrpura, azul eléctrico y hollín).
- **Normal:** Depresión central profunda, costras de escoria sobreelevadas y micro-arrugas por enfriamiento rápido del metal fundido.
- **ORM:** AO en cavidades de escoria (R = 0.25); rugosidad reflectante en el núcleo líquido (G = 0.12) y mate en la carbonilla externa (G = 0.80); metalicidad en placa de titanio (B = 0.92) y nula en escoria/hollín (B = 0.05).
- **Emissive:** Máscara HDR de alta intensidad calibrada para el núcleo fundido y micro-fisuras térmicas (brillo emissive = 4.5).

---

### 3.11. `T_Luxury_Marble_Gold_Inlay` (Mármol Calacatta Pulido con Mosaico de Oro 24k)
- **Tier / Contexto:** Tier 2 Crucero de Placer 'Celestia' (Gran Salón, Suites Presidenciales).
- **BaseColor:** Mármol blanco Calacatta extra-fino con vetas orgánicas fluidas en gris perla y ocre suave, interrumpido por un intrincado mosaico geométrico Art Déco de pletinas de latón y oro macizo de 24k (#E4BC44) con bandas biseladas y chevrons simétricos.
- **Normal:** Superficie de mármol pulida espejo con micro-relieve en las juntas de dilatación e incrustaciones metálicas ligeramente sobresalientes (+0.08 mm).
- **ORM:** AO en la ranura de junta de oro (R = 0.40); rugosidad extremadamente baja en mármol pulido espejo (G = 0.08) y acabado satinado en oro (G = 0.18); metalicidad 0.98 en bandas de oro y 0.02 en piedra calcárea.
- **Emissive:** Nulo (0, 0, 0).

### 3.12. `T_Luxury_Walnut_Wood_Panels` (Boiserie Vertical de Nogal Noble con Molduras de Latón)
- **Tier / Contexto:** Tier 2 Crucero de Placer 'Celestia' (Biblioteca, Pasillos VIP y Camas de Primera Clase).
- **BaseColor:** Tableros verticales de madera noble de nogal americano con vetas continuas profundas en tonos marrón chocolate (#3C2114) y castaño cálido (#623820). Secciones acanaladas *fluted tambour* y listeles verticales de separación en latón dorado satinado.
- **Normal:** Micro-grano de madera longitudinal y volumen estriado semicilíndrico en las acanaladuras de ebanistería.
- **ORM:** AO en ranuras de moldura (R = 0.30); rugosidad satinada de barniz al aceite (G = 0.28–0.32) y pulida en latón (G = 0.16); metalicidad en listeles de latón (B = 0.96) y nula en madera (B = 0.01).
- **Emissive:** Nulo (0, 0, 0).

### 3.13. `T_Luxury_ArtDeco_Gilded_Brass` (Relieve de Escamas Solares en Latón Dorado Art Déco)
- **Tier / Contexto:** Tier 2 Crucero de Placer 'Celestia' (Puertas Monumentales, Mamparos de Salón de Gala).
- **BaseColor:** Panel metálico arquitectónico monumental con abanicos solares escalonados en 3D, motivos geométricos de greca clásica y escamas biseladas en latón dorado brillante (#E8C654) con sombras de pátina envejecida en las hendiduras (#463216).
- **Normal:** Fuerte mapa de relieve con niveles escalonados (*stepped relief*), acanaladuras radiales y biseles agudos a 30°.
- **ORM:** AO pronunciado en los fondos del bajorrelieve (R = 0.22); rugosidad de latón cepillado fino (G = 0.20) que asciende en ranuras oscuras (G = 0.58); metalicidad dominante (B = 0.98).
- **Emissive:** Nulo (0, 0, 0).

### 3.14. `T_Luxury_Quilted_Velvet_Leather` (Capitoné Chesterfield Azul Noche con Botones Dorados)
- **Tier / Contexto:** Tier 2 Crucero de Placer 'Celestia' (Mobiliario de Lujo, Salones Lounge, Butacas).
- **BaseColor:** Tapicería capitoné clásica en rombos de cuero suave y terciopelo azul marino noche (#0E1A33) con pliegues realistas de tensión pinched hacia los botones y botones metálicos de latón dorado tapicero en cada intersección.
- **Normal:** Volúmenes almohadillados convexos marcados, arrugas radiales de tensión en torno a los botones y micro-porosidad dérmica de cuero noble.
- **ORM:** Oclusión ambiental en el pozo de cada botón (R = 0.18); rugosidad diferenciada (G = 0.40 en cuero mate, G = 0.14 en botones dorados); metalicidad en botones (B = 0.98) y cero en cuero (B = 0.0).
- **Emissive:** Nulo (0, 0, 0).

### 3.15. `T_Luxury_Smoked_Glass_Lattice` (Vidrio Obsidiana con Celosía de Latón y Retroiluminación)
- **Tier / Contexto:** Tier 2 Crucero de Placer 'Celestia' (Mamparos Divisorios de Suite y Ventanales de Salón).
- **BaseColor:** Panel de vidrio ahumado obsidiana templado de alta reflectancia con un enrejado tridimensional de celosía geométrica Art Déco rematado en tachuelas doradas, retroiluminado por una fuente de luz cálida difusa ámbar 2700K desde el interior.
- **Normal:** Relieve del enrejado de latón sobresaliente con chaflanes en bordes y tachuelas semiesféricas.
- **ORM:** AO en uniones de la celosía (R = 0.28); rugosidad ultra-baja en cristal templado espejo (G = 0.06) y satinada en latón (G = 0.22); metalicidad en la celosía (B = 0.95) y nula en vidrio (B = 0.05).
- **Emissive:** Máscara ámbar cálida (#FFAC30) en las zonas donde la luz interior se filtra a través del cristal translúcido (intensidad 3.5 en shader).

---

## 4. Arquitectura de Shaders y Material Test Bench

### 4.1. Grafo de Sombreado en Blender 5.2 LTS (`M_Master_PBR_CelShade`)
El script [`generar_material_test_bench.py`](file:///F:/Dev/Game/Art/Blender/generar_material_test_bench.py) automatiza la configuración de la red de nodos:
- **`ShaderNodeTexCoord` (UV) + `ShaderNodeMapping`:** Permite control de escalado y repetición (*tiling*).
- **`ShaderNodeTexImage` (BaseColor - sRGB):** Alimentación directa al albedo del `Principled BSDF`.
- **`ShaderNodeTexImage` (ORM - Non-Color) + `ShaderNodeSeparateColor`:**
  - `Canal G (Green)` $\rightarrow$ `Roughness`.
  - `Canal B (Blue)` $\rightarrow$ `Metallic`.
  - `Canal R (Red)` $\rightarrow$ Oclusión multiplicativa sobre sombras cel-shade.
- **`ShaderNodeTexImage` (Normal - Non-Color) + `ShaderNodeNormalMap` (Tangent Space):** Fuerza 1.2 $\rightarrow$ Entrada `Normal` del BSDF.
- **`ShaderNodeTexImage` (Emissive - sRGB):** $\rightarrow$ `Emission Color` con `Emission Strength` = 3.5.
- **Freestyle Ink Lines:** Trazo de contorno negro con grosor de 1.8 px y ángulo de quiebre a 135° para siluetas de cómic nítidas.

### 4.2. Escena del Banco de Pruebas V5 (`Material_Test_Bench.blend`)
- **Ciclorama de Estudio:** Fondo curvo continuo en grafito mate de baja reflectancia con iluminación de tres puntos (Key Sun a 45° cálido 4500K, Rim Light cian posterior y Fill Light rasante).
- **Estaciones 1 a 5:** Cada estación cuenta con:
  - Una **Shader Ball Pro V5** clásica de 4 componentes:
    - Cáscara exterior esférica con **UVs nativas preservadas** (`primitive_uv_sphere_add` en lugar de constructos bmesh crudos sin capas de coordenadas UV).
    - **Corte seccional en el cuadrante frontal-derecho** (`x > 0.04, y < -0.04, z > -0.22`): revela el interior sin comprometer el 75% del área frontal donde se exhibe el material texturizado.
    - Núcleo interior reflectante de latón pulido (*Roughness* 0.08, *Metallic* 1.0).
    - Anillo de acople estilizado con inclinación cinemática a 14°.
    - Plinto cilíndrico de soporte asentado firmemente en $Z = 0.50\text{ m}$ sobre la columna del pedestal (erradicando holguras flotantes).
  - Un **Prop Contextual Específico** en lugar de cubos genéricos:
    - *Estación 01 (Trim):* Muro arquitectónico modular con zócalo corrugado y baliza.
    - *Estación 02 (Steel):* Mamparo blindado de 4 placas con remaches y marcas diagonales.
    - *Estación 03 (Grating):* Plataforma elevada con patas de soporte y malla antideslizante.
    - *Estación 04 (Concrete):* Columna octagonal de cemento armado con micro-fisuras.
    - *Estación 05 (Props):* Consola de control diegética con visera biselada y pantalla CRT.
  - Una **Tableta de Muestra Inclinada** a 35° para exhibición plana ortogonal.
  - **Placas de Identificación 3D Centradas:** Texto geométrico 3D alineado en $Z = 0.12\text{ m}$ centrado en placas de latón satinado.

---

## 5. Auditoría Diagnóstica y Progresión V1 $\rightarrow$ V5

En cumplimiento de las normas de ingeniería de software, se realizó una auditoría visual y geométrica rigurosa de las primeras versiones, corrigiendo sistemáticamente cada deficiencia:

| Componente / Área | Falla Identificada en V1–V3 | Causa Raíz Técnica | Solución Implementada en V5 Oficial |
| :--- | :--- | :--- | :--- |
| **Mapeo UV en Shader Ball** | Color plano sin textura en la esfera exterior. | `bmesh.new()` instanciaba geometría sin capa activa `uv_layers`, provocando lectura UV fija en $(0,0)$. | Uso de `primitive_uv_sphere_add` nativo con supresión de vértices en Edit Mode preservando el mapeo UV continuo. |
| **Encuadre de Cámaras Focales** | Recorte superior (*clipping*) de las esferas. | Distancia focal corta ($Y = -4.5\text{ m}$) y altura insuficiente. | Cámaras calibradas a $Y = -5.6\text{ m}, Z = 1.35\text{ m}, \text{Rot} = 80^\circ, \text{FOV} = 48^\circ$ con *headroom* holgado. |
| **Encuadre Panorámico** | Extremos laterales cortados y vacío excesivo. | FOV estrecho y posición de cámara demasiado elevada. | Cámara panorámica calibrada a $Y = -13.0\text{ m}, Z = 2.1\text{ m}, \text{FOV} = 75^\circ$, cubriendo las 5 estaciones al 92% del encuadre. |
| **Sección de Shader Ball** | Hueco girado hacia atrás o corte excesivo frontal. | Rotación acumulada en Z posterior a la eliminación de vértices. | Eliminación de rotaciones en Z; corte acotado exclusivamente al cuadrante frontal-derecho (+X, -Y). |
| **Contacto Físico de Base** | Holgura de 24 cm entre el stand y el pedestal. | Cota Z incorrecta en el centroide del cilindro. | Asentamiento exacto en $Z = 0.50\text{ m}$, garantizando contacto físico con gravedad realista. |
| **Placas de Texto 3D** | Texto descentrado o superpuesto a bordes. | Falta de alineación en el eje vertical del texto. | Configuración de `align_y = 'CENTER'` y anclaje paramétrico a la placa dorada. |
| **Props Contextuales** | Cubos genéricos primitivos sin relación contextual. | Ausencia de lógica de construcción procedural especializada. | 5 props modulares temáticos específicos por estación (Muro, Mamparo, Plataforma, Columna, Consola). |
| **Composición Infográfica** | Distorsión de aspecto en tarjetas (esferas ovaladas). | Redimensionado libre a $569\times510\text{ px}$ sin conservar el aspect-ratio nativo. | Recorte centrado a proporción 4:3 nativa y 5 columnas independientes con píldoras de especificaciones técnicas. |

---

## 6. Razón de Diseño (Rationale) y Principios SOLID

1. **Single Responsibility Principle (SRP):**
   - La textura almacena únicamente información superficial de materiales (reflectancia, micro-relieve, albedo, emisión). La geometría del actor o mapa sólo aporta la forma y coordenadas UV.
   - La separación de canales ORM aísla la oclusión ambiental, la micro-rugosidad y la conducción eléctrica en canales monocromáticos independientes sin interferencia mutua.

2. **Open/Closed Principle (OCP):**
   - El uso de **Trim Sheets modulares** permite vestir infinitos modelos de mallas (tuberías, pasarelas, contenedores, muros) mapeando diferentes coordenadas UV a las franjas predefinidas sin alterar los mapas de textura base ni recompilar shaders.

3. **Dependency Inversion Principle (DIP):**
   - El sistema de materiales depende de abstracciones estándar (PBR Tangent Space + ORM Channel Packing) soportadas idénticamente por Blender EEVEE Next y Unreal Engine 5 (Nanite/Lumen), desacoplando los activos artísticos del motor de render concreto.

4. **Filosofía Fail-Fast:**
   - El generador [`generar_pbr_texturas_industriales_v2.py`](file:///F:/Dev/Game/Art/Textures/Modular/generar_pbr_texturas_industriales_v2.py) valida estrictamente los rangos de altura [0.0, 1.0], normaliza los vectores tangentes mediante Sobel con guarda `np.maximum(norm, 1e-6)` para impedir divisiones por cero, y asegura la no inversión de canales en los mapas generados.

---

## 7. Registro de Archivos y Renders Oficiales

| Recurso | Archivo en Proyecto | Propósito |
| :--- | :--- | :--- |
| **Generador Texturas PBR V2** | [`generar_pbr_texturas_industriales_v2.py`](file:///F:/Dev/Game/Art/Textures/Modular/generar_pbr_texturas_industriales_v2.py) | Script de síntesis procedural de los 20 mapas PBR V2 en 2048x2048 con mejoras orgánicas. |
| **Generador Test Bench V5** | [`generar_material_test_bench_v5.py`](file:///F:/Dev/Game/Art/Blender/generar_material_test_bench_v5.py) | Automatización oficial de escena 3D y renderizado multicámara en Blender 5.2 LTS. |
| **Compositor Lámina Maestra** | [`componer_showcase_texturas.py`](file:///F:/Dev/Game/Art/Blender/componer_showcase_texturas.py) | Montaje de la infografía maestra 2560x1440 con 5 estaciones y píldoras de especificaciones técnicas. |
| **Escena Blender Oficial** | [`Material_Test_Bench.blend`](file:///F:/Dev/Game/Art/Blender/Material_Test_Bench.blend) | Proyecto 3D editable con los 5 materiales PBR aplicados a shader balls y props. |
| **Lámina Maestra 2.5K** | [`Showcase_Catalogo_Texturas_Master.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Catalogo_Texturas_Master.png) | Infografía maestra con panorama y 5 columnas focales nativas 4:3. |
| **Panorama Test Bench** | [`Showcase_Material_Test_Bench_Master.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Material_Test_Bench_Master.png) | Render panorámico 2560x1440 de las 5 estaciones de prueba. |
| **Estación 01: Trim Industrial** | [`Showcase_Material_Trim_Industrial.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Material_Trim_Industrial.png) | Render 1080p close-up de shader ball, muro de advertencia y tableta de Trim Sheet. |
| **Estación 02: Steel Plates** | [`Showcase_Material_Steel_Plates.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Material_Steel_Plates.png) | Render 1080p close-up de placas de blindaje remachadas y mamparo contextual. |
| **Estación 03: Grating Walkway** | [`Showcase_Material_Grating_Walkway.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Material_Grating_Walkway.png) | Render 1080p close-up de pasarela de rejilla calada y plataforma modular. |
| **Estación 04: Concrete Factory** | [`Showcase_Material_Concrete_Factory.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Material_Concrete_Factory.png) | Render 1080p close-up de hormigón agrietado con pilar octagonal y manchas de grasa. |
| **Estación 05: Props Machinery** | [`Showcase_Material_Props_Machinery.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Material_Props_Machinery.png) | Render 1080p close-up de consola diegética, osciloscopio CRT y diales analógicos. |
| **Procesador PBR Cinemático** | [`procesar_mapas_pbr_cinematograficos.py`](file:///F:/Dev/Game/Art/Textures/Modular/procesar_mapas_pbr_cinematograficos.py) | Pipeline de procesamiento y extracción de los 40 mapas PBR cinemáticos (Normal DirectX UE5, ORM, Emissive) a 2048x2048. |
| **Generador Showcases Blender** | [`generar_showcase_oxidados_y_lujo.py`](file:///F:/Dev/Game/Art/Blender/generar_showcase_oxidados_y_lujo.py) | Automatización en Blender 5.2 LTS de los dos showrooms completos (Oxidados y Lujo) con Shader Balls Pro V5, pedestales, placas 3D y props específicos. |
| **Compositor Lámina Oxidados** | [`componer_showcase_oxidados_master.py`](file:///F:/Dev/Game/Art/Textures/Modular/componer_showcase_oxidados_master.py) | Montaje de la infografía maestra 2560x1440 para el pack de texturas oxidadas y percutidas. |
| **Compositor Lámina Lujo** | [`componer_showcase_lujo_master.py`](file:///F:/Dev/Game/Art/Textures/Modular/componer_showcase_lujo_master.py) | Montaje de la infografía maestra 2560x1440 para el pack de mapas de lujo Art Déco Celestia. |
| **Escena Blender Oxidados** | [`Showcase_Texturas_Oxidadas.blend`](file:///F:/Dev/Game/Art/Blender/Showcase_Texturas_Oxidadas.blend) | Archivo 3D editable con el showroom completo de los 5 materiales oxidados y percutidos. |
| **Escena Blender Lujo** | [`Showcase_Texturas_Lujo.blend`](file:///F:/Dev/Game/Art/Blender/Showcase_Texturas_Lujo.blend) | Archivo 3D editable con el showroom completo de los 5 materiales de lujo Art Déco. |
| **Lámina Maestra Oxidados 2.5K** | [`Showcase_Texturas_Oxidadas_Master.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Texturas_Oxidadas_Master.png) | Lámina infográfica 2560x1440 con panorama, 5 close-ups y swatches PBR (BaseColor, Normal, ORM, Emissive) del pack Derelict. |
| **Lámina Maestra Lujo 2.5K** | [`Showcase_Texturas_Lujo_Master.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Texturas_Lujo_Master.png) | Lámina infográfica 2560x1440 con panorama, 5 close-ups y swatches PBR del pack Luxury Celestia. |
| **Panorama Oxidados 2.5K** | [`Showcase_Texturas_Oxidados_Panorama.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Texturas_Oxidados_Panorama.png) | Render panorámico 2560x1440 de las 5 estaciones oxidadas y percutidas. |
| **Panorama Lujo 2.5K** | [`Showcase_Texturas_Lujo_Panorama.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Texturas_Lujo_Panorama.png) | Render panorámico 2560x1440 de las 5 estaciones de lujo Art Déco. |

