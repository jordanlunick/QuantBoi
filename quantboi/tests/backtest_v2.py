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


class LinearRegression(bt.Indicator):
    lines = (
        'linreg',
    )
    params = (
        ('period', 10), # number of periods to look back
    )
    plotinfo = dict(
        plot=True,
        subplot=False, # Keep the indicator in a separate subplot
    )
    plotlines = dict(
        linreg=dict(
            _name='linreg', 
            #_method='line',
            alpha=0.50,
            #width=1.0,
            linestyle='--',
            #color='green'
        ),
    )

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        # Gather the necessary data points for the linear regression
        y = np.array(self.data.close.get(size=self.p.period))
        
        # Ensure that we have enough valid data points
        if len(y) < self.p.period:
            return
        
        # Create the X matrix
        X = np.column_stack((np.arange(len(y)), np.ones(len(y))))

        # Calculate the coefficients of the linear regression
        try:
            slope, intercept = np.linalg.lstsq(X, y, rcond=None)[0]
        except np.linalg.LinAlgError:
            slope = 0
            intercept = 0

        # Calculate the linear regression value for T + 1
        self.lines.linreg[0] = (slope * (self.p.period - 0) + intercept)


class LinearRegressionDelta(bt.Indicator):
    lines = (
        'linreg_delta',
    )
    params = (
        ('period', 10),
    )
    plotlines = dict(
        linreg_delta=dict(
            _name='linreg_delta', 
            _method='bar',
            #alpha=0.50,
            #width=1.0,
            #color='green'
        ),
    )

    def __init__(self):
        self.addminperiod(self.params.period)
        self.linreg = LinearRegression(self.data, period=self.params.period)

    def next(self):
        # Ensure that we have enough valid data points
        if len(self.linreg.lines.linreg) < self.p.period:
            return
        
        self.lines.linreg_delta[0] = self.linreg.lines.linreg[0] - self.linreg.lines.linreg[-1]


class PriceDelta(bt.Indicator):
    lines = (
        'price_delta',
    )
    plotlines = dict(
        price_delta=dict(
            _name='price_delta', 
            _method='bar',
            #alpha=0.50,
            #width=1.0,
            #color='green'
        ),
    )

    def next(self):
        self.lines.price_delta[0] = self.data.close[0] - self.data.close[-1]
        #self.lines.price_delta[0] = self.data.close[0] - self.data.open[0]


class EntrySignal(bt.Indicator):
    lines = (
        'entry_signal',
    )
    params = (
        ('period', 10),
    )

    def __init__(self):
        self.addminperiod(self.params.period)
        self.lines.linreg_delta = LinearRegressionDelta(self.data).lines.linreg_delta
        self.lines.price_delta = PriceDelta(self.data).lines.price_delta

    def next(self):
        self.lines.entry_signal[0] = 0
        
        # Ensure that we have enough valid data points
        if len(self.data.close) < self.params.period + 1:
            return

        # Initialize the variables
        linreg_delta_current_0 = self.lines.linreg_delta[0] # Current linear regression delta        
        linreg_delta_previous_1 = self.lines.linreg_delta[-1] # Previous linear regression delta
        price_delta_current = self.lines.price_delta[0] # Current price delta

        # Check the conditions for trade signals
        if linreg_delta_current_0 and linreg_delta_previous_1 > 0:# and linreg_delta_previous_2 > 0:
            # If the linear regression delta is positive
            if price_delta_current < 0:
                # If the current close price is less than the previous close price
                self.lines.entry_signal[0] = 1
        elif linreg_delta_current_0 and linreg_delta_previous_1 < 0:#  and linreg_delta_previous_2 < 0:
            # If the linear regression delta is negative
            if price_delta_current > 0:
                # If the current close price is greater than the previous close price
                self.lines.entry_signal[0] = -1


        
class ExitSignal(bt.Indicator):
    lines = (
        'exit_signal',
    )
    params = (
        ('period', 10),
    )

    def __init__(self):
        self.addminperiod(self.params.period)
        self.lines.linreg_delta = LinearRegressionDelta(self.data).lines.linreg_delta
        self.lines.price_delta = PriceDelta(self.data).lines.price_delta

    def next(self):
        self.lines.exit_signal[0] = 0

        # Ensure that we have enough valid data points
        if len(self.data.close) < self.params.period + 1:
            return

        # Initialize the variables
        linreg_delta_current_0 = self.lines.linreg_delta[0] # Current linear regression delta        
        linreg_delta_previous_1 = self.lines.linreg_delta[-1] # Previous linear regression delta

        





class TradeSignal(bt.Indicator):
    lines = (
        'trade_signal',)
    params = (
        ('period', 10),
    )
    plotlines = dict(
        trade_signal=dict(
            _name='trade_signal', 
            #_method='bar',
            #alpha=0.50,
            #width=1.0,
            #color='green'
        ),
    )

    def __init__(self):
        self.addminperiod(self.params.period)
        self.lines.linreg = LinearRegression(self.data).lines.linreg
        self.lines.linreg_delta = LinearRegressionDelta(self.data).lines.linreg_delta
        self.lines.price_delta = PriceDelta(self.data).lines.price_delta

    def next(self):
        # Ensure that we have enough valid data points
        self.lines.trade_signal[0] = 0
        if len(self.data.close) < self.params.period + 1:
            return #self.lines.trade_signal[0] = 0

        # Initialize the variables
        linreg_delta_current_0 = self.lines.linreg_delta[0] # Current linear regression delta        
        linreg_delta_previous_1 = self.lines.linreg_delta[-1] # Previous linear regression delta
        linreg_delta_previous_2 = self.lines.linreg_delta[-2] # Previous linear regression delta
        price_delta_current = self.lines.price_delta[0] # Current price delta


        # Check if there is a potential reversal in the trade signal
        if self.lines.trade_signal[-1] == 1:
            # If the previous trade signal was long
            if linreg_delta_current_0 and linreg_delta_previous_1 < 0:
                # If the previous linear regression delta is negative
                self.lines.trade_signal[0] = -1
            else:
                # If the previous linear regression delta is positive
                self.lines.trade_signal[0] = 1
        elif self.lines.trade_signal[-1] == -1:
            # If the previous trade signal was short
            if linreg_delta_current_0 and linreg_delta_previous_1 > 0:
                # If the previous linear regression delta is positive
                self.lines.trade_signal[0] = 1
            else:
                # If the previous linear regression delta is negative
                self.lines.trade_signal[0] = -1

        # Check the conditions for trade signals
        if linreg_delta_current_0 and linreg_delta_previous_1 > 0:# and linreg_delta_previous_2 > 0:
            # If the linear regression delta is positive
            if price_delta_current < 0:
                # If the current close price is less than the previous close price
                self.lines.trade_signal[0] = 1
        elif linreg_delta_current_0 and linreg_delta_previous_1 < 0:#  and linreg_delta_previous_2 < 0:
            # If the linear regression delta is negative
            if price_delta_current > 0:
                # If the current close price is greater than the previous close price
                self.lines.trade_signal[0] = -1
        else:
            # Do not trade if none of the conditions are met
            self.lines.trade_signal[0] = 0
        

class MyStrategy(bt.Strategy):
    params = (
        ('period', 21), # number of periods to look back
        ('last_entry_tol_perc', 0.9), # tolerance for the last entry price
        ('trailpercent', 0.005), # trailing stop percentage
    )


    def __init__(self):
        # Initialize the line indicators
        self.lines.linreg = LinearRegression(self.data, period=self.params.period).lines.linreg
        self.lines.linreg_delta = LinearRegressionDelta(self.data, period=self.params.period).lines.linreg_delta
        self.lines.price_delta = PriceDelta(self.data).lines.price_delta
        self.lines.entry_signal = EntrySignal(self.data, period=self.params.period).lines.entry_signal
        self.lines.exit_signal = ExitSignal(self.data, period=self.params.period).lines.exit_signal
        self.lines.trade_signal = TradeSignal(self.data, period=self.params.period).lines.trade_signal
        self.last_entry = 0
        

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.datetime(0)
        print(f'{dt.isoformat()} {txt}')

    def check_trade_signal(self):
        trade_signal = 0

        # Ensure that we have enough valid data points
        if len(self.data.close) < self.params.period + 1:
            return

        # Initialize the variables        
        linreg_delta_current = self.lines.linreg_delta[0] # Current linear regression delta
        linreg_delta_previous = self.lines.linreg_delta[-1] # Previous linear regression delta
        price_delta_current = self.lines.price_delta[0] # Current price delta

        # Check the conditions for trade signals
        if linreg_delta_current and linreg_delta_previous > 0:
            # If the linear regression delta is positive
            if price_delta_current < 0:
                # If the current close price is less than the previous close price
                trade_signal = 1
        elif linreg_delta_current and linreg_delta_previous < 0:
            # If the linear regression delta is negative
            if price_delta_current > 0:
                # If the current close price is greater than the previous close price
                trade_signal = -1
        else:
            # Do not trade if none of the conditions are met
            trade_signal = 0
        
        log_msg_header = f'Close: {self.data.close[0]:.2f}, Trade Signal: {trade_signal},'
        log_msg_content = f'\tCurrent Linreg_delta: {linreg_delta_current:.2f},\n\tPrevious Linreg_delta: {linreg_delta_previous:.2f}, \n\tPrice Delta: {price_delta_current:.2f}, \n\tLast Entry: {self.last_entry:.2f},'
        self.log(f'{log_msg_header}\n{log_msg_content}')
        return trade_signal

    def close_positions(self):
        if self.position.size != 0:
            # If there is an open position
            if self.lines.trade_signal == 1 and self.position.size < 0:
                # If the trade signal is long and the position is short
                self.close()
                self.last_entry = 0
            
            elif self.lines.trade_signal == -1 and self.position.size > 0:
                # If the trade signal is short and the position is long
                self.close()
                self.last_entry = 0
            
            else:
                # Do not trade if none of the conditions are met
                return
        
    def open_positions(self):
        # Check if there is an open position
        if self.position.size == 0:
            # If there is no open position
            if self.lines.trade_signal == 1:
                # If the trade signal is long then buy
                #self.buy(exectype=bt.Order.StopTrail, trailpercent=self.params.trailpercent)
                self.buy()
                self.last_entry = self.data.close[0]
            elif self.lines.trade_signal == -1:
                # If the trade signal is short then sell
                #self.sell(exectype=bt.Order.StopTrail, trailpercent=self.params.trailpercent)
                self.sell()
                self.last_entry = self.data.close[0]
        
        # Check if there is an open long position
        elif self.position.size > 0:
            # If there is an open long position
            if self.lines.trade_signal == 1:
                # If the trade signal is long
                if self.data.close[0] > (self.last_entry * (1 + self.params.last_entry_tol_perc)):
                    # If the current close price is greater than the last entry price plus the tolerance
                    self.buy()
                    self.last_entry = self.data.close[0]
        
        # Check if there is an open short position
        elif self.position.size < 0:
            # If there is an open short position
            if self.lines.trade_signal == -1:
                if self.data.close[0] < (self.last_entry * (1 - self.params.last_entry_tol_perc)):
                    # If the current close price is less than the last entry price minus the tolerance
                    self.sell()
                    self.last_entry = self.data.close[0]
        else:
            return
    


    def next(self):
        """
        # Ensure that we have enough valid data points
        if len(self.data.close) < self.params.period + 1:
            return
        
        # Initialize the variables        
        linreg_delta_current = self.lines.linreg_delta[0]
        linreg_delta_previous = self.lines.linreg_delta[-1]
        price_delta_current = self.lines.price_delta[0]

        # Check the conditions for trade signals
        if linreg_delta_current and linreg_delta_previous > 0:
            # If the linear regression delta is positive
            if price_delta_current < 0:
                # If the current close price is less than the previous close price
                self.trade_signal = 1
        elif linreg_delta_current and linreg_delta_previous < 0:
            # If the linear regression delta is negative
            if price_delta_current > 0:
                # If the current close price is greater than the previous close price
                self.trade_signal = -1
        else:
            # Do not trade if none of the conditions are met
            self.trade_signal = 0
        
        # Log the trade signals
        if self.trade_signal == 1:
            self.log(f'LONG SIGNAL: \n  Current Linreg_delta: \t {linreg_delta_current} \n  Previous Linreg_delta: \t {linreg_delta_previous} \n  Price Delta: \t\t\t {price_delta_current}')
        elif self.trade_signal == -1:
            self.log(f'SHORT SIGNAL: \n  Current Linreg_delta: \t {linreg_delta_current} \n  Previous Linreg_delta: \t {linreg_delta_previous} \n  Price Delta: \t\t\t {price_delta_current}')
        else:
            self.log(f'NO SIGNAL: \n  Current Linreg_delta: \t {linreg_delta_current} \n  Previous Linreg_delta: \t {linreg_delta_previous} \n  Price Delta: \t\t\t {price_delta_current}')
        """
        #self.trade_signal = self.check_trade_signal()

        """
        # Check if there is an open position
        if self.position.size == 0:
            # If there is no open position
            if self.trade_signal == 1:
                # If the trade signal is long then buy
                self.buy()
            elif self.trade_signal == -1:
                # If the trade signal is short then sell
                self.sell()
        
        # Check if there is an open long position
        elif self.position.size > 0:
            # If there is an open long position
            if self.trade_signal == 1:
                # If the trade signal is long then add to the long position
                self.buy()
            elif self.trade_signal == -1:
                # If the trade signal is short then close the long position
                self.close()

        # Check if there is an open short position
        elif self.position.size < 0:
            # If there is an open short position
            if self.trade_signal == 1:
                # If the trade signal is long then close the short position
                self.close()
            elif self.trade_signal == -1:
                # If the trade signal is short then add to the short position
                self.sell()
        """
        self.close_positions()
        self.open_positions()

        
        # Log the trade signals
        #self.log(f'Close: {self.data.close[0]}, Trade Signal: {self.trade_signal}')




class DataExporter(bt.Analyzer):
    def __init__(self):
        # Initialize the dictionary to store the data
        self.data_dict = {}
        # Initialize the dictionary to store the indicator data
        self.ind_dict = {}
    
    def start(self):
        # Prepare to store all the data points
        self.data_dict['datetime'] = []
        self.data_dict['open'] = []
        self.data_dict['high'] = []
        self.data_dict['low'] = []
        self.data_dict['close'] = []
        self.data_dict['volume'] = []

        # Prepare to store all the indicator data points
        for indicator in self.strategy.getindicators():
            line_aliases: tuple[str] = indicator.lines.getlinealiases()
            for alias in line_aliases:
                self.ind_dict[alias.lower()] = []

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
            line_aliases = indicator.lines.getlinealiases()
            for alias in line_aliases:
                self.ind_dict[alias.lower()].append(getattr(indicator.lines, alias)[0])
        
    def get_analysis(self):
        # Create a DataFrame to store the data
        df = pd.DataFrame(self.data_dict)
        df.set_index('datetime', inplace=True)

        # Add the indicator data to the DataFrame
        for key, value in self.ind_dict.items():
            df[key] = value
        return df



data = get_historical_data()
print('Successfully retrieved historical data')

# Setup the cerebro engine
cerebro = bt.Cerebro()
cerebro.adddata(bt.feeds.PandasData(dataname=data))
cerebro.addstrategy(MyStrategy)
#cerebro.addanalyzer(DataExporter, _name='data_exporter')


#cerebro.addsizer(bt.sizers.PercentSizer, percents=50)


# Run the strategy
backtest_results = cerebro.run()
strategy_results = backtest_results[0]
#data_export = strategy_results.analyzers.data_exporter.get_analysis()

#print(data_export)
#data_export.to_excel('backtest_results.xlsx')


cerebro.plot(
    iplot=False,
    style='candlestick',)

