from .base import Bootstrapper
from .bond_bootstrapper import BondBootstrapper
from .deposit_bootstrapper import DepositBootstrapper
from .registry import BootstrapperRegistry

# Register default bootstrappers
BootstrapperRegistry.register("bond", BondBootstrapper)
BootstrapperRegistry.register("deposit", DepositBootstrapper)

__all__ = ["Bootstrapper", "BondBootstrapper", "DepositBootstrapper", "BootstrapperRegistry"]

