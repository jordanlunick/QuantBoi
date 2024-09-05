import pandas as pd

from ib_async import IB, Ticker

from IPython.display import display, clear_output

import time

def read_test_data(test_type: str = 'sample') -> pd.DataFrame:
    from quantboi.core.data_management import Reader
    reader = Reader()
    
    if test_type == 'sample':
        test_data = reader.load_test_sample()
    elif test_type == 'dataset':
        test_data = reader.load_test_dataset()
    
    return test_data

def spoof_update_ticker(ticker: Ticker, row: pd.Series) -> None:
    ticker.time = row['Date']
    ticker.bid = row['Bid Price']
    ticker.bidSize = row['Bid Size']
    ticker.ask = row['Ask Price']
    ticker.askSize = row['Ask Size']
    ticker.last = row['Last Price']
    ticker.volume = row['Volume']
    ticker.open = row['Open Price']
    ticker.high = row['High Price']
    ticker.low = row['Low Price']
    ticker.close = row['Last Close Price']

    ticker.updateEvent.emit(ticker)    

def on_tick_handler(ticker: Ticker) -> None:
    #print(f"{ticker.contract} at {ticker.time}. Price: {ticker.close}")
    clear_output(wait=True)
    print_str = f'{ticker.contract} at {ticker.time}. Price: {ticker.close}'
    print(print_str)


class TestClass:
    def __init__(
        self, 
        ticker,
        test_data
    ) -> None:
        self.ticker = ticker
        self.test_data = test_data

    def set_row(self, row: int) -> None:
        spoof_update_ticker(self.ticker, self.test_data.loc[row])


ib = IB()
ticker = Ticker('TD')

test_data = read_test_data('dataset')
test_data = test_data[test_data['Symbol'] == 'TD'].reset_index(drop=True)

# Set up the event handler and when the event is emitted, the handler is called
ticker.updateEvent += on_tick_handler

testclass = TestClass(ticker, test_data)
for i in range(len(testclass.test_data)):
    testclass.set_row(i)
    time.sleep(0.1)
