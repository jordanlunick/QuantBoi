# /// Root Path: root/src/config.py /// #


# /// Import libraries /// #
from dotenv import load_dotenv
import os


# /// Import modules /// #


# /// Define global variables /// #


# Directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Parent directory (i.e., root)
ROOT_DIR = os.path.abspath(
    os.path.join(SCRIPT_DIR, os.pardir, os.pardir))

# Load environment variables
DOTENV = os.path.join(ROOT_DIR, '.env')
load_dotenv(DOTENV)

# Quantboi directory
QB_DIR = os.path.join(ROOT_DIR, 'quantboi')

# Data directory
DATA_DIR = os.path.join(QB_DIR, 'data')
INPUT_DIR = os.path.join(DATA_DIR, 'input')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')

# Directory of the logs
LOG_DIR = os.path.join(ROOT_DIR, 'logs')

# Directory of the databases
DB_DIR = os.path.join(ROOT_DIR, 'db/')
DB_NAME = 'cwdb'

