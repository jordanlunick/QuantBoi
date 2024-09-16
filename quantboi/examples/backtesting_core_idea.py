import backtrader as bt
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG
from dataclasses import dataclass
import datetime as dt
import enum
from functools import wraps
from ib_async import (
    IB, util, Contract, Stock, BarDataList)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
from typing import cast, Dict, Union, Optional, List, Tuple
import warnings


class Array(np.ndarray):
    def __new__(cls, array, *, name=None, **kwargs):
        obj = np.asarray(array).view(cls)
        obj.name = name or getattr(array, 'name', '')
        obj._opts = kwargs
        return obj
    
    def __array_finalize__(self, obj):
        if obj is not None:
            self.name = getattr(obj, 'name', '')
            self._opts = getattr(obj, '_opts', {})

    def __reduce__(self):
        value = super().__reduce__()
        return value[:2] + (value[2] + (self.__dict__,),)

    def __setstate__(self, state):
        self.__dict__.update(state[-1])
        super().__setstate__(state[:-1])

    def __bool__(self):
        try:
            return bool(self[-1])
        except IndexError:
            return super().__bool__()

    def __float__(self):
        try:
            return float(self[-1])
        except IndexError:
            return super().__float__()

    def to_series(self):
        warnings.warn("`.to_series()` is deprecated. For pd.Series conversion, use accessor `.s`")
        return self.s

    @property
    def s(self) -> pd.Series:
        values = np.atleast_2d(self)
        index = self._opts['index'][:values.shape[1]]
        return pd.Series(values[0], index=index, name=self.name)

    @property
    def df(self) -> pd.DataFrame:
        values = np.atleast_2d(np.asarray(self))
        index = self._opts['index'][:values.shape[1]]
        df = pd.DataFrame(values.T, index=index, columns=[self.name] * len(values))
        return df


class DataArray:
    """DataArray is a data array accessor."""
    def __init__(self) -> None:#, df: pd.DataFrame) -> None:
        #self.__df = df
        self.__df = pd.DataFrame()
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
    
    def _set_length(self, i):
        self.__i = i
        self.__cache.clear()
    
    def _update(self):
        index = self.__df.index.copy()
        self.__arrays = {col: Array(arr, index=index)
                         for col, arr in self.__df.items()}
        # Leave index as Series because pd.Timestamp nicer API to work with
        self.__arrays['__index'] = index

    def _load(self, df: pd.DataFrame) -> None:
        self.__df = df
        self.__i = len(df)
        self._update()

    def __repr__(self):
        i = min(self.__i, len(self.__df) - 1)
        index = self.__arrays['__index'][i]
        items = ', '.join(f'{k}={v}' for k, v in self.__df.iloc[i].items())
        return f'<Data i={i} ({index}) {items}>'

    def __len__(self):
        return self.__i

    @property
    def df(self) -> pd.DataFrame:
        return (self.__df.iloc[:self.__i]
                if self.__i < len(self.__df)
                else self.__df)

    @property
    def pip(self) -> float:
        if self.__pip is None:
            self.__pip = float(10**-np.median([len(s.partition('.')[-1])
                                               for s in self.__arrays['Close'].astype(str)]))
        return self.__pip

    def __get_array(self, key) -> Array:
        arr = self.__cache.get(key)
        if arr is None:
            arr = self.__cache[key] = cast(Array, self.__arrays[key][:self.__i])
        return arr

    @property
    def Open(self) -> Array:
        return self.__get_array('Open')

    @property
    def High(self) -> Array:
        return self.__get_array('High')

    @property
    def Low(self) -> Array:
        return self.__get_array('Low')

    @property
    def Close(self) -> Array:
        return self.__get_array('Close')

    @property
    def Volume(self) -> Array:
        return self.__get_array('Volume')

    @property
    def index(self) -> pd.DatetimeIndex:
        return self.__get_array('__index')

    # Make pickling in Backtest.optimize() work with our catch-all __getattr__
    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state


class Indicator:
    def __init__(self) -> None:
        pass

    def init(self):
        pass

    def next(self):
        pass


class MyIndicator(Indicator):
    def init(self):
        pass

    def next(self):
        pass


class Strategy:
    def __init__(self):
        pass

    def init(self):
        pass

    def next(self):
        pass


class MyStrategy(Strategy):
    def init(self):
        pass

    def next(self):
        pass
    

class Engine:
    def __init__(self):
        self.data = DataArray()
        self.indicator = None

    def load_dataframe(self, df: pd.DataFrame) -> None:
        self.data._load(df)


engine = Engine()
engine.load_dataframe(GOOG)

indicator = Indicator()