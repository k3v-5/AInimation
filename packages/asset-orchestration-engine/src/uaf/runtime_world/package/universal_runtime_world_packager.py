"""
Universal Runtime World Packager for Unreal Engine 5.
Complies with UAF-81.73 specification.
"""

from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Union

from uaf.runtime_world.models.definition import RuntimeWorld


class UniversalRuntimeWorldPackager:
    """Generates Unreal Engine 5 Subsystem C++ wrappers, manifest, and signed package for runtime worlds."""

    @staticmethod
    def generate_cpp_header() -> str:
        return """#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "UUAFRuntimeWorldSubsystem.generated.h"

UENUM(BlueprintType)
enum class EUAFWorldState : uint8
{
    Uninitialized UMETA(DisplayName = "Uninitialized"),
    Initializing UMETA(DisplayName = "Initializing"),
    Initialized UMETA(DisplayName = "Initialized"),
    Active UMETA(DisplayName = "Active"),
    Paused UMETA(DisplayName = "Paused"),
    Stopped UMETA(DisplayName = "Stopped"),
    Terminated UMETA(DisplayName = "Terminated")
};

UCLASS(DisplayName = "UAF Runtime World Subsystem")
class UAF_API UUAFRuntimeWorldSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    UUAFRuntimeWorldSubsystem();

    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = "UAF|RuntimeWorld")
    bool LoadWorldManifest(const FString& ManifestFilePath);

    UFUNCTION(BlueprintCallable, Category = "UAF|RuntimeWorld")
    EUAFWorldState GetWorldState() const;

    UFUNCTION(BlueprintCallable, Category = "UAF|RuntimeWorld")
    void TickSimulation(float DeltaTime);

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "UAF|RuntimeWorld")
    EUAFWorldState CurrentWorldState;
};
"""

    @staticmethod
    def generate_cpp_source() -> str:
        return """#include "UUAFRuntimeWorldSubsystem.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

UUAFRuntimeWorldSubsystem::UUAFRuntimeWorldSubsystem()
    : CurrentWorldState(EUAFWorldState::Uninitialized)
{
}

void UUAFRuntimeWorldSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    CurrentWorldState = EUAFWorldState::Initialized;
}

void UUAFRuntimeWorldSubsystem::Deinitialize()
{
    CurrentWorldState = EUAFWorldState::Terminated;
    Super::Deinitialize();
}

bool UUAFRuntimeWorldSubsystem::LoadWorldManifest(const FString& ManifestFilePath)
{
    if (!FPaths::FileExists(ManifestFilePath))
    {
        return false;
    }
    FString JsonContent;
    return FFileHelper::LoadFileToString(JsonContent, *ManifestFilePath);
}

EUAFWorldState UUAFRuntimeWorldSubsystem::GetWorldState() const
{
    return CurrentWorldState;
}

void UUAFRuntimeWorldSubsystem::TickSimulation(float DeltaTime)
{
    if (CurrentWorldState == EUAFWorldState::Active)
    {
        // Scheduled system execution step
    }
}
"""

    @staticmethod
    def generate_world_manifest(world: RuntimeWorld) -> str:
        data = world.to_dict()
        return json.dumps(data, indent=2, sort_keys=True)

    @classmethod
    def export_package(
        cls,
        world: RuntimeWorld,
        output_dir: Union[str, Path]
    ) -> Dict[str, str]:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        header_content = cls.generate_cpp_header()
        source_content = cls.generate_cpp_source()
        manifest_content = cls.generate_world_manifest(world)
        sig_hash = hashlib.sha256(manifest_content.encode("utf-8")).hexdigest()

        header_file = out_path / "UUAFRuntimeWorldSubsystem.h"
        source_file = out_path / "UUAFRuntimeWorldSubsystem.cpp"
        manifest_file = out_path / "uaf_runtime_world.json"
        sig_file = out_path / "uaf_runtime_world.sig"

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
