from typing import Dict, Type
from .base import Compounding


class CompoundingRegistry:
    """Registry for compounding methods."""
    _registry: Dict[str, Type[Compounding]] = {}

    @classmethod
    def register(cls, name: str, compounding_class: Type[Compounding]) -> None:
        cls._registry[name.lower()] = compounding_class

    @classmethod
    def get(cls, name: str) -> Compounding:
        compounding_class = cls._registry.get(name.lower())
        if not compounding_class:
            raise ValueError(f"Unknown compounding: {name}. Available: {list(cls._registry.keys())}")
        return compounding_class()

    @classmethod
    def list_available(cls) -> list:
        return list(cls._registry.keys())

