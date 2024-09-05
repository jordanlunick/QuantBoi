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
class MarketData:
    observation_date: dt.datetime
    #symbol: str
    #ohlcv: OHLCV
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int

    #market_book: MarketBook
    bid_price: float
    bid_size: int
    ask_price: float
    ask_size: int

@dataclass
class Symbol:
    security_type: str
    symbol: str
    symbol_underlying: Optional[str] = field(default=None)

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
class TestDataObject:
    symbol: Symbol
    instrument: Optional[Union[Stock, Option]] = field(default=None)
    market_data: Optional[list[MarketData]] = field(default=None)


def read_test_data(test_type: str = 'sample') -> pd.DataFrame:
    from quantboi.core.data_management import Reader
    reader = Reader()
    
    if test_type == 'sample':
        test_data = reader.load_test_sample()
    elif test_type == 'dataset':
        test_data = reader.load_test_dataset()
    
    return test_data

def create_test_data_object(
        symbol: Symbol, 
        instrument: Union[Stock, Option], 
        market_data: MarketData
        ) -> TestDataObject:
    
    return TestDataObject(
        symbol=symbol,
        instrument=instrument,
        market_data=market_data
    )


def load_test_data(test_type: str = 'sample') -> dict:
    df = read_test_data(test_type=test_type)
    test_data = {
        'stock': [],
        'option': []
    }
    length = len(df)
    print(f'Processing test data for {length} securities')
    row_num = 0
    for i in range(len(df)):
        row = df.iloc[i]
                
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
                dividend_yield=0,
                price=row['Last Price'],
                volatility=row['Implied Volatility']
            )
        elif symbol.security_type == 'Option':
            instrument = Option(
                expiry_date=row['Expiry Date'],
                implied_volatility=row['Implied Volatility'],
                right='Call' if row['Call/Put'] == 0 else 'Put',
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
        
        # Create MarketData object
        observation_date = row['Date']
        market_data = MarketData(
            observation_date=observation_date,
            ohlcv=ohlcv,
            market_book=market_book
        )

        # Check if symbol already exists in test_data
        if symbol.symbol in [s.symbol for s in test_data[symbol.security_type.lower()]]:
            # Find the existing object and append market_data
            for obj in test_data[symbol.security_type.lower()]:
                if obj.symbol.symbol == symbol.symbol:
                    obj.market_data.append(market_data)
                    break
        else:
            # Create TestDataObject object
            security = create_test_data_object(
                symbol=symbol,
                instrument=instrument,
                market_data=[market_data]  # Wrap market_data in a list
            )

            # Append to test_data dictionary based on security type
            if symbol.security_type == 'Stock':
                test_data['stock'].append(security)
            elif symbol.security_type == 'Option':
                test_data['option'].append(security)
            else:
                raise ValueError('Invalid security type')
        
        row_num += 1
        print(f'Processed {row_num} of {length} securities - {symbol.symbol} - {symbol.security_type}')
        
    return test_data

df = read_test_data(test_type='dataset')



# Find list of unique symbols
symbol_list = df['Symbol'].unique()
symbol_dict = {}
for symbol in symbol_list:
    symbol_dict[symbol] = df[df['Symbol'] == symbol]

