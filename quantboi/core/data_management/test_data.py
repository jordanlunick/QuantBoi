from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import datetime as dt
from enum import Enum
import QuantLib as ql
from typing import Optional, Union
import pandas as pd


@dataclass
class OHLCV:
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int

@dataclass
class MarketBook:
    bid_price: float
    bid_size: int
    ask_price: float
    ask_size: int

@dataclass
class Symbol:
    security_type: str
    symbol: str
    symbol_underlying: str = None

@dataclass
class Stock:
    dividend_yield: float
    price: float
    volatility: float

@dataclass
class Option:
    expiry_date: dt.datetime
    implied_volatility: float
    right: str
    strike: float

@dataclass
class TestDataStructure:
    observation_date: dt.datetime
    symbol: Symbol
    instrument: Union[Stock, Option]
    ohlcv: OHLCV
    market_book: MarketBook


def read_test_data(test_type: str = 'sample') -> pd.DataFrame:
    from quantboi.core.data import Data
    data = Data()
    
    if test_type == 'sample':
        test_data = data.reader.load_test_sample()
    elif test_type == 'dataset':
        test_data = data.reader.load_test_dataset()
    
    return test_data

def create_test_data_structure(
        observation_date: dt.datetime, symbol: Symbol, 
        instrument: Union[Stock, Option], 
        ohlcv: OHLCV, market_book: MarketBook
        ) -> TestDataStructure:
    
    return TestDataStructure(
        observation_date=observation_date,
        symbol=symbol,
        instrument=instrument,
        ohlcv=ohlcv,
        market_book=market_book
    )

def load_test_data(test_type: str = 'dataset') -> dict:
    df = read_test_data(test_type=test_type)
    test_data = {
        'stock': [],
        'option': []
    }
    for i in range(len(df)):
        row = df.iloc[i]
        
        # Determine observation date
        observation_date = row['Date']
        
        # Determine security type
        if row['Ins. Type'] == 3:
            security_type = 'Stock'
        elif row['Ins. Type'] == 0:
            security_type = 'Option'
        else:
            raise ValueError('Invalid security type')
        # Determine symbol and underlying symbol
        symbol = row['Symbol']
        symbol_underlying = row['Underlying Symbol']
        
        # Create symbol object
        symbol = Symbol(
            security_type=security_type, 
            symbol=symbol, 
            symbol_underlying=symbol_underlying)

        # Create instrument object
        if symbol.security_type == 'Stock':
            instrument = Stock(
                #dividend_yield=row['dividend_yield'], no dividend info
                dividend_yield=0,
                price=row['Last Price'],
                volatility=row['Implied Volatility']
            )
        elif symbol.security_type == 'Option':
            instrument = Option(
                expiry_date=row['Expiry Date'],
                implied_volatility=row['Implied Volatility'],
                
                # if row['Call/Put'] == 0:
                #     right = 'Call'
                # elif row['Call/Put'] == 1:
                #     right = 'Put'
                right = 'Call' if row['Call/Put'] == 0 else 'Put',
                strike=row['Strike Price']
            )
        else:
            raise ValueError('Invalid security type')

        # Create OHLCV and MarketBook objects
        ohlcv = OHLCV(
            open_price=row['Open Price'],
            high_price=row['High Price'],
            low_price=row['Low Price'],
            close_price=row['Last Price'],
            volume=row['Volume']
        )
        market_book = MarketBook(
            bid_price=row['Bid Price'],
            bid_size=row['Bid Size'],
            ask_price=row['Ask Price'],
            ask_size=row['Ask Size']
        )
        # Create TestDataStructure object
        security = create_test_data_structure(
            observation_date=observation_date,
            symbol=symbol,
            instrument=instrument,
            ohlcv=ohlcv,
            market_book=market_book
        )

        # Append to test_data dictionary based on security type
        if symbol.security_type == 'Stock':
            test_data['stock'].append(security)
        elif symbol.security_type == 'Option':
            test_data['option'].append(security)
        else:
            raise ValueError('Invalid security type')
    
    return test_data

