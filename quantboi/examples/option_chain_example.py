from ib_async import *
util.startLoop()






class IBWrapper:
    def __init__(self) -> None:
        self.ib = IB()

    def connect(self, host='127.0.0.1', port=7496, clientId=1) -> None:
        self.ib.connect(host=host, port=port, clientId=clientId)

    def disconnect(self) -> None:
        self.ib.disconnect()

    def get_option_ticker(self, symbol, expiry, strike, right, exchange, currency) -> Ticker:
        contract = Option(
            symbol=symbol, 
            lastTradeDateOrContractMonth=expiry, 
            strike=strike, 
            right=right, 
            exchange=exchange, 
            multiplier='100',
            currency=currency)
        self.ib.qualifyContracts(contract)
        ticker = self.ib.reqMktData(contract, genericTickList='101')
        return ticker


ib = IBWrapper()
ib.connect()
ticker = ib.get_option_ticker('TD', '20241004', 85, 'C', 'CDE', 'CAD')






ib = IB()
#ib.connect('127.0.0.1', 7497, clientId=1)
ib.connect('127.0.0.1', 7496, clientId=1)





contract = Option(
    symbol='TD', 
    lastTradeDateOrContractMonth='20241004', 
    strike=85, 
    right='C', 
    exchange='CDE', 
    multiplier='100',
    currency='CAD')
ib.qualifyContracts(contract)
ticker = ib.reqMktData(contract, genericTickList='101')

ib.sleep(2)

ib.disconnect()