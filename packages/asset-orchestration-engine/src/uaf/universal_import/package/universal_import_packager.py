"""
UAF-81.70: Universal Asset Import Packager.
Exports C++ Unreal Engine 5 Import Pipeline integration,
import manifests, and cryptographic verification signatures.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Union

from uaf.universal_import.engine.universal_import_fabricator import (
    UniversalImportFabricator,
)


class UniversalImportPackager:
    """
    Authoritative packager exporting the import pipeline to Unreal Engine 5.
    """

    @staticmethod
    def generate_cpp_header() -> str:
        return '''#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UUAFAssetImportComponent.generated.h"

UENUM(BlueprintType)
enum class EUAFImportJobState : uint8
{
    Queued UMETA(DisplayName = "Queued"),
    Preparing UMETA(DisplayName = "Preparing"),
    Running UMETA(DisplayName = "Running"),
    Completed UMETA(DisplayName = "Completed"),
    Failed UMETA(DisplayName = "Failed"),
    Cancelled UMETA(DisplayName = "Cancelled")
};

USTRUCT(BlueprintType)
struct FUAFImportJobInfo
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UAF|Import")
    FString JobId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UAF|Import")
    FString SourcePath;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UAF|Import")
    EUAFImportJobState State;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UAF|Import")
    float Progress = 0.0f;
};

UCLASS(ClassGroup = (UAF), meta = (BlueprintSpawnableComponent))
class UAF_API UUAFAssetImportComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UUAFAssetImportComponent();

    UFUNCTION(BlueprintCallable, Category = "UAF|Import")
    void LoadImportManifest(const FString& ManifestJson);

    UFUNCTION(BlueprintCallable, Category = "UAF|Import")
    FString SubmitImportJob(const FString& SourcePath, const FString& ProfileId, int32 Priority);

    UFUNCTION(BlueprintCallable, Category = "UAF|Import")
    bool CancelImportJob(const FString& JobId);

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "UAF|Import")
    int32 TotalActiveJobs = 0;
};
'''

    @staticmethod
    def generate_cpp_source() -> str:
        return '''#include "UUAFAssetImportComponent.h"

UUAFAssetImportComponent::UUAFAssetImportComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UUAFAssetImportComponent::LoadImportManifest(const FString& ManifestJson)
{
    UE_LOG(LogTemp, Log, TEXT("UAF Import: Loading import manifest..."));
}

FString UUAFAssetImportComponent::SubmitImportJob(const FString& SourcePath, const FString& ProfileId, int32 Priority)
{
    UE_LOG(LogTemp, Log, TEXT("UAF Import: Submitting job for '%s' using profile '%s'"), *SourcePath, *ProfileId);
    return FString::Printf(TEXT("job_%llu"), FPlatformTime::Cycles64());
}

bool UUAFAssetImportComponent::CancelImportJob(const FString& JobId)
{
    UE_LOG(LogTemp, Log, TEXT("UAF Import: Cancelling job '%s'"), *JobId);
    return true;
}
'''

    @classmethod
    def generate_import_manifest(cls, fabricator: UniversalImportFabricator) -> str:
        jobs_data = [j.to_dict() for j in fabricator.jobs.values()]
        sources_data = [s.to_dict() for s in fabricator.sources.values()]
        profiles_data = [p.to_dict() for p in fabricator.profiles.values()]

        manifest_data = {
            "schema_version": "1.0.0",
            "module": "UAF-81.70-ASSET-IMPORT-PIPELINE",
            "total_jobs": len(jobs_data),
            "jobs": jobs_data,
            "sources": sources_data,
            "profiles": profiles_data,
            "telemetry": fabricator.telemetry.__dict__,
        }
        return json.dumps(manifest_data, indent=2, sort_keys=True)

    @classmethod
    def export_package(
        cls,
        fabricator: UniversalImportFabricator,
        output_dir: Union[str, Path]
    ) -> Dict[str, str]:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        header_path = out_path / "UUAFAssetImportComponent.h"
        source_path = out_path / "UUAFAssetImportComponent.cpp"
        manifest_path = out_path / "uaf_import_manifest.json"
        sig_path = out_path / "uaf_import_manifest.sig"

        header_content = cls.generate_cpp_header()
        source_content = cls.generate_cpp_source()
        manifest_json = cls.generate_import_manifest(fabricator)
        manifest_bytes = manifest_json.encode("utf-8")
        sha256_hash = hashlib.sha256(manifest_bytes).hexdigest()

        header_path.write_bytes(header_content.encode("utf-8"))
        source_path.write_bytes(source_content.encode("utf-8"))
        manifest_path.write_bytes(manifest_bytes)
        sig_path.write_bytes(sha256_hash.encode("utf-8"))

        return {
            "header": str(header_path),
            "source": str(source_path),
            "manifest": str(manifest_path),
            "signature": str(sig_path),
            "sha256": sha256_hash,
        }
