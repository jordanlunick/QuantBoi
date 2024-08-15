from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class SecurityType:
    value: str
    description: str

STOCK = SecurityType(
    value='STK', description='Stock'
)

OPTION = SecurityType(
    value='OPT', description='Option'
)

FUTURE = SecurityType(
    value='FUT', description='Future'
)

CASH = SecurityType(
    value='CASH', description='Cash'
)

BOND = SecurityType(
    value='BOND', description='Bond'
)

COMMODITY = SecurityType(
    value='CMDTY', description='Commodity'
)

INDEX = SecurityType(
    value='IND', description='Index'
)

FOP = SecurityType(
    value='FOP', description='Future Option'
)


class SecType(Enum):
    Stock = STOCK
    Option = OPTION
    Future = FUTURE
    Cash = CASH
    Bond = BOND
    Commodity = COMMODITY
    Index = INDEX
    FutureOption = FOP    
