from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass, field
from typing import Dict, Optional, TypeVar, Generic, List, Any

from quantboi import config

# Generic type for DataStore
T = TypeVar('T')



# Abstract class for Data Store (responsible for actual storage)
class AbstractDataStore(ABC, Generic[T]):
    @abstractmethod
    def get(self, key: str) -> Optional[T]:
        pass

    @abstractmethod
    def create(self, key: str, value: T) -> None:
        pass

    @abstractmethod
    def read(self) -> Dict[str, T]:
        pass

    @abstractmethod
    def update(self, key: str, value: T) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass


# Base class for Data Store (responsible for actual storage)
@dataclass
class BaseDataStore(AbstractDataStore[Any]):
    _data: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str) -> Optional[Any]:
        return self._data.get(key)

    def create(self, key: str, value: Any) -> None:
        self._data[key] = value

    def read(self) -> Dict[str, Any]:
        return self._data

    def update(self, key: str, value: Any) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
        else:
            raise KeyError(f"Key '{key}' not found in data store.")


# Abstract repository class enforcing CRUD interface
class AbstractDataRepository(ABC):#, metaclass=ABCMeta):
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


# Base repository class with in-memory data store
@dataclass
class BaseDataRepository:#(AbstractDataRepository):
    _data_store: BaseDataStore = field(default_factory=BaseDataStore)
    
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

#    def __getstate__(self) -> object:
#        state = self.__dict__.copy()
#        return state
    
#    def __setstate__(self, state: dict) -> None:
#        self.__dict__.update(state)


@dataclass
class SimpleRepo:
    _data_store: Dict[str, Any] = field(default_factory=dict)


if __name__ == "__main__":
    import pickle

    # Instantiate the repository with the default in-memory store
    repo = BaseDataRepository()

    """
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

    data_store = repo._data_store
    """