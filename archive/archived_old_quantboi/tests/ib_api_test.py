import pandas as pd
from ib_async import (
    IB, Stock, util, Contract, Option, Index)

from archived_old_quantboi import config
from archived_old_quantboi.core.ib_api import (
    IBAPI, IBClient)






util.startLoop()
client = IBClient(host='127.0.0.1', port=7497, clientId=1)
client.connect()

contract = Index('SPX', 'CBOE')
client.qualify_contracts(contract)

# Request delayed market data type
client.req_market_data_type(4)

# Request tickers
[ticker] = client.req_tickers(contract)

spxValue = ticker.marketPrice()

chains = client.ib.reqSecDefOptParams(
    underlyingSymbol=contract.symbol,
    futFopExchange='',
    underlyingSecType=contract.secType,
    underlyingConId=contract.conId,
)
chain = chains[0] # CDE
strikes = chain.strikes
expirations = chain.expirations
rights = ['P', 'C']

# Create a Option contract for each option in the chain and qualify them
strikes = [strike for strike in chain.strikes
        if strike % 5 == 0
        and spxValue - 20 < strike < spxValue + 20]
expirations = sorted(exp for exp in chain.expirations)[:3]
rights = ['P', 'C']

contracts = [Option('SPX', expiration, strike, right, 'SMART', tradingClass='SPX')
        for right in rights
        for expiration in expirations
        for strike in strikes]

contracts = client.qualify_contracts(*contracts)

# Request tickers for the option contracts
client.req_market_data_type(4)
tickers = client.req_tickers(*contracts)
df = util.df(tickers)

# Expand the modelGreeks column into separate columns
#df = df.join(df['modelGreeks'].apply(pd.Series))

# Disconnect the client
client.disconnect()