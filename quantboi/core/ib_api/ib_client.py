import asyncio
import datetime
from enum import Enum


from typing import Any, Awaitable, Dict, Iterator, List, Optional, Union


from ib_async import (
    BarData, BarDataList,
    Contract, IB, Stock, util, TagValue, Ticker)


#util.startLoop()

class IBClient:
    def __init__(self, host: str, port: int, clientId: int) -> None:
        self.ib = IB()
        self.host = host
        self.port = port
        self.clientId = clientId

    def connect(self) -> None:
        self.ib.connect(host=self.host, port=self.port, clientId=self.clientId)

    def disconnect(self) -> None:
        self.ib.disconnect()

    def qualify_contracts(self, *contracts: Contract) -> list[Contract]:
        return self.ib.qualifyContracts(*contracts)

    def req_historical_data(
        self, 
        contract: Contract,
        endDateTime: Union[datetime.datetime, datetime.date, str, None],
        durationStr: str = '1 D',
        barSizeSetting: str = '15 mins',
        whatToShow: str = 'TRADES',
        useRTH: bool = True,
        formatDate: int = 1,
        keepUpToDate: bool = False,
        chartOptions: List[TagValue] = [],
        timeout: float = 60,
    ) -> BarDataList:
        """
        Request historical data for a contract.
        
        Args:
            contract: The contract for which to request historical data.
            endDateTime: The end date and time of the request.
            durationStr: The duration of the request.
            barSizeSetting: The bar size setting of the request.
            whatToShow: The type of data to show.
            useRTH: Whether to use regular trading hours.
            formatDate: The date format.
            keepUpToDate: Whether to keep the request up to date.
            chartOptions: The chart options.
            timeout: The timeout of the request.
        """
        return self.ib.reqHistoricalData(
            contract,
            endDateTime=endDateTime,
            durationStr=durationStr,
            barSizeSetting=barSizeSetting,
            whatToShow=whatToShow,
            useRTH=useRTH,
            formatDate=formatDate,
            keepUpToDate=keepUpToDate,
            chartOptions=chartOptions,
            timeout=timeout
        )
    
    def req_market_data_type(self, market_data_type: int) -> None:
        self.ib.reqMarketDataType(market_data_type)
    
    def req_tickers(self, *contracts: Contract) -> List[Ticker]:
        return self.ib.reqTickers(*contracts)

    # /// Example of async methods /// #
    async def async_connect(self) -> None:
        self.connect()

    async def async_disconnect(self) -> None:
        self.disconnect()
    
    async def async_qualify_contracts(self, *contracts: Contract) -> list[Contract]:
        return self.qualify_contracts(*contracts)
    
    async def async_req_historical_data(self, contract: Contract) -> BarDataList:
        return self.req_historical_data(contract)
    
