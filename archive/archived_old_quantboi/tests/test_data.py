from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import datetime as dt
from enum import Enum
import QuantLib as ql
from typing import Optional, Union
import pandas as pd
import numpy as np

def read_test_data(test_type: str = 'sample') -> pd.DataFrame:
    from archived_old_quantboi.core.data_management import Reader
    reader = Reader()
    
    if test_type == 'sample':
        test_data = reader.load_test_sample()
    elif test_type == 'dataset':
        test_data = reader.load_test_dataset()
    
    return test_data







@dataclass
class MarketDataTick:
    # Date and time of the observation
    observation_date: dt.datetime
    
    # OHLCV attributes
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    
    # Market book attributes
    bid_price: float
    bid_size: int
    ask_price: float
    ask_size: int

    implied_volatility: Optional[float] = field(default=None)
    

@dataclass
class Security:
    # Symbol attributes
    symbol: Optional[str] = field(default=None)
    symbol_underlying: Optional[str] = field(default=None)
    
    # Security attributes
    security_type: Optional[str] = field(default=None)
    security_expiry: Optional[dt.datetime] = field(default=None)
    security_right: Optional[str] = field(default=None)
    security_strike: Optional[float] = field(default=None)
        
    # Market data
    current_data: Optional[MarketDataTick] = field(default=None)
    historical_data: Optional[list[MarketDataTick]] = field(default=None)
    #historical_start_date: Optional[dt.datetime] = field(default=None)
    #historical_end_date: Optional[dt.datetime] = field(default=None)

    def set_current_data(self, observation_date: dt.datetime) -> None:
        try:
            for market_data in self.historical_data:
                if market_data.observation_date == observation_date:
                    self.current_data = market_data
                    break
                else:
                    self.current_data = None
                
            #print(f'Successfully set current data for {self.symbol} on {observation_date}')
        except IndexError:
            #raise ValueError(f'No data available for {self.symbol} on {observation_date}')
            #print(f'No data available for {self.symbol} on {observation_date}')
            pass

    
def gen_test_data_objects(test_type: str = 'sample') -> list[Security]:
    test_objects = []
    
    # Read test data
    df = read_test_data(test_type=test_type)
    
    # Get unique symbols
    unique_symbols = df['Symbol'].unique()
    symbol_data = df[df['Symbol'].isin(unique_symbols)][
        ['Symbol', 'Underlying Symbol', 
        'Strike Price', 'Expiry Date',
        'Ins. Type', 'Call/Put']]

    # Drop duplicates
    symbol_data.drop_duplicates(inplace=True)

    # Rename columns
    symbol_data.columns = [
        'symbol', 'symbol_underlying', 
        'security_strike', 'security_expiry',
        'security_type', 'security_right']

    # Vectorized operation to convert security type and right to human readable format
    symbol_data['security_type'] = np.where(
        symbol_data['security_type'] == 3, 'Stock', 'Option')
        
    symbol_data['security_right'] = np.where(
        symbol_data['security_right'] == 0, 'Call', 'Put')
    
    symbol_data['security_right'] = np.where(
        symbol_data['security_type'] == 'Stock', None, symbol_data['security_right'])

    # Vectorized operation to convert symbol_data to list of TestObject
    test_objects = symbol_data.apply(
        lambda x: Security(
            symbol=x['symbol'],
            symbol_underlying=x['symbol_underlying'],
            security_type=x['security_type'],
            security_expiry=x['security_expiry'],
            security_right=x['security_right'], 
            security_strike=x['security_strike']),
        axis=1
    ).tolist()

    # Add historical data to each TestObject by appending MarketData objects
    for i, test_object in enumerate(test_objects):
        symbol = test_object.symbol
        historical_data = df[df['Symbol'] == symbol][
            ['Date', 'Open Price', 'High Price', 
            'Low Price', 'Last Close Price', 'Volume', 
            'Bid Price', 'Bid Size', 'Ask Price', 'Ask Size',
            'Implied Volatility']]
        
        # Rename columns
        historical_data.columns = [
            'observation_date', 'open_price', 'high_price', 
            'low_price', 'close_price', 'volume', 
            'bid_price', 'bid_size', 'ask_price', 'ask_size',
            'implied_volatility']
        
        # Convert observation_date to datetime
        historical_data['observation_date'] = pd.to_datetime(historical_data['observation_date'])
        
        # Convert historical_data to list of MarketData
        test_objects[i].historical_data = historical_data.apply(
            lambda x: MarketDataTick(
                observation_date=x['observation_date'],
                open_price=x['open_price'],
                high_price=x['high_price'],
                low_price=x['low_price'],
                close_price=x['close_price'],
                volume=x['volume'],
                bid_price=x['bid_price'],
                bid_size=x['bid_size'],
                ask_price=x['ask_price'],
                ask_size=x['ask_size'],
                implied_volatility=x['implied_volatility']), 
            axis=1
        ).tolist()

    return test_objects


@dataclass
class TestDataBook:
    #test_objects: Optional[list[Security]] = field(default=None)
    test_type: Optional[str] = field(default='sample')
    stock_data: Optional[list[Security]] = field(default=None)
    option_data: Optional[list[Security]] = field(default=None)
    
    
    def __post_init__(self):
        #self.test_objects = gen_test_data_objects(test_type=self.test_type)
        self._init_test_objects()

    def _init_test_objects(self) -> None:
        test_objects = gen_test_data_objects(test_type=self.test_type)
        self.stock_data = [test_object for test_object in test_objects if test_object.security_type == 'Stock']
        self.option_data = [test_object for test_object in test_objects if test_object.security_type == 'Option']

    def set_current_data(self, observation_date: dt.datetime) -> None:
        # Set current data for stock objects
        for stock_object in self.stock_data:
            stock_object.set_current_data(observation_date=observation_date)
        
        # Set current data for option objects
        for option_object in self.option_data:
            option_object.set_current_data(observation_date=observation_date)
    
    def create_option_array(self) -> pd.DataFrame:
        # Find minimum and maximum observation dates
        min_observation_date = min(
            [min([market_data.observation_date for market_data in test_object.historical_data]) for test_object in self.option_data])

        self.set_current_data(observation_date=min_observation_date)

        # Get a sorted list of expiry dates with no duplicates
        expiry_dates = sorted([option.security_expiry for option in self.option_data])
        expiry_dates = [expiry_dates[i] for i in range(len(expiry_dates)) if i == 0 or expiry_dates[i] != expiry_dates[i-1]]

        # Get a sorted list of strike prices with no duplicates
        strike_prices = sorted([option.security_strike for option in self.option_data])
        strike_prices = [strike_prices[i] for i in range(len(strike_prices)) if i == 0 or strike_prices[i] != strike_prices[i-1]]

        # Create a 2-axis pd.DataFrame of expiry_dates and strike_prices
        # Expiry dates are rows and Strike prices are columns
        option_array = pd.DataFrame(
            index=expiry_dates, 
            columns=strike_prices, 
            data=0.0)

        # Fill the option_array with implied volatilities
        for option in self.option_data:
            expiry_date = option.security_expiry
            strike_price = option.security_strike
            try:
                implied_volatility = option.current_data.implied_volatility
            except AttributeError:
                implied_volatility = 0.0
            
            option_array.loc[expiry_date, strike_price] = implied_volatility

        return option_array

    
    def to_df(self) -> pd.DataFrame:
        data = []
        for option in self.option_data:
            data.append({
                'symbol': getattr(option, 'symbol', None),
                'symbol_underlying': getattr(option, 'symbol_underlying', None),
                'security_type': getattr(option, 'security_type', None),
                'security_expiry': getattr(option, 'security_expiry', None),
                'security_right': getattr(option, 'security_right', None),
                'security_strike': getattr(option, 'security_strike', None),
                'observation_date': getattr(getattr(option, 'current_data', None), 'observation_date', None),
                'close_price': getattr(getattr(option, 'current_data', None), 'close_price', None),
                'implied_volatility': getattr(getattr(option, 'current_data', None), 'implied_volatility', None)
                #'historical_data': getattr(test_object, 'historical_data', None)
            })
        return pd.DataFrame(data)


data_book = TestDataBook(test_type='dataset')
option_array = data_book.create_option_array()

"""
# Find minimum and maximum observation dates
min_observation_date = min(
    [min([market_data.observation_date for market_data in test_object.historical_data]) for test_object in data_book.option_data])

data_book.set_current_data(observation_date=min_observation_date)


# Get a sorted list of expiry dates with no duplicates
expiry_dates = sorted([option.security_expiry for option in data_book.option_data])
expiry_dates = [expiry_dates[i] for i in range(len(expiry_dates)) if i == 0 or expiry_dates[i] != expiry_dates[i-1]]

# Get a sorted list of strike prices with no duplicates
strike_prices = sorted([option.security_strike for option in data_book.option_data])
strike_prices = [strike_prices[i] for i in range(len(strike_prices)) if i == 0 or strike_prices[i] != strike_prices[i-1]]

# Create a 2-axis pd.DataFrame of expiry_dates and strike_prices
# Expiry dates are rows and Strike prices are columns
option_array = pd.DataFrame(
    #index=expiry_dates, 
    #columns=strike_prices, 
    index=strike_prices,
    columns=expiry_dates,
    data=0.0)

# Fill the option_array with implied volatilities
for option in data_book.option_data:
    expiry_date = option.security_expiry
    strike_price = option.security_strike
    try:
        implied_volatility = option.current_data.implied_volatility
    except AttributeError:
        implied_volatility = 0.0
    
    option_array.loc[strike_price, expiry_date] = implied_volatility

# calculate the average implied volatility for each expiry_date and drop if all values are 0
option_array = option_array.T
option_array['average_iv'] = option_array.mean(axis=1)
option_array = option_array[option_array['average_iv'] != 0.0]
option_array.drop(columns=['average_iv'], inplace=True)
option_array = option_array.T

# calculate the average implied volatility for each strike_price and drop if all values are 0
option_array['average_iv'] = option_array.mean(axis=1)
option_array = option_array[option_array['average_iv'] != 0.0]
option_array.drop(columns=['average_iv'], inplace=True)

# Smooth the implied_volatility values using a 2D interpolation
for column in option_array.columns:
    print(f'{column} before interpolation: {option_array[column].mean()}')
    option_array[column] = option_array[column].interpolate()
    print(f'{column} after interpolation: {option_array[column].mean()}')
"""