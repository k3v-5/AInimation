"""
Synthetic image fixture generators for IANIMATION E2E tests.
Generates valid PNG files (RFC 2083) using Python's standard library (struct + zlib).
"""
from __future__ import annotations

from pathlib import Path
import struct
import zlib


def _build_png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    """Build a standard PNG chunk with 4-byte length and CRC32."""
    length = len(data)
    chunk = struct.pack(">I", length) + chunk_type + data
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return chunk + struct.pack(">I", crc)


def create_solid_png(
    file_path: Path,
    width: int = 64,
    height: int = 64,
    color: tuple[int, int, int, int] = (100, 150, 250, 255),
) -> Path:
    """
    Generate a valid RGBA PNG image with solid color.
    Uses pure standard library without requiring Pillow or external image libraries.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # PNG signature
    png_signature = b"\x89PNG\r\n\x1a\n"
    
    # IHDR chunk: width, height, bit_depth=8, color_type=6 (RGBA), comp=0, filter=0, interlace=0
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    ihdr_chunk = _build_png_chunk(b"IHDR", ihdr_data)
    
    # Construct scanlines (each row starts with filter byte 0x00)
    r, g, b, a = color
    pixel_bytes = bytes([r, g, b, a]) * width
    raw_scanlines = bytearray()
    for _ in range(height):
        raw_scanlines.append(0)  # Filter byte None
        raw_scanlines.extend(pixel_bytes)
        
    compressed_idat = zlib.compress(bytes(raw_scanlines), level=6)
    idat_chunk = _build_png_chunk(b"IDAT", compressed_idat)
    
    # IEND chunk
    iend_chunk = _build_png_chunk(b"IEND", b"")
    
    full_png = png_signature + ihdr_chunk + idat_chunk + iend_chunk
    file_path.write_bytes(full_png)
    return file_path


def create_1x1_png(file_path: Path) -> Path:
    """Generate a minimal valid 1x1 RGBA pixel PNG image for boundary testing."""
    return create_solid_png(file_path, width=1, height=1, color=(255, 255, 255, 255))


def create_corrupt_png(file_path: Path) -> Path:
    """Generate a corrupt image with valid PNG signature followed by garbage."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"\x89PNG\r\n\x1a\nCORRUPT_HEADER_TRUNCATED_CHUNKS")
    return file_path
