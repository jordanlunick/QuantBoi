from abc import ABC, abstractmethod
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


# Implementation of in-memory data store using dataclass
@dataclass
class InMemoryDataStore(AbstractDataStore[Any]):
    data: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str) -> Optional[Any]:
        return self.data.get(key)

    def create(self, key: str, value: Any) -> None:
        self.data[key] = value

    def read(self) -> Dict[str, Any]:
        return self.data

    def update(self, key: str, value: Any) -> None:
        self.data[key] = value

    def delete(self, key: str) -> None:
        if key in self.data:
            del self.data[key]
        else:
            raise KeyError(f"Key '{key}' not found in data store.")
        
    def __getstate__(self) -> object:
        return {'data': self.data}
    
    def __setstate__(self, state: object) -> None:
        self.data = state['data']
        

class ArrayStore(InMemoryDataStore):
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

    
