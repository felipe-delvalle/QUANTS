"""Interest Rate Index Registry - Defines standard market indexes (SOFR, LIBOR, EURIBOR, etc.)"""

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class IndexType(Enum):
    """Types of interest rate indexes"""
    OIS = "OIS"
    IBOR = "IBOR"
    TREASURY = "TREASURY"
    SWAP = "SWAP"


@dataclass
class InterestRateIndex:
    """Represents an interest rate index (e.g., SOFR, LIBOR, EURIBOR)"""
    code: str
    name: str
    currency: str
    index_type: IndexType
    day_count: str = "ACT/360"
    compounding: str = "simple"
    fixing_frequency: str = "daily"
    description: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.code} ({self.currency})"


class IndexRegistry:
    """Registry of standard interest rate indexes"""
    _indexes: Dict[str, InterestRateIndex] = {}

    @classmethod
    def register(cls, code: str, index: InterestRateIndex) -> None:
        cls._indexes[code.upper()] = index

    @classmethod
    def get(cls, code: str) -> Optional[InterestRateIndex]:
        return cls._indexes.get(code.upper())

    @classmethod
    def list_all(cls) -> Dict[str, InterestRateIndex]:
        return cls._indexes.copy()

    @classmethod
    def initialize_defaults(cls) -> None:
        """Initialize standard market indexes"""
        # US Dollar Indexes
        cls.register("SOFR", InterestRateIndex(
            code="SOFR", name="Secured Overnight Financing Rate", currency="USD",
            index_type=IndexType.OIS, day_count="ACT/360", compounding="simple",
            fixing_frequency="daily", description="US Dollar overnight rate, replacement for LIBOR"
        ))
        cls.register("USD-LIBOR-1M", InterestRateIndex(
            code="USD-LIBOR-1M", name="US Dollar LIBOR 1 Month", currency="USD",
            index_type=IndexType.IBOR, day_count="ACT/360", compounding="simple",
            fixing_frequency="monthly", description="US Dollar 1-month interbank offered rate"
        ))
        cls.register("USD-LIBOR-3M", InterestRateIndex(
            code="USD-LIBOR-3M", name="US Dollar LIBOR 3 Month", currency="USD",
            index_type=IndexType.IBOR, day_count="ACT/360", compounding="simple",
            fixing_frequency="quarterly", description="US Dollar 3-month interbank offered rate"
        ))
        cls.register("USD-LIBOR-6M", InterestRateIndex(
            code="USD-LIBOR-6M", name="US Dollar LIBOR 6 Month", currency="USD",
            index_type=IndexType.IBOR, day_count="ACT/360", compounding="simple",
            fixing_frequency="semi-annual", description="US Dollar 6-month interbank offered rate"
        ))
        # Euro Indexes
        cls.register("EURIBOR-1M", InterestRateIndex(
            code="EURIBOR-1M", name="Euro Interbank Offered Rate 1 Month", currency="EUR",
            index_type=IndexType.IBOR, day_count="ACT/360", compounding="simple",
            fixing_frequency="monthly", description="Euro 1-month interbank offered rate"
        ))
        cls.register("EURIBOR-3M", InterestRateIndex(
            code="EURIBOR-3M", name="Euro Interbank Offered Rate 3 Month", currency="EUR",
            index_type=IndexType.IBOR, day_count="ACT/360", compounding="simple",
            fixing_frequency="quarterly", description="Euro 3-month interbank offered rate"
        ))
        cls.register("EURIBOR-6M", InterestRateIndex(
            code="EURIBOR-6M", name="Euro Interbank Offered Rate 6 Month", currency="EUR",
            index_type=IndexType.IBOR, day_count="ACT/360", compounding="simple",
            fixing_frequency="semi-annual", description="Euro 6-month interbank offered rate"
        ))
        cls.register("ESTR", InterestRateIndex(
            code="ESTR", name="Euro Short-Term Rate", currency="EUR",
            index_type=IndexType.OIS, day_count="ACT/360", compounding="simple",
            fixing_frequency="daily", description="Euro overnight rate, replacement for EONIA"
        ))
        # British Pound Indexes
        cls.register("SONIA", InterestRateIndex(
            code="SONIA", name="Sterling Overnight Index Average", currency="GBP",
            index_type=IndexType.OIS, day_count="ACT/365", compounding="simple",
            fixing_frequency="daily", description="British Pound overnight rate"
        ))
        cls.register("GBP-LIBOR-3M", InterestRateIndex(
            code="GBP-LIBOR-3M", name="British Pound LIBOR 3 Month", currency="GBP",
            index_type=IndexType.IBOR, day_count="ACT/365", compounding="simple",
            fixing_frequency="quarterly", description="British Pound 3-month interbank offered rate"
        ))
        # Treasury-based
        cls.register("USD-TREASURY", InterestRateIndex(
            code="USD-TREASURY", name="US Treasury Constant Maturity", currency="USD",
            index_type=IndexType.TREASURY, day_count="ACT/365", compounding="simple",
            fixing_frequency="daily", description="US Treasury constant maturity rates"
        ))


# Initialize default indexes
IndexRegistry.initialize_defaults()

