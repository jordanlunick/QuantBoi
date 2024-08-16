# /// Project Path: quantboi/core/data_management/__init__.py /// #

import os


# target_path = 'quantboi\config'
from quantboi.config import (INPUT_DIR)
print(INPUT_DIR)




TEST_SAMPLE = os.path.join(INPUT_DIR, 'test_sample.csv')
TEST_DATASET = os.path.join(INPUT_DIR, 'test_dataset.csv')