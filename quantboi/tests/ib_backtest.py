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
    ib.connect('127.0.0.1', 7497, clientId=2)
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
        self.vwap_linreg = StrategyIndicators()
        #self.dataclose = self.datas[0].close
        self.trade_direction = 'neutral'
        self.new_trade_direction = None
        self.order = None  # To track the active order
        self.stop_loss_order = None  # To track the stop loss order
        self.trailing_stop_order = None  # To track the trailing stop loss order
        self.highest_price = None  # To track the highest price for trailing stop
        self.lowest_price = None  # To track the lowest price for short trailing stop
    
    def determine_trade_direction(self):
        # Determine the trade direction based on the delta of the linear regression values
        delta_lr_0 = self.vwap_linreg.lr_vwap[0] - self.vwap_linreg.lr_vwap[-1] 
        delta_lr_1 = self.vwap_linreg.lr_vwap[-1] - self.vwap_linreg.lr_vwap[-2] 
        if delta_lr_0 > 0 and delta_lr_1 > 0:
            return 'long'
        elif delta_lr_0 < 0 and delta_lr_1 < 0:
            return 'short'
        else:
            return 'neutral'
        
    def close_existing_positions(self):
        # Close the exisitng short position if we're switching to long
        if self.new_trade_direction == 'long' and self.position.size < 0:
            # Close the short position if we're switching to long
            self.close()
            """
            if self.stop_loss_order:
                self.cancel(self.stop_loss_order)  # Cancel stop loss order
            if self.trailing_stop_order:
                self.cancel(self.trailing_stop_order)  # Cancel trailing stop order
            """
        
        # Close the existing long position if we're switching to short
        elif self.new_trade_direction == 'short' and self.position.size > 0:
            # Close the long position if we're switching to short
            self.close()
            """
            if self.stop_loss_order:
                self.cancel(self.stop_loss_order)  # Cancel stop loss order
            if self.trailing_stop_order:
                self.cancel(self.trailing_stop_order)  # Cancel trailing stop order
            """
        
        # Update trade direction
        self.trade_direction = self.new_trade_direction
        self.log(f'New trade direction: {self.trade_direction}')
        self.new_trade_direction = None


    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.data.close[0])
        
        # Determine the trade direction based on the delta of the linear regression values
        delta_lr_0 = self.vwap_linreg.lr_vwap[0] - self.vwap_linreg.lr_vwap[-1] 
        delta_lr_1 = self.vwap_linreg.lr_vwap[-1] - self.vwap_linreg.lr_vwap[-2] 
        if delta_lr_0 > 0 and delta_lr_1 > 0:
            self.new_trade_direction = 'long'
        elif delta_lr_0 < 0 and delta_lr_1 < 0:
            self.new_trade_direction = 'short'
        else:
            self.new_trade_direction = 'neutral'
        #self.new_trade_direction = self.determine_trade_direction()
            

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
        
        #if self.new_trade_direction != self.trade_direction:
        #    self.close_existing_positions()

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
                
                #self.buy(size=1, exectype=bt.Order.StopTrail, trailpercent=self.params.stop_trail_perc)
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
        
        """
        # Adjust trailing stop for long positions
        if self.position.size > 0:  # If a long position is open
            if self.data.close[0] > self.highest_price:
                self.highest_price = self.data.close[0]  # Update the highest price
            trailing_stop_price = self.highest_price * (1.0 - self.params.stop_trail_perc)
            if self.trailing_stop_order:
                self.cancel(self.trailing_stop_order)  # Cancel previous trailing stop order
            self.trailing_stop_order = self.sell(exectype=bt.Order.Stop, price=trailing_stop_price)

        # Adjust trailing stop for short positions
        if self.position.size < 0:  # If a short position is open
            if self.data.close[0] < self.lowest_price:
                self.lowest_price = self.data.close[0]  # Update the lowest price
            trailing_stop_price = self.lowest_price * (1.0 + self.params.stop_trail_perc)
            if self.trailing_stop_order:
                self.cancel(self.trailing_stop_order)  # Cancel previous trailing stop order
            self.trailing_stop_order = self.buy(exectype=bt.Order.Stop, price=trailing_stop_price)
        """
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
#cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
#cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.Transactions, _name='trans')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
#cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

# Run the backtest
back = cerebro.run()

cerebro.broker.getvalue()
transactions = back[0].analyzers.trans.get_analysis()
trades = back[0].analyzers.trades.get_analysis()


# Plot the results
cerebro.plot(
    iplot=False,  # Don't know if this works https://github.com/jupyterlab/jupyterlab/issues/7715
    style='candlestick',)
    #plotdist=0.001,)
