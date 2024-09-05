from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

# Define the base class for declarative models
Base = declarative_base()

# Enum for transaction types
class TransactionType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    INTEREST = "INTEREST"
    FEE = "FEE"

# Define the Transaction class
class Transaction(Base):
    __tablename__ = 'transaction_ledger'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    symbol = Column(String(10), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    fee = Column(Float, nullable=True, default=0.0)
    description = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Transaction(id={self.id}, date={self.date}, type={self.transaction_type}, symbol={self.symbol}, quantity={self.quantity}, price={self.price}, total_value={self.total_value}, fee={self.fee})>"

# Create an SQLite database and establish a connection
engine = create_engine('sqlite:///investment_ledger.db', echo=True)

# Create the transaction ledger table
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Example of adding a new transaction to the ledger
new_transaction = Transaction(
    date='2024-08-27',
    transaction_type=TransactionType.BUY,
    symbol='AAPL',
    quantity=10,
    price=150.00,
    total_value=1500.00,
    fee=10.00,
    description="Bought 10 shares of AAPL"
)

# Add the transaction to the session and commit
session.add(new_transaction)
session.commit()

# Query the transaction ledger
transactions = session.query(Transaction).all()
for transaction in transactions:
    print(transaction)

# Close the session
session.close()
