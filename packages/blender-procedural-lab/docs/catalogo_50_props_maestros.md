# Catálogo Maestro de 50 Props Interactivos y Ambientales
## Astra Hazard - Rescue Squad

Este documento define la planificación estratégica y técnica de **50 nuevos props interactivos, narrativos y mecánicos** para *Astra Hazard - Rescue Squad*. Los props se estructuran en **10 lotes temáticos de 5 unidades**, cubriendo todas las facetas del bucle de juego: acceso y evacuación, energía, contención de peligros, medicina de emergencia, datos corporativos, vida a bordo, sensores, logística pesada, lujo/contrabando y trampas activas.

---

## 1. Análisis del Ecosistema de Arte y Jugabilidad

### 1.1. Lo que ya se ha construido (Estado Actual)
Hasta la fecha, el proyecto cuenta con:
1. **Kit Modular Arquitectónico (12 bloques):** Suelos, paredes de mamparo, columnas y techos (400x400x350 cm).
2. **Catálogo V6 de Activos Modulares (26 activos):** Contenedores TEU, tuberías en L/T, cubas de ácido, consolas CRT, pasarelas, sofás, boiseries Art Déco, candelabros, reactores Tokamak y racks de baterías.
3. **Dioramas de Misión Ensamblados:**
   - Tier 1: Carguero Químico Derelict.
   - Tier 2: Crucero de Lujo *Celestia*.
   - Tier 3: Refinería Tokamak de Plasma *Black Rock*.
4. **Herramientas de Bombero (Lotes 1, 2 y 3):** Manguera Hydra, Camilla Tándem, Hacha Térmica, Extintor CO2, Desfibrilador, Lanzador de Espuma, Lanza-Redes y Gato Hidráulico 15T.
5. **Entidades y Supervivientes:** Bombero riggeado, Civil con pánico/histeria, Mascota hexápoda Blobby, Lobo Mecánico, Dron Auditor, Trasgo Chatarrero, Araña de Techo y Cinder Spirit.

### 1.2. Lo que falta en el Entorno (Carencias Identificadas)
A pesar de la sólida base modular, los mapas carecen de:
- **Rutas de Navegación Alternativas:** Si un pasillo está bloqueado por fuego o una viga colapsada, los jugadores no tienen conductos de ventilación, escotillas de escape o compuertas hidráulicas para sortear el peligro.
- **Sistemas de Energía Dinámicos:** Falta infraestructura eléctrica interactiva (generadores auxiliares, cajas de fusibles, racks de condensadores) que los jugadores deban reactivar para devolver la energía a puertas selladas o soporte vital.
- **Interacción y Descontaminación de Peligros:** Faltan duchas de descontaminación, incineradores de residuos, válvulas de alivio criogénico y mamparas de plomo.
- **Medicina Táctica In-Situ:** Los supervivientes solo pueden ser evacuados o reanimados; faltan botiquines de pared rompe-fácil, cápsulas de estasis temporales y depuradores de O2.
- **Objetivos de Alto Valor y Lore Corporativo:** Cajas negras blindadas, racks de servidores corporativos encriptados, pianos de cola cyberpunk y alijos de contrabando ocultos bajo baldosas falsas.
- **Peligros Ambientales Cinéticos:** Cables cortados de alta tensión chisporroteantes, aspas de turbinas giratorias y rejillas de suelo trampa que ceden al peso.

### 1.3. Valor que aportan los 50 nuevos props (Gameplay & Sinergia)
- **Profundidad Cooperativa:** Varios props requieren coordinación de dos jugadores (uno acciona una manivela o palanca de derivación mientras el otro rescata o transporta a la víctima).
- **Riesgo vs. Recompensa:** Desbloquear una caja fuerte corporativa o reparar un generador añade tiempo contra el reloj de oxígeno y la deuda de $1,000,000, pero otorga bonificaciones masivas.
- **Narrativa Diegética (Environmental Storytelling):** El entorno muestra la lucha desesperada de la tripulación antes del colapso, convirtiendo los mapas en espacios vivos y creíbles.

---

## 2. Catálogo Maestro de los 50 Props (10 Lotes de 5)

| ID | Nombre del Activo | Lote Temático | Dimensiones (cm) | Materiales / Shaders | Valor de Jugabilidad & Mecánicas |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | `SM_Airlock_Heavy_Hatch` | Lote 1: Acceso & Esclusas | $140 \times 220 \times 35$ | Acero naval, goma, emisor LED | Compuerta de esclusa de doble hoja con volante manual; sella zonas despresurizadas. |
| **02** | `SM_Ventilation_Grating_Duct` | Lote 1: Acceso & Esclusas | $90 \times 90 \times 120$ | Chapa cincada, filtro sucio | Conducto transitable agachado; bypass de pasillos bloqueados y refugio de mascota. |
| **03** | `SM_Hydraulic_Blast_Door` | Lote 1: Acceso & Esclusas | $240 \times 280 \times 40$ | Blindaje compuesto, chevrons | Portón cortafuegos masivo; requiere palanca manual o energía auxiliar para abrir. |
| **04** | `SM_Crawlway_Escape_Portal` | Lote 1: Acceso & Esclusas | $110 \times 110 \times 30$ | Bronce, acero, vidrio blindado | Escotilla circular de evacuación rápida con 4 pestillos sincronizados. |
| **05** | `SM_Cryo_Tube_Maintenance_Hatch` | Lote 1: Acceso & Esclusas | $100 \times 160 \times 25$ | Titanio, tuberías escarchadas | Panel técnico con cerrojos de 1/4 de vuelta; acceso a llaves de paso de refrigerante. |
| **06** | `SM_Backup_Diesel_Generator` | Lote 2: Energía & Red Auxiliar | $180 \times 120 \times 140$ | Fundición de hierro, óxido, combustible | Generador auxiliar; arranque manual por tirador para restaurar luces locales. |
| **07** | `SM_High_Voltage_Breaker_Box` | Lote 2: Energía & Red Auxiliar | $80 \times 130 \times 30$ | Chapa esmaltada gris, chispas | Cuadro eléctrico de mamparo; rearmado de interruptores para desenergizar agua electrificada. |
| **08** | `SM_Portable_Battery_Rack` | Lote 2: Energía & Red Auxiliar | $60 \times 90 \times 40$ | Grafeno, asas de goma, LED ámbar | Celda de energía extraíble; transportable con `ICarriableInterface` para alimentar puertas. |
| **09** | `SM_Industrial_Cable_Reel` | Lote 2: Energía & Red Auxiliar | $70 \times 70 \times 90$ | Bobina de acero, cable caucho naranja | Carrete móvil de cable trifásico; conexión provisional entre generador y maquinaria. |
| **10** | `SM_Emergency_Capacitor_Bank` | Lote 2: Energía & Red Auxiliar | $120 \times 200 \times 60$ | Cobre, aisladores cerámicos | Banco de condensadores; pulso electromagnético voluntario para aturdir robots/drones. |
| **11** | `SM_Decontamination_Shower_Unit` | Lote 3: Contención & Residuos | $120 \times 120 \times 240$ | Acero inoxidable, rociador latón | Ducha de descontaminación; limpia trajes empapados de ácido para frenar daño continuo. |
| **12** | `SM_Hazardous_Waste_Incinerator` | Lote 3: Contención & Residuos | $160 \times 140 \times 210$ | Ladrillo refractario, chapa térmica | Horno de mamparo; incineración de residuos biológicos y muestras contaminadas. |
| **13** | `SM_Pressurized_Coolant_Manifold` | Lote 3: Contención & Residuos | $140 \times 80 \times 60$ | Cobre oxidado, válvulas criogénicas | Manifold distribuidor de nitrógeno; cierre de fuga térmica que sobrecalienta la sala. |
| **14** | `SM_Biohazard_Storage_Vault` | Lote 3: Contención & Residuos | $90 \times 150 \times 70$ | Plomo, sellos magnéticos amarillos | Arcón hermético para guardar muestras orgánicas recolectadas para bonificación de contrato. |
| **15** | `SM_Radiation_Lead_Shield_Screen` | Lote 3: Contención & Residuos | $150 \times 30 \times 200$ | Láminas de plomo, vidrio amarillo | Mampara móvil sobre ruedas para empujar y usar como cobertura contra radiación o fuego. |
| **16** | `SM_Trauma_Kit_Wall_Cabinet` | Lote 4: Medicina & Triage | $50 \times 70 \times 25$ | Esmalte blanco, cruz roja, vidrio | Armario de primeros auxilios; romper cristal para obtener autoinyectores de morfina/O2. |
| **17** | `SM_Stasis_Sleeper_Pod` | Lote 4: Medicina & Triage | $220 \times 90 \times 110$ | Cápsula acrílica, interfaz médica | Pod de hibernación rápida; detiene la hemorragia de un civil hasta que termine la misión. |
| **18** | `SM_Oxygen_Scrubber_Cartridge_Rack` | Lote 4: Medicina & Triage | $110 \times 170 \times 40$ | Zeolita sintética, conectores rápidos | Estante de filtros de aire; recambio para purgar atmósfera viciada de CO2 en la zona. |
| **19** | `SM_Burn_Triage_Gurney` | Lote 4: Medicina & Triage | $200 \times 80 \times 95$ | Tubo cromado, colchón ignífugo | Camilla de hospital móvil; transporte pasivo alternativo para civiles inconscientes. |
| **20** | `SM_Casualty_Identification_Kiosk` | Lote 4: Medicina & Triage | $70 \times 50 \times 165$ | Plástico rugoso, escáner dactilar | Kiosco de telemetría médica; escaneo de pulseras de víctimas para confirmar bajas confirmadas. |
| **21** | `SM_Flight_Data_Recorder_BlackBox` | Lote 5: Cajas Negras & Datos | $45 \times 35 \times 35$ | Titanio naranja alta visibilidad | Baliza de vuelo reforzada; objetivo secundario de rescate de datos de alto valor corporativo. |
| **22** | `SM_Server_Rack_Reinforced` | Lote 5: Cajas Negras & Datos | $80 \times 100 \times 220$ | Gunmetal, leds parpadeantes, HDDs | Rack de base de datos; extracción manual de discos duros antes de que se quemen. |
| **23** | `SM_Captains_Secure_Vault` | Lote 5: Cajas Negras & Datos | $100 \times 80 \times 140$ | Acero forjado, dial de combinación | Caja fuerte blindada de capitanía; contiene lingotes o contratos clasificados. |
| **24** | `SM_Cartographic_Navigation_Table` | Lote 5: Cajas Negras & Datos | $160 \times 120 \times 95$ | Madera barnizada, bronce náutico | Mesa de derrota física; revela el mapa completo de la cubierta tras interactuar. |
| **25** | `SM_SOS_Transponder_Mast` | Lote 5: Cajas Negras & Datos | $60 \times 60 \times 260$ | Antena telescópica, baliza estroboscópica | Mástil de radio de emergencia; desplegable en zonas abiertas para llamar a la lanzadera. |
| **26** | `SM_Crew_Bunk_Double_Fold` | Lote 6: Vida a Bordo & Hábitat | $210 \times 90 \times 180$ | Estructura tubular, lona gris | Literas plegables de camarote; refugio donde pueden esconderse civiles aterrorizados. |
| **27** | `SM_Nutrient_Paste_Dispenser` | Lote 6: Vida a Bordo & Hábitat | $90 \times 60 \times 170$ | Inox industrial, grifo dosificador | Dispensador de comida de emergencia; consumible improvisado para tranquilizar a la mascota. |
| **28** | `SM_Hydroponic_Sprout_Chamber` | Lote 6: Vida a Bordo & Hábitat | $130 \times 70 \times 210$ | Vidrio, luz de cultivo violeta | Vitrina hidropónica; genera pequeñas burbujas de O2 puro si se reactiva su energía. |
| **29** | `SM_Sanitation_Locker_Unit` | Lote 6: Vida a Bordo & Hábitat | $100 \times 80 \times 200$ | Fibra de vidrio, puerta estanca | Módulo sanitario estanco; escondite o trampa para encerrar temporalmente al trasgo. |
| **30** | `SM_Crew_Personal_Locker` | Lote 6: Vida a Bordo & Hábitat | $50 \times 50 \times 190$ | Chapa perforada, candado forzado | Taquilla personal de tripulante; botín aleatorio (pilas, tarjetas de acceso, cintas). |
| **31** | `SM_Holonav_Tactical_Globe` | Lote 7: Navegación & Telecomunicaciones | $120 \times 120 \times 135$ | Latón naval, proyector cian, diales | Globo holográfico de navegación; cálculo de coordenadas y rutas seguras. |
| **32** | `SM_Comms_Array_Console` | Lote 7: Navegación & Telecomunicaciones | $130 \times 75 \times 155$ | Acero naval, CRT fósforo verde, baquelita | Pupitre de radio de mamparo; restablecimiento de enlace de audio del escuadrón. |
| **33** | `SM_Mainframe_Tape_Drive` | Lote 7: Navegación & Telecomunicaciones | $110 \times 80 \times 195$ | Chapa industrial, bobinas abiertas, leds | Computador de cintas vintage; volcado de memoria y logs del incidente. |
| **34** | `SM_Radar_Sweeper_Terminal` | Lote 7: Navegación & Telecomunicaciones | $90 \times 85 \times 140$ | Pedestal orientable, capucha goma, fósforo ámbar | Terminal de sonar pasamuros; revela siluetas hostiles a través de mamparos. |
| **35** | `SM_Auxiliary_Pilot_Chair` | Lote 7: Navegación & Telecomunicaciones | $85 \times 90 \times 145$ | Cuero ignífugo, pistón hidráulico, HOTAS | Butaca de copiloto articulada; puesto de control remoto de compuertas y torretas. |
| **36** | `SM_Heavy_Pallet_Jack` | Lote 8: Almacén & Logística | $160 \times 68 \times 125$ | Acero amarillo hazard, bomba cromada, nylon | Transpaleta hidráulica pesada; empujable para mover cargas y desbloquear pasajes. |
| **37** | `SM_Cargo_Container_Maglock` | Lote 8: Almacén & Logística | $210 \times 280 \times 210$ | Chapa corrugada azul, cantoneras ISO, terminal Maglock | Contenedor intermodal pesado; almacén blindado hackeable con botín de alto nivel. |
| **38** | `SM_Overhead_Crane_Trolley` | Lote 8: Almacén & Logística | $330 \times 95 \times 250$ | Pórtico en I, tambor acanalado, gancho forjado | Polipasto de pórtico industrial; izado de escombros de mamparo y trampas de aplastamiento. |
| **39** | `SM_Barrel_Storage_Rack` | Lote 8: Almacén & Logística | $210 \times 140 \times 215$ | Estructura mecano, balsa colectora, 4 barriles | Rack de tambores químicos; riesgo inflamable reactivo con fuga de gases o combustible. |
| **40** | `SM_Cargo_Scale_Platform` | Lote 8: Almacén & Logística | $190 \times 210 \times 155$ | Chapa estriada, células de carga, visor LED | Báscula de suelo industrial; placa de presión diegética por masa para compuertas. |
| **41** | `SM_Security_Turnstile_Barrier` | Lote 9: Seguridad & Blindaje | $48 \times 135 \times 105$ | Acero inoxidable, trípode tubular, lector NFC | Torniquete biométrico unidireccional; requiere credencial de paso. |
| **42** | `SM_Wall_Mounted_Keycard_Box` | Lote 9: Seguridad & Blindaje | $65 \times 32 \times 92$ | Fundición gris, teclado táctico, escáner dactilar | Terminal mural de acceso seguro; anulación de alarmas y esclusas BSL-4. |
| **43** | `SM_Surveillance_Dome_Turret` | Lote 9: Seguridad & Blindaje | $85 \times 75 \times 110$ | Domo blindado amarillo, doble focal, leds IR | Cúpula de videovigilancia acorazada; sensor de alerta de intrusión para IA enemiga. |
| **44** | `SM_Weapon_Locker_Reinforced` | Lote 9: Seguridad & Blindaje | $125 \times 65 \times 210$ | Acero naval, reja de seguridad, candado macizo | Armero de asalto blindado; depósito de municiones y fusiles tácticos. |
| **45** | `SM_Emergency_Breach_Axe_Box` | Lote 9: Seguridad & Blindaje | $68 \times 24 \times 125$ | Esmalte rojo fuego, cristal rompible, martillo | Vitrina mural de hacha de brecha; obtención in-situ de herramienta de choque. |
| **46** | `SM_Heavy_Duty_Workbench` | Lote 10: Taller & Mecanizado | $190 \times 95 \times 155$ | Chapa 6mm, tornillo de banco, panel perforado | Banco de trabajo con herramientas; crafteo y mantenimiento de instrumental. |
| **47** | `SM_Arc_Welding_Rig_Cart` | Lote 10: Taller & Mecanizado | $75 \times 125 \times 180$ | Chasis rodante, botella argón, inverter, antorcha TIG | Equipo móvil de soldadura; sellado de grietas y mamparos despresurizados. |
| **48** | `SM_Pedestal_Drill_Press` | Lote 10: Taller & Mecanizado | $65 \times 85 \times 220$ | Fundición ranurada, cremallera, mandril cromado | Taladro de columna industrial; perforación de cerraduras agarrotadas. |
| **49** | `SM_Parts_Washer_Station` | Lote 10: Taller & Mecanizado | $125 \times 85 \times 165$ | Cuba desengrase, grifo Loc-Line, tapa cortafuegos | Estación de lavado de piezas; descontaminación de componentes cáusticos. |
| **50** | `SM_Heavy_Hydraulic_Floor_Press` | Lote 10: Taller & Mecanizado | $155 \times 95 \times 245$ | Bastidor H, pistón 50T, manómetro glicerina | Prensa hidráulica de taller; compresión de residuos y enderezado estructural. |

---

## 3. Especificación Técnica de Fabricación: Lote 1 (Props 01-05)

El **Lote 1: Sistemas de Acceso, Compuertas y Conductos de Evacuación** ha sido seleccionado para entrar inmediatamente a producción en Blender 5.2 LTS:

### 3.1. Prop 01: `SM_Airlock_Heavy_Hatch`
- **Morfología:** Marco biselado de mamparo pesado ($140 \times 220 \times 35\,\text{cm}$), dos hojas de acero con junta de estanqueidad de neopreno negro, manivela circular central cromada conectada a 4 pestillos de anclaje de bronce, placa diegética de telemetría de presión y luces gemelas de estado (rojo/verde).
- **Colisión UCX:** Marco hueco perimétrico y placa base (`UCX_SM_Airlock_Heavy_Hatch_01`, `_02`).

### 3.2. Prop 02: `SM_Ventilation_Grating_Duct`
- **Morfología:** Conducto cúbico hueco de chapa plegada ($90 \times 90 \times 120\,\text{cm}$), marco frontal con 8 pernos de cabeza hexagonal, rejilla abatible con 12 lamas inclinadas a $45^\circ$, marcas de arañazos mecánicos en los bordes y filtro interior de aire.
- **Colisión UCX:** Caja de colisión permeable con paso interior para personajes agachados (`UCX_SM_Ventilation_Grating_Duct_01`).

### 3.3. Prop 03: `SM_Hydraulic_Blast_Door`
- **Morfología:** Portón blindado masivo de doble hoja vertical ($240 \times 280 \times 40\,\text{cm}$), refuerzos de placa compuesta en V, franjas diagonales de peligro amarillo/negro desgastadas, 2 pistones hidráulicos superiores telescópicos con mangueras reforzadas y palanca de derivación manual de emergencia protegida por caja acrílica roja.
- **Colisión UCX:** 2 pilares laterales, dintel y hojas (`UCX_SM_Hydraulic_Blast_Door_01`, `_02`).

### 3.4. Prop 04: `SM_Crawlway_Escape_Portal`
- **Morfología:** Marco circular de mamparo ($110 \times 110 \times 30\,\text{cm}$) con brida de 16 pernos, escotilla circular central abisagrada con contrapeso de hierro, 4 cierres radiales de bronce movidos por engranaje central y ojo de buey de vidrio blindado con cruz de alambre de protección.
- **Colisión UCX:** Cilindro hueco y puerta abatible (`UCX_SM_Crawlway_Escape_Portal_01`).

### 3.5. Prop 05: `SM_Cryo_Tube_Maintenance_Hatch`
- **Morfología:** Panel rectangular empotrado ($100 \times 160 \times 25\,\text{cm}$) con cerraduras de un cuarto de vuelta, bisagras externas reforzadas, interior visible con 3 tuberías criogénicas aisladas cubiertas de escarcha blanca, llave de paso esférica de latón y manómetro analógico.
- **Colisión UCX:** Caja plana de mamparo (`UCX_SM_Cryo_Tube_Maintenance_Hatch_01`).

---

## 4. Especificación Técnica de Fabricación: Lote 2 (Props 06-10)

El **Lote 2: Energía, Generadores y Red Eléctrica Auxiliar** cubre la infraestructura de potencia diegética necesaria para reactivar zonas apagadas:

### 4.1. Prop 06: `SM_Backup_Diesel_Generator`
- **Morfología:** Chasis patín de vigas en U ($180 \times 120 \times 140\,\text{cm}$), bloque motor diésel de fundición de hierro con tapa de balancines naranja, radiador frontal masivo con chevrons amarillos y negros, tanque de combustible superior cilíndrico con tapón de latón y tubo visor de diésel, tubo de escape con silenciador, tirador manual de arranque en T y panel de control con tacómetro analógico, manómetro de aceite y LEDs gemelos.
- **Colisión UCX:** Patín base, bloque motor y radiador (`UCX_SM_Backup_Diesel_Generator_01`, `_02`).

### 4.2. Prop 07: `SM_High_Voltage_Breaker_Box`
- **Morfología:** Gabinete hueco de mamparo esmaltado gris oscuro ($80 \times 130 \times 30\,\text{cm}$), puerta batiente abierta a $75^\circ$ hacia la izquierda con rótulo de peligro de 480V, placa interior de baquelita con 3 disyuntores de cuchilla de cobre puro con mangos aislantes rojos/naranjas, aisladores cerámicos acanalados, voltímetro analógico de aguja y pasamuros de conductos de potencia.
- **Colisión UCX:** Caja de mamparo (`UCX_SM_High_Voltage_Breaker_Box_01`).

### 4.3. Prop 08: `SM_Portable_Battery_Rack`
- **Morfología:** Jaula estructural de aleación ligera naranja ($90 \times 55 \times 38\,\text{cm}$) con dos asas ergonómicas reforzadas de goma para transporte bipersonal o individual (`ICarriableInterface`), 4 celdas cilíndricas de grafeno con barras luminosas LED de carga (plasma cian), display frontal digital de telemetría y conector de acople rápido macho trifásico.
- **Colisión UCX:** Caja de colisión transportable (`UCX_SM_Portable_Battery_Rack_01`).

### 4.4. Prop 09: `SM_Industrial_Cable_Reel`
- **Morfología:** Carro tubular móvil de acero naranja ($70 \times 70 \times 90\,\text{cm}$) con ruedas de goma maciza y asa de arrastre, tambor central con bridas circulares de acero, mazo de cable trifásico enrollado de caucho naranja de alta resistencia, manivela lateral de rebobinado con mango giratorio y extremo de cable desenrollado en el piso con clavija industrial amarilla de bloqueo por giro.
- **Colisión UCX:** Carro base y tambor cilíndrico (`UCX_SM_Industrial_Cable_Reel_01`).

### 4.5. Prop 10: `SM_Emergency_Capacitor_Bank`
- **Morfología:** Bastidor abierto de 4 columnas de acero ($120 \times 60 \times 205\,\text{cm}$), 6 condensadores cilíndricos de aluminio pulido dispuestos en 2 niveles con aisladores cerámicos y bornes de latón, busbars masivas horizontales de cobre puro, brecha de chispa (Spark Gap) central con plasma cian vivo para pulsos EMP de aturdimiento robótico, palanca lateral masiva de descarga de emergencia (Dump Switch) roja y baliza de alarma ámbar superior.
- **Colisión UCX:** Bastidor de 4 postes y travesaños (`UCX_SM_Emergency_Capacitor_Bank_01`).

---

## 5. Especificación Técnica de Fabricación: Lote 3 (Props 11-15)

El **Lote 3: Contención de Peligros, Mitigación y Residuos** cubre elementos de bioseguridad, radiación, criogenia y descontaminación activa:

### 5.1. Prop 11: `SM_Decontamination_Shower_Unit`
- **Morfología:** Cabina de descontaminación de perfil cuadrado ($120 \times 120 \times 240\,\text{cm}$) con bandeja base colectora de acero antideslizante con rejilla de sumidero central, arco estructural tubular de acero inoxidable con 4 boquillas de pulverización de latón, rociador cónico superior masivo con tirador triangular de cadena y estación secundaria de lavaojos con doble chorro y palanca de empuje amarilla.
- **Colisión UCX:** Plato base y postes perimétricos permeables (`UCX_SM_Decontamination_Shower_Unit_01`).

### 5.2. Prop 12: `SM_Hazardous_Waste_Incinerator`
- **Morfología:** Horno cúbico pesado de hierro fundido refractario ($160 \times 140 \times 210\,\text{cm}$) con aletas térmicas de disipación perimétricas, compuerta vertical blindada deslizante con visor central perforado de cuarzo refractario que revela fuego activo interior a 1200°C (emisión naranja ardiente), palanca lateral de elevación con contrapeso, termómetro analógico de aguja y chimenea superior con válvula de alivio.
- **Colisión UCX:** Cuerpo principal del horno y chimenea (`UCX_SM_Hazardous_Waste_Incinerator_01`, `_02`).

### 5.3. Prop 13: `SM_Pressurized_Coolant_Manifold`
- **Morfología:** Manifold distribuidor de refrigerante criogénico ($140 \times 80 \times 60\,\text{cm}$) con colector horizontal maestro de cobre con bridas empernadas en los extremos, 3 ramales verticales con manguitos aislantes cubiertos de escarcha criogénica y volantes cian de cuatro radios, manómetro analógico superior de doble escala y dos placas traseras de montaje a mamparo.
- **Colisión UCX:** Colector cilíndrico maestro (`UCX_SM_Pressurized_Coolant_Manifold_01`).

### 5.4. Prop 14: `SM_Biohazard_Storage_Vault`
- **Morfología:** Arcón blindado hermético de plomo ($135 \times 75 \times 65\,\text{cm}$) apoyado en zócalo reforzado, tapa superior de cierre perimétrico con dos cierres mecánicos de tracción magnética pintados en amarillo preventivo, placa central con símbolo internacional de peligro biológico en relieve, display frontal de integridad de vacío con barra luminosa verde y asas tubulares de arrastre lateral.
- **Colisión UCX:** Arcón cúbico estanco (`UCX_SM_Biohazard_Storage_Vault_01`).

### 5.5. Prop 15: `SM_Radiation_Lead_Shield_Screen`
- **Morfología:** Mampara móvil de blindaje radiológico ($150 \times 30 \times 200\,\text{cm}$) compuesta por chasis de perfil en U de acero naval, panel central de plomo de 20 mm con chevrons amarillos y negros, ventana superior de observación en vidrio plomado de alta densidad tintado en amarillo transparente, barra tubular trasera de empuje ergonómico y cuatro ruedas industriales de poliuretano de alta carga con frenos.
- **Colisión UCX:** Panel vertical y patas estabilizadoras (`UCX_SM_Radiation_Lead_Shield_Screen_01`).

---

## 6. Especificación Técnica de Fabricación: Lote 4 (Props 16-20)

El **Lote 4: Medicina, Triage y Soporte Vital** integra los activos de intervención clínica in-situ y estabilización de bajas:

### 6.1. Prop 16: `SM_Trauma_Kit_Wall_Cabinet`
- **Morfología:** Armario de primeros auxilios de mamparo ($50 \times 25 \times 70\,\text{cm}$) con chapa de esmalte blanco hospitalario gastado, panel frontal de vidrio protector rompible con cruz de emergencia médica emisiva, martillo percutor rojo colgado en el lateral mediante cadena metálica diegética, estantes interiores visibles con 3 autoinyectores de epinefrina/morfina, paquete de gasas hemostáticas y frasco de antiséptico.
- **Colisión UCX:** Caja prismática de mamparo (`UCX_SM_Trauma_Kit_Wall_Cabinet_01`).
- **Mecánica UE5:** `IInteractableInterface` para romper vidrio o abrir; dispensa consumibles que restablecen salud o reducen consumo de oxígeno.

### 6.2. Prop 17: `SM_Stasis_Sleeper_Pod`
- **Morfología:** Cápsula médica de estasis criogénica ($220 \times 90 \times 110\,\text{cm}$) con chasis ergonómico curvado de titanio gris grafito, cúpula cilíndrica de vidrio acrílico transparente con fluido azul/cian emisivo con partículas de congelación, monitor lateral de signos vitales con electrocardiograma verde interactivo, mangueras corrugadas flexibles de retorno de refrigerante y cabezal acolchado con mascarilla de soporte vital.
- **Colisión UCX:** Base pod y cúpula (`UCX_SM_Stasis_Sleeper_Pod_01`, `_02`).
- **Mecánica UE5:** Aloja a un superviviente crítico inconsciente; congela el sangrado y el temporizador de muerte hasta el final de la partida.

### 6.3. Prop 18: `SM_Oxygen_Scrubber_Cartridge_Rack`
- **Morfología:** Depurador atmosférico de mamparo ($110 \times 40 \times 170\,\text{cm}$) con bastidor de acero blanco médico, 4 compartimentos para cartuchos de zeolita cilíndricos horizontales con mangos amarillos y conectores rápidos, conducto colector inferior con turbina centrífuga de succión de aire viciado, panel indicador con LEDs de saturación de CO2 (verde/naranja/rojo) y manómetro de presión de cabina.
- **Colisión UCX:** Bastidor prismático vertical (`UCX_SM_Oxygen_Scrubber_Cartridge_Rack_01`).
- **Mecánica UE5:** Los jugadores pueden sustituir un cartucho saturado con uno nuevo de la nave para purificar el aire de una sala tóxica.

### 6.4. Prop 19: `SM_Burn_Triage_Gurney`
- **Morfología:** Camilla móvil de tratamiento intensivo de quemados ($200 \times 80 \times 95\,\text{cm}$) con chasis tubular de acero inoxidable soldado, 4 ruedas orientables de goma con pedales de freno, colchoneta clínica segmentada de vinilo antibacteriano cian/azul petróleo, dos correas de sujeción rápida de nylon naranja con hebillas metálicas, mástil telescópico con bolsa de suero IV y gotero translúcido, y monitor portátil de constantes vitales fijado en la barandilla de pies.
- **Colisión UCX:** Chasis tubular inferior y cama (`UCX_SM_Burn_Triage_Gurney_01`).
- **Mecánica UE5:** Vehículo de empuje monoplaza (`ICarriableInterface` / `IInteractableInterface`) para evacuar supervivientes inconscientes al doble de velocidad que a hombros.

### 6.5. Prop 20: `SM_Casualty_Identification_Kiosk`
- **Morfología:** Terminal vertical de triaje y registro de bajas ($70 \times 50 \times 165\,\text{cm}$) de carcasa aerodinámica de polímero técnico blanco y grafito, pantalla interactiva superior en ángulo de 30° con GUI diegética holográfica de telemetría de personal, ranura con escáner óptico cian de pulseras de identificación RFID, dispensador diegético de precintos de triaje con ticket saliente y baliza cilíndrica tricolor superior de triaje de gravedad (Rojo = Inmediato, Amarillo = Demorado, Verde = Menor).
- **Colisión UCX:** Columna y consola (`UCX_SM_Casualty_Identification_Kiosk_01`).
- **Mecánica UE5:** Al interactuar con la pulsera biométrica de un civil o cadáver, confirma la baja ante el sistema corporativo, liquidando la recompensa económica de rescate de inmediato.

---

## 7. Especificación Técnica de Fabricación: Lote 5 (Props 21-25)

El **Lote 5: Cajas Negras, Servidores y Datos Corporativos** define los objetivos de extracción de inteligencia clasificada, valor económico corporativo y cartografía táctica:

### 7.1. Prop 21: `SM_Flight_Data_Recorder_BlackBox`
- **Morfología:** Registrador de datos de vuelo blindado ($45 \times 35 \times 35\,\text{cm}$) de chapa de titanio esmaltada en naranja internacional de rescate fluorescente con franjas reflectantes blancas, leyenda diegética "FLIGHT RECORDER // DO NOT OPEN", baliza acústica cilíndrica acoplada en el lateral con LED estroboscópico de pulso blanco/ámbar, asa superior ergonómica abatible de transporte y conector de interfaz multipin blindado con tapa de rosca de latón.
- **Colisión UCX:** Caja prismática compacta (`UCX_SM_Flight_Data_Recorder_BlackBox_01`).
- **Mecánica UE5:** Ítem transportable a una o dos manos (`ICarriableInterface`); evacuarlo en la lanzadera otorga un bono directo de $50,000 en el subsistema de deuda (`UAstraEconomySubsystem`).

### 7.2. Prop 22: `SM_Server_Rack_Reinforced`
- **Morfología:** Bastidor vertical blindado de mamparo ($80 \times 100 \times 220\,\text{cm}$) en acero gunmetal oscuro y titanio con rejilla perforada hexagonal en la puerta frontal, 6 bahías con bandejas modulares para discos duros óptico-magnéticos (con una bandeja superior parcialmente extraída hacia afuera revelando el asa de extracción y matriz de conectores dorados), matriz de LEDs parpadeantes de actividad de datos verde y ámbar, mazo trasero de cableado de fibra óptica y zócalo inferior con turbina de refrigeración.
- **Colisión UCX:** Bastidor prismático vertical (`UCX_SM_Server_Rack_Reinforced_01`).
- **Mecánica UE5:** `IInteractableInterface` para extracción de datos o discos duros; si se incendia la sala, la integridad del servidor decae hasta destruir la información clasificada.

### 7.3. Prop 23: `SM_Captains_Secure_Vault`
- **Morfología:** Caja fuerte acorazada de capitanía ($100 \times 80 \times 140\,\text{cm}$) en aleación naval pesada con bisagras externas cilíndricas reforzadas de 80 mm, volante o dial analógico circular de combinación de latón pulido con escala numérica grabada, palanca de cerrojo de tres bulones cilíndricos cromados salientes, panel numérico electrónico de respaldo con display ámbar y marcas de impacto/soplete térmico en una de las esquinas.
- **Colisión UCX:** Arcón cúbico de alta resistencia (`UCX_SM_Captains_Secure_Vault_01`).
- **Mecánica UE5:** `IInteractableInterface` para descifrado de combinación mediante claves ocultas en PDA o forzado mecánico mediante el hacha térmica (`ABaseEquipment`); contiene lingotes de platino o contratos clasificados.

### 7.4. Prop 24: `SM_Cartographic_Navigation_Table`
- **Morfología:** Mesa de puente de navegación táctica ($160 \times 120 \times 95\,\text{cm}$) con base cónica pesada de bronce náutico y molduras de madera barnizada oscura, superficie de vidrio blindado negro antracita con proyector volumétrico central activo que emite un mapa holográfico 3D en plasma cian y dorado de la nave en emergencia, 4 pantallas táctiles perimétricas de cuadrante con telemetría de mamparos y barandilla perimétrica con apoyamanos engomado.
- **Colisión UCX:** Mesa prismática con pedestal (`UCX_SM_Cartographic_Navigation_Table_01`).
- **Mecánica UE5:** Al interactuar con la mesa, se actualiza el minimapa y la interfaz HUD del escuadrón, revelando las rutas de escape más directas y la ubicación de las esclusas no comprometidas.

### 7.5. Prop 25: `SM_SOS_Transponder_Mast`
- **Morfología:** Mástil de baliza de socorro SOS ($60 \times 60 \times 260\,\text{cm}$) con trípode inferior de soporte articulado con zapatas magnéticas de anclaje, mástil telescópico escalonado de aluminio aeronáutico y titanio, plato de antena parabólica superior orientable a $45^\circ$ con iluminador cian de pulso, baliza estroboscópica de xenón superior con cúpula de vidrio ámbar de alta visibilidad y módulo generador térmico RTG inferior con aletas de refrigeración y símbolo de advertencia radiactiva.
- **Colisión UCX:** Base trípode y columna vertical (`UCX_SM_SOS_Transponder_Mast_01`).
- **Mecánica UE5:** Desplegable o activable en cubiertas abiertas o pasillos con brecha; extiende el alcance del enlace de radio con la lanzadera (`AAstraSignalRepeaterActor`) y desbloquea la orden de rescate a distancia.

---

## 8. Especificación Técnica de Fabricación: Lote 6 (Props 26-30)

El **Lote 6: Vida a Bordo, Camarotes & Hábitat** integra los activos de alojamiento de la tripulación, racionamiento de emergencia, botánica regenerativa y privacidad en gravedad cero:

### 8.1. Prop 26: `SM_Crew_Bunk_Double_Fold`
- **Morfología:** Conjunto de literas dobles tubulares de mamparo ($210 \times 95 \times 190\,\text{cm}$) con estructura de acero antracita soldada a zapatas cuadradas de anclaje de 4 pernos, largueros de refuerzo perimétrico, dos colchonetas ergonómicas acolchadas de espuma de alta densidad con funda de lona ignífuga verde oliva (`Thermal_Canvas_Olive`) y almohada anatómica integrada, dos cinchas elásticas cruzadas de retención para gravedad cero con hebillas metálicas de liberación rápida, barandilla de seguridad tubular anticaída en la litera superior, escalera tubular vertical en el lateral derecho de 4 peldaños estriados antideslizantes, dos lámparas de lectura individuales diegéticas empotradas con reflectores LED ámbar cálidos y taquilla/cajón inferior deslizable con tirador cromado y pestillo de latón.
- **Colisión UCX:** Compuesto OBB por postes y bastidores (`UCX_SM_Crew_Bunk_Double_Fold_01`, `_02`).
- **Mecánica UE5:** Punto de cobertura táctica agachado (`ICoverInterface`); funciona como escondite diegético para civiles en estado de pánico extremo (`ASurvivorCharacter`), requiriendo interacción para calmarlos e iniciar la escolta.

### 8.2. Prop 27: `SM_Nutrient_Paste_Dispenser`
- **Morfología:** Estación dispensadora industrial de pasta nutritiva ($92 \times 68 \times 185\,\text{cm}$) en esmalte blanco de electrodoméstico pesado (`Offwhite_Appliance`) con zócalo y cantoneras de gunmetal oscuro, tolva superior cilíndrica de policarbonato acrílico translúcido claro (`Clear_Acrylic_Hopper`) que contiene pasta hipercalórica semisólida naranja brillante (`Nutrient_Paste_Orange`, con ligero brillo emisivo) y conducto superior de recarga desde el techo, manómetro analógico superior de presión de impulsión con aguja roja percutida, terminal de pantalla CRT verde fósforo (`Screen_Phosphor_Green`) que muestra la matriz de raciones y calorías junto a 3 botones de selección de sabor, nicho frontal abierto con boquilla dosificadora de latón/cromo, bloque de gel dosificado fresco sobre bandeja de rejilla de goteo perforada de acero inoxidable, palanca manual lateral derecha de accionamiento con pomo esférico ergonómico rojo (`Emergency_Red`) y mazo lateral izquierdo de tubos corrugados y filtro de carbón activo.
- **Colisión UCX:** Caja prismática vertical (`UCX_SM_Nutrient_Paste_Dispenser_01`).
- **Mecánica UE5:** `IInteractableInterface` para dosificación de pasta; entrega un consumible alimenticio que restaura stamina al bombero, o que puede ser arrojado al suelo para sobornar y distraer a la entidad Scrapper Goblin o pacificar temporalmente a la mascota hexápoda Blobby.

### 8.3. Prop 28: `SM_Hydroponic_Sprout_Chamber`
- **Morfología:** Vitrina botánica vertical estanca de regeneración de O2 ($130 \times 72 \times 215\,\text{cm}$) con perfilería de aluminio blanco perlado y zócalo reforzado de titanio oscuro, cavidad interior completamente abierta y despejada con 3 bandejas horizontales de cultivo hidropónico escalonadas que contienen sustrato poroso de perlita y densas hileras de brotes verdes vivos bioluminiscentes (`Hydroponic_Plant_Green`), reflectores lineales en el techo de cada nivel con barras de LEDs hortícolas UV magenta/violeta resplandecientes (`Grow_LED_VioletMagenta`, Emissive Strength 9.5), puerta frontal abatible acristalada montada sobre robustas bisagras de mamparo abiertas a $45^\circ$ hacia afuera con marco de titanio oscuro, panel acristalado ultra-transparente (`Chamber_Glass_Clear`) y maneta hermética de compresión de latón, sistema lateral de tuberías de subida de solución de nutrientes con abrazaderas doradas, bomba de recirculación en la base, panel digital derecho con telemetría de fotosíntesis (pH 6.2 / O2 +14%) y difusor superior circular de oxígeno con corona de LEDs verdes.
- **Colisión UCX:** Caja prismática vertical con puerta (`UCX_SM_Hydroponic_Sprout_Chamber_01`, `_02`).
- **Mecánica UE5:** `IInteractableInterface` vinculado al sistema eléctrico (`UAstraPowerGridSubsystem`); cuando los jugadores reenergizan la sala o activan la cámara, el sistema comienza a purgar O2 enriquecido, generando una burbuja esférica diegética donde el consumo de oxígeno del traje espacial se reduce a cero.

### 8.4. Prop 29: `SM_Sanitation_Locker_Unit`
- **Morfología:** Módulo sanitario de descontaminación de mamparo monobloque ($112 \times 92 \times 205\,\text{cm}$) acabado en resina epoxi naval azul marino (`Sanitation_Navy_Blue`) con cantoneras de acero oscuro, cavidad interior higiénica de paredes blancas pulidas iluminada con un foco UV germicida azul cian central tenue (`Sanitation_LED_Status`), techo interior con cabezal de ducha sónica cromado con 8 micro-boquillas circulares de aspersión de alta frecuencia, suelo con rejilla de drenaje circular perforada con orificio central de succión en gravedad cero, barra pasamanos ergonómica tubular curva en la pared izquierda y dispensador de líquido higiénico con dosificador de latón, puerta de escotilla ovalada presurizada montada sobre bisagras industriales abiertas a $65^\circ$ hacia afuera a la izquierda para máxima visibilidad simultánea de la cara interior y exterior, ventana circular de ojo de buey con aro de pernos cromado y vidrio laminado, volante circular cromado de cerrojo de tres bulones cilíndricos, y consola lateral exterior con panel de estado y tres balizas luminosas (Verde = Desinfectado, Ámbar = Ciclo activo, Rojo = Peligro biológico).
- **Colisión UCX:** Caja perimétrica con puerta batiente (`UCX_SM_Sanitation_Locker_Unit_01`, `_02`).
- **Mecánica UE5:** `IInteractableInterface` de acceso; sirve como refugio estanco temporal contra nubes químicas cáusticas o explosiones de vacío, o como trampa cinética cooperativa para encerrar y bloquear a una entidad enemiga en su interior mediante el volante exterior.

### 8.5. Prop 30: `SM_Crew_Personal_Locker`
- **Morfología:** Taquilla personal vertical de mamparo ($58 \times 54 \times 196\,\text{cm}$) fabricada en chapa de acero doblada esmaltada en gris industrial (`Locker_Steel_Grey`) con zócalo reforzado, cavidad interior completamente abierta y dividida en tres baldas horizontales, estante superior con termo cilíndrico de titanio para café con tapón rojo brillante (`Emergency_Red`) y tarjeta magnética de identificación de tripulante con foto, estante intermedio con linterna táctica imantada al mamparo con haz de luz ámbar encendido y maletín de herramientas naranja de alto impacto, compartimento secreto en la base con trampilla de falso fondo metálica levantada que revela un alijo de 2 lingotes/chips de datos dorados emisivos de alto valor (`Gold_Chip_Glow`), puerta frontal de mamparo con ranuras de ventilación troqueladas abierta a $60^\circ$ hacia la izquierda sobre bisagras exteriores de pasador, aldaba de seguridad rota con corte térmico y candado forzado colgando de un eslabón suelto (`Machinery_Brass`).
- **Colisión UCX:** Columna vertical prismática (`UCX_SM_Crew_Personal_Locker_01`).
- **Mecánica UE5:** `IInteractableInterface` de saqueo; recompensa al jugador con créditos corporativos para mitigar la deuda del escuadrón ($10,000 - $25,000), baterías de repuesto o tarjetas de acceso maestras para atajos en la nave.

---

## 9. Especificación Técnica de Fabricación: Lote 7 (Props 31-35)

El **Lote 7: Navegación, Telecomunicaciones & Control Táctico** define la infraestructura de puente de mando, cartografía estelar, comunicaciones por radio y puestos de pilotaje:

### 9.1. Prop 31: `SM_Holonav_Tactical_Globe`
- **Morfología:** Pedestal octogonal de navegación ($120 \times 120 \times 135\,\text{cm}$) con zócalo biselado de acero naval, tres anillos armilares concéntricos de latón pulido articulados en cardán y esfera holográfica central volumétrica con meridianos cian resplandecientes (`emissive_strength=2.6`), rejilla proctora de coordenadas espaciales y conmutadores de alineación.
- **Colisión UCX:** Base octogonal con prisma de exclusión (`UCX_SM_Holonav_Tactical_Globe_01`).
- **Mecánica UE5:** `IInteractableInterface` para recalcular trayectorias de salto o triangular la posición de supervivientes atrapados en la nave.

### 9.2. Prop 32: `SM_Comms_Array_Console`
- **Morfología:** Pupitre de radio de mamparo ($130 \times 75 \times 155\,\text{cm}$) en esmalte gris naval, pantalla CRT de osciloscopio con barrido sinusoidal en fósforo verde, antena dipolo articulada, diales analógicos de sintonía en baquelita, auricular telefónico blindado colgado en horquilla y banco de fusibles de conmutación de frecuencias.
- **Colisión UCX:** Escritorio angular con soporte mural (`UCX_SM_Comms_Array_Console_01`).
- **Mecánica UE5:** `IInteractableInterface` para restaurar el canal de audio del escuadrón con la nave nodriza Vanguard ante tormentas de plasma.

### 9.3. Prop 33: `SM_Mainframe_Tape_Drive`
- **Morfología:** Armario de computación mainframe vintage ($110 \times 80 \times 195\,\text{cm}$) con doble carrete abierto de cinta magnética giratoria de 12 pulgadas, cabezal de lectura cromado con columnas de vacío de amortiguación, panel inferior con 16 lámparas de estado multicolores y conmutadores de palanca de arranque.
- **Colisión UCX:** Prisma vertical de suelo (`UCX_SM_Mainframe_Tape_Drive_01`).
- **Mecánica UE5:** `IInteractableInterface` para volcado de memoria del núcleo de la estación; preserva el registro de eventos previos al accidente.

### 9.4. Prop 34: `SM_Radar_Sweeper_Terminal`
- **Morfología:** Terminal de radar sonar de barrido ($90 \times 85 \times 140\,\text{cm}$) montado sobre pedestal cilíndrico angulado a $30^\circ$, pantalla circular de fósforo ámbar protegida por una capucha cónica de goma negra antideslumbrante para observación ocular, diales perimétricos y selector de ganancia.
- **Colisión UCX:** Pedestal y campana de visor (`UCX_SM_Radar_Sweeper_Terminal_01`).
- **Mecánica UE5:** Interacción para barrido activo de sonar que revela entidades biomecánicas hostiles a través de paredes y mamparos cerrados.

### 9.5. Prop 35: `SM_Auxiliary_Pilot_Chair`
- **Morfología:** Butaca de copiloto articulada para gravedad cero ($85 \times 90 \times 145\,\text{cm}$) con base hidráulica pesada de acero oscuro, acolchado ergonómico en cuero técnico ignífugo con costuras reforzadas, arnés de cuatro puntos con hebilla central, reposabrazos con mini-joysticks de pilotaje integrados y apoyacabezas regulable.
- **Colisión UCX:** Asiento con peana rotatoria (`UCX_SM_Auxiliary_Pilot_Chair_01`).
- **Mecánica UE5:** Puesto de interacción que permite controlar manualmente torretas defensivas o compuertas de atraque desde cabina.

---

## 10. Especificación Técnica de Fabricación: Lote 8 (Props 36-40)

El **Lote 8: Almacén, Logística & Carga Pesada** dota a las bodegas de carga de equipos funcionales para el transporte, estiba y pesaje de contenedores e insumos:

### 10.1. Prop 36: `SM_Heavy_Pallet_Jack`
- **Morfología:** Transpaleta hidráulica pesada ($160 \times 68 \times 125\,\text{cm}$) en amarillo hazard industrial con horquillas de acero de 1.6 m, ruedas tándem de poliuretano, respaldo metálico de retención de carga (load backrest guard), carcasa frontal en A que aloja el pistón cromado de elevación y timón de dirección ergonómico cerrado en bucle D con palanca de 3 posiciones.
- **Colisión UCX:** Horquillas, chasis y timón articulado (`UCX_SM_Heavy_Pallet_Jack_01`, `_02`).
- **Mecánica UE5:** Actor empujable con física de transporte (`ICarriableInterface` / `IInteractableInterface`) para mover palets con supervivientes o barricadas de carga.

### 10.2. Prop 37: `SM_Cargo_Container_Maglock`
- **Morfología:** Contenedor intermodal pesado ($210 \times 280 \times 210\,\text{cm}$) de chapa corrugada azul ultramar con 11 nervaduras verticales por flanco, 8 cantoneras ISO de fundición con ranuras para grúa, túneles inferiores para horquillas de montacargas, puertas dobles con 4 barras de cierre galvanizadas y terminal magnético Maglock con display ámbar.
- **Colisión UCX:** Caja hueca envolvente con apertura de puertas (`UCX_SM_Cargo_Container_Maglock_01`).
- **Mecánica UE5:** Almacén blindado que puede ser abierto ingresando códigos o hackeando el teclado numérico; contiene equipamiento táctico de nivel 3.

### 10.3. Prop 38: `SM_Overhead_Crane_Trolley`
- **Morfología:** Polipasto de pórtico industrial ($330 \times 95 \times 250\,\text{cm}$) con columnas laterales en A y viga carril I, carro móvil motorizado con 4 ruedas de pestaña de latón, motorreductor con ventilador, tambor de cable ranurado, cables de acero gemelos, bloque de polea con gancho forjado con pestillo y botonera colgante con cable espiral y seta de emergencia.
- **Colisión UCX:** Pórtico completo, viga y bloque de gancho (`UCX_SM_Overhead_Crane_Trolley_01`).
- **Mecánica UE5:** `IInteractableInterface` para izar escombros pesados de mamparos o activar la grúa para aplastar entidades monstruosas en la bodega.

### 10.4. Prop 39: `SM_Barrel_Storage_Rack`
- **Morfología:** Estantería tubular mecano ($210 \times 140 \times 215\,\text{cm}$) en 2 niveles con cruces de San Andrés de rigidización trasera, balsa inferior colectora de derrames con grifo de purga de latón y rejilla amarilla, 4 barriles de 200L horizontales (2 verdes químicos y 2 amarillos hazard) con tapones de boca y grifos dosificadores.
- **Colisión UCX:** Armazón mecano y barriles estibados (`UCX_SM_Barrel_Storage_Rack_01`).
- **Mecánica UE5:** Peligro reactivo con fluidos inflamables; disparos o altas temperaturas provocan fugas y deflagraciones térmicas en cadena.

### 10.5. Prop 40: `SM_Cargo_Scale_Platform`
- **Morfología:** Báscula de suelo industrial de perfil bajo ($190 \times 210 \times 155\,\text{cm}$) con plataforma de chapa estriada antideslizante, rampas biseladas de acceso delantera y trasera, células de carga de latón en las 4 esquinas, cajón blindado de prueba asegurado con cincha naranja, canaleta de cableado y columna vertical con cabezal de pesaje y pantalla LED roja brillante.
- **Colisión UCX:** Plataforma de suelo y columna indicadora (`UCX_SM_Cargo_Scale_Platform_01`).
- **Mecánica UE5:** Interruptor de presión diegético por peso; detecta la carga transportada o puede requerir un peso específico para desbloquear compuertas automatizadas.

---

## 11. Especificación Técnica de Fabricación: Lote 9 (Props 41-45)

El **Lote 9: Seguridad, Blindaje & Contención** establece los sistemas de control de acceso perimetral, videovigilancia y almacenamiento de armamento y herramientas críticas de brecha:

### 11.1. Prop 41: `SM_Security_Turnstile_Barrier`
- **Morfología:** Torniquete de paso biométrico ($48 \times 135 \times 105\,\text{cm}$) en acero inoxidable cepillado con bordes achaflanados, rotor central inclinado a $45^\circ$ con trípode de 3 brazos tubulares cromados con topes de goma, visor superior con lector NFC cian y matriz de flecha LED verde de paso autorizado, y barandilla lateral de guiado peatonal.
- **Colisión UCX:** Mueble vertical y barrera trípode (`UCX_SM_Security_Turnstile_Barrier_01`).
- **Mecánica UE5:** Barrera física de una sola dirección; requiere tarjeta de identificación corporativa para liberar el rotor de giro.

### 11.2. Prop 42: `SM_Wall_Mounted_Keycard_Box`
- **Morfología:** Terminal mural de acceso seguro ($65 \times 32 \times 92\,\text{cm}$) montado en placa de pared reforzada, carcasa de fundición con visera protectora superior contra impactos, pernos de anclaje de latón, teclado numérico de goma negra con teclas metálicas, escáner óptico de huella dactilar con prisma verde resplandeciente, ranura de tarjeta iluminada en cian y baliza de estado roja superior.
- **Colisión UCX:** Caja mural compacta (`UCX_SM_Wall_Mounted_Keycard_Box_01`).
- **Mecánica UE5:** Mecánica de hackeo o autorización para anular alarmas y abrir esclusas de cuarentena en niveles BSL-4.

### 11.3. Prop 43: `SM_Surveillance_Dome_Turret`
- **Morfología:** Torreta esférica de videovigilancia acorazada ($85 \times 75 \times 110\,\text{cm}$) anclada a una viga I de techo mediante brida pesada y brazo en cuello de cisne, carcasa de cúpula en amarillo hazard con ceja protectora de acero oscuro, domo de cristal oscurecido con lentes ópticas motorizadas duales, corona de 8 LEDs infrarrojos, baliza estroboscópica roja de grabación y jaula de varillas anticaída.
- **Colisión UCX:** Base superior y esfera suspendida (`UCX_SM_Surveillance_Dome_Turret_01`).
- **Mecánica UE5:** Sensor de IA que detecta al escuadrón o a los monstruos biomecánicos, activando torretas de defensa o sirenas de sector.

### 11.4. Prop 44: `SM_Weapon_Locker_Reinforced`
- **Morfología:** Armero blindado de asalto ($125 \times 65 \times 210\,\text{cm}$) de chapa naval de 10 mm con interior hueco visible, estante superior con tres cajas de munición militares verde oliva, cremallera inferior con 4 fusiles tácticos en cunas de goma, puerta izquierda cerrada con barrotes de acero y puerta derecha abierta a $65^\circ$ revelando el interior, con aldaba y candado macizo de latón.
- **Colisión UCX:** Armario perimétrico y puerta batiente abierta (`UCX_SM_Weapon_Locker_Reinforced_01`, `_02`).
- **Mecánica UE5:** Alijo de reabastecimiento de munición y armas pesadas para el escuadrón tras abrir el candado con cizalla o llave maestra.

### 11.5. Prop 45: `SM_Emergency_Breach_Axe_Box`
- **Morfología:** Vitrina mural de emergencias ($68 \times 24 \times 125\,\text{cm}$) en esmalte rojo fuego con interior hueco visible, puerta con marco amarillo hazard abierta a $35^\circ$ con panel de cristal templado serigrafiado, hacha táctica pesada contra incendios y brechas montada en el interior sobre clips de latón con mango rojo y filo cromado, y martillo percutor exterior colgado de una cadena de eslabones de acero.
- **Colisión UCX:** Vitrina mural y hacha interior (`UCX_SM_Emergency_Breach_Axe_Box_01`).
- **Mecánica UE5:** Permite a los jugadores romper el cristal o abrir la vitrina para equipar el hacha de choque (`AThermalAxeEquipment`) ante pérdidas de herramientas.

---

## 12. Especificación Técnica de Fabricación: Lote 10 (Props 46-50)

El **Lote 10: Taller, Mecanizado & Reparaciones Pesadas** cierra el catálogo de 50 props proporcionando el equipamiento de mecanizado y ajuste necesario para mantener operativa la nave:

### 12.1. Prop 46: `SM_Heavy_Duty_Workbench`
- **Morfología:** Banco de trabajo de taller industrial ($190 \times 95 \times 155\,\text{cm}$) con patas de tubo cuadrado y regatones de latón, encimera de chapa de acero de 6 mm con reborde perimetral en amarillo hazard, cajonera lateral de dos gavetas con tiradores cromados, tornillo de banco de fundición pesado con husillo y maneta, panel trasero perforado con martillo de peña y juego de llaves fijas, y flexo orientable con pantalla cónica y bombilla cálida resplandeciente.
- **Colisión UCX:** Mesa compuesta con panel posterior (`UCX_SM_Heavy_Duty_Workbench_01`).
- **Mecánica UE5:** Estación de crafteo y reparación donde los jugadores pueden recargar herramientas de corte o calibrar sensores dañados.

### 12.2. Prop 47: `SM_Arc_Welding_Rig_Cart`
- **Morfología:** Carro móvil de soldadura por arco ($75 \times 125 \times 180\,\text{cm}$) con chasis azul maquinaria, ruedas grandes traseras engomadas y ruedas locas delanteras, asa tubular de empuje, botella de gas argón verde azulado con cadena y manorreductor de latón de doble reloj, máquina inverter en amarillo hazard con potenciómetro y bornes Dinse, carrete de cable de masa, antorcha TIG y careta de soldadura abatible.
- **Colisión UCX:** Chasis de carro y botella de gas (`UCX_SM_Arc_Welding_Rig_Cart_01`).
- **Mecánica UE5:** Equipo móvil de reparación estructural para soldar brechas en mamparos agrietados o puertas selladas.

### 12.3. Prop 48: `SM_Pedestal_Drill_Press`
- **Morfología:** Taladro de columna industrial ($65 \times 85 \times 220\,\text{cm}$) con base ranurada de fundición con ranuras en T, columna de acero rectificado con cremallera dentada de elevación, mesa de trabajo basculante regulable por manivela, cabezal motorizado azul maquinaria con motor aleteado trasero, seta de parada de emergencia, husillo con volante de tres radios y bolas de baquelita, mandril portabrocas y broca helicoidal cromada.
- **Colisión UCX:** Base, columna y cabezal superior (`UCX_SM_Pedestal_Drill_Press_01`).
- **Mecánica UE5:** Máquina de taller interactiva que puede ser accionada para perforar cerraduras blindadas o pernos agarrotados.

### 12.4. Prop 49: `SM_Parts_Washer_Station`
- **Morfología:** Estación desengrasante de piezas ($125 \times 85 \times 165\,\text{cm}$) con cuba de lavado azul maquinaria con patas tubulares y bandeja inferior con bidón de disolvente, pedal de bombeo, rejilla galvanizada interior con engranaje de latón sumergido, manguera flexible articulada Loc-Line con boquilla dosificadora, y tapa cortafuegos batiente abierta a $65^\circ$ con placa de advertencia hazard y eslabón fusible de cierre automático contra incendios.
- **Colisión UCX:** Cuba cúbica con patas (`UCX_SM_Parts_Washer_Station_01`).
- **Mecánica UE5:** Permite lavar fluidos cáusticos de componentes mecánicos para que puedan ser reinstalados en sistemas críticos.

### 12.5. Prop 50: `SM_Heavy_Hydraulic_Floor_Press`
- **Morfología:** Prensa hidráulica de taller de 50 toneladas ($155 \times 95 \times 245\,\text{cm}$) con bastidor en H de vigas canal UPN en amarillo hazard, taladros de regulación con pasadores pasantes cromados, bancada móvil reforzada con bloques en V, cilindro hidráulico central azul maquinaria con émbolo cromado y resortes laterales de retorno, manómetro superior de glicerina con bisel de latón y bomba manual lateral con palanca larga de accionamiento.
- **Colisión UCX:** Bastidor en H y cilindro central (`UCX_SM_Heavy_Hydraulic_Floor_Press_01`).
- **Mecánica UE5:** Herramienta de fuerza bruta para enderezar piezas deformadas por calor o comprimir baterías inestables para neutralizarlas.

---

## 13. Lámina Maestra Consolidada de 50 Props (`Showcase_50_Props_Maestros_Master.png`)

Para certificar la integridad visual, el cumplimiento riguroso de la estética comic/industrial y la ausencia total de errores visuales o primitivas geométricas básicas, se ha compuesto e inspeccionado la **Lámina Maestra Oficial de 50 Props**:
- **Archivo:** `Art/Renders/Showcase_50_Props_Maestros_Master.png`
- **Resolución:** $2560 \times 3100$ píxeles (Formato vertical de alta densidad).
- **Estructura:** Matriz de 10 filas temáticas (una fila por Lote) con 5 tarjetas por fila, cada una conteniendo:
  - Miniatura 3D individual de alta resolución con cel-shading comic y PBR.
  - Título en español y categoría técnica de jugabilidad.
  - Especificaciones técnicas: Cel-Shading Comic 3D, PBR Stylized, Colisión UCX e Interactividad Táctica.
  - Sello verde de certificación: `ESTADO: CERTIFICADO 100% 3D // PID_XX`.
- **Certificación:** Todos los 50 props han sido inspeccionados visualmente mediante herramientas de visión artificial y certificados conformes a los estándares de ingeniería y diseño del proyecto.

---

## 14. Pipeline de Exportación FBX y Colisiones UCX

### 14.1. Propósito y Alcance
El script `Art/Blender/exportar_50_props_fbx.py` automatiza la extracción determinista de los 50 modelos procedurales creados a lo largo de los 10 archivos `.blend` maestros (`Lote1_Props_Maestros_Oficial.blend` a `Lote10_Props_Maestros.blend`) hacia archivos FBX estándar independientes en `Art/FBX/Props/`.

### 14.2. Contratos y Transformaciones Geométricas
Para garantizar la compatibilidad estricta con Unreal Engine 5.8 sin requerir ajustes manuales en el editor:
1. **Centrado en Origen y Base en el Suelo:**
   - Se calcula el bounding box en coordenadas de mundo del activo: $(\text{min}_x, \text{max}_x, \text{min}_y, \text{max}_y, \text{min}_z, \text{max}_z)$.
   - Se desplazan todos los vértices por $(-\text{center}_x, -\text{center}_y, -\text{min}_z)$ de modo que el pivote de la malla estática quede exactamente en el punto de apoyo inferior $(0, 0, 0)$.
2. **Jerarquías Compuestas Unificadas:**
   - En lotes donde el modelo consta de múltiples componentes acoplados (Lotes 7 al 10 con 10 a 60 submallas por prop), el script duplica y une las mallas en un único `StaticMesh` unificado preservando los slots de material PBR per-face.
3. **Generación de Volúmenes de Colisión `UCX_`:**
   - Por cada modelo `SM_<Nombre>`, se genera una malla convexa de colisión simplificada con el prefijo `UCX_SM_<Nombre>_01`.
   - Esto permite que el importador nativo de Unreal Engine detecte automáticamente la envolvente física precisa sin costo de renderizado adicional.
4. **Configuración de Exportador FBX:**
   - `apply_unit_scale=True`, `apply_scale_options='FBX_SCALE_ALL'`, `axis_forward='-Z'`, `axis_up='Y'`, `mesh_smooth_type='FACE'`.

---

## 15. Pipeline de Importación y Validación en Unreal Engine 5.8

### 15.1. Propósito y Filosofía Fail-Fast
El script `Scripts/importar_50_props_maestros_ue5.py` se ejecuta de forma headless mediante `UnrealEditor-Cmd.exe` en el proyecto `AstraHazard.uproject`. Implementa la ingesta por lotes de los 50 archivos FBX a la ruta canónica del Content Browser:
`/Game/Meshes/Environment/Props/MasterProps/`

### 15.2. Parámetros de Ingesta `FbxImportUI`
- **Combine Meshes:** `True` (unifica jerarquías en caso de nodos secundarios).
- **Auto Generate Collision:** `True` (respeta los convex hulls `UCX_` provistos y genera colisión de respaldo si faltase).
- **One Convex Hull Per UCX:** `True` (garantiza colisiones convexas físicas estables para Chaos Physics).
- **Nanite:** `True` (`build_nanite=True` para virtualización de geometría de alta resolución).
- **Generación de Lightmaps UVs:** `False` (el proyecto utiliza Lumen completamente dinámico).

### 15.3. Validación Automatizada
Tras ejecutar cada tarea de importación (`AssetImportTask`), el script:
1. Carga el activo con `unreal.EditorAssetLibrary.load_asset`.
2. Inspecciona `get_bounds().box_extent` para validar dimensiones físicas positivas no nulas.
3. Persiste el activo en disco (`save_loaded_asset`).
4. Genera un reporte consolidado de éxito/fallo con detección temprana de errores.

---

## 16. Nivel Gym de Exhibición e Integración en Unreal Engine 5.8

### 16.1. Propósito y Arquitectura de Validación
El script `Scripts/construir_gym_50_props_ue5.py` construye el mapa interactivo de validación de escala, colisión y rendimiento:
`/Game/Maps/Gym_MasterProps_Showcase.umap`

### 16.2. Distribución Espacial en el Showroom
- **Pabellón Hangar:** Pavimento modular de $20 \times 48\,\text{m}$ construido con baldosas de acero corrugado y rejillas de mamparo (`SM_Floor_Plate_400x400` y `SM_Floor_MetalGrid_400x400`).
- **10 Avenidas Temáticas:**
  - Los 10 Lotes (Lote 01 al 10) se distribuyen escalonados a lo largo del eje $Y$ ($Y = 0, 400, 800, \dots, 3600\,\text{cm}$).
  - Los 5 props de cada lote se ubican a lo largo del eje $X$ en $X \in \{-600, -300, 0, +300, +600\}\,\text{cm}$.
- **Punto de Inicio y Telemetría:**
  - `PlayerStart_Showcase_Entrance` posicionado en $(0, -350, 50)$ con orientación $Yaw = 90^\circ$, permitiendo iniciar la partida frente al pabellón.
- **Iluminación Dinámica Lumen:**
  - `DirectionalLight_Showcase_Sun` a $45^\circ$ y `SkyLight_Ambient` para sombras nítidas y lectura clara de los materiales PBR Stylized.

---

## 17. Clases C++ de Props Maestros Interactivos

Para dotar al entorno de interactividad diegética profunda, se han implementado 5 clases C++ orientadas al bucle de juego cooperativo y contingencias en la nave:

### 17.1. `ACargoScalePlatformActor` (Báscula de Suelo y Placa de Presión - Prop 40)
- **Malla:** `SM_Cargo_Scale_Platform`
- **Responsabilidad:** Detección en tiempo real de la masa acumulada sobre la plataforma mediante un `UBoxComponent` volumétrico.
- **Contratos:**
  - `EvaluateScaleState(CurrentWeight, TargetThreshold, MaxCapacity)` -> Retorna `ECargoScaleState` (`Inactive`, `Weighing`, `TargetReached`, `Overload`).
  - `CalculateTotalMassInBounds(ItemMasses)` -> Suma segura no negativa de masas en Kg.
  - Eventos replicados: `OnCargoScaleWeightChanged`, `OnCargoScaleTriggerStateChanged`.
- **Rationale:** Permite crear puertas de hangar que solo se abren al colocar palets con cierta masa o rompecabezas cooperativos donde dos bomberos deben subirse a la vez.

### 17.2. `ASecurityTurnstileBarrierActor` (Torniquete Biométrico Trípode - Prop 41)
- **Malla:** `SM_Security_Turnstile_Barrier`
- **Responsabilidad:** Control de flujo peatonal unidireccional y filtrado por rango corporativo.
- **Contratos:**
  - Implementa `IInteractableInterface` (`CanInteract`, `ExecuteInteraction`, `GetInteractionPromptText`).
  - `EvaluateAccessPermitted(UserRank, RequiredRank, bEmergencyLockdown)`.
  - Desactiva dinámicamente la colisión de `PhysicalBarrierComponent` durante la ventana de paso autorizada y la rearma al cruzar `PassageDetectorComponent`.
- **Rationale:** Control de zonas restringidas en la nave (BSL-4 o puente de mando), integrando la jerarquía de rangos corporativos sin acoplamiento rígido.

### 17.3. `AWeaponLockerReinforcedActor` (Armero de Asalto Blindado - Prop 44)
- **Malla:** `SM_Weapon_Locker_Reinforced`
- **Responsabilidad:** Almacén de suministros defensivos con candado reforzado destructible.
- **Contratos:**
  - Implementa `IInteractableInterface`.
  - Sobrescribe `AActor::TakeDamage` para recibir impactos físicos directos de `ThermalAxeEquipment`.
  - `CalculateBreachIntegrityAfterDamage(CurrentIntegrity, DamageAmount)`.
  - Al ceder el candado (0% integridad), pasa a `BreachedOpen` y permite saquear cajas de munición táctica.
- **Rationale:** Fomenta el uso de herramientas pesadas de rescate como palancas o hachas para abrir alijos de emergencia en pasillos aislados.

### 17.4. `APortableBatteryRackActor` (Celda de Energía Extraíble - Prop 08)
- **Malla:** `SM_Portable_Battery_Rack`
- **Responsabilidad:** Batería modular transportable con física activa y penalización de sobrecarga.
- **Contratos:**
  - Implementa `IInteractableInterface` y `ICarriableInterface` (`CanBeCarried`, `OnPickedUp`, `OnDropped`, `GetCarriableWeightKg = 25.0f`).
  - `CalculateDischarge(CurrentCharge, ConsumptionRate, DeltaTime)`.
  - `EvaluateBatteryStatus(CurrentCharge)` -> `EBatteryChargeStatus` (`Charged`, `Discharging`, `Depleted`).
- **Rationale:** Pieza clave de sinergia cooperativa: un jugador debe transportar la batería pesada mientras el otro lo escolta con el extintor o el lanzador de espuma.

### 17.5. `AAuxiliaryDieselGeneratorActor` (Generador Diésel Auxiliar - Prop 06)
- **Malla:** `SM_Backup_Diesel_Generator`
- **Responsabilidad:** Fuente de alimentación autónoma para subredes eléctricas locales apagadas.
- **Contratos:**
  - Implementa `IInteractableInterface`.
  - Mecánica diegética de tirón manual en T: requiere 3 tirones consecutivos dentro de una ventana de 2.5s para arrancar la compresión del motor.
  - `EvaluateCrankStartSuccess(CurrentTugs, RequiredTugs, FuelLevel)`.
  - Consumo continuo de combustible y entrega de 15,000 W (15 kW) a la red mediante el delegate `OnGeneratorPowerSupplied`.
- **Rationale:** Permite revivir salas sin soporte vital, reactivando cámaras hidropónicas de O2 o terminales de mamparo en momentos de crisis.

### 17.6. `ATraumaKitCabinetActor` (Armario Mural de Primeros Auxilios - Prop 16)
- **Malla:** `SM_Trauma_Kit_Wall_Cabinet`
- **Responsabilidad:** Dispensación de autoinyectores de estabilización y fármacos de campo de mamparo.
- **Contratos:**
  - Implementa `IInteractableInterface`.
  - El primer toque rompe el cristal de seguridad diegético; los toques subsiguientes dispensan inyecciones médicas individuales (3 unidades iniciales).
  - `CalculateRemainingDoses(CurrentDoses, DosesToTake)` -> Cálculo clampeado a 0.
  - `EvaluateCabinetState(RemainingDoses, bIsOpened)` -> Retorna `ETraumaKitState` (`Intact`, `Opened`, `Depleted`).
  - Delegado: `OnTraumaKitDispensed`.
- **Rationale:** Proporciona un recurso vital in-situ para restaurar salud o desacelerar el consumo de O2 de los bomberos y estabilizar civiles heridos antes del transporte.

### 17.7. `ADecontaminationShowerActor` (Ducha de Descontaminación Química - Prop 11)
- **Malla:** `SM_Decontamination_Shower_Unit`
- **Responsabilidad:** Purga y neutralización de contaminantes químicos, ácido sulfúrico cáustico y quemaduras térmicas.
- **Contratos:**
  - Implementa `IInteractableInterface`.
  - Activación por tirador de cadena triangular diegético; inicia ciclo de aspersión de 6.0s con cooldown de 4.0s.
  - Detección volumétrica en `UBoxComponent` (`ShowerZoneComponent`) para purgar alteraciones ambientales en actores superpuestos.
  - `CalculateRemainingShowerDuration(CurrentTimeRemaining, DeltaTime)`.
  - `EvaluateIsCycleComplete(RemainingTime)`.
  - Delegado: `OnDeconShowerStateChanged`.
- **Rationale:** Sinergia directa con los focos de peligro químico (`AAcidPuddleHazardActor`) y biológico, permitiendo limpiar el traje antes de que el daño continuo penetre la armadura.

### 17.8. `AEmergencyCapacitorBankActor` (Banco de Condensadores de Alto Voltaje - Prop 10)
- **Malla:** `SM_Emergency_Capacitor_Bank`
- **Responsabilidad:** Almacenamiento electrostático masivo y descarga de pulso electromagnético (EMP) radial defensivo.
- **Contratos:**
  - Implementa `IInteractableInterface`.
  - Palanca de descarga masiva (Dump Switch); emite un pulso radial de 900 cm que sobrecarga circuitos y aturde robots/drones hostiles (`ACorporateAuditorThreatActor`, `ACinderStalkerThreatActor`).
  - Recarga progresiva autónoma (6.66%/s, ~15s de ciclo completo).
  - `CalculateRechargePercent(CurrentPercent, RechargeRatePercentPerSec, DeltaTime)`.
  - `EvaluateEmpRadiusImpact(SourceLocation, TargetLocation, EmpRadius)`.
  - Delegados: `OnCapacitorDischarged`, `OnCapacitorRecharged`.
- **Rationale:** Arma táctica ambiental integrada en la arquitectura de la nave que los jugadores pueden preparar y coordinar para crear zonas seguras temporales.

### 17.9. `AHydraulicBlastDoorActor` (Portón Blindado Cortafuegos - Prop 03)
- **Malla:** `SM_Hydraulic_Blast_Door`
- **Responsabilidad:** Aislamiento físico y térmico masivo entre sectores estructurales de la nave.
- **Contratos:**
  - Implementa `IInteractableInterface`.
  - Modo Dual Motorizado/Manual:
    - Con energía auxiliar (`bHasPower = true`): Apertura/cierre motorizado rápido en 2.5s mediante pulsador.
    - Sin energía (`bHasPower = false`): Requiere bombeo con palanca de derivación manual de emergencia (3 pulsaciones coordinadas de bombero).
  - `CalculateBlastDoorProgress(CurrentProgress, DeltaTime, MoveDuration, bOpening)`.
  - `EvaluateCanManualOverride(bHasPower, CurrentManualPumps, RequiredPumps)`.
  - Desplazamiento visual de hojas en `LeftDoorMeshComponent` y `RightDoorMeshComponent`.
  - Delegado: `OnBlastDoorStateChanged`.
- **Rationale:** Pieza angular del diseño de niveles que obliga a los jugadores a restaurar generadores o cooperar manualmente para franquear mamparos sellados.

### 17.10. `AArcWeldingRigCartActor` (Carro Móvil de Soldadura de Arco TIG - Prop 47)
- **Malla:** `SM_Arc_Welding_Rig_Cart`
- **Responsabilidad:** Unidad de soldadura móvil transportable para reparación estructural y sellado de brechas al vacío.
- **Contratos:**
  - Implementa `IInteractableInterface` y `ICarriableInterface` (peso 45 Kg, arrastre físico acoplado a socket).
  - Botella de gas argón (50.0L) con consumo continuo (2.5 L/s) durante el arco activo.
  - `CalculateArgonConsumption(CurrentGasLiters, ConsumptionRateLitersPerSec, DeltaTime)`.
  - `EvaluateCanWeld(CurrentGasLiters, MinRequiredGasLiters)`.
  - `EvaluateRigStatus(CurrentGasLiters, bIsArcActive)`.
  - Delegado: `OnWeldingRigGasChanged`.
- **Rationale:** Permite a la escuadra transportar el equipo pesado hacia zonas de descompresión (`AVacuumBreachHazardActor`) para sellar el casco antes de agotar el oxígeno.

---

## 18. Catálogo de Blueprints Interactivos en Content Browser

Todos los Blueprints han sido generados en `/Game/Blueprints/Environment/Props/` asignando las mallas estáticas de alta fidelidad a sus componentes CDO:

| Blueprint Asset | Clase C++ Padre | Malla Estática Asignada | Rol Mecánico en Juego |
| :--- | :--- | :--- | :--- |
| [`BP_CargoScalePlatform`](file:///F:/Dev/Game/Content/Blueprints/Environment/Props/BP_CargoScalePlatform.uasset) | `ACargoScalePlatformActor` | `SM_Cargo_Scale_Platform` | Báscula de masa diegética y placa de presión |
| [`BP_SecurityTurnstileBarrier`](file:///F:/Dev/Game/Content/Blueprints/Environment/Props/BP_SecurityTurnstileBarrier.uasset) | `ASecurityTurnstileBarrierActor` | `SM_Security_Turnstile_Barrier` | Torniquete biométrico con control de rango |
| [`BP_WeaponLockerReinforced`](file:///F:/Dev/Game/Content/Blueprints/Environment/Props/BP_WeaponLockerReinforced.uasset) | `AWeaponLockerReinforcedActor` | `SM_Weapon_Locker_Reinforced` | Armero blindado rompible con Hacha Térmica |
| [`BP_PortableBatteryRack`](file:///F:/Dev/Game/Content/Blueprints/Environment/Props/BP_PortableBatteryRack.uasset) | `APortableBatteryRackActor` | `SM_Portable_Battery_Rack` | Celda de energía portátil (25 Kg) transportable |
| [`BP_AuxiliaryDieselGenerator`](file:///F:/Dev/Game/Content/Blueprints/Environment/Props/BP_AuxiliaryDieselGenerator.uasset) | `AAuxiliaryDieselGeneratorActor` | `SM_Backup_Diesel_Generator` | Generador diésel auxiliar con arranque por tirador |
| [`BP_TraumaKitCabinet`](file:///F:/Dev/Game/Content/Blueprints/Environment/Props/BP_TraumaKitCabinet.uasset) | `ATraumaKitCabinetActor` | `SM_Trauma_Kit_Wall_Cabinet` | Armario de primeros auxilios con cristal rompible |
| [`BP_DecontaminationShower`](file:///F:/Dev/Game/Content/Blueprints/Environment/Props/BP_DecontaminationShower.uasset) | `ADecontaminationShowerActor` | `SM_Decontamination_Shower_Unit` | Ducha de descontaminación de fluidos cáusticos |
| [`BP_EmergencyCapacitorBank`](file:///F:/Dev/Game/Content/Blueprints/Environment/Props/BP_EmergencyCapacitorBank.uasset) | `AEmergencyCapacitorBankActor` | `SM_Emergency_Capacitor_Bank` | Banco de condensadores con descarga EMP radial |
| [`BP_HydraulicBlastDoor`](file:///F:/Dev/Game/Content/Blueprints/Environment/Props/BP_HydraulicBlastDoor.uasset) | `AHydraulicBlastDoorActor` | `SM_Hydraulic_Blast_Door` | Portón cortafuegos motorizado y bypass manual |
| [`BP_ArcWeldingRigCart`](file:///F:/Dev/Game/Content/Blueprints/Environment/Props/BP_ArcWeldingRigCart.uasset) | `AArcWeldingRigCartActor` | `SM_Arc_Welding_Rig_Cart` | Carro de soldadura TIG móvil con botella de argón |

---

## 19. Verificación por Automatización (Automation Testing)

La suite de pruebas automatizadas `FAstraInteractivePropsTest` (`AstraHazard.Environment.InteractivePropsCalculation`) valida los contratos numéricos, fórmulas físicas y transiciones de estado de las 10 clases:

- **Ruta de Ejecución:** `AstraHazard.Environment.InteractivePropsCalculation`
- **Resultados de Validación:**
  - `Masa total calculada debe ser 150 Kg`: **PASS**
  - `Estados de báscula (Inactive, Weighing, TargetReached, Overload)`: **PASS**
  - `Permisos de torniquete por rango corporativo y lockdown`: **PASS**
  - `Integridad de armero y apertura destructible`: **PASS**
  - `Descarga y estados de batería de grafeno`: **PASS**
  - `Arranque de generador por 3 tirones y consumo de diésel`: **PASS**
  - `Dispensación de dosis médicas y estados de botiquín`: **PASS**
  - `Ciclo temporal de ducha de descontaminación`: **PASS**
  - `Recarga de condensadores y radio de aturdimiento EMP`: **PASS**
  - `Progresión de apertura y bypass manual de portón cortafuegos`: **PASS**
  - `Consumo de argón y umbral de soldadura de arco TIG`: **PASS**
- **Resultado Global:** `Test Completed. Result={Success} Name={InteractivePropsCalculation}` (100% de éxito en UE 5.8).
