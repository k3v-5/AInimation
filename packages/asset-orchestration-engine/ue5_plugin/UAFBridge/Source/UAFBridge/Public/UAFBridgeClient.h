// Copyright (c) 2026 AOE Team. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "UAFBridgeClient.generated.h"

UENUM(BlueprintType)
enum class EUAFBridgeAuthority : uint8
{
	UAFAuthoritative UMETA(DisplayName = "UAF Authoritative"),
	UEAuthoritative  UMETA(DisplayName = "UE Authoritative"),
	Shared           UMETA(DisplayName = "Shared")
};

/**
 * Main client actor/object that handles TCP/WebSocket connection to UAF LiveLink core.
 */
UCLASS(BlueprintType, Blueprintable)
class UAFBRIDGE_API UUAFBridgeClient : public UObject
{
	GENERATED_BODY()

public:
	UUAFBridgeClient();

	UFUNCTION(BlueprintCallable, Category = "UAF|Bridge")
	bool Connect(const FString& Endpoint, int32 Port);

	UFUNCTION(BlueprintCallable, Category = "UAF|Bridge")
	void Disconnect();

	UFUNCTION(BlueprintPure, Category = "UAF|Bridge")
	bool IsConnected() const;

	UFUNCTION(BlueprintCallable, Category = "UAF|Bridge")
	void SendHeartbeat();

private:
	bool bIsConnected;
};
