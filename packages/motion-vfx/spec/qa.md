# 🎯 Especificación del Protocolo de Control de Calidad Visual y Técnico (QA Engine)

**Estándar:** `Autonomous After Effects MCP — Visual & Technical QA Specification`  
**Referencia:** `REQ-026`, `REQ-028`  

---

## 1. Las 7 Familias de Verificación QA Obligatorias

Todo proyecto debe superar la batería completa de 7 familias antes de autorizar la entrega:

1. **Detección de Fotogramas Negros / Huecos (`BlackFrames & Gaps`):** Detecta fotogramas con luminancia media $< 0.01$ no declarados explícitamente como fundidos a negro.
2. **Detección de Fotogramas Congelados (`FreezeFrames`):** Identifica congelamiento de video mayor a $0.5\text{ s}$ salvo fotogramas 'hero' intencionales.
3. **Colisiones y Solapamientos Tipográficos (`TextCollisions & Overflows`):** Detecta textos que se superponen entre sí o con la interfaz.
4. **Violación de Zonas Seguras (`SafeZoneViolations`):** Comprueba que todo elemento interactivo o legible permanezca dentro de los márgenes seguros.
5. **Desincronización Audio/Video (`AVDrift`):** Comprueba que la deriva entre transientes de audio y cortes visuales sea $\le 40\text{ ms}$.
6. **Anomalías de Exposición y Parpadeo (`Flicker & Exposure`):** Detecta cambios bruscos de luminancia no intencionales.
7. **Integridad de Alpha y Recorte 3D (`AlphaMatteIntegrity`):** Comprueba que los bordes de los sujetos recortados no tengan halos negros o artefactos de color.
