from date import Date


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


# /// Enum Classes /// #
class OptionType(Enum):
    CALL = 1 # Previously: ql.Option.Call
    PUT = -1 # Previously: ql.Option.Put

class ExerciseType(Enum):
    AMERICAN = 1
    EUROPEAN = 2

# /// QuantLib Quote and Handle Wrappers /// #
class SimpleQuote(ql.SimpleQuote):
    def __init__(self, value: float = 0.0):
        super().__init__(value)
        self.observers = []
            
    def registerObserver(self, observer: ql.Observer):
        self.observers.append(observer)
    
    def unregisterObserver(self, observer: ql.Observer):
        self.observers.remove(observer)
    
    def setValue(self, value: float):
        super().setValue(value)
        for observer in self.observers:
            observer.update()

class QuoteHandle(ql.QuoteHandle):
    def __init__(self, quote: ql.Quote):
        super().__init__(quote)
        self.observers = []
    
    def registerObserver(self, observer: ql.Observer):
        self.observers.append(observer)
    
    def unregisterObserver(self, observer: ql.Observer):
        self.observers.remove(observer)
    
    def setValue(self, value: float):
        super().setValue(value)
        for observer in self.observers:
            observer.update()

# /// QuantLib Option Wrappers /// #
class VanillaPayoff(ql.PlainVanillaPayoff):
    def __init__(self, option_type: OptionType, strike_price: float):
        super().__init__(type=option_type.value, strike=strike_price)

class AmericanExercise(ql.AmericanExercise):
    def __init__(self, earliest_date: Date, exercise_date: Date):
        super().__init__(earliestDate=earliest_date.to_ql(), latestDate=exercise_date.to_ql())

class EuropeanExercise(ql.EuropeanExercise):
    def __init__(self, exercise_date: Date):
        super().__init__(date=exercise_date.to_ql())

class VanillaOption(ql.VanillaOption):
    def __init__(self, payoff: VanillaPayoff, exercise: ql.Exercise):
        super().__init__(payoff, exercise)





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
    
    def update(self, value: float = 0.0):
        self.value = value
        self.quote.setValue(value)

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
        self.quote.quote.registerObserver(self)
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
    

@dataclass
class Payoff:
    option_type: OptionType
    strike_price: float
    payoff: Optional[VanillaPayoff] = field(init=False)

    def __post_init__(self):
        self.payoff = VanillaPayoff(self.option_type, self.strike_price)

    def __getstate__(self) -> object:
        state = self.__dict__.copy()
        state['payoff'] = (self.option_type, self.strike_price)
        return state
    
    def __setstate__(self, state: object) -> None:
        self.__dict__.update(state)
        self.payoff = VanillaPayoff(self.option_type, self.strike_price)
    
    def __repr__(self) -> str:
        return f"Payoff(option_type={self.option_type}, strike_price={self.strike_price})"


@dataclass
class Exercise:
    exercise_type: ExerciseType
    earliest_date: Optional[Date] = None
    exercise_date: Optional[Date] = None
    exercise: Union[AmericanExercise, EuropeanExercise] = field(init=False)

    def __post_init__(self):
        if self.exercise_type == ExerciseType.AMERICAN:
            self.exercise = AmericanExercise(self.earliest_date, self.exercise_date)
        elif self.exercise_type == ExerciseType.EUROPEAN:
            self.exercise = EuropeanExercise(self.exercise_date)

    def __getstate__(self) -> object:
        state = self.__dict__.copy()
        if self.exercise_type == ExerciseType.AMERICAN:
            state['exercise'] = (self.earliest_date, self.exercise_date)
        elif self.exercise_type == ExerciseType.EUROPEAN:
            state['exercise'] = self.exercise_date
        return state
    
    def __setstate__(self, state: object) -> None:
        self.__dict__.update(state)
        if self.exercise_type == ExerciseType.AMERICAN:
            self.exercise = AmericanExercise(self.earliest_date, self.exercise_date)
        elif self.exercise_type == ExerciseType.EUROPEAN:
            self.exercise = EuropeanExercise(self.exercise_date)
    
    def __repr__(self) -> str:
        return f"Exercise(exercise_type={self.exercise_type})"


test = Quote(100)

pickle.dumps(test)

#test_date = Date(year=2024, month=8, day=14)

#option_type = OptionType.CALL
#strike_price = 100.0
#payoff = Payoff(option_type=option_type, strike_price=strike_price)

#exercise_type = ExerciseType.EUROPEAN
#exercise_date = Date(year=2024, month=8, day=14)
#exercise = Exercise(exercise_type=exercise_type, exercise_date=exercise_date)

#pickle.dumps(test_date)
#pickle.dumps(exercise_date)