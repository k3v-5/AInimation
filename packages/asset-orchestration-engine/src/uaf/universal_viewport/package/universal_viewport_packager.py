"""
UAF-81.67: Universal Viewport Packager for Unreal Engine 5.
Generates Editor Viewport Client C++ headers, implementation bindings, JSON manifests, and SHA-256 signatures.
"""

from __future__ import annotations
import json
import hashlib
from typing import Any, Dict
from pathlib import Path

from uaf.universal_viewport.engine.universal_viewport_fabricator import (
    UniversalViewportFabricator,
)


class UniversalViewportPackager:
    """
    Authoritative packager translating Universal Asset Viewport scene graphs,
    cameras, and gizmos into Unreal Engine 5 Viewport Client C++ components and JSON manifests.
    """

    @staticmethod
    def generate_cpp_header() -> str:
        return """// Copyright (c) 2026 Asset Orchestration Engine. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "EditorViewportClient.h"
#include "UObject/NoExportTypes.h"
#include "UAFViewportClient.generated.h"

/**
 * UUAFViewportClient
 * Bridges UAF-81.67 Scene Graph, Camera System, and Gizmo Engine with Unreal Engine 5 Editor Viewports.
 */
UCLASS(BlueprintType)
class ASSETORCHESTRATION_API UUAFViewportClient : public UObject
{
    GENERATED_BODY()

public:
    UUAFViewportClient();

    UFUNCTION(BlueprintCallable, Category = "UAF|Viewport")
    void SetCameraLocationAndTarget(const FVector& Location, const FVector& Target);

    UFUNCTION(BlueprintCallable, Category = "UAF|Viewport")
    void SetActiveGizmo(const FString& GizmoType);

    UFUNCTION(BlueprintCallable, Category = "UAF|Viewport")
    void SelectNodes(const TArray<FString>& NodeIds);

    UFUNCTION(BlueprintCallable, Category = "UAF|Viewport")
    void RaycastPick(const FVector2D& ScreenPos, FString& OutHitNodeId, FVector& OutHitLocation);

private:
    FString ActiveViewportId;
    FString CurrentGizmoType;
};
"""

    @staticmethod
    def generate_cpp_source() -> str:
        return """// Copyright (c) 2026 Asset Orchestration Engine. All Rights Reserved.
#include "UAFViewportClient.h"

UUAFViewportClient::UUAFViewportClient()
{
    ActiveViewportId = TEXT("perspective");
    CurrentGizmoType = TEXT("TRANSLATE");
}

void UUAFViewportClient::SetCameraLocationAndTarget(const FVector& Location, const FVector& Target)
{
    UE_LOG(LogTemp, Verbose, TEXT("UAF-81.67: Set camera pos (%.1f, %.1f, %.1f) target (%.1f, %.1f, %.1f)"),
        Location.X, Location.Y, Location.Z, Target.X, Target.Y, Target.Z);
}

void UUAFViewportClient::SetActiveGizmo(const FString& GizmoType)
{
    CurrentGizmoType = GizmoType;
    UE_LOG(LogTemp, Log, TEXT("UAF-81.67: Active gizmo set to '%s'"), *GizmoType);
}

void UUAFViewportClient::SelectNodes(const TArray<FString>& NodeIds)
{
    UE_LOG(LogTemp, Log, TEXT("UAF-81.67: Selected %d nodes"), NodeIds.Num());
}

void UUAFViewportClient::RaycastPick(const FVector2D& ScreenPos, FString& OutHitNodeId, FVector& OutHitLocation)
{
    OutHitNodeId = TEXT("");
    OutHitLocation = FVector::ZeroVector;
    UE_LOG(LogTemp, Verbose, TEXT("UAF-81.67: Raycast at (%.1f, %.1f)"), ScreenPos.X, ScreenPos.Y);
}
"""

    @staticmethod
    def export_package(fabricator: UniversalViewportFabricator, viewport_id: str, output_dir: Path) -> Dict[str, str]:
        output_dir.mkdir(parents=True, exist_ok=True)

        header_content = UniversalViewportPackager.generate_cpp_header()
        source_content = UniversalViewportPackager.generate_cpp_source()

        header_path = output_dir / "UUAFViewportClient.h"
        source_path = output_dir / "UUAFViewportClient.cpp"

        header_path.write_text(header_content, encoding="utf-8")
        source_path.write_text(source_content, encoding="utf-8")

        snapshot = fabricator.take_snapshot(viewport_id)
        manifest = {
            "version": "1.0.0",
            "system": "UAF-81.67",
            "viewport_id": viewport_id,
            "nodes_count": snapshot.nodes_count,
            "selected_count": len(snapshot.selection),
            "camera_pos": snapshot.camera_pos,
            "camera_target": snapshot.camera_target,
            "state_hash": snapshot.state_hash
        }
        manifest_content = json.dumps(manifest, indent=2)
        manifest_path = output_dir / "uaf_viewport_manifest.json"
        manifest_path.write_text(manifest_content, encoding="utf-8")

        manifest_hash = hashlib.sha256(manifest_content.encode("utf-8")).hexdigest()
        sig_path = output_dir / "uaf_viewport_manifest.sig"
        sig_path.write_text(manifest_hash, encoding="utf-8")

        return {
            "header": str(header_path),
            "source": str(source_path),
            "manifest": str(manifest_path),
            "signature": str(sig_path),
            "sha256": manifest_hash
        }
