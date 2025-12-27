from __future__ import annotations

from typing import Dict, List, Type

from .base import Bootstrapper


class BootstrapperRegistry:
    _registry: Dict[str, Type[Bootstrapper]] = {}

    @classmethod
    def register(cls, name: str, bootstrapper_class: Type[Bootstrapper]) -> None:
        cls._registry[name] = bootstrapper_class

    @classmethod
    def get(cls, name: str) -> Bootstrapper:
        if name not in cls._registry:
            raise ValueError(f"Unknown bootstrapper: {name}")
        return cls._registry[name]()  # type: ignore[call-arg]

    @classmethod
    def list_available(cls) -> List[str]:
        return list(cls._registry.keys())


