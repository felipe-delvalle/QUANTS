from typing import Dict, Type
from .base import Interpolator


class InterpolatorRegistry:
    """Registry for interpolation strategies."""
    _registry: Dict[str, Type[Interpolator]] = {}

    @classmethod
    def register(cls, name: str, interpolator_class: Type[Interpolator]) -> None:
        cls._registry[name.lower()] = interpolator_class

    @classmethod
    def get(cls, name: str) -> Interpolator:
        interpolator_class = cls._registry.get(name.lower())
        if not interpolator_class:
            raise ValueError(f"Unknown interpolator: {name}. Available: {list(cls._registry.keys())}")
        return interpolator_class()

    @classmethod
    def list_available(cls) -> list:
        return list(cls._registry.keys())

