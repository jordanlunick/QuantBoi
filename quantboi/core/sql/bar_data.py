#from ib_async import BarData

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum


"""
@dataclass
class BarData:
    date: Union[date_, datetime] = EPOCH
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float = 0
    average: float = 0.0
    barCount: int = 0
"""

# Define the base class for declarative models
Base = declarative_base()

class BarData(Base):
    __tablename__ = 'bar_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    average = Column(Float, nullable=False)
    barCount = Column(Integer, nullable=False)


# Create an SQLite database and establish a connection
engine = create_engine('sqlite:///bar_data.db', echo=True)

# Create the bar data table
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Example of adding a new bar data to the table
new_bar_data = BarData(
    ticker='AAPL',
    date='2024-08-27',
    open=150.00,
    high=155.00,
    low=148.00,
    close=152.00,
    volume=10000,
    average=151.00,
    barCount=10
)

