from .base import Interpolator
from .linear import LinearInterpolator
from .cubic_spline import CubicSplineInterpolator
from .log_linear import LogLinearInterpolator
from .registry import InterpolatorRegistry

# Register default implementations
InterpolatorRegistry.register("linear", LinearInterpolator)
InterpolatorRegistry.register("cubic_spline", CubicSplineInterpolator)
InterpolatorRegistry.register("log_linear", LogLinearInterpolator)

__all__ = [
    "Interpolator",
    "LinearInterpolator",
    "CubicSplineInterpolator",
    "LogLinearInterpolator",
    "InterpolatorRegistry",
]


