"""
Abstract Base AI Provider and Provider Registry for IANIMATION.

Follows SOLID (Liskov Substitution Principle and Open/Closed Principle) to allow
seamless plug-and-play addition of local and cloud generative AI backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Type
from backend.core.models import StrictBaseModel


class BaseAIProvider(ABC):
    """
    Abstract base class for all generative AI model providers (Local and Cloud).
    """

    def __init__(self, name: str, is_cloud: bool = False) -> None:
        self.name: str = name
        self.is_cloud: bool = is_cloud

    @abstractmethod
    def health_check(self) -> bool:
        """Verify provider availability and connection status."""
        raise NotImplementedError


class ProviderRegistry:
    """
    Registry for managing available and active AI inference providers.
    """

    def __init__(self) -> None:
        self._providers: Dict[str, Dict[str, BaseAIProvider]] = {
            "audio": {},
            "image_to_3d": {},
            "rigging": {},
            "mocap": {},
            "neural": {},
        }

    def register(self, category: str, provider: BaseAIProvider) -> None:
        """Register a provider within a specific domain category."""
        if category not in self._providers:
            self._providers[category] = {}
        self._providers[category][provider.name] = provider

    def get_provider(self, category: str, name: Optional[str] = None) -> Optional[BaseAIProvider]:
        """Retrieve a registered provider, or the first available if name is None or 'auto'."""
        category_providers = self._providers.get(category, {})
        if not category_providers:
            return None
        if name and name != "auto" and name in category_providers:
            return category_providers[name]
        return next(iter(category_providers.values()), None)

    def list_providers(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """List all registered providers across categories."""
        if category:
            return {category: list(self._providers.get(category, {}).keys())}
        return {cat: list(provs.keys()) for cat, provs in self._providers.items()}


# Global singleton registry
provider_registry = ProviderRegistry()
