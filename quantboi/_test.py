
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





import logging
import QuantLib as ql
from typing import List

#logging.basicConfig(level=logging.INFO)

class Subject:
    def __init__(self):
        self._observers: List[ql.Observer] = []

    def register_observer(self, observer: ql.Observer) -> None:
        """Register an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
            #logging.info(f"Observer {observer} registered.")
        else:
            pass#logging.warning(f"Observer {observer} is already registered.")
            

    def unregister_observer(self, observer: ql.Observer) -> None:
        """Unregister an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
            #logging.info(f"Observer {observer} unregistered.")
        else:
            pass#logging.warning(f"Observer {observer} is not registered.")
            

    def notify_observers(self) -> None:
        """Notify all registered observers."""
        #logging.info(f"Notifying {len(self._observers)} observers.")
        for observer in self._observers:
            observer.update()


class Observer(ql.Observer):
    def __init__(self):
        def callback():
            self.update()
        super().__init__(callback)

    def update(self) -> None:
        """Override the update method with custom logic."""
        #logging.info("ConcreteObserver has been notified!")


# /// QuantLib Wrappers /// #
class SimpleQuote(ql.SimpleQuote, Subject):
    def __init__(self, value: float = 0.0):
        ql.SimpleQuote.__init__(self, value)
        Subject.__init__(self)
            
    def set_value(self, value: float):
        #print(f"Setting quote value to {value}")
        if self.value() != value:
            self.setValue(value)
            self.notify_observers()
            #print(f"Quote value is now {self.value()}")


class QuoteHandle(ql.QuoteHandle, Subject):
    def __init__(self, quote: SimpleQuote):
        ql.QuoteHandle.__init__(self, quote)
        Subject.__init__(self)
            

# /// Data Classes /// #
@dataclass
class Quote:
    value: float = field(default=0.0)
    quote: Optional[SimpleQuote] = field(init=False)

    def __post_init__(self):
        self.quote = SimpleQuote(self.value)
        #self.quote.register_observer(self)

    def __getstate__(self) -> object:
        state = self.__dict__.copy()
        state['quote'] = self.quote.value()
        return state
    
    def __setstate__(self, state: object) -> None:
        self.__dict__.update(state)
        self.quote = SimpleQuote(self.quote)
        #self.quote.register_observer(self)
    
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



# Initialize quote and handle objects
quote = Quote(100.0)
handle = Handle(quote)

# Should print 100.0
print(handle.value)

# Should update and print 200.0
quote.update(200.0)
print(handle.value)



"""
# initialize a quote object
quote = Quote(100.0)

# should print 100.0
print(quote.value)

# should update and print 200.0
quote.update(200)
print(quote.value)
"""