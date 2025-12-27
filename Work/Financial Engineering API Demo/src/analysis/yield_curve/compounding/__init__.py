from .base import Compounding
from .simple import SimpleCompounding
from .continuous import ContinuousCompounding
from .registry import CompoundingRegistry

# Register default compounding methods
CompoundingRegistry.register("simple", SimpleCompounding)
CompoundingRegistry.register("continuous", ContinuousCompounding)

__all__ = ["Compounding", "SimpleCompounding", "ContinuousCompounding", "CompoundingRegistry"]

