from .observer import Observer

# /// Library Imports /// #
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import datetime as dt
from enum import Enum
import QuantLib as ql
from typing import Optional, Union

import pickle

import ib_insync
import unittest
import timeit
import random

# /// Enum Classes /// #


# /// QuantLib Wrappers /// #
class SimpleQuote(ql.SimpleQuote, Observer):
    def __init__(self, value: float = 0.0):
        ql.SimpleQuote.__init__(self, value)
        Observer.__init__(self)
            
    def set_value(self, value: float):
        if self.value() != value:
            super().setValue(value)
            self.notify_observers()


class QuoteHandle(ql.QuoteHandle, Observer):
    def __init__(self, quote: SimpleQuote):
        ql.QuoteHandle.__init__(self, quote)
        Observer.__init__(self)
            

# /// Data Classes /// #
@dataclass
class Quote:
    value: float = field(default=0.0)
    quote: Optional[SimpleQuote] = field(init=False)

    def __post_init__(self):
        self.quote = SimpleQuote(self.value)

    def __getstate__(self) -> object:
        state = self.__dict__.copy()
        state['quote'] = self.quote.value()
        return state
    
    def __setstate__(self, state: object) -> None:
        self.__dict__.update(state)
        self.quote = SimpleQuote(self.quote)
    
    def __repr__(self) -> str:
        return f"Quote(value={self.value})"
    
    def update(self, value: float):
        self.quote.set_value(value)
        self.value = self.quote.value()

    def get(self) -> float:
        self.value = self.quote.value()
        return self.value


@dataclass
class Handle:
    quote: Quote
    handle: Optional[QuoteHandle] = field(init=False)
    value: float = field(init=False)

    def __post_init__(self):
        self.handle = QuoteHandle(self.quote.quote)
        self.value = self.handle.value()
        self.quote.quote.register_observer(self)
        self.update()

    def __getstate__(self) -> object:
        state = self.__dict__.copy()
        state['handle'] = self.handle.value()
        return state
    
    def __setstate__(self, state: object) -> None:
        self.__dict__.update(state)
        self.handle = QuoteHandle(self.quote.quote)

    def __repr__(self) -> str:
        return f"Handle(quote={self.quote})"

    def update(self):
        self.value = self.handle.value()

# /// Unit Test /// #
class Test(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.main()

    def test_quote(self):
        quote = Quote(value=100.0)
        handle = Handle(quote=quote)
        self.assertEqual(handle.value, 100.0)
        quote.update(200.0)
        self.assertEqual(handle.value, 200.0)

    def benchmark_quote_update(self, n: int = 100):
        quote_list = [Quote(value=round(random.uniform(100, 1000))) for _ in range(n)]
        handle_list = [Handle(quote=quote) for quote in quote_list]

        def update_quote():
            for quote in quote_list:
                old_value = quote.value
                new_value = old_value + round(random.uniform(1, 10))  # Simulate some update
                quote.update(new_value)
                print(f"Updated Quote from {old_value} to {new_value}")
            
            for quote, handle in zip(quote_list, handle_list):
                self.assertEqual(handle.value, quote.value)
                print(f"Handle value: {handle.value}, Quote value: {quote.value}")

        execution_time = timeit.timeit(update_quote, number=100)
        print(f"Benchmark: {execution_time} seconds for {n} updates")

    def main(self):
        self.test_quote()
        self.benchmark_quote_update()

if __name__ == '__main__':
    Test()

