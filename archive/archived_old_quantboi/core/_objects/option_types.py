from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class OptionType:
    int_value: int
    str_values: list[str]
    description: str

CALL = OptionType(
    int_value=1, 
    str_values=['C', 'Call'], 
    description='Call Option'
)

PUT = OptionType(
    int_value=-1, 
    str_values=['P', 'Put'], 
    description='Put Option'
)


class OptType(Enum):
    Call = CALL
    Put = PUT