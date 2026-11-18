// Copyright (c) 2026 AOE Team. All Rights Reserved.

#include "UAFBridgeClient.h"

UUAFBridgeClient::UUAFBridgeClient()
	: bIsConnected(false)
{
}

bool UUAFBridgeClient::Connect(const FString& Endpoint, int32 Port)
{
	// Implementation connects to UAF Bridge endpoint via TCP / WebSocket
	bIsConnected = true;
	return true;
}

void UUAFBridgeClient::Disconnect()
{
	bIsConnected = false;
}

bool UUAFBridgeClient::IsConnected() const
{
	return bIsConnected;
}

void UUAFBridgeClient::SendHeartbeat()
{
	// Heartbeat implementation
}
