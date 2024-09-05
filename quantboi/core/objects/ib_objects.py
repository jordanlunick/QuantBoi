from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import datetime as dt
from enum import Enum
import QuantLib as ql
from typing import Optional, Union
import pandas as pd


from ib_async import Contract, Stock, Option


class IBContract(Contract):
    def __init__(self, 
                 **kwargs):
        Contract.__init__(
            self, **kwargs)


class IBStock(Stock):
    def __init__(self, 
                 symbol, 
                 exchange, 
                 currency, 
                 **kwargs):
        Stock.__init__(
            self, symbol=symbol, 
            exchange=exchange, 
            currency=currency, **kwargs)


class IBOption(Option):
    def __init__(self, 
                 symbol, 
                 lastTradeDateOrContractMonth, 
                 strike, 
                 right, 
                 exchange, 
                 multiplier, 
                 currency,
                 **kwargs):
        Option.__init__(
            self, symbol=symbol, 
            lastTradeDateOrContractMonth=lastTradeDateOrContractMonth, 
            strike=strike, right=right, exchange=exchange, 
            multiplier=multiplier, currency=currency, **kwargs)


@dataclass
class DataClassOption:
    symbol: str
    lastTradeDateOrContractMonth: str
    strike: float
    right: str
    exchange: str
    multiplier: str
    currency: str


kwargs = {
    'symbol': 'AAPL', 
    'lastTradeDateOrContractMonth': '20220318', 
    'strike': 145.0, 
    'right': 'C', 
    'exchange': 'SMART', 
    'multiplier': '100', 
    'currency': 'USD',
    #'secType': 'OPT'
}

test_contract = IBStock(**kwargs)

test = test_contract.create(**kwargs)

"""
test_option = IBOption(
    symbol = 'AAPL', 
    lastTradeDateOrContractMonth = '20220318', 
    strike = 145.0, 
    right = 'C', 
    exchange = 'SMART', 
    multiplier = '100', 
    currency = 'USD')
"""