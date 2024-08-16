# /// Project Path: quantboi/core/data.py /// #

from quantboi.core.data_management import TEST_SAMPLE, TEST_DATASET

import pandas as pd


class Data:
    def __init__(self) -> None:
        pass

    def load_data(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)
    
    def load_test_sample(self) -> pd.DataFrame:
        return self.load_data(TEST_SAMPLE)
    
    def load_test_dataset(self) -> pd.DataFrame:
        return self.load_data(TEST_DATASET)
    