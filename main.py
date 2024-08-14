import ib_insync as ib
import QuantLib as ql
from typing import List, NamedTuple, Optional


from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class OptionOBject(Base, ib.Option):
    __tablename__ = 'options'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False)
    lastTradeDateOrContractMonth = Column(String, nullable=False)
    strike = Column(Float, nullable=False)
    right = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    multiplier = Column(String, nullable=False)
    currency = Column(String, nullable=False)

    def __init__(self, symbol: str = '', lastTradeDateOrContractMonth: str = '',
                 strike: float = 0.0, right: str = '', exchange: str = '',
                 multiplier: str = '', currency: str = '', **kwargs):
        super().__init__(symbol=symbol, lastTradeDateOrContractMonth=lastTradeDateOrContractMonth,
                         strike=strike, right=right, exchange=exchange,
                         multiplier=multiplier, currency=currency, **kwargs)

    def __repr__(self):
        return f"Option(symbol={self.symbol}, lastTradeDateOrContractMonth={self.lastTradeDateOrContractMonth}, " \
               f"strike={self.strike}, right={self.right}, exchange={self.exchange}, multiplier={self.multiplier}, " \
               f"currency={self.currency})"
    
    def _to_quantlib(self):
        return ql.EuropeanOption(ql.PlainVanillaPayoff(ql.Option.Call if self.right == 'C' else ql.Option.Put, self.strike),
                                 ql.EuropeanExercise(self.lastTradeDateOrContractMonth))


option = OptionOBject(
    symbol='AAPL', lastTradeDateOrContractMonth='20210716', strike=145.0, 
    right='C', exchange='SMART', multiplier='100', currency='USD')

test = option._to_quantlib()