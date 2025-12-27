from typing import Dict, List, Tuple
import numpy as np
from .base import Bootstrapper
from ..compounding import SimpleCompounding


class BondBootstrapper(Bootstrapper):
    """Bootstrap a spot curve from coupon bond prices."""

    def bootstrap(self, market_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        if not market_data:
            raise ValueError("No bond data provided for bootstrapping")

        bonds = sorted(market_data, key=lambda x: x["maturity"])
        comp = SimpleCompounding()

        tenors = []
        rates = []

        for bond in bonds:
            maturity = float(bond["maturity"])
            coupon = float(bond.get("coupon", 0))
            price = float(bond["price"])
            frequency = int(bond.get("frequency", 2))

            # Simple bootstrap: solve for yield that prices the bond
            # For zero-coupon or short maturity, use simple formula
            if coupon == 0 or maturity <= 1.0:
                # Zero-coupon: rate = (FV/PV - 1) / T
                face_value = float(bond.get("face_value", 100))
                rate = (face_value / price - 1) / maturity
            else:
                # Approximate: use bond's YTM as spot rate
                # Full bootstrap would interpolate previously found rates
                face_value = float(bond.get("face_value", 100))
                coupon_payment = face_value * coupon / frequency
                periods = int(maturity * frequency)
                
                # Newton-Raphson to find rate
                rate = coupon  # Initial guess
                for _ in range(50):
                    pv = 0
                    dpv = 0
                    for n in range(1, periods + 1):
                        t = n / frequency
                        df = comp.discount_factor(rate, t)
                        cf = coupon_payment if n < periods else coupon_payment + face_value
                        pv += cf * df
                        dpv -= cf * t * df / (1 + rate * t)
                    
                    error = pv - price
                    if abs(error) < 1e-8:
                        break
                    if abs(dpv) > 1e-10:
                        rate -= error / dpv

            tenors.append(maturity)
            rates.append(rate)

        return np.array(tenors), np.array(rates)

