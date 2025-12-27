from typing import Dict, Type
from .base import Bootstrapper


class BootstrapperRegistry:
    """Registry for bootstrapping algorithms."""
    _registry: Dict[str, Type[Bootstrapper]] = {}

    @classmethod
    def register(cls, name: str, bootstrapper_class: Type[Bootstrapper]) -> None:
        cls._registry[name.lower()] = bootstrapper_class

    @classmethod
    def get(cls, name: str) -> Bootstrapper:
        bootstrapper_class = cls._registry.get(name.lower())
        if not bootstrapper_class:
            raise ValueError(f"Unknown bootstrapper: {name}. Available: {list(cls._registry.keys())}")
        return bootstrapper_class()

    @classmethod
    def list_available(cls) -> list:
        return list(cls._registry.keys())

