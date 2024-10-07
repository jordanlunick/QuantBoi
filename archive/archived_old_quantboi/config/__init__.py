# /// Project Path: QuantBoi/quantboi/config/__init__.py /// #


# /// Import libraries /// #
from dotenv import load_dotenv
import os


# /// Import modules /// #



# /// Define global variables /// #
# Project path
PROJECT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 
        os.pardir, os.pardir
    )
)
#print(f'Project path: {PROJECT_PATH}')

# Load environment variables
DOTENV = os.path.join(PROJECT_PATH, '.env')
#print(f'DOTENV path: {DOTENV}')
load_dotenv(DOTENV)
#print(f'PYTHONPATH: {os.getenv("PYTHONPATH")}')


# Quantboi directory
QB_DIR = os.path.join(PROJECT_PATH, 'quantboi')

# Data directory
DATA_DIR = os.path.join(QB_DIR, 'data')
INPUT_DIR = os.path.join(DATA_DIR, 'input')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
TEST_SAMPLE_FILE = os.path.join(INPUT_DIR, 'test_sample.csv')
TEST_DATASET_FILE = os.path.join(INPUT_DIR, 'test_dataset.csv')

# Directory of the logs
LOG_DIR = os.path.join(PROJECT_PATH, 'logs')

# Directory of the databases
DB_DIR = os.path.join(PROJECT_PATH, 'db/')
DB_NAME = 'cwdb'

