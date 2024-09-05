import asyncio
from ib_async import (
    IB, Stock, util, Contract)

from quantboi.core.ib_api.ib_client import IBClient


class IBAPI:
    def __init__(self, host: str = '127.0.0.1', port: int = 7497) -> None:
        # TWS Gateway host and port
        self.host = host
        self.port = port
        
        # Dictionary of TWS Gateway connected clients
        self.clients: dict[int, IBClient] = {}
        self.available_clientId = 1

    def connect_client(self) -> None:
        # Find the first available client ID
        while self.available_clientId in self.clients:
            self.available_clientId += 1
        
        client = IBClient(host=self.host, port=self.port, clientId=self.available_clientId)
        client.connect()
        self.clients[self.available_clientId] = client

    def disconnect_client(self, clientId: int) -> None:
        if clientId in self.clients:
            client = self.clients[clientId]
            client.disconnect()
            del self.clients[clientId]

            # Reset available_clientId if it's the disconnected client ID
            if clientId == self.available_clientId:
                self.available_clientId = clientId

    def qualify_contracts(self, *contracts: Contract) -> list[Contract]:
        # Ensure at least one client is connected
        if not self.clients:
            raise RuntimeError("No clients connected")
        first_client_id = next(iter(self.clients))
        return self.clients[first_client_id].qualify_contracts(*contracts)
    
    def req_historical_data(self, *args, **kwargs):
        # Ensure at least one client is connected
        if not self.clients:
            raise RuntimeError("No clients connected")
        first_client_id = next(iter(self.clients))
        return self.clients[first_client_id].req_historical_data(*args, **kwargs)

    def req_market_data_type(self, *args, **kwargs):
        # Ensure at least one client is connected
        if not self.clients:
            raise RuntimeError("No clients connected")
        first_client_id = next(iter(self.clients))
        return self.clients[first_client_id].req_market_data_type(*args, **kwargs)
    
    def req_tickers(self, *args, **kwargs):
        # Ensure at least one client is connected
        if not self.clients:
            raise RuntimeError("No clients connected")
        first_client_id = next(iter(self.clients))
        return self.clients[first_client_id].req_tickers(*args, **kwargs)


