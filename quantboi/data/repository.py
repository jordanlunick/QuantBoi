from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass, field
from typing import Dict, Optional, TypeVar, Generic, List, Any

from quantboi import config
from quantboi.data.store import (
    AbstractDataStore, InMemoryDataStore)


# Generic type for DataStore
T = TypeVar('T')


# Meta class to enforce proper class setup
class MetaDataRepository(ABCMeta):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)
        # Ensure that the class has a valid _data attribute if it's not abstract
        if not new_cls.__abstractmethods__:
            if not hasattr(new_cls, '_data_store'):
                raise AttributeError(f"Class {name} must define a '_data_store' attribute.")
        return new_cls


# Abstract repository class enforcing CRUD interface
#class AbstractDataRepository(metaclass=ABCMeta):
class AbstractDataRepository(ABC, metaclass=ABCMeta):
    _data_store: AbstractDataStore

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def create(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def read(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass


# Base repository providing shared functionality using the metaclass and DataStore
class BaseDataRepository(AbstractDataRepository, metaclass=MetaDataRepository):
    _data_store: AbstractDataStore = InMemoryDataStore() # Default to in-memory store
    
    def __init__(self, data_store: Optional[AbstractDataStore] = None):
        self._data_store = data_store or InMemoryDataStore()

    def get(self, key: str) -> Any:
        return self._data_store.get(key)

    def create(self, key: str, value: Any) -> None:
        if key is None:
            raise ValueError("Key cannot be None")
        self._data_store.create(key, value)

    def read(self) -> Dict[str, Any]:
        return self._data_store.read()

    def update(self, key: str, value: Any) -> None:
        if key not in self._data_store.read():
            raise KeyError(f"Key '{key}' does not exist.")
        self._data_store.update(key, value)

    def delete(self, key: str) -> None:
        if key not in self._data_store.read():
            raise KeyError(f"Key '{key}' does not exist.")
        self._data_store.delete(key)

    def __getstate__(self) -> object:
        state = self.__dict__.copy()
        return state
    
    def __setstate__(self, state: object) -> None:
        self.__dict__.update(state)


# Concrete Data Repository that can extend with additional logic
class DataRepository(BaseDataRepository):
    def __init__(self, data_store: Optional[AbstractDataStore] = None):
        # Allow custom DataStore injection, fallback to default
        #self._data_store = data_store or InMemoryDataStore()
        super().__init__(data_store)

    # You can add additional logic specific to this repository if needed

if __name__ == "__main__":
    import pickle

    # Instantiate the repository with the default in-memory store
    repo = DataRepository()

    # Perform some CRUD operations
    repo.create("item1", {"name": "Item One", "price": 100})
    repo.create("item2", {"name": "Item Two", "price": 200})

    print(repo.read())  # Read all items

    repo.update("item1", {"name": "Updated Item One", "price": 150})
    print(repo.get("item1"))  # Read specific item

    repo.delete("item2")
    print(repo.read())  # Read remaining items

    # Pickle the repository
    pickled_repo = pickle.dumps(repo)

    # Unpickle the repository
    unpickled_repo = pickle.loads(pickled_repo)
    print(unpickled_repo.read())  # Verify the state is preserved