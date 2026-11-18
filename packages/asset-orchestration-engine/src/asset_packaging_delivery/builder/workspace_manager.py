import os
import shutil
from typing import Dict, Any, List
from ..core.package_schema import PackageFileEntry, PackageProfile

class WorkspaceManager:
    @classmethod
    def setup_workspace(
        cls,
        base_dir: str,
        package_id: str,
        profile: PackageProfile
    ) -> str:
        workspace_path = os.path.join(base_dir, package_id)
        os.makedirs(workspace_path, exist_ok=True)
        return workspace_path

    @classmethod
    def cleanup_workspace(cls, workspace_path: str):
        if os.path.exists(workspace_path):
            try:
                shutil.rmtree(workspace_path)
            except Exception:
                pass
