# Importing config.py from quantboi package to test the import functionality

# Should always be successful
try:
    import archived_old_quantboi.config
    print('Import was successful!')
except ImportError:
    print('Import failed!')

try:
    import archived_old_quantboi.core.data_management as data
    print('Import was successful!')
    print(data.TEST_DATASET_FILE)

except ImportError:
    print('Import failed!')

