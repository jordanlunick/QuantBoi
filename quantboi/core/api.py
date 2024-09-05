
from ib_async import (
    IB, Stock, util, Contract)

from quantboi import config
from quantboi.core.ib_api import (
    IBAPI, IBClient)






util.startLoop()
ib = IBAPI()
clientId = ib.available_clientId
ib.connect_client()

# Create a Stock contract for TD Bank
contract = Stock('TD', 'SMART', 'CAD')
contract = ib.qualify_contracts(contract)[0]
"""
historical_data = ib.req_historical_data(
    contract,
    endDateTime='',
    durationStr='1 D',
    barSizeSetting='15 mins',
    whatToShow='TRADES',
    useRTH=True,
    formatDate=1,
    keepUpToDate=False,
    chartOptions=[],
    timeout=60,
)

# Disconnect the client ID
#ib.disconnect_client(clientId)
"""