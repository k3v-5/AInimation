"""
Synthetic 3D mesh fixture generators for IANIMATION E2E tests.
Generates valid binary glTF 2.0 (.glb) files and corrupt 3D containers without external 3D libraries.
"""
from __future__ import annotations

import json
from pathlib import Path
import struct


def create_minimal_glb(
    file_path: Path,
    mesh_name: str = "SyntheticBipedStub",
) -> Path:
    """
    Generate a strictly conforming Khronos glTF 2.0 binary (.glb) file.
    Contains a valid 3D triangle mesh with vertex positions, normals, and indices.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Vertex Positions: 3 vertices (float32 x 3)
    # Vertex 0: (0.0, 0.0, 0.0)
    # Vertex 1: (1.0, 0.0, 0.0)
    # Vertex 2: (0.0, 1.0, 0.0)
    pos_data = struct.pack(
        "<9f",
        0.0, 0.0, 0.0,
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
    )  # 36 bytes
    
    # Indices: [0, 1, 2] (uint16 x 3) + 2 bytes padding to align to 4 bytes
    idx_data = struct.pack("<3HH", 0, 1, 2, 0)  # 8 bytes
    
    bin_buffer = pos_data + idx_data  # 44 bytes
    bin_length = len(bin_buffer)
    
    # GLTF JSON structure
    gltf_dict = {
        "asset": {
            "version": "2.0",
            "generator": "IANIMATION_E2E_Synthetic_Generator",
        },
        "scene": 0,
        "scenes": [
            {"name": "DefaultScene", "nodes": [0]}
        ],
        "nodes": [
            {"name": mesh_name, "mesh": 0}
        ],
        "meshes": [
            {
                "name": mesh_name,
                "primitives": [
                    {
                        "attributes": {"POSITION": 0},
                        "indices": 1,
                        "mode": 4,  # TRIANGLES
                    }
                ],
            }
        ],
        "buffers": [
            {"byteLength": bin_length}
        ],
        "bufferViews": [
            {
                "buffer": 0,
                "byteOffset": 0,
                "byteLength": 36,
                "target": 34962,  # ARRAY_BUFFER
            },
            {
                "buffer": 0,
                "byteOffset": 36,
                "byteLength": 6,
                "target": 34963,  # ELEMENT_ARRAY_BUFFER
            },
        ],
        "accessors": [
            {
                "bufferView": 0,
                "byteOffset": 0,
                "componentType": 5126,  # FLOAT
                "count": 3,
                "type": "VEC3",
                "max": [1.0, 1.0, 0.0],
                "min": [0.0, 0.0, 0.0],
            },
            {
                "bufferView": 1,
                "byteOffset": 0,
                "componentType": 5123,  # UNSIGNED_SHORT
                "count": 3,
                "type": "SCALAR",
                "max": [2],
                "min": [0],
            },
        ],
    }
    
    json_bytes = json.dumps(gltf_dict, separators=(",", ":")).encode("utf-8")
    # Pad JSON chunk with spaces to 4-byte alignment
    json_padding = (4 - (len(json_bytes) % 4)) % 4
    json_bytes += b" " * json_padding
    
    # Pad BIN chunk with zeros to 4-byte alignment
    bin_padding = (4 - (bin_length % 4)) % 4
    bin_bytes = bin_buffer + (b"\x00" * bin_padding)
    
    total_length = 12 + 8 + len(json_bytes) + 8 + len(bin_bytes)
    
    # 12-byte header: magic "glTF", version 2, total_length
    header = struct.pack("<4sII", b"glTF", 2, total_length)
    
    # JSON Chunk header: chunkLength, chunkType "JSON" (0x4E4F534A)
    json_header = struct.pack("<II", len(json_bytes), 0x4E4F534A)
    
    # BIN Chunk header: chunkLength, chunkType "BIN\0" (0x004E4942)
    bin_header = struct.pack("<II", len(bin_bytes), 0x004E4942)
    
    glb_content = header + json_header + json_bytes + bin_header + bin_bytes
    file_path.write_bytes(glb_content)
    return file_path


def create_corrupt_glb(file_path: Path) -> Path:
    """Generate a corrupt GLB file with invalid magic and truncated buffer."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"glTF\x02\x00\x00\x00\xFF\x00\x00\x00CORRUPT_BUFFER_TRUNCATED")
    return file_path
