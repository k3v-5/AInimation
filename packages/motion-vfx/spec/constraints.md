# 🛡️ Especificación del Motor de Restricciones (Constraint Engine)

**Estándar:** `Autonomous After Effects MCP — Constraint Engine Specification`  
**Referencia:** `REQ-023`, `REQ-024`, `REQ-025`  

---

## 1. Catálogo de Restricciones Formales

El motor evalúa restricciones espaciales, tipográficas y perceptuales antes de autorizar cualquier compilación:

1. **`inside_safe_area` (Área Segura):**
   - Para 9:16 (TikTok/Reels/Shorts): Ningún texto puede residir en los márgenes de interfaz (arriba $< 15\%$, abajo $< 22\%$, derecha $< 18\%$).
2. **`not_overlap_face` (Protección de Rostro y Sujeto):**
   - La caja delimitadora del texto no puede intersecar con la zona de saliency del rostro ($IoU = 0$).
3. **`not_overlap_existing_text` (Evasión OCR):**
   - El texto generado debe tener $IoU \le 0.05$ respecto a cualquier texto detectado por `VideoOCREngine`.
4. **`minimum_contrast_ratio` (Contraste Mínimo WCAG):**
   - El ratio de luminancia entre el texto y el fondo debe ser $\ge 4.5:1$. Si es menor, se inyecta automáticamente una sombra paralela o viñeta de contraste.
