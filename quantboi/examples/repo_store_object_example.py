from dataclasses import dataclass, field
from typing import Dict, Optional, TypeVar, Generic

# Step 1: Define generic DataObject classes (User, Product)

@dataclass
class User:
    id: int
    name: str
    email: str

@dataclass
class Product:
    id: int
    name: str
    price: float

# Step 2: Define a generic DataStore for handling a single type of DataObject
T = TypeVar('T')  # Generic type for DataObject

@dataclass
class DataStore(Generic[T]):
    objects: Dict[int, T] = field(default_factory=dict)

    def add(self, obj: T):
        self.objects[obj.id] = obj

    def get(self, obj_id: int) -> Optional[T]:
        return self.objects.get(obj_id)

    def remove(self, obj_id: int):
        if obj_id in self.objects:
            del self.objects[obj_id]


# Step 3: Define the DataRepository that holds multiple DataStores

@dataclass
class DataRepository:
    user_store: DataStore[User]
    product_store: DataStore[Product]

    def get_user(self, user_id: int) -> Optional[User]:
        return self.user_store.get(user_id)

    def add_user(self, user: User):
        self.user_store.add(user)

    def remove_user(self, user_id: int):
        self.user_store.remove(user_id)

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.product_store.get(product_id)

    def add_product(self, product: Product):
        self.product_store.add(product)

    def remove_product(self, product_id: int):
        self.product_store.remove(product_id)


# Step 4: Usage example

# Initialize individual DataStores
user_store = DataStore[User]()
product_store = DataStore[Product]()

# Initialize DataRepository that holds multiple DataStores
repository = DataRepository(user_store=user_store, product_store=product_store)

# Add users and products
user1 = User(id=1, name="Alice", email="alice@example.com")
product1 = Product(id=101, name="Laptop", price=999.99)

repository.add_user(user1)
repository.add_product(product1)

# Fetch and print data
retrieved_user = repository.get_user(1)
retrieved_product = repository.get_product(101)

print(f"Retrieved User: {retrieved_user}")
print(f"Retrieved Product: {retrieved_product}")

# Remove data
repository.remove_user(1)
repository.remove_product(101)

# Try to fetch removed data
retrieved_user = repository.get_user(1)
retrieved_product = repository.get_product(101)

print(f"User after removal: {retrieved_user}")
print(f"Product after removal: {retrieved_product}")
