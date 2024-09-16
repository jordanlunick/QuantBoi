from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from ib_async import IB, util, Stock, BarDataList
from typing import List
import asyncio
import ib_api
# Database Setup
Base = declarative_base()

# Market Data Table
class MarketData(Base):
    __tablename__ = 'market_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    indicators = relationship('IndicatorData', back_populates='market_data')  # Relationship for related indicators

# Indicator Data Table
class IndicatorData(Base):
    __tablename__ = 'indicator_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_data_id = Column(Integer, ForeignKey('market_data.id'), nullable=False)  # Foreign key to market data
    indicator_name = Column(String, nullable=False)  # e.g., 'SMA', 'RSI'
    value = Column(Float, nullable=False)
    market_data = relationship('MarketData', back_populates='indicators')  # Link back to market data

# Database Access Layer (DAL)
class DataRepository:
    def __init__(self, session):
        self.session = session

    def save_market_data(self, data: MarketData):
        self.session.add(data)
        self.session.commit()

    def save_market_data_batch(self, data: List[MarketData]):
        self.session.add_all(data)
        self.session.commit()

    def save_indicator_data(self, indicators: List[IndicatorData]):
        self.session.add_all(indicators)
        self.session.commit()

    def fetch_market_data(self, symbol, start_time, end_time):
        return self.session.query(MarketData).filter(
            MarketData.symbol == symbol,
            MarketData.timestamp.between(start_time, end_time)
        ).all()

# IBKR Data Fetching Class
class IBKRClient:
    def __init__(self):
        self.ib = IB()

    async def connect(self):
        await self.ib.connectAsync('127.0.0.1', 7497, clientId=1)

    async def get_historical_data(self, symbol: str, duration: str = '10 D', bar_size: str = '1 min') -> BarDataList:
        contract = Stock(symbol, 'SMART', 'USD')
        await self.ib.qualifyContractsAsync(contract)
        historical_data = await self.ib.reqHistoricalDataAsync(
            contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='TRADES',
            useRTH=True
        )
        return historical_data

    async def disconnect(self):
        self.ib.disconnect()

# Market Data and Indicator Manager
class MarketDataManager:
    def __init__(self, repository: DataRepository):
        self.repository = repository

    def store_data(self, symbol: str, historical_data: List[BarDataList]):
        data_list = []
        for bar in historical_data:
            data_entry = MarketData(
                symbol=symbol,
                timestamp=bar.date,
                open_price=bar.open,
                high_price=bar.high,
                low_price=bar.low,
                close_price=bar.close,
                volume=bar.volume
            )
            data_list.append(data_entry)
        self.repository.save_market_data_batch(data_list)

# Indicator Manager
class IndicatorManager:
    def __init__(self, repository: DataRepository):
        self.repository = repository

    def calculate_sma(self, data: List[MarketData], period: int):
        sma_values = []
        close_prices = [d.close_price for d in data]
        for i in range(len(close_prices) - period + 1):
            sma_value = sum(close_prices[i:i + period]) / period
            sma_values.append(sma_value)
        return sma_values

    def calculate_rsi(self, data: List[MarketData], period: int = 14):
        gains = []
        losses = []
        close_prices = [d.close_price for d in data]
        for i in range(1, len(close_prices)):
            diff = close_prices[i] - close_prices[i - 1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                losses.append(-diff)
                gains.append(0)
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        rsi_values = []

        for i in range(period, len(gains)):
            avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
            avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs))
            rsi_values.append(rsi)
        
        return rsi_values

    def store_indicators(self, symbol: str, data: List[MarketData]):
        sma_5 = self.calculate_sma(data, 5)
        rsi_14 = self.calculate_rsi(data)

        indicator_list = []
        for i, bar in enumerate(data):
            if i >= 5:
                sma_entry = IndicatorData(
                    market_data_id=bar.id,
                    indicator_name='SMA_5',
                    value=sma_5[i - 5]
                )
                indicator_list.append(sma_entry)

            if i >= 14:
                rsi_entry = IndicatorData(
                    market_data_id=bar.id,
                    indicator_name='RSI_14',
                    value=rsi_14[i - 14]
                )
                indicator_list.append(rsi_entry)
        
        self.repository.save_indicator_data(indicator_list)

# Main Execution Flow
async def main():
    # Setup the database engine and session
    engine = create_engine('sqlite:///market_data.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Initialize the repository and manager
    repository = DataRepository(session)
    market_data_manager = MarketDataManager(repository)
    indicator_manager = IndicatorManager(repository)

    # Initialize IBKR client and fetch historical data
    ibkr_client = IBKRClient()
    await ibkr_client.connect()
    historical_data = await ibkr_client.get_historical_data(symbol='SPY')
    await ibkr_client.disconnect()

    # Store the fetched data into the database
    market_data_manager.store_data(symbol='SPY', historical_data=historical_data)

    # Fetch the stored data and calculate indicators
    stored_data = repository.fetch_market_data('SPY', '2024-08-29', '2024-09-11')
    indicator_manager.store_indicators(symbol='SPY', data=stored_data)

# Run the asyncio loop
if __name__ == '__main__':
    util.startLoop()
    asyncio.run(main())
