# /// Library Imports /// #
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import datetime as dt
from enum import Enum
import QuantLib as ql
from typing import Optional

import ib_insync
import unittest


@dataclass
class Quote:
    quote: Optional[ql.SimpleQuote] = field(default=None)
    value: Optional[float] = field(default=None)

    def set_value(self, value: float):
        if self.quote is None:
            self.quote = ql.SimpleQuote(value)
        else:
            self.quote.setValue(value)

    def get_value(self) -> ql.SimpleQuote:
        return self.quote

