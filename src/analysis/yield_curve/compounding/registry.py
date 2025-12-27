from __future__ import annotations

from typing import Dict, List, Type

from .base import Compounding


class CompoundingRegistry:
    _registry: Dict[str, Type[Compounding]] = {}

    @classmethod
    def register(cls, name: str, comp_class: Type[Compounding]) -> None:
        cls._registry[name] = comp_class

    @classmethod
    def get(cls, name: str) -> Compounding:
        if name not in cls._registry:
            raise ValueError(f"Unknown compounding method: {name}")
        return cls._registry[name]()  # type: ignore[call-arg]

    @classmethod
    def list_available(cls) -> List[str]:
        return list(cls._registry.keys())


