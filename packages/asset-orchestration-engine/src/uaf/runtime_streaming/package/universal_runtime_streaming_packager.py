"""
Universal Runtime Streaming Packager (UAF-81.81 Section 9).
Exports streaming cell manifests and Unreal Engine 5 World Partitioning / Data Layers configurations.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional

from ..models.definition import (
    CellDefinition,
    copy_dict_deterministic,
)
from ..engine.universal_runtime_streaming_fabricator import (
    UniversalRuntimeStreamingFabricator,
)


class UniversalRuntimeStreamingPackager:
    """
    Authoritative packager creating deployment bundles and UE5 World Partition manifests.
    """

    @classmethod
    def package_streaming_world(
        cls,
        fab: UniversalRuntimeStreamingFabricator,
        target_engine: str = "UNREAL_ENGINE_5",
    ) -> Dict[str, Any]:
        timestamp = time.time()
        pkg_id = f"pkg_stream_{fab.streaming_world_id}_{int(timestamp * 1000)}"

        # Generate UE5 World Partition configuration
        ue5_manifest = cls._generate_ue5_world_partition_manifest(fab)

        cells_data = {
            k.to_string(): cell.to_dict()
            for k, cell in sorted(fab.registered_cells.items(), key=lambda x: x[0].to_string())
        }

        package_payload = {
            "package_id": pkg_id,
            "version": "1.0.0",
            "target_engine": target_engine,
            "timestamp": round(float(timestamp), 6),
            "streaming_world_id": fab.streaming_world_id,
            "total_cells_count": len(fab.registered_cells),
            "base_cell_size": fab.grid.base_cell_size,
            "budget": fab.budget.to_dict(),
            "cells": cells_data,
            "ue5_world_partition": ue5_manifest,
        }

        # Calculate package hash
        canonical = copy_dict_deterministic(package_payload)
        payload_bytes = json.dumps(canonical, sort_keys=True).encode("utf-8")
        package_payload["package_hash"] = hashlib.sha256(payload_bytes).hexdigest()

        return package_payload

    @classmethod
    def _generate_ue5_world_partition_manifest(cls, fab: UniversalRuntimeStreamingFabricator) -> Dict[str, Any]:
        """Generate Unreal Engine 5 UWorldPartition and UDataLayerSubsystem descriptor."""
        data_layers_found = sorted(list({c.data_layer for c in fab.registered_cells.values()}))

        cells_export = []
        for key, cell in sorted(fab.registered_cells.items(), key=lambda x: x[0]):
            cells_export.append({
                "CellName": key.to_string(),
                "GridLevel": key.level,
                "GridCoordinates": [key.x, key.y, key.z],
                "BoundsMin": [round(float(c), 4) for c in cell.bounds.min_corner],
                "BoundsMax": [round(float(c), 4) for c in cell.bounds.max_corner],
                "DataLayer": cell.data_layer,
                "bIsSpatiallyLoaded": True,
                "bIsCritical": cell.is_critical,
                "HLODParent": cell.hlod_parent_key.to_string() if cell.hlod_parent_key else None,
                "TotalRAMFootprintBytes": cell.total_ram_bytes(),
                "TotalVRAMFootprintBytes": cell.total_vram_bytes(),
            })

        return {
            "WorldPartitionClass": "UWorldPartition",
            "DefaultGrid": {
                "GridName": "MainGrid",
                "CellSize": fab.grid.base_cell_size,
                "LoadingRange": fab.observers.get("main", None).view_distance if fab.observers.get("main") else 500.0,
                "bBlockOnSlowStreaming": False,
            },
            "DataLayers": data_layers_found,
            "Cells": cells_export,
            "SupportedEngineVersion": "5.4+",
        }
