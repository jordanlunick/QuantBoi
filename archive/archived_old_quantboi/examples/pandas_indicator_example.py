from dataclasses import dataclass
from ib_async import (
    IB, util, Contract, Stock, BarDataList)
import pandas as pd
import numpy as np
from typing import Union
import time
from functools import wraps


def benchmark(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Function '{func.__name__}' executed in {duration:.4f} seconds")
        return result
    return wrapper

@benchmark
def get_historical_data() -> Union[Contract, BarDataList]:
    util.startLoop()
    ib = IB()
    ib.sleep(1)
    ib.connect('127.0.0.1', 7497, clientId=1)
    contract = Stock('SPY', 'SMART', 'USD')
    ib.qualifyContracts(contract)
    ib.reqMarketDataType(4)
    ib.sleep(1)
    
    historical_data: BarDataList = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='10 D',
        barSizeSetting='1 min', whatToShow='TRADES', useRTH=True)
    ib.disconnect()
    return contract, historical_data



class Main:
    def __init__(self):
        self.contract: Contract = None
        self.market_data: BarDataList = None
        self.indicators = None
        
    def get_historical_data(self):
        contract, market_data = get_historical_data()
        self.contract = contract
        self.market_data = market_data
        
    def calculate_sma(self, window_size: int = 3):
        
        
        self.market_data['SMA'] = self.market_data['close'].rolling(window=window_size).mean()


# Example OHLCV DataFrame (Open, High, Low, Close, Volume)
data = {
    'Open': [100, 102, 104, 103, 105],
    'High': [102, 105, 106, 107, 109],
    'Low': [99, 101, 103, 102, 104],
    'Close': [101, 104, 105, 106, 108],
    'Volume': [1000, 1100, 1200, 1300, 1400]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Define the moving average window
window_size = 3

# Calculate the Simple Moving Average (SMA) on the 'Close' column
df['SMA'] = df['Close'].rolling(window=window_size).mean()

# Display the DataFrame with the SMA column
print(df)
