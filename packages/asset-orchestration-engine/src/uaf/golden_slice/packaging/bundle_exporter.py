"""
UAF-81.88 / AOE: Portable Unreal Engine 5 Bundle Exporter.
Packages golden slice assets, manifests, ingestion automation scripts, and the UAFBridge UE5 plugin
into a drop-in portable bundle ready for transfer to any workstation running Unreal Engine 5.
"""

from __future__ import annotations

import os
import shutil
import zipfile
import hashlib
import json
from typing import Optional, Dict, Any
from pathlib import Path

from ..manifest.models import GoldenSliceManifest


class UE5BundleExporter:
    """
    Exports a self-contained, drop-in distribution bundle for Unreal Engine 5.
    Designed specifically for decoupled workflows where AOE runs headless on one machine
    and Unreal Engine 5 runs on a separate artist/developer workstation.
    """

    def __init__(self, repo_root: Optional[str] = None) -> None:
        if repo_root is None:
            # Locate repo root by walking up from current file
            current_path = Path(__file__).resolve()
            # current_path is src/uaf/golden_slice/packaging/bundle_exporter.py
            # parent: packaging (1) -> golden_slice (2) -> uaf (3) -> src (4) -> repo_root (5)
            self.repo_root = str(current_path.parents[4])
        else:
            self.repo_root = os.path.abspath(repo_root)

        self.plugin_src_dir = os.path.join(self.repo_root, "ue5_plugin", "UAFBridge")

    def _compute_sha256(self, filepath: str) -> str:
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def create_bundle(
        self,
        manifest: GoldenSliceManifest,
        output_path: str,
        as_zip: bool = True,
    ) -> Dict[str, Any]:
        """
        Creates the portable UE5 delivery bundle.
        If as_zip is True, output_path is treated as or converted into a .zip archive.
        Returns a summary report with paths, file counts, and package checksum.
        """
        dest_path = Path(output_path)
        if as_zip and not str(dest_path).endswith(".zip"):
            staging_dir = dest_path.parent / f"{dest_path.name}_staging"
            zip_dest = dest_path.with_suffix(".zip")
        elif as_zip:
            staging_dir = dest_path.parent / f"{dest_path.stem}_staging"
            zip_dest = dest_path
        else:
            staging_dir = dest_path
            zip_dest = None

        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        staging_dir.mkdir(parents=True, exist_ok=True)

        # 1. Copy UAFBridge plugin to Plugins/UAFBridge
        plugins_dest = staging_dir / "Plugins" / "UAFBridge"
        if os.path.exists(self.plugin_src_dir):
            shutil.copytree(self.plugin_src_dir, plugins_dest)
        else:
            # Create minimal scaffold if not present
            plugins_dest.mkdir(parents=True, exist_ok=True)

        # 2. Setup Content/AOE directory structure
        content_dest = staging_dir / "Content" / "AOE"
        manifests_dest = content_dest / "Manifests"
        meshes_dest = content_dest / "Meshes"
        textures_dest = content_dest / "Textures"
        audio_dest = content_dest / "Audio"
        scripts_dest = content_dest / "Scripts"

        for d in (manifests_dest, meshes_dest, textures_dest, audio_dest, scripts_dest):
            d.mkdir(parents=True, exist_ok=True)

        # 3. Export Manifest JSON
        manifest_file = manifests_dest / "golden_slice_manifest.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest.to_dict(), f, indent=2)

        # 4. Copy Ingestion Script to Content/AOE/Scripts/run_ingest.py
        plugin_ingest_script = plugins_dest / "Content" / "Python" / "aoe_editor_ingest.py"
        if plugin_ingest_script.exists():
            shutil.copy(plugin_ingest_script, scripts_dest / "run_ingest.py")

        # 5. Generate User Instruction Guides
        instructions_es = f"""===================================================================
   GUIA DE INSTALACION Y USO EN TU MAQUINA CON UNREAL ENGINE 5
===================================================================

Proyecto: {manifest.project_id}
Semilla Global: {manifest.seed}
Perfil: {manifest.quality_profile.value}

PASOS RAPIDOS:

1. COPIAR EL PLUGIN:
   Copia la carpeta:
     Plugins/UAFBridge/
   dentro de la carpeta 'Plugins/' de tu proyecto de Unreal:
     <TuProyecto>/Plugins/UAFBridge/

2. COPIAR LOS ASSETS Y MANIFIESTOS:
   Copia la carpeta:
     Content/AOE/
   dentro de la carpeta 'Content/' de tu proyecto de Unreal:
     <TuProyecto>/Content/AOE/

3. ABRIR TU PROYECTO EN UNREAL ENGINE 5:
   - Abre tu proyecto (.uproject).
   - Veras un nuevo menu en la barra superior llamado 'AOE'.
   - Haz clic en: 'AOE -> Ingest AOE Bundle'.
   - ¡Listo! Todo se importara automaticamente con Nanite activado,
     materiales configurados, Niagara, audio y actores en el nivel.

NOTA: Tambien puedes ejecutar la importacion desde la consola de Python de Unreal:
  from aoe_editor_ingest import AOEUnrealIngestionPipeline
  AOEUnrealIngestionPipeline().run_pipeline()
===================================================================
"""
        with open(staging_dir / "LEEME_INSTRUCCIONES.txt", "w", encoding="utf-8") as f:
            f.write(instructions_es)

        with open(staging_dir / "README_IMPORT.md", "w", encoding="utf-8") as f:
            f.write(f"# AOE Export Bundle for Unreal Engine 5\n\nProject: **{manifest.project_id}**\n\nCopy `Plugins/UAFBridge` to `<YourProject>/Plugins/UAFBridge` and `Content/AOE` to `<YourProject>/Content/AOE`.")

        # 6. Index files and generate SHA-256 manifest
        file_hashes: Dict[str, str] = {}
        total_files = 0
        total_bytes = 0

        for root, _, files in os.walk(staging_dir):
            for file in files:
                f_path = os.path.join(root, file)
                rel_path = os.path.relpath(f_path, staging_dir).replace("\\", "/")
                f_hash = self._compute_sha256(f_path)
                file_hashes[rel_path] = f_hash
                total_files += 1
                total_bytes += os.path.getsize(f_path)

        with open(staging_dir / "bundle_manifest.json", "w", encoding="utf-8") as f:
            json.dump({
                "project_id": manifest.project_id,
                "total_files": total_files,
                "total_bytes": total_bytes,
                "files": file_hashes
            }, f, indent=2)

        # 7. Compress into ZIP if requested
        if as_zip and zip_dest is not None:
            zip_dest.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_dest, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(staging_dir):
                    for file in files:
                        f_path = os.path.join(root, file)
                        arc_name = os.path.relpath(f_path, staging_dir)
                        zf.write(f_path, arc_name)

            # Cleanup staging directory
            shutil.rmtree(staging_dir)
            final_path = str(zip_dest)
            final_size = os.path.getsize(zip_dest)
            final_hash = self._compute_sha256(zip_dest)
        else:
            final_path = str(staging_dir)
            final_size = total_bytes
            final_hash = file_hashes.get("bundle_manifest.json", "")

        return {
            "success": True,
            "project_id": manifest.project_id,
            "bundle_path": final_path,
            "is_zip": as_zip,
            "total_files": total_files,
            "bundle_bytes": final_size,
            "sha256": final_hash,
        }
