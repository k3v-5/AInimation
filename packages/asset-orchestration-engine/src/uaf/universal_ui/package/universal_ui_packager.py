"""
Universal UI Packager (UAF-81.61).
Transforms universal UI specifications into Unreal Engine 5 UMG WidgetBlueprint
and Slate manifest deliverables with cryptographic SHA-256 integrity proofs.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..models.definition import (
    WidgetType,
    UIWidget,
    UIScreen,
    UIAsset,
)
from ..validation.universal_ui_validator import UniversalUIValidator


@dataclass
class ProductionReadyUI:
    """Production deliverable containing UMG manifests, Slate declarations, and hash proof."""
    ui_id: str
    version: str
    ue_umg_manifest: Dict[str, Any]
    slate_manifest: Dict[str, Any]
    localization_manifest: List[str]
    checksum: str
    is_verified: bool = False


class UniversalUIPackager:
    """
    Packages validated UI assets into Unreal Engine 5 UMG and Slate architectures.
    """

    def __init__(self):
        self._validator = UniversalUIValidator()

    def package(self, asset: UIAsset) -> ProductionReadyUI:
        """Packages UI asset into production-ready UMG schema."""
        # 1. Validate
        val_rep = self._validator.validate_all(asset)
        if not val_rep.is_valid:
            raise ValueError(f"Cannot package invalid UIAsset: {val_rep.errors}")

        # 2. Build UMG Hierarchy
        umg_widgets = []
        screen = asset.root_screen
        for w in screen.widgets.values():
            umg_class = self._map_to_umg_class(w.widget_type)
            umg_widgets.append({
                "WidgetName": w.widget_id,
                "WidgetClass": umg_class,
                "ParentWidget": w.parent_id or "CanvasPanel_Root",
                "Children": w.children,
                "Slot": {
                    "X": w.bounds.x,
                    "Y": w.bounds.y,
                    "Width": w.bounds.width,
                    "Height": w.bounds.height,
                    "Anchor": w.anchor.value,
                },
                "Visibility": "Visible" if w.visibility else "Collapsed",
                "IsEnabled": w.enabled,
                "IsFocusable": w.focusable,
                "Accessibility": {
                    "Role": w.accessibility_role.value,
                    "Label": w.accessibility_label,
                    "Hint": w.accessibility_hint,
                },
            })

        ue_manifest = {
            "BlueprintType": "WidgetBlueprint",
            "WidgetTree": {
                "Root": "CanvasPanel_Root",
                "ScreenId": screen.screen_id,
                "ModalPolicy": screen.modal_policy.value,
                "Widgets": umg_widgets,
            }
        }

        # 3. Slate Declarations Manifest
        slate_manifest = {
            "CompoundWidget": f"S{asset.ui_id}",
            "WidgetCount": len(screen.widgets),
            "GeneratedAt": "UniversalAssetFactory_UE5",
        }

        # 4. Deterministic Checksum
        content_str = json.dumps({
            "ui_id": asset.ui_id,
            "version": asset.version,
            "umg": ue_manifest,
            "slate": slate_manifest,
            "keys": sorted(asset.localization_keys),
        }, sort_keys=True)
        checksum = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

        product = ProductionReadyUI(
            ui_id=asset.ui_id,
            version=asset.version,
            ue_umg_manifest=ue_manifest,
            slate_manifest=slate_manifest,
            localization_manifest=asset.localization_keys,
            checksum=checksum,
            is_verified=True,
        )
        return product

    def _map_to_umg_class(self, widget_type: WidgetType) -> str:
        """Maps universal widget type to Unreal Engine UMG class name."""
        mapping = {
            WidgetType.TEXT: "UTextBlock",
            WidgetType.IMAGE: "UImage",
            WidgetType.ICON: "UImage",
            WidgetType.BUTTON: "UButton",
            WidgetType.CHECKBOX: "UCheckBox",
            WidgetType.TOGGLE: "UCheckBox",
            WidgetType.SLIDER: "USlider",
            WidgetType.PROGRESS_BAR: "UProgressBar",
            WidgetType.LIST: "UListView",
            WidgetType.GRID: "UUniformGridPanel",
            WidgetType.SCROLL_VIEW: "UScrollBox",
            WidgetType.DROPDOWN: "UComboBoxString",
            WidgetType.TAB: "UButton",
            WidgetType.INPUT_FIELD: "UEditableTextBox",
            WidgetType.TOOLTIP: "UWidgetComponent",
            WidgetType.PANEL: "UCanvasPanel",
            WidgetType.WINDOW: "UOverlay",
            WidgetType.CONTAINER: "USizeBox",
        }
        return mapping.get(widget_type, "UUserWidget")
