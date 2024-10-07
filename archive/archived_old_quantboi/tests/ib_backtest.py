import backtrader as bt
from ib_async import *

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
        contract, endDateTime='', durationStr='100 D',
        barSizeSetting='1 day', whatToShow='TRADES', useRTH=True)
    ib.disconnect()
    data = util.df(historical_data)
    data['datetime'] = pd.to_datetime(data['date'])
    data.set_index('datetime', inplace=True)
    data.drop(columns=['date', 'average', 'barCount'], inplace=True)
    return data

def export_strategy_df(rets: bt.Strategy) -> pd.DataFrame:
    tmp_dict = {}
    
    # Loop through each data object in the strategy
    for i, data_obj in enumerate(rets.datas):
        tmp_df = data_obj._dataname  # Original data
        
        # Start with the original data as a DataFrame
        data_export = pd.DataFrame(tmp_df)
        
        # Gather all indicators and their line values
        indicators = {attr: getattr(rets, attr) for attr in dir(rets) if isinstance(getattr(rets, attr), bt.Indicator)}
        
        for indicator_name, indicator in indicators.items():
            line_aliases = indicator.lines.getlinealiases()
            
            # Assign all lines of the indicator to the DataFrame at once
            for j, line_name in enumerate(line_aliases):
                data_export[line_name] = indicator.lines[j].get(size=len(data_export))
        
        # Assign the dataframe for each data object to the tmp_dict
        tmp_dict[f'data_{i}'] = data_export

    return tmp_dict




class StrategyIndicators(bt.Indicator):
    lines = ('vwap', 'lr_vwap')
    params = (
        ('period', 14),  # Default period value for VWAP and linear regression
    )

    def __init__(self):
        self.addminperiod(self.p.period)  # Ensure there are enough periods to calculate VWAP and regression
        self.vsum = bt.indicators.SumN(self.data.volume, period=self.p.period)
        self.pvsum = bt.indicators.SumN(self.data.close * self.data.volume, period=self.p.period)
    
    def next(self):
        # Calculate VWAP
        if self.vsum[0] != 0:
            self.lines.vwap[0] = self.pvsum[0] / self.vsum[0]
        else:
            self.lines.vwap[0] = float('nan')
        
        # Gather the necessary data points for linear regression
        y = np.array(self.lines.vwap.get(size=self.p.period))
        
        # Ensure we have enough valid data (i.e., no NaNs) before proceeding
        if np.any(np.isnan(y)) or len(y) < self.p.period:
            self.lines.lr_vwap[0] = float('nan')
            return
        
        x = np.arange(self.p.period)

        # Calculate the linear regression using numpy's polyfit
        try:
            slope, intercept = np.polyfit(x, y, 1)
            self.lines.lr_vwap[0] = slope * (self.p.period - 1) + intercept
        except np.linalg.LinAlgError:
            self.lines.lr_vwap[0] = float('nan')


class StrategyLogic(bt.Strategy):
    params = (
        ('stop_loss_perc', 0.02),  # Initial stop loss percentage (2% by default)
        ('stop_trail_perc', 0.01),  # Trailing stop loss percentage (1% by default)
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Added the StrategyIndicators indicator directly to the engine rather than strategy
        self.trade_direction = 'neutral'
        self.new_trade_direction = None
        self.order = None  # To track the active order
        self.stop_loss_order = None  # To track the stop loss order
        self.trailing_stop_order = None  # To track the trailing stop loss order
        self.highest_price = None  # To track the highest price for trailing stop
        self.lowest_price = None  # To track the lowest price for short trailing stop
        
        
        self.strat_ind = StrategyIndicators(self.data)
        #self.delta_lr_0 = self.strat_ind.lr_vwap[0] - self.strat_ind.lr_vwap[-1] 
        #self.delta_lr_1 = self.strat_ind.lr_vwap[-1] - self.strat_ind.lr_vwap[-2] 


    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.data.close[0])
        
        # Determine the trade direction based on the delta of the linear regression values
        #delta_lr_0 = self.indicators.lr_vwap[0] - self.indicators.lr_vwap[-1]      # Moved to __init__
        
        #delta_lr_1 = self.indicators.lr_vwap[-1] - self.indicators.lr_vwap[-2]     # Moved to __init__
        if len(self.data) > 2:  # Check that at least 3 bars have passed
            self.delta_lr_0 = self.strat_ind.lr_vwap[0] - self.strat_ind.lr_vwap[-1]
            self.delta_lr_1 = self.strat_ind.lr_vwap[-1] - self.strat_ind.lr_vwap[-2]
        

        
        if self.delta_lr_0 > 0 and self.delta_lr_1 > 0:
            self.new_trade_direction = 'long'
        elif self.delta_lr_0 < 0 and self.delta_lr_1 < 0:
            self.new_trade_direction = 'short'
        else:
            self.new_trade_direction = 'neutral'

        # Close existing positions if the direction changes
        if self.new_trade_direction != self.trade_direction:
            if self.new_trade_direction == 'long' and self.position.size < 0:
                # Close the short position if we're switching to long
                self.close()
                if self.stop_loss_order:
                    self.cancel(self.stop_loss_order)  # Cancel stop loss order
                if self.trailing_stop_order:
                    self.cancel(self.trailing_stop_order)  # Cancel trailing stop order
            elif self.new_trade_direction == 'short' and self.position.size > 0:
                # Close the long position if we're switching to short
                self.close()
                if self.stop_loss_order:
                    self.cancel(self.stop_loss_order)  # Cancel stop loss order
                if self.trailing_stop_order:
                    self.cancel(self.trailing_stop_order)  # Cancel trailing stop order
            # Update trade direction
            self.trade_direction = self.new_trade_direction
        
        # Execute trades and set stop losses based on the new trade direction
        if self.trade_direction == 'long':
            if self.data.close[-1] > self.data.close[-2]:
                
                if not self.position:  # Ensure no existing position
                    self.buy()
                    # Place initial stop loss order
                    stop_price = self.data.close[0] * (1.0 - self.params.stop_loss_perc)
                    self.stop_loss_order = self.sell(exectype=bt.Order.Stop, price=stop_price)
                    # Reset the highest price for trailing stop
                    self.highest_price = self.data.close[0]

        elif self.trade_direction == 'short':
            if self.data.close[-1] < self.data.close[-2]:
                
                if not self.position:  # Ensure no existing position
                    self.sell()
                    # Place initial stop loss order
                    stop_price = self.data.close[0] * (1.0 + self.params.stop_loss_perc)
                    self.stop_loss_order = self.buy(exectype=bt.Order.Stop, price=stop_price)
                    # Reset the lowest price for trailing stop
                    self.lowest_price = self.data.close[0]
                #self.sell(size=1, exectype=bt.Order.StopTrail, trailpercent=self.params.stop_trail_perc)

        # Adjust trailing stop for long positions
        if self.position.size > 0:  # If a long position is open
            if self.highest_price is None or self.data.close[0] > self.highest_price:
                self.highest_price = self.data.close[0]  # Update the highest price
            trailing_stop_price = self.highest_price * (1.0 - self.params.stop_trail_perc)
            if self.trailing_stop_order:
                self.cancel(self.trailing_stop_order)  # Cancel previous trailing stop order
            self.trailing_stop_order = self.sell(exectype=bt.Order.Stop, price=trailing_stop_price)

        # Adjust trailing stop for short positions
        if self.position.size < 0:  # If a short position is open
            if self.lowest_price is None or self.data.close[0] < self.lowest_price:
                self.lowest_price = self.data.close[0]  # Update the lowest price
            trailing_stop_price = self.lowest_price * (1.0 + self.params.stop_trail_perc)
            if self.trailing_stop_order:
                self.cancel(self.trailing_stop_order)  # Cancel previous trailing stop order
            self.trailing_stop_order = self.buy(exectype=bt.Order.Stop, price=trailing_stop_price)

        
        self.log(f'Close: {self.data.close[0]} Position size: {self.position.size} Open PnL: {self.position.size * (self.data.close[0] - self.data.close[-1])}')

    def notify_order(self, order):
        # Track order status
        if order.status in [order.Submitted, order.Accepted]:
            # Order is submitted/accepted by the broker - no further action required.
            return
        
        # Check if the order is completed (either fully or partially)
        if order.status in [order.Completed]:
            if order.isbuy():
                #self.log('BUY EXECUTED, %.2f' % order.executed.price)
                self.log(f'BUY EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}')
            elif order.issell():
                #self.log('SELL EXECUTED, %.2f' % order.executed.price)
                self.log(f'SELL EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}')
            self.order = None  # Reset order tracking

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            self.order = None  # Reset order tracking



class StrategyAnalyzer(bt.Analyzer):
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

        # Capture indicator data used in the strategy
        self.indicators_dict = {}

        # Loop over all indicators in the strategy
        for ind in self.strategy.getindicators():
            self.indicators_dict[ind] = []

    def next(self):
        # Collect price data
        self.data_dict['datetime'].append(self.data.datetime.datetime(0))
        self.data_dict['open'].append(self.data.open[0])
        self.data_dict['high'].append(self.data.high[0])
        self.data_dict['low'].append(self.data.low[0])
        self.data_dict['close'].append(self.data.close[0])
        self.data_dict['volume'].append(self.data.volume[0])

        # Collect indicator data and print the current values for debugging
        for ind, values in self.indicators_dict.items():
            # Append the current value of each line (vwap, lr_vwap)
            current_value = ind[0]  # Current value of the indicator
            print(f"Appending indicator value: {current_value} for indicator {ind}")
            values.append(current_value)

    def get_analysis(self):
        # Convert price data to DataFrame
        df = pd.DataFrame(self.data_dict)

        # Add indicators to the DataFrame and check the length of values
        for ind, values in self.indicators_dict.items():
            line_aliases = ind.lines.getlinealiases()

            # Debug print: Check how many values we have for the indicator
            print(f"Adding {len(values)} values for indicator {ind}")

            # Add each line to the DataFrame
            for line_name, line_values in zip(line_aliases, values):
                df[line_name] = line_values  # Add indicator values to the DataFrame

        # Debug print: Show the DataFrame after adding indicator values
        print(df)

        return df




# Get historical data
data = get_historical_data()

# Convert the historical data to Backtrader data feed
data_feed = bt.feeds.PandasData(dataname=data)

# Initialize Cerebro engine
cerebro = bt.Cerebro()
cerebro.adddata(data_feed)

# Add the StrategyIndicators indicator to the engine
#cerebro.addindicator(StrategyIndicators)

# Add the strategy to the engine
cerebro.addstrategy(StrategyLogic)

# Add analyzers
cerebro.addanalyzer(StrategyAnalyzer, _name='export_data')

# Run the backtest
bt_rets = cerebro.run()

export_data = bt_rets[0].analyzers.export_data.get_analysis()
#print(export_data.head())
