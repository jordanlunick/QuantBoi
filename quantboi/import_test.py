# Importing config.py from quantboi package to test the import functionality

# Relative import of config.py from quantboi package
# May not work in all cases
try:
    import config
    print('Import was successful!')
except ImportError:
    print('Import failed!')

# Should always be successful
try:
    import quantboi.config
    print('Import was successful!')
except ImportError:
    print('Import failed!')

# Does not seem to work well with relative imports
try:
    from ..quantboi import config
    print('Import was successful!')
except ImportError:
    print('Import failed!')
