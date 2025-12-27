---
name: Interest Rate Curve Module
overview: Create a modular, extensible interest rate curve calculation system with clear separation of concerns. Uses strategy patterns and plugin-style interfaces for easy extension.
todos: []
---

# Interest Rate Curve Calculations Module (Modular & Scalable)

## Overview

Create a modular, extensible interest rate curve calculation system with clear separation of concerns. This is a foundational financial engineering module. The architecture uses strategy patterns and plugin-style interfaces to allow easy extension without modifying core code.

## Why This Feature

- **Core financial engineering**: Yield curves are fundamental to fixed income
- **Modular design**: Easy to extend with new interpolation methods, day count conventions, curve types
- **Scalable**: Plugin architecture allows adding swap curves, credit curves, volatility curves without core changes
- **Valuable**: Essential for bond pricing, derivatives, risk management

## Modular Architecture

### Directory Structure

```
src/analysis/yield_curve/
├── __init__.py                 # Public API exports
├── core/
│   ├── __init__.py
│   ├── curve.py                # Base YieldCurve class
│   └── curve_factory.py        # Factory for creating curves
├── interpolation/
│   ├── __init__.py
│   ├── base.py                 # Abstract Interpolator base class
│   ├── linear.py               # Linear interpolation
│   ├── cubic_spline.py         # Cubic spline interpolation
│   ├── log_linear.py           # Log-linear interpolation
│   └── registry.py             # Interpolator registry
├── day_count/
│   ├── __init__.py
│   ├── base.py                 # Abstract DayCount base class
│   ├── act365.py               # ACT/365 convention
│   ├── act360.py               # ACT/360 convention
│   ├── thirty360.py            # 30/360 convention
│   └── registry.py             # DayCount registry
├── compounding/
│   ├── __init__.py
│   ├── base.py                 # Abstract Compounding base class
│   ├── simple.py               # Simple compounding
│   ├── continuous.py           # Continuous compounding
│   └── registry.py             # Compounding registry
├── bootstrapping/
│   ├── __init__.py
│   ├── base.py                 # Abstract Bootstrapper base class
│   ├── bond_bootstrapper.py    # Bootstrap from bonds
│   ├── deposit_bootstrapper.py # Bootstrap from deposits
│   └── swap_bootstrapper.py    # Bootstrap from swaps (future)
└── utilities/
    ├── __init__.py
    ├── forward_rates.py         # Forward rate calculations
    ├── par_yields.py           # Par yield calculations
    └── curve_operations.py    # Common curve operations
```

## Core Components

### 1. Base Classes (Abstract Interfaces)

#### `Interpolator` (Abstract Base Class)

```python
from abc import ABC, abstractmethod
import numpy as np

class Interpolator(ABC):
    @abstractmethod
    def interpolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        """Interpolate rate for target tenor"""
        pass
    
    @abstractmethod
    def extrapolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        """Extrapolate rate beyond curve"""
        pass
```

#### `DayCount` (Abstract Base Class)

```python
from datetime import datetime

class DayCount(ABC):
    @abstractmethod
    def year_fraction(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate year fraction between dates"""
        pass
```

#### `Compounding` (Abstract Base Class)

```python
class Compounding(ABC):
    @abstractmethod
    def discount_factor(self, rate: float, tenor: float) -> float:
        """Calculate discount factor"""
        pass
    
    @abstractmethod
    def forward_rate(self, r1: float, t1: float, r2: float, t2: float) -> float:
        """Calculate forward rate"""
        pass
```

#### `Bootstrapper` (Abstract Base Class)

```python
from typing import List, Dict, Tuple

class Bootstrapper(ABC):
    @abstractmethod
    def bootstrap(self, market_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Bootstrap spot curve from market data. Returns (tenors, rates)"""
        pass
```

### 2. Core YieldCurve Class

#### `YieldCurve` (Main Class)

```python
class YieldCurve:
    def __init__(
        self,
        tenors: List[float],
        rates: List[float],
        interpolator: Optional[Interpolator] = None,
        day_count: Optional[DayCount] = None,
        compounding: Optional[Compounding] = None,
        curve_type: str = 'spot'
    ):
        # Initialize with strategy objects
        self.interpolator = interpolator or InterpolatorRegistry.get('linear')
        self.day_count = day_count or DayCountRegistry.get('ACT/365')
        self.compounding = compounding or CompoundingRegistry.get('simple')
        self.curve_type = curve_type
        self.tenors = np.array(tenors)
        self.rates = np.array(rates)
        # ... validation
    
    def spot_rate(self, tenor: float) -> float:
        """Get spot rate with interpolation"""
        return self.interpolator.interpolate(self.tenors, self.rates, tenor)
    
    def discount_factor(self, tenor: float) -> float:
        """Calculate discount factor"""
        rate = self.spot_rate(tenor)
        return self.compounding.discount_factor(rate, tenor)
    
    def forward_rate(self, t1: float, t2: float) -> float:
        """Calculate forward rate"""
        r1 = self.spot_rate(t1)
        r2 = self.spot_rate(t2)
        return self.compounding.forward_rate(r1, t1, r2, t2)
    
    def zero_coupon_price(self, tenor: float, face_value: float = 100.0) -> float:
        """Price zero coupon bond"""
        df = self.discount_factor(tenor)
        return face_value * df
```

### 3. Registry Pattern for Extensibility

#### Interpolator Registry

```python
class InterpolatorRegistry:
    _interpolators: Dict[str, Type[Interpolator]] = {}
    
    @classmethod
    def register(cls, name: str, interpolator_class: Type[Interpolator]):
        """Register new interpolator"""
        cls._interpolators[name] = interpolator_class
    
    @classmethod
    def get(cls, name: str) -> Interpolator:
        """Get interpolator instance"""
        if name not in cls._interpolators:
            raise ValueError(f"Unknown interpolator: {name}")
        return cls._interpolators[name]()
    
    @classmethod
    def list_available(cls) -> List[str]:
        """List all registered interpolators"""
        return list(cls._interpolators.keys())
```

Similar registries for `DayCountRegistry`, `CompoundingRegistry`, and `BootstrapperRegistry`.

### 4. Factory Pattern

#### Curve Factory

```python
class CurveFactory:
    @staticmethod
    def create_spot_curve(
        tenors: List[float],
        rates: List[float],
        interpolation: str = 'linear',
        day_count: str = 'ACT/365',
        compounding: str = 'simple'
    ) -> YieldCurve:
        """Factory method to create spot curve with specified components"""
        interpolator = InterpolatorRegistry.get(interpolation)
        day_count_obj = DayCountRegistry.get(day_count)
        compounding_obj = CompoundingRegistry.get(compounding)
        
        return YieldCurve(
            tenors=tenors,
            rates=rates,
            interpolator=interpolator,
            day_count=day_count_obj,
            compounding=compounding_obj,
            curve_type='spot'
        )
    
    @staticmethod
    def create_from_bonds(
        bonds: List[Dict],
        bootstrapper_type: str = 'bond',
        interpolation: str = 'cubic_spline',
        day_count: str = 'ACT/365',
        compounding: str = 'simple'
    ) -> YieldCurve:
        """Factory method to bootstrap curve from bonds"""
        bootstrapper = BootstrapperRegistry.get(bootstrapper_type)
        tenors, rates = bootstrapper.bootstrap(bonds)
        return CurveFactory.create_spot_curve(tenors, rates, interpolation, day_count, compounding)
```

## Implementation Details

### Interpolation Implementations

#### Linear Interpolation

```python
class LinearInterpolator(Interpolator):
    def interpolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        # Linear interpolation logic
        return np.interp(target_tenor, tenors, rates)
    
    def extrapolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        # Flat extrapolation (or linear)
        if target_tenor < tenors[0]:
            return rates[0]
        return rates[-1]
```

#### Cubic Spline Interpolation

```python
from scipy.interpolate import CubicSpline

class CubicSplineInterpolator(Interpolator):
    def __init__(self):
        self._spline = None
    
    def interpolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        if self._spline is None or not np.array_equal(self._spline.x, tenors):
            self._spline = CubicSpline(tenors, rates, bc_type='natural')
        return float(self._spline(target_tenor))
```

### Compounding Implementations

#### Simple Compounding

```python
class SimpleCompounding(Compounding):
    def discount_factor(self, rate: float, tenor: float) -> float:
        return 1.0 / (1.0 + rate * tenor)
    
    def forward_rate(self, r1: float, t1: float, r2: float, t2: float) -> float:
        df1 = self.discount_factor(r1, t1)
        df2 = self.discount_factor(r2, t2)
        return (df1 / df2 - 1.0) / (t2 - t1)
```

#### Continuous Compounding

```python
import numpy as np

class ContinuousCompounding(Compounding):
    def discount_factor(self, rate: float, tenor: float) -> float:
        return np.exp(-rate * tenor)
    
    def forward_rate(self, r1: float, t1: float, r2: float, t2: float) -> float:
        return (r2 * t2 - r1 * t1) / (t2 - t1)
```

### Bootstrapping Implementations

#### Bond Bootstrapper

```python
from scipy.optimize import fsolve

class BondBootstrapper(Bootstrapper):
    def bootstrap(self, bonds: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Bootstrap spot curve from coupon bonds.
        Bonds format: [{"maturity": float, "coupon": float, "price": float, "frequency": int}, ...]
        """
        bonds_sorted = sorted(bonds, key=lambda x: x["maturity"])
        tenors = []
        spot_rates = []
        
        for bond in bonds_sorted:
            maturity = bond["maturity"]
            # Solve for spot rate that prices bond correctly
            spot_rate = self._solve_spot_rate(bond, tenors, spot_rates)
            tenors.append(maturity)
            spot_rates.append(spot_rate)
        
        return np.array(tenors), np.array(spot_rates)
    
    def _solve_spot_rate(self, bond: Dict, known_tenors: List[float], known_rates: List[float]) -> float:
        # Bootstrapping logic using known spot rates for earlier cashflows
        # ... implementation
        pass
```

## Example Usage

### Basic Usage

```python
from src.analysis.yield_curve import YieldCurve, CurveFactory

# Create curve from market data
tenors = [0.25, 0.5, 1.0, 2.0, 5.0, 10.0]  # years
rates = [0.045, 0.047, 0.048, 0.050, 0.052, 0.055]  # 4.5%, 4.7%, etc.

curve = CurveFactory.create_spot_curve(
    tenors, rates,
    interpolation='cubic_spline',
    day_count='ACT/365',
    compounding='simple'
)

# Get spot rate for 3 years (interpolated)
spot_3y = curve.spot_rate(3.0)

# Get discount factor
df_3y = curve.discount_factor(3.0)

# Forward rate from 2y to 5y
forward_2y_5y = curve.forward_rate(2.0, 5.0)
```

### Bootstrapping from Bonds

```python
bonds = [
    {"maturity": 1.0, "coupon": 0.04, "price": 100.0, "frequency": 2},
    {"maturity": 2.0, "coupon": 0.045, "price": 100.5, "frequency": 2},
    {"maturity": 5.0, "coupon": 0.05, "price": 101.0, "frequency": 2},
]

spot_curve = CurveFactory.create_from_bonds(
    bonds,
    bootstrapper_type='bond',
    interpolation='cubic_spline'
)
```

### Adding Custom Interpolator (Extensibility Example)

```python
from src.analysis.yield_curve.interpolation import Interpolator, InterpolatorRegistry

class HermiteInterpolator(Interpolator):
    def interpolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        # Custom Hermite interpolation
        pass
    
    def extrapolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        # Custom extrapolation
        pass

# Register new interpolator
InterpolatorRegistry.register('hermite', HermiteInterpolator)

# Use it
curve = CurveFactory.create_spot_curve(tenors, rates, interpolation='hermite')
```

## Files to Create

### Core Module

1. `src/analysis/yield_curve/__init__.py` - Public API exports
2. `src/analysis/yield_curve/core/__init__.py`
3. `src/analysis/yield_curve/core/curve.py` - YieldCurve class (~150 lines)
4. `src/analysis/yield_curve/core/curve_factory.py` - Factory (~80 lines)

### Interpolation Module

5. `src/analysis/yield_curve/interpolation/__init__.py`
6. `src/analysis/yield_curve/interpolation/base.py` - Abstract base (~30 lines)
7. `src/analysis/yield_curve/interpolation/linear.py` - Linear (~40 lines)
8. `src/analysis/yield_curve/interpolation/cubic_spline.py` - Cubic spline (~50 lines)
9. `src/analysis/yield_curve/interpolation/log_linear.py` - Log-linear (~40 lines)
10. `src/analysis/yield_curve/interpolation/registry.py` - Registry (~40 lines)

### Day Count Module

11. `src/analysis/yield_curve/day_count/__init__.py`
12. `src/analysis/yield_curve/day_count/base.py` - Abstract base (~20 lines)
13. `src/analysis/yield_curve/day_count/act365.py` - ACT/365 (~30 lines)
14. `src/analysis/yield_curve/day_count/act360.py` - ACT/360 (~30 lines)
15. `src/analysis/yield_curve/day_count/thirty360.py` - 30/360 (~40 lines)
16. `src/analysis/yield_curve/day_count/registry.py` - Registry (~30 lines)

### Compounding Module

17. `src/analysis/yield_curve/compounding/__init__.py`
18. `src/analysis/yield_curve/compounding/base.py` - Abstract base (~25 lines)
19. `src/analysis/yield_curve/compounding/simple.py` - Simple (~40 lines)
20. `src/analysis/yield_curve/compounding/continuous.py` - Continuous (~40 lines)
21. `src/analysis/yield_curve/compounding/registry.py` - Registry (~30 lines)

### Bootstrapping Module

22. `src/analysis/yield_curve/bootstrapping/__init__.py`
23. `src/analysis/yield_curve/bootstrapping/base.py` - Abstract base (~25 lines)
24. `src/analysis/yield_curve/bootstrapping/bond_bootstrapper.py` - Bond bootstrap (~120 lines)
25. `src/analysis/yield_curve/bootstrapping/deposit_bootstrapper.py` - Deposit bootstrap (~80 lines)
26. `src/analysis/yield_curve/bootstrapping/registry.py` - Registry (~30 lines)

### Utilities Module

27. `src/analysis/yield_curve/utilities/__init__.py`
28. `src/analysis/yield_curve/utilities/forward_rates.py` - Forward rate utils (~60 lines)
29. `src/analysis/yield_curve/utilities/par_yields.py` - Par yield utils (~50 lines)
30. `src/analysis/yield_curve/utilities/curve_operations.py` - Common ops (~80 lines)

### Modified Files

31. `src/analysis/__init__.py` - Export YieldCurve classes

## Dependencies

- `numpy` - Already in requirements
- `scipy` - For cubic spline interpolation (add to requirements.txt if not present)

## Scalability Features

### 1. Easy Extension Points

- **New Interpolation**: Inherit from `Interpolator`, register with `InterpolatorRegistry`
- **New Day Count**: Inherit from `DayCount`, register with `DayCountRegistry`
- **New Compounding**: Inherit from `Compounding`, register with `CompoundingRegistry`
- **New Bootstrapper**: Inherit from `Bootstrapper`, register with `BootstrapperRegistry`

### 2. Future Curve Types

- **Swap Curves**: Create `SwapCurve` class inheriting from `YieldCurve`
- **Credit Curves**: Create `CreditCurve` class with spread calculations
- **Volatility Curves**: Create `VolatilityCurve` class for options pricing
- **Inflation Curves**: Create `InflationCurve` class for inflation-linked bonds

### 3. Advanced Features (Future)

- Curve fitting (Nelson-Siegel, Svensson models)
- Multi-curve framework (OIS, LIBOR, etc.)
- Curve calibration to market instruments
- Curve risk metrics (DV01, convexity)

## Mathematical Notes

- Support both simple and continuous compounding
- Handle day count conventions (ACT/365, ACT/360, 30/360)
- Validate input data (tenors sorted, rates positive, etc.)
- Handle edge cases (extrapolation beyond curve, interpolation methods)
- Bootstrapping algorithm: sequential solving starting from shortest maturity

## Time Estimate

- **Core architecture & base classes**: 90 minutes
- **Interpolation implementations**: 60 minutes
- **Day count implementations**: 45 minutes
- **Compounding implementations**: 30 minutes
- **Bootstrapping implementations**: 90 minutes
- **Utilities & factory**: 45 minutes
- **Testing & validation**: 60 minutes
- **Total**: ~6-7 hours

## Future Enhancements (Easy to Add)

- Swap curve construction
- Credit spread curves
- Volatility term structure
- Curve fitting models (Nelson-Siegel, Svensson)
- Multi-curve framework
- Integration with bond pricer
- Curve visualization utilities