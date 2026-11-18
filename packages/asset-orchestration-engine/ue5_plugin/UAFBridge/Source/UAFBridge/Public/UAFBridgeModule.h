// Copyright (c) 2026 AOE Team. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FUAFBridgeModule : public IModuleInterface
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

	static inline FUAFBridgeModule& Get()
	{
		return FModuleManager::LoadModuleChecked<FUAFBridgeModule>("UAFBridge");
	}

	static inline bool IsAvailable()
	{
		return FModuleManager::Get().IsModuleLoaded("UAFBridge");
	}
};
