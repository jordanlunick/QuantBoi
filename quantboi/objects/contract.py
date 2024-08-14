from .base import Quote
from .date import Date


# /// Library Imports /// #
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import datetime as dt
from enum import Enum
import QuantLib as ql
from typing import Optional

import ib_insync
import unittest

# /// Enum Classes /// #
class SecurityType(Enum):
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


class OptionType(Enum):
    CALL = 1 # Previously: ql.Option.Call
    PUT = -1 # Previously: ql.Option.Put


# /// Helper Functions /// #
def create_option_symbol_string(
        stock_symbol: str, exercise_date: Date, 
        option_type: OptionType, strike_price: float) -> str:
    """
    Create a local symbol string for an option contract in the OCC string format (21 characters):
    Root Symbol (six characters), Expiration Date (six digits in the format yymmdd), 
    Option Type (C or P) and Strike Price (eight digits, including decimals)
    
    Args:
        stock_symbol (str): Symbol of the underlying stock
        exercise_date (Date): Exercise date of the option
        option_type (OptionType): Type of the option
        strike_price (float): Strike price of the option
    """
    # Format the stock symbol to six characters
    if len(stock_symbol) < 6:
        root_symbol_str = stock_symbol.ljust(6, ' ')
    elif len(stock_symbol) == 6:
        root_symbol_str = stock_symbol
    else:
        raise ValueError('Stock symbol must be less than or equal to six characters.')
    
    # Format the expiration date to six digits in the format 'yymmdd'
    expiration_date_str = exercise_date.to_string()
    
    # Format the option type to 'C' or 'P'
    option_type_str = 'C' if option_type == OptionType.CALL else 'P'
    
    # Format the strike price to eight digits, including decimals
    strike_price_int = int(strike_price * 1000)
    strike_price_str = f'{strike_price_int:08d}'
    
    # Combine the formatted strings to create the local symbol
    local_symbol_str = f'{root_symbol_str}{expiration_date_str}{option_type_str}{strike_price_str}'
    if len(local_symbol_str) != 21:
        raise ValueError('Local symbol must be 21 characters long.')
    elif len(local_symbol_str) == 21:
        return local_symbol_str
    else:
        raise ValueError('Local symbol creation failed.') 
    

@dataclass
class Contract:
    """
    Contract class
    
    Args:
        symbol (str): Symbol of the contract (or its underlying)
        security_type (SecurityType): Type of the security
        security_id (int): Contract ID
        local_symbol (str): Local symbol of the contract (for options this will be OCC symbol)
        exchange (str): Exchange where the contract is traded
        currency (str): Currency of the contract
        multiplier (str): Multiplier of the contract
        last_trade_date (str): Last trade date of the contract
        strike (float): Strike price of the contract
        Option_type (OptionType): Type of the option
    """
    # /// Contract Attributes ///
    security_id: Optional[int] = field(default=None)
    security_type: Optional[SecurityType] = field(default=None) # Security type (Stock, Option, Future, etc.)
    exchange: Optional[str] = field(default=None) # Exchange where the contract is traded
    currency: Optional[str] = field(default=None) # Currency of the contract
    multiplier: Optional[str] = field(default=None) # Contract multiplier (e.g. 100 for options)
    volatility: Optional[float] = field(default=None)

    # /// Symbol Attributes ///
    symbol: Optional[str] = field(default=None) # Symbol of the contract (or its underlying)
    local_symbol: Optional[str] = field(default=None) # Local symbol of the contract (for options this will be OCC symbol)

    # /// Date Objects ///
    exercise_date: Optional[Date] = field(default=None) # Exercise date of the contract
    last_trade_date: Optional[Date] = field(default=None) # Last trade date of the contract
    
    # /// Option Attributes ///
    option_type: Optional[OptionType] = field(default=None) # Option type (Call=1 or Put=-1)
    strike_price: Optional[float] = field(default=None)

    # /// QuantLib Objects ///
    ql_quote: Optional[ql.SimpleQuote] = field(default=None) # Quote for the current contract
    ql_handle: Optional[ql.QuoteHandle] = field(default=None) # Quote handle for the underlying contract
    ql_option: Optional[ql.VanillaOption] = field(default=None) # Option object for the contract

    def set_ql_quote(self, value: float):
        """
        Set the QuantLib quote for the contract
        
        Args:
            value (float): Quote value
        """
        if self.ql_quote is None:
            self.ql_quote = ql.SimpleQuote(value)
        else:
            self.ql_quote.setValue(value)

    def set_ql_handle(self, ql_quote: ql.SimpleQuote):
        """
        Set the QuantLib quote handle for the contract. 
        Handles are used to link quotes to other objects.
        
        Args:
            ql_quote (ql.SimpleQuote): Quote object
        """
        if self.ql_handle is None:
            self.ql_handle = ql.QuoteHandle(ql_quote)


class Stock(Contract):
    def __init__(
            self, symbol: str, exchange: str, currency: str):
        Contract.__init__(
            self, security_type=SecurityType.STOCK, symbol=symbol, 
            exchange=exchange, currency=currency)


class Option(Contract):
    def __init__(
            self, stock: Stock,
            option_type: int, strike_price: float, 
            exercise_date: Date, multiplier: str):
        """
        Option contract class. Inherits from the Contract class. 
        Initializes an option contract and its QuantLib objects.
        
        Args:
            symbol (str): Symbol of the contract (or its underlying)
            option_type (OptionType): Type of the option
            strike_price (float): Strike price of the option
            exercise_date (Date): Exercise date of the option
            multiplier (str): Multiplier of the option
            local_symbol (str): Local symbol of the contract (for options this will be OCC symbol)
        """
        local_symbol = create_option_symbol_string(
            stock_symbol=stock.symbol, exercise_date=exercise_date, 
            option_type=option_type, strike_price=strike_price)
        
        Contract.__init__(
            self, security_type=SecurityType.OPTION, symbol=stock.symbol, option_type=option_type,
            strike_price=strike_price, exercise_date=exercise_date, multiplier=multiplier, 
            local_symbol=local_symbol)
        
        payoff = ql.PlainVanillaPayoff(self.option_type, self.strike_price)
        exercise = ql.EuropeanExercise(self.exercise_date.to_ql())
        self.ql_option = ql.VanillaOption(payoff, exercise)
