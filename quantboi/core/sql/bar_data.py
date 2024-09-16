#from ib_async import BarData

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

import datetime as dt
import backtrader as bt
from ib_async import (
    IB, util, Contract, Stock, BarDataList)

import matplotlib.pyplot as plt
import numpy as np
from typing import Union

import pandas as pd

# Define the base class for declarative models
Base = declarative_base()

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

@benchmark
def commit_hist_data_to_db(contract: Contract, historical_data: BarDataList):
    # Create an SQLite database and establish a connection
    engine = create_engine('sqlite:///historical_bar_data.db', echo=True)

    # Create the bar data table
    Base.metadata.create_all(engine)

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Insert the historical data into the database
    for bar_data in historical_data:
        bar = HistoricalBarData(
            conId=contract.conId, symbol=contract.symbol,
            currency=contract.currency, exchange=contract.exchange,
            datetime=bar_data.date, open=bar_data.open, high=bar_data.high,
            low=bar_data.low, close=bar_data.close, volume=bar_data.volume,
            average=bar_data.average, barCount=bar_data.barCount)
        session.add(bar)
        session.commit()


class HistoricalBarData(Base):
    __tablename__ = 'historical_bar_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    conId = Column(Integer, nullable=False)
    symbol = Column(String(10), nullable=False)
    currency = Column(String(3), nullable=False)
    exchange = Column(String(10), nullable=False)
    datetime = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    average = Column(Float, nullable=False)
    barCount = Column(Integer, nullable=False)


# Create an SQLite database and establish a connection
#engine = create_engine('sqlite:///historical_bar_data.db', echo=True)

# Create the bar data table
#Base.metadata.create_all(engine)

# Create a session
#Session = sessionmaker(bind=engine)
#session = Session()

# Fetch historical data from IB
contract, historical_data = get_historical_data()
#commit_hist_data_to_db(contract, historical_data)


# Insert the historical data into the database

#for bar_data in historical_data:
#    bar = HistoricalBarData(
#        conId=contract.conId, symbol=contract.symbol,
#        currency=contract.currency, exchange=contract.exchange,
#        datetime=bar_data.date, open=bar_data.open, high=bar_data.high,
#        low=bar_data.low, close=bar_data.close, volume=bar_data.volume,
#        average=bar_data.average, barCount=bar_data.barCount)
#    session.add(bar)
#    session.commit()


# Query the database
# query = session.query(HistoricalBarData)
# for bar_data in query:
#     print(
#         bar_data.date, bar_data.open, bar_data.high, 
#         bar_data.low, bar_data.close, bar_data.volume)
