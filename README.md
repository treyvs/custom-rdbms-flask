# Simple RDBMS - Relational Database Management System

A lightweight, feature-rich relational database management system built in Python with SQL-like interface, complete CRUD operations, indexing, and constraint support.

## 📁 Project Structure

```
flask_project/
│
├── app.py                      # Flask web application
├── rdbms/
│   ├── __init__.py            # Package initializer
│   ├── engine.py              # Core DB engine (tables, indexes, operations)
│   ├── parser.py              # SQL-like parser (regex-based)
│   ├── storage.py             # JSON file storage manager
│   └── repl.py                # Interactive REPL interface
│
├── templates/
│   └── index.html             # Web UI template
│
├── static/
│   └── style.css              # Web UI styles
│
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
└── db_data/                   # Database storage (created on first run)
    ├── users.json
    └── tasks.json
```

## 🎯 Features

### Core Database Features
- ✅ **Data Types**: INTEGER, TEXT, FLOAT, BOOLEAN, DATETIME
- ✅ **Constraints**: PRIMARY KEY, UNIQUE, NOT NULL, AUTO_INCREMENT
- ✅ **CRUD Operations**: Full Create, Read, Update, Delete support
- ✅ **Indexing**: Automatic hash-based indexing on primary/unique keys
- ✅ **Joins**: INNER JOIN support
- ✅ **Persistence**: JSON file storage (one file per table)
- ✅ **SQL Interface**: Familiar SQL-like syntax
- ✅ **REPL Mode**: Interactive command-line interface

### Web Application Features
- ✅ User Management (CREATE, DELETE)
- ✅ Task Management (CREATE, UPDATE, DELETE)
- ✅ Task Status Tracking (Pending → In Progress → Completed)
- ✅ Priority Levels (Low, Medium, High)
- ✅ Real-time Statistics Dashboard
- ✅ Modern, Responsive UI

## 🚀 Quick Start

### Installation

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install flask

# 4. Create __init__.py in rdbms folder
touch rdbms/__init__.py  # or manually create empty file
```

### Running the REPL

```bash
python -m rdbms.repl
```

Example REPL session:
```sql
SQL> CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL
);
✓ Table 'users' created successfully.

SQL> INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com');
✓ 1 row inserted with ID: 1

SQL> SELECT * FROM users;
_id | id | username | email              
----------------------------------------
1   | 1  | alice    | alice@example.com  

1 row(s) returned

SQL> .tables
Tables:
  - users (1 rows)

SQL> .schema users
Table: users
  id                   INTEGER         (PRIMARY KEY, AUTO_INCREMENT)
  username             TEXT            (UNIQUE, NOT NULL)
  email                TEXT            (NOT NULL)

SQL> .exit
Goodbye!
```

### Running the Web Application

```bash
python app.py
```

Then visit: **http://127.0.0.1:5000**

## 📚 SQL Syntax Reference

### CREATE TABLE
```sql
CREATE TABLE table_name (
  column_name DATA_TYPE [PRIMARY KEY] [UNIQUE] [NOT NULL] [AUTO_INCREMENT],
  ...
);
```

### INSERT
```sql
INSERT INTO table_name (col1, col2, ...) VALUES (val1, val2, ...);
```

### SELECT
```sql
SELECT * FROM table_name;
SELECT col1, col2 FROM table_name WHERE condition ORDER BY column LIMIT n;
```

### UPDATE
```sql
UPDATE table_name SET col1=val1, col2=val2 WHERE condition;
```

### DELETE
```sql
DELETE FROM table_name WHERE condition;
```

### DROP TABLE
```sql
DROP TABLE table_name;
```

## 💻 Programmatic Usage

```python
from rdbms.engine import Database, Column, DataType
from rdbms.storage import StorageManager

# Initialize
storage = StorageManager("./my_database")
db = Database(storage)

# Create table
db.create_table('products', [
    Column('id', DataType.INTEGER, primary_key=True, auto_increment=True),
    Column('name', DataType.TEXT, nullable=False),
    Column('price', DataType.FLOAT, nullable=False)
])

# Insert
db.insert('products', {
    'name': 'Laptop',
    'price': 999.99
})

# Select
products = db.select('products', where={'price': 999.99})

# Update
db.update('products', {'price': 899.99}, where={'name': 'Laptop'})

# Delete
db.delete('products', where={'id': 1})
```

## 🏗️ Architecture

### Components

1. **engine.py** - Core database engine
   - `DataType`: Type validation and conversion
   - `Column`: Column definition with constraints
   - `Index`: Hash-based indexing for O(1) lookups
   - `Table`: Row storage, operations, constraint enforcement
   - `Database`: Table orchestration and persistence

2. **storage.py** - File storage manager
   - JSON serialization/deserialization
   - File I/O operations
   - Table persistence

3. **parser.py** - SQL parser
   - Regex-based tokenization
   - Command parsing (CREATE, INSERT, SELECT, UPDATE, DELETE)
   - Value type conversion

4. **repl.py** - Interactive interface
   - Command execution
   - Result formatting
   - Special commands (.tables, .schema, .help, .exit)

5. **app.py** - Flask web application
   - RESTful routes
   - CRUD operations
   - Statistics calculation

### Data Storage Format

Tables stored as JSON files:
```json
{
  "name": "users",
  "columns": [
    {
      "name": "id",
      "data_type": "INTEGER",
      "nullable": false,
      "primary_key": true,
      "auto_increment": true
    }
  ],
  "rows": [
    {
      "_id": 1,
      "id": 1,
      "username": "alice",
      "email": "alice@example.com"
    }
  ],
  "next_id": 2
}
```

## 🎓 Example Use Cases

### Blog System
```python
# Create posts table
db.create_table('posts', [
    Column('id', DataType.INTEGER, primary_key=True, auto_increment=True),
    Column('title', DataType.TEXT, nullable=False),
    Column('content', DataType.TEXT),
    Column('author_id', DataType.INTEGER, nullable=False),
    Column('published', DataType.BOOLEAN)
])

# Insert post
db.insert('posts', {
    'title': 'My First Post',
    'content': 'Hello World!',
    'author_id': 1,
    'published': True
})

# Get published posts
posts = db.select('posts', where={'published': True}, order_by='-id')
```

### E-Commerce Inventory
```python
# Products with indexing
db.create_table('products', [
    Column('sku', DataType.TEXT, primary_key=True),
    Column('name', DataType.TEXT, nullable=False),
    Column('category', DataType.TEXT),
    Column('stock', DataType.INTEGER)
])

# Fast lookup by category (uses index)
electronics = db.select('products', where={'category': 'Electronics'})

# Update stock
db.update('products', {'stock': 50}, where={'sku': 'LAPTOP-001'})
```

## ⚠️ Limitations

1. **WHERE Clause**: Only supports AND with equality operators
2. **Joins**: Only INNER JOIN implemented
3. **Transactions**: No transaction support (each operation is atomic)
4. **Concurrency**: Not thread-safe (single-process only)
5. **Query Optimization**: No query planner
6. **Scale**: Designed for small to medium datasets (< 100k rows)

## 📝 Credits & Acknowledgments

### Author
Built with AI assistance (Claude by Anthropic)

### AI Contributions
- SQL parsing regex patterns optimized with AI
- Index structure design influenced by standard database patterns
- Error handling and validation logic
- Web application UI/UX design

### Inspiration
- **SQLite**: Lightweight database architecture
- **PostgreSQL**: SQL syntax standards
- **Redis**: Key-value indexing approach

## 🐛 Testing

Run basic tests:

```python
# test_db.py
from rdbms.engine import Database, Column, DataType
from rdbms.storage import StorageManager

storage = StorageManager("./test_db")
db = Database(storage)

# Create
db.create_table('test', [
    Column('id', DataType.INTEGER, primary_key=True, auto_increment=True),
    Column('name', DataType.TEXT, unique=True)
])

# Insert
result = db.insert('test', {'name': 'Alice'})
assert result['id'] == 1

# Read
rows = db.select('test', where={'name': 'Alice'})
assert len(rows) == 1

# Update
count = db.update('test', {'name': 'Bob'}, where={'id': 1})
assert count == 1

# Delete
count = db.delete('test', where={'id': 1})
assert count == 1

# Cleanup
db.drop_table('test')
print("✓ All tests passed!")
```

## 🔮 Future Enhancements

- [ ] OR conditions in WHERE
- [ ] LEFT/RIGHT/OUTER joins
- [ ] Aggregation functions (COUNT, SUM, AVG)
- [ ] GROUP BY and HAVING
- [ ] Sub-queries
- [ ] Foreign key constraints
- [ ] Transaction support (BEGIN, COMMIT, ROLLBACK)
- [ ] Multi-threading with locks
- [ ] Query optimization
- [ ] Binary storage format

## 📄 License

Educational/demonstration project. Free to use and modify.

---

**Enjoy using Simple RDBMS! 🚀**