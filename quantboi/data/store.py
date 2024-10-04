from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, TypeVar, Generic, List, Any

from quantboi import config
from quantboi.data.array import Array

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
#    def __init__(self) -> None:
#        super().__init__()
#        self._data: Dict[str, Any] = {}
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
        
#    def __getstate__(self) -> object:
#        state = self.__dict__.copy()
#        return state
    
#    def __setstate__(self, state: dict) -> None:
#        self.__dict__.update(state)
        

class ArrayStore(BaseDataStore):
    def __init__(self):
        super().__init__()
        self.__i: int = 0
        self.__pip: Optional[float] = None
        self.__cache: Dict[str, Array] = {}
        self.__arrays: Dict[str, Array] = {}
        self._update()

    def __getitem__(self, item):
        return self.__get_array(item)

    def __getattr__(self, item):
        try:
            return self.__get_array(item)
        except KeyError:
            raise AttributeError(f"Column '{item}' not in data") from None

    def __get_array(self, item):
        if item in self.__cache:
            return self.__cache[item]
        if item in self.__arrays:
            return self.__arrays[item]
        if item in self.data:
            self.__cache[item] = self.data[item]
            return self.__cache[item]
        raise KeyError(f"Column '{item}' not in data")

    def __setitem__(self, key, value):
        self.data[key] = value
        self._update()

    def __setattr__(self, key, value):
        if key in self.__dict__:
            super().__setattr__(key, value)
        else:
            self.__setitem__(key, value)

    def __setitem__(self, key, value):
        self.data[key] = value
        self._update()

    def __setattr__(self, key, value):
        if key in self.__dict__:
            super().__setattr__(key, value)
        else:
            self.__setitem__(key, value)

    def __iter__(self):
        return iter(self.__arrays)

    def __contains__(self, item):
        return item in self.__arrays

    def __len__(self):
        return len(self.__arrays)

    def __bool__(self):
        return bool(self.__arrays)

    def __float__(self):
        return float(self.__arrays)

    def _update(self):
        self.__arrays = {k: v for k, v in self.data.items() if isinstance(v, Array)}
        self.__cache = {k: v for k, v in self.data.items() if not isinstance(v, Array)}
        self.__pip = None
        for k, v in self.__arrays.items():
            if self.__pip is None:
                self.__pip = v._opts.get('pip')
            elif self.__pip != v._opts.get('pip'):
                self.__pip = None
                break

    
if __name__ == "__main__":
    import pickle

    # Instantiate the data store
    store = BaseDataStore()

    # Perform some CRUD operations
    store.create("item1", {"name": "Item One", "price": 100})
    store.create("item2", {"name": "Item Two", "price": 200})

    print(store.read())  # Read all items

    store.update("item1", {"name": "Updated Item One", "price": 150})
    print(store.get("item1"))  # Read specific item

    store.delete("item2")

    print(store.read())  # Read remaining items

    # Pickle the store
    pickled_store = pickle.dumps(store)

    # Unpickle the store
    unpickled_store = pickle.loads(pickled_store)
    print(store.read())  # Read all items
