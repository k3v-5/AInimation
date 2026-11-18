# Integridad y Relocalización de Assets (Fase 18)

## Integridad
- Cada asset registrado posee su identificador `assetId`, ruta o URI de origen y checksum SHA-256 opcional.
- La validación referencial detecta assets referenciados que no existen en el `AssetRegistry`.
- Confinamiento estricto en el sandbox para evitar escapes mediante rutas maliciosas (`../`).
