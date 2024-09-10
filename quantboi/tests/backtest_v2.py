import backtrader as bt
from ib_async import (
    IB, util, Stock, BarDataList)

import matplotlib.pyplot as plt
import numpy as np
from typing import Union

import pandas as pd


def get_historical_data():
    util.startLoop()
    ib = IB()
    ib.sleep(1)
    ib.connect('127.0.0.1', 7497, clientId=1)
    #print('connected to IB')


    contract = Stock('SPY', 'SMART', 'USD')
    ib.qualifyContracts(contract)
    ib.reqMarketDataType(4)
    ib.sleep(1)
    
    historical_data: BarDataList = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='10 Y',
        barSizeSetting='1 day', whatToShow='TRADES', useRTH=True)
    ib.disconnect()
    data = util.df(historical_data)
    data['datetime'] = pd.to_datetime(data['date'])
    data.set_index('datetime', inplace=True)
    data.drop(columns=['date', 'average', 'barCount'], inplace=True)
    return data


class MyIndicator(bt.Indicator):
    lines = ('sma', 'ema')

    def __init__(self):
        self.lines.sma = bt.indicators.MovingAverageSimple(self.data, period=20)
        self.lines.ema = bt.indicators.ExponentialMovingAverage(self.data, period=20)

    def next(self):
        self.lines.sma[0] = self.data.close[0]
        self.lines.ema[0] = self.data.close[0]


class MyStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.MovingAverageSimple(self.data, period=20)
        self.ema = bt.indicators.ExponentialMovingAverage(self.data, period=20)
        #self.myindicator = MyIndicator(self.data)
        self.buy_sig = bt.indicators.CrossOver(self.sma, self.ema)
        

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.datetime(0)
        print(f'{dt.isoformat()} {txt}')
    
    def next(self):
        if self.buy_sig > 0:
            self.log('BUY CREATE, %.2f' % self.data.close[0])
            self.buy()
        elif self.buy_sig < 0:
            self.log('SELL CREATE, %.2f' % self.data.close[0])
            self.sell()
        #self.log(f'Close, {self.data.close[0]}, SMA, {self.myindicator.lines.sma[0]}, EMA, {self.myindicator.lines.ema[0]}')

class MyAnalyzer(bt.Analyzer):
    def __init__(self):
        self.data_dict = {}

    def start(self):
        # Prepare to store all the data points
        self.data_dict['datetime'] = []
        self.data_dict['open'] = []
        self.data_dict['high'] = []
        self.data_dict['low'] = []
        self.data_dict['close'] = []
        self.data_dict['volume'] = []

        # Prepare to store all the indicator data points
        self.ind_dict = {}
        for indicator in self.strategy.getindicators():
            if indicator is not None:
                self.ind_dict[indicator.alias[0].lower()] = []

    def next(self):
        # Collect price data
        self.data_dict['datetime'].append(self.data.datetime.datetime(0))
        self.data_dict['open'].append(self.data.open[0])
        self.data_dict['high'].append(self.data.high[0])
        self.data_dict['low'].append(self.data.low[0])
        self.data_dict['close'].append(self.data.close[0])
        self.data_dict['volume'].append(self.data.volume[0])

        # Collect indicator data
        for indicator in self.strategy.getindicators():
            self.ind_dict[indicator.alias[0].lower()].append(indicator[0])

    def get_analysis(self):
        # Create a DataFrame to store the data
        df = pd.DataFrame(self.data_dict)
        df.set_index('datetime', inplace=True)

        # Add the indicator data to the DataFrame
        for key, value in self.ind_dict.items():
            df[key] = value
        return df

# Setup the cerebro engine
cerebro = bt.Cerebro()
cerebro.adddata(bt.feeds.PandasData(dataname=get_historical_data()))
cerebro.addstrategy(MyStrategy)
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days)
cerebro.addanalyzer(bt.analyzers.Transactions, _name='trans')


cerebro.addsizer(bt.sizers.PercentSizer, percents=50)


# Run the strategy
backtest_results = cerebro.run()
strategy_results = backtest_results[0]


# Get the results of the backtest
trade_analysis = strategy_results.analyzers.ta.get_analysis()
sharpe = strategy_results.analyzers.sharpe.get_analysis()
transactions = strategy_results.analyzers.trans.get_analysis()
import pprint as pp
pp.pprint(trade_analysis)
pp.pprint(sharpe)
pp.pp(transactions)

cerebro.plot(
    iplot=False)

