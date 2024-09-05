# /// Project Path: quantboi/core/data.py /// #

from quantboi import config
from quantboi.core.data_management import (
    Reader, MarketBook, Symbol, Stock, Option,
    TestDataObject, read_test_data,
    create_test_data_object, load_test_data)


class Data:
    def __init__(self) -> None:
        self.reader = Reader()

#data = load_test_data()
