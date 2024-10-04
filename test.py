from quantboi.data import (BaseDataRepository, BaseDataStore)

import pickle

# Instantiate the repository with the default in-memory store
repo = BaseDataRepository()

# Perform some CRUD operations
repo.create("item1", {"name": "Item One", "price": 100})
repo.create("item2", {"name": "Item Two", "price": 200})

print(repo.read())  # Read all items

repo.update("item1", {"name": "Updated Item One", "price": 150})
print(repo.get("item1"))  # Read specific item

repo.delete("item2")
print(repo.read())  # Read remaining items

# Pickle the repository
pickled_repo = pickle.dumps(repo)

# Unpickle the repository
unpickled_repo = pickle.loads(pickled_repo)
print(unpickled_repo.read())  # Verify the state is preserved

data_store: BaseDataStore = repo._data_store

test = BaseDataStore()