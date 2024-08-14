# /// Library Imports /// #
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Union
import QuantLib as ql
import ib_insync
import unittest

# /// Enum Classes /// #
class SecType(Enum):
    """
    Security type enum class
    
    Args:
        STK (str): Stock
        OPT (str): Option
        FUT (str): Future
        CASH (str): Cash
        BOND (str): Bond
        CMDTY (str): Commodity
        IND (str): Index
        FOP (str): Future option
    """
    STOCK = 'STK'
    OPTION = 'OPT'
    FUTURE = 'FUT'
    CASH = 'CASH'
    BOND = 'BOND'
    COMMODITY = 'CMDTY'
    INDEX = 'IND'
    FOP = 'FOP'

class OptType(Enum):
    """
    Option type enum class
    
    Args:
        CALL (str): Call option
        PUT (str): Put option
    """
    CALL = 'C'
    PUT = 'P'

class DateObject(ql.Date):
    def __init__(self, date: str):
        """
        Date object
        
        Args:
            date (str): Date in string format
        """
        ql.Date.__init__(self, date)
        
    def __str__(self):
        return self.ISO()
    
    def __repr__(self):
        return self.ISO()




@dataclass
class Contract:
    """
    Contract class
    
    Args:
        symbol (str): Symbol of the contract (or its underlying)
        security_type (SecType): Type of the security
        contract_id (int): Contract ID
        local_symbol (str): Local symbol of the contract (for options this will be OCC symbol)
        exchange (str): Exchange where the contract is traded
        currency (str): Currency of the contract
        multiplier (str): Multiplier of the contract
        last_trade_date (str): Last trade date of the contract
        strike (float): Strike price of the contract
        Option_type (OptType): Type of the option
    """
    security_type: Optional[SecType] = None
    symbol: Optional[str] = None
    contract_id: Optional[int] = None
    local_symbol: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None
    multiplier: Optional[str] = None
    currency: Optional[str] = None
    last_trade_date: Optional[str] = None
    strike: Optional[float] = None
    option_type: Optional[OptType] = None

class Stock(Contract):
    def __init__(
            self, symbol: str, exchange: str, currency: str):
        """
        Stock contract
        
        Args:
            symbol (str): Symbol of the stock
            exchange (str): Exchange where the stock is traded
            currency (str): Currency of the stock
        """
        Contract.__init__(
            self, security_type=SecType.STOCK, symbol=symbol, 
            exchange=exchange, currency=currency)


class Option(Contract):
    def __init__(
            self, symbol: str, option_type: OptType, strike: float, last_trade_date: str, 
            multiplier: str, local_symbol: Optional[str] = None):
        """
        Option contract
        
        Args:
            symbol (str): Symbol of the underlying
            option_type (OptType): Type of the option (Call or Put)
            strike (float): Strike price of the option
            last_trade_date (str): Last trade date of the option
            multiplier (str): Multiplier of the option
            local_symbol (str): Local symbol of the option
        """
        Contract.__init__(
            self, security_type=SecType.OPTION, symbol=symbol, option_type=option_type,
            strike=strike, last_trade_date=last_trade_date, multiplier=multiplier, 
            local_symbol=local_symbol)
        
class UnitTest(unittest.TestCase):
    def test_option(self):
        option = Option(
            symbol='AAPL', option_type=OptType.CALL, strike=145.0, last_trade_date='20210716',
            multiplier='100', local_symbol='AAPL_0716C145')
        self.assertEqual(option.symbol, 'AAPL')
        self.assertEqual(option.option_type, OptType.CALL)
        self.assertEqual(option.strike, 145.0)
        self.assertEqual(option.last_trade_date, '20210716')
        self.assertEqual(option.multiplier, '100')
        self.assertEqual(option.local_symbol, 'AAPL_0716C145')
        self.assertEqual(option.security_type, SecType.OPTION)

    def test_stock(self):
        stock = Stock(symbol='AAPL', exchange='SMART', currency='USD')
        self.assertEqual(stock.symbol, 'AAPL')
        self.assertEqual(stock.exchange, 'SMART')
        self.assertEqual(stock.currency, 'USD')
        self.assertEqual(stock.security_type, SecType.STOCK)
    
    def test_objects(self):
        self.test_option()
        self.test_stock()

if __name__ == '__main__':
    UnitTest().test_objects()

spot_price = 100
spot_quote = ql.SimpleQuote(spot_price)
spot_handle = ql.QuoteHandle(spot_quote)
print(spot_handle.value())

for i in range(10):
    spot_quote.setValue(spot_price + i)
    print(spot_handle.value())