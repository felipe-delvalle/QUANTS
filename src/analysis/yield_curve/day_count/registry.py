from __future__ import annotations

from typing import Dict, List, Type

from .base import DayCount


class DayCountRegistry:
    _registry: Dict[str, Type[DayCount]] = {}

    @classmethod
    def register(cls, name: str, dc_class: Type[DayCount]) -> None:
        cls._registry[name] = dc_class

    @classmethod
    def get(cls, name: str) -> DayCount:
        if name not in cls._registry:
            raise ValueError(f"Unknown day count convention: {name}")
        return cls._registry[name]()  # type: ignore[call-arg]

    @classmethod
    def list_available(cls) -> List[str]:
        return list(cls._registry.keys())


