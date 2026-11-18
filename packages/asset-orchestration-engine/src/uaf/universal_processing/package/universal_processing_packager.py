"""
Universal Asset Processing Unreal Engine 5 C++ Packager & Manifest Generator.
Complies with UAF-81.71 specification.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Union

from uaf.universal_processing.engine.universal_processing_fabricator import UniversalProcessingFabricator


class UniversalProcessingPackager:
    """Exports C++ headers, sources, and signed manifest files for Unreal Engine 5 integration."""

    @staticmethod
    def generate_cpp_header() -> str:
        return """#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UUAFAssetProcessingComponent.generated.h"

UENUM(BlueprintType)
enum class EUAFProcessingResourceType : uint8
{
    Texture UMETA(DisplayName = "Texture"),
    Mesh UMETA(DisplayName = "Mesh"),
    Audio UMETA(DisplayName = "Audio"),
    Material UMETA(DisplayName = "Material"),
    Shader UMETA(DisplayName = "Shader"),
    Generic UMETA(DisplayName = "Generic")
};

UENUM(BlueprintType)
enum class EUAFProcessingQualityLevel : uint8
{
    Low UMETA(DisplayName = "Low"),
    Medium UMETA(DisplayName = "Medium"),
    High UMETA(DisplayName = "High"),
    Ultra UMETA(DisplayName = "Ultra"),
    Custom UMETA(DisplayName = "Custom")
};

UCLASS(ClassGroup = (UAF), meta = (BlueprintSpawnableComponent))
class UAF_API UUAFAssetProcessingComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UUAFAssetProcessingComponent();

    UFUNCTION(BlueprintCallable, Category = "UAF|Processing")
    bool LoadProcessingManifest(const FString& ManifestFilePath);

    UFUNCTION(BlueprintCallable, Category = "UAF|Processing")
    FString GetDerivedResourceHash(const FString& ResourceId) const;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UAF|Processing")
    EUAFProcessingQualityLevel ActiveQualityLevel;
};
"""

    @staticmethod
    def generate_cpp_source() -> str:
        return """#include "UUAFAssetProcessingComponent.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

UUAFAssetProcessingComponent::UUAFAssetProcessingComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    ActiveQualityLevel = EUAFProcessingQualityLevel::High;
}

bool UUAFAssetProcessingComponent::LoadProcessingManifest(const FString& ManifestFilePath)
{
    if (!FPaths::FileExists(ManifestFilePath))
    {
        return false;
    }
    FString JsonString;
    return FFileHelper::LoadFileToString(JsonString, *ManifestFilePath);
}

FString UUAFAssetProcessingComponent::GetDerivedResourceHash(const FString& ResourceId) const
{
    return FString(TEXT("SHA256_STUB"));
}
"""

    @staticmethod
    def generate_processing_manifest(fabricator: UniversalProcessingFabricator) -> str:
        payload = {
            "schema_version": "1.0.0",
            "derived_resources": {
                rid: res.to_dict() for rid, res in fabricator.derived_resources.items()
            },
            "artifacts": {
                aid: vars(art) for aid, art in fabricator.artifacts.items()
            },
            "telemetry": vars(fabricator.telemetry),
        }
        return json.dumps(payload, indent=2, sort_keys=True)

    @classmethod
    def export_package(
        cls,
        fabricator: UniversalProcessingFabricator,
        output_dir: Union[str, Path]
    ) -> Dict[str, str]:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        header_content = cls.generate_cpp_header()
        source_content = cls.generate_cpp_source()
        manifest_content = cls.generate_processing_manifest(fabricator)
        sig_hash = hashlib.sha256(manifest_content.encode("utf-8")).hexdigest()

        header_file = out_path / "UUAFAssetProcessingComponent.h"
        source_file = out_path / "UUAFAssetProcessingComponent.cpp"
        manifest_file = out_path / "uaf_processing_manifest.json"
        sig_file = out_path / "uaf_processing_manifest.sig"

        header_file.write_bytes(header_content.encode("utf-8"))
        source_file.write_bytes(source_content.encode("utf-8"))
        manifest_file.write_bytes(manifest_content.encode("utf-8"))
        sig_file.write_bytes(sig_hash.encode("utf-8"))

        return {
            "header": str(header_file),
            "source": str(source_file),
            "manifest": str(manifest_file),
            "signature": str(sig_file),
            "sha256": sig_hash,
        }
