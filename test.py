from rdbms.engine import Database, Column, DataType
from rdbms.storage import StorageManager

# Initialize
storage = StorageManager("./test_db")
db = Database(storage)

# Create table
db.create_table('products', [
    Column('id', DataType.INTEGER, primary_key=True, auto_increment=True),
    Column('name', DataType.TEXT, nullable=False),
    Column('price', DataType.FLOAT)
])

# Insert
db.insert('products', {'name': 'Laptop', 'price': 999.99})
db.insert('products', {'name': 'Mouse', 'price': 29.99})

# Select all
products = db.select('products')
print(f"Found {len(products)} products")

# Select with filter
expensive = db.select('products', where={'name': 'Laptop'})
print(f"Laptop price: ${expensive[0]['price']}")

# Update
db.update('products', {'price': 899.99}, where={'name': 'Laptop'})

# Delete
db.delete('products', where={'name': 'Mouse'})

# Clean up
db.drop_table('products')

print("✓ All tests passed!")