from ib_async import *
util.startLoop()

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

spx = Index('SPX', 'CBOE')
ib.qualifyContracts(spx)

ib.reqMarketDataType(4)
ticker = ib.reqTickers(spx)[0]
