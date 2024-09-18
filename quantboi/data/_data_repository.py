from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, TypeVar, Generic, List, Any

class MetaDataRepository(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)
        if not new_cls.__abstractmethods__:
            new_cls._data = {}
        return new_cls


class AbstractDataRepository(ABC):
    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass

class BaseDataRepository(AbstractDataRepository, metaclass=MetaDataRepository):
    _data: Dict[str, Any] = {}
    _name: str = "BaseDataRepository"

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def create(self, key: str, value: Any) -> None:
        self._data[key] = value

    def read(self) -> Dict[str, Any]:
        return self._data

    def update(self, key: str, value: Any) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        del self._data[key]

class DataRepository(BaseDataRepository):
    def __init__(self):
        self._data = {}

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def create(self, key: str, value: Any) -> None:
        self._data[key] = value

    def read(self) -> Dict[str, Any]:
        return self._data

    def update(self, key: str, value: Any) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        del self._data[key]
    

