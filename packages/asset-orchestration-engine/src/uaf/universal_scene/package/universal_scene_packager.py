"""
Universal Scene Assembly Unreal Engine 5 C++ Packager & Manifest Generator.
Complies with UAF-81.72 specification.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Union

from uaf.universal_scene.models.definition import Scene


class UniversalScenePackager:
    """Exports C++ headers, sources, and signed manifest files for Unreal Engine 5 scene assembly."""

    @staticmethod
    def generate_cpp_header() -> str:
        return """#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UUAFSceneAssemblyComponent.generated.h"

UENUM(BlueprintType)
enum class EUAFSceneBuildMode : uint8
{
    Development UMETA(DisplayName = "Development"),
    Shipping UMETA(DisplayName = "Shipping"),
    Preview UMETA(DisplayName = "Preview")
};

UCLASS(ClassGroup = (UAF), meta = (BlueprintSpawnableComponent))
class UAF_API UUAFSceneAssemblyComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UUAFSceneAssemblyComponent();

    UFUNCTION(BlueprintCallable, Category = "UAF|Scene")
    bool LoadSceneManifest(const FString& ManifestFilePath);

    UFUNCTION(BlueprintCallable, Category = "UAF|Scene")
    FString GetSceneFingerprint() const;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UAF|Scene")
    EUAFSceneBuildMode ActiveBuildMode;
};
"""

    @staticmethod
    def generate_cpp_source() -> str:
        return """#include "UUAFSceneAssemblyComponent.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

UUAFSceneAssemblyComponent::UUAFSceneAssemblyComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    ActiveBuildMode = EUAFSceneBuildMode::Development;
}

bool UUAFSceneAssemblyComponent::LoadSceneManifest(const FString& ManifestFilePath)
{
    if (!FPaths::FileExists(ManifestFilePath))
    {
        return false;
    }
    FString JsonString;
    return FFileHelper::LoadFileToString(JsonString, *ManifestFilePath);
}

FString UUAFSceneAssemblyComponent::GetSceneFingerprint() const
{
    return FString(TEXT("SCENE_FINGERPRINT_STUB"));
}
"""

    @staticmethod
    def generate_scene_manifest(scene: Scene) -> str:
        return scene.to_json()

    @classmethod
    def export_package(
        cls,
        scene: Scene,
        output_dir: Union[str, Path]
    ) -> Dict[str, str]:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        header_content = cls.generate_cpp_header()
        source_content = cls.generate_cpp_source()
        manifest_content = cls.generate_scene_manifest(scene)
        sig_hash = hashlib.sha256(manifest_content.encode("utf-8")).hexdigest()

        header_file = out_path / "UUAFSceneAssemblyComponent.h"
        source_file = out_path / "UUAFSceneAssemblyComponent.cpp"
        manifest_file = out_path / "uaf_scene_manifest.json"
        sig_file = out_path / "uaf_scene_manifest.sig"

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
