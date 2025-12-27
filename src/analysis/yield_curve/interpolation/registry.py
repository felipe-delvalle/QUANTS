from __future__ import annotations

from typing import Dict, List, Type

from .base import Interpolator


class InterpolatorRegistry:
    _interpolators: Dict[str, Type[Interpolator]] = {}

    @classmethod
    def register(cls, name: str, interpolator_class: Type[Interpolator]) -> None:
        cls._interpolators[name] = interpolator_class

    @classmethod
    def get(cls, name: str) -> Interpolator:
        if name not in cls._interpolators:
            raise ValueError(f"Unknown interpolator: {name}")
        return cls._interpolators[name]()  # type: ignore[call-arg]

    @classmethod
    def list_available(cls) -> List[str]:
        return list(cls._interpolators.keys())


