from typing import Dict, Type
from .base import DayCount


class DayCountRegistry:
    """Registry for day count conventions."""
    _registry: Dict[str, Type[DayCount]] = {}

    @classmethod
    def register(cls, name: str, day_count_class: Type[DayCount]) -> None:
        cls._registry[name.upper()] = day_count_class

    @classmethod
    def get(cls, name: str) -> DayCount:
        day_count_class = cls._registry.get(name.upper())
        if not day_count_class:
            raise ValueError(f"Unknown day count: {name}. Available: {list(cls._registry.keys())}")
        return day_count_class()

    @classmethod
    def list_available(cls) -> list:
        return list(cls._registry.keys())

