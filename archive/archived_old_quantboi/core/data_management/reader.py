# /// Project Path: quantboi/core/data_management/reader.py /// #

from archived_old_quantboi import config

import pandas as pd

class Reader:
    def __init__(self) -> None:
        pass

    def load_data(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)
    
    def load_test_sample(self) -> pd.DataFrame:
        return self.load_data(config.TEST_SAMPLE_FILE)
    
    def load_test_dataset(self) -> pd.DataFrame:
        return self.load_data(config.TEST_DATASET_FILE)
    
#reader = Reader()
#test_sample = reader.load_test_sample()
#test_dataset = reader.load_test_dataset()
