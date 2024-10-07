from ib_async import (IB, util, Contract, Stock, BarDataList)
from typing import NamedTuple, Union, List, Optional
from dataclasses import dataclass, field

class ClientId(NamedTuple):
    id: int
    name: Optional[str] = None










# Store classes - something that holds data
    # store.metadata
    # store.get()
    # store.create()
    # store.read()
    # store.update()
    # store.delete()
# Entity classes - something that represents data
# Filter classes - something that filters entities in the store



@dataclass
class ClientStore:
    clientIds: List[ClientId] = field(default_factory=list)

    def add(self, id: int, name: str = None) -> None:
        if not self.check(id):
            self.clientIds.append(ClientId(id, name))
        else:
            print(f"Client ID {id} already exists.")
    
    def delete(self, id: int) -> None:
        for client in self.clientIds:
            if client.id == id:
                self.clientIds.remove(client)
                return

    def check(self, id: int) -> bool:
        for client in self.clientIds:
            if client.id == id:
                return True
        return False


@dataclass
class ContractStore:
    contracts: List[Contract] = field(default_factory=list)

    def add(self, contract: Contract) -> None:
        self.contracts.append(contract)

    def delete(self, contract: Contract) -> None:
        self.contracts.remove(contract)

    def check(self, contract: Contract) -> bool:
        return contract in self.contracts
    
    def get(self, contract: Contract) -> Contract:
        pass


class IBAPI:
    def __init__(self, ):
        self.ib: IB = IB()
        self.clients: ClientStore = ClientStore()
        self.contracts: ContractStore = ContractStore()
    
    def connect(self, host: str, port: int, clientId: int) -> None:
        if not self.clients.check(clientId):
            self.ib.connect(host, port, clientId=clientId)
            self.clients.add(clientId)
        else:
            print(f"Client ID {clientId} already connected.")

    def disconnect(self, clientId: int) -> None:
        if self.clients.check(clientId):
            self.ib.disconnect()
            self.clients.delete(clientId)
        else:
            print(f"Client ID {clientId} not connected.")


    



util.startLoop()
ib = IBAPI()
ib.connect('127.0.0.1', 7497, 1)
contract = Stock('SPY', 'SMART', 'USD')
ib.ib.qualifyContracts(contract)
ib.contracts.add(contract)
ib.disconnect(1)