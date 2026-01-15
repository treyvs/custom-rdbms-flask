"""
rdbms/repl.py
Interactive REPL mode for database operations
"""

from typing import List, Dict, Any
from rdbms.engine import Database
from rdbms.storage import StorageManager
from rdbms.parser import SQLParser


def print_results(results: List[Dict[str, Any]]):
    """Pretty print query results in table format"""
    if not results:
        print("No results found.")
        return
    
    # Get all column names
    columns = list(results[0].keys())
    
    # Calculate column widths
    widths = {col: len(str(col)) for col in columns}
    for row in results:
        for col in columns:
            val_str = str(row.get(col, ''))
            widths[col] = max(widths[col], len(val_str))
    
    # Print header
    header = " | ".join(str(col).ljust(widths[col]) for col in columns)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in results:
        print(" | ".join(str(row.get(col, '')).ljust(widths[col]) for col in columns))
    
    print(f"\n{len(results)} row(s) returned")


def print_table_schema(db: Database, table_name: str):
    """Print table schema"""
    if table_name not in db.tables:
        print(f"Table '{table_name}' not found.")
        return
    
    table = db.tables[table_name]
    print(f"\nTable: {table_name}")
    print("-" * 60)
    
    for col in table.columns.values():
        constraints = []
        if col.primary_key:
            constraints.append("PRIMARY KEY")
        if col.unique:
            constraints.append("UNIQUE")
        if not col.nullable:
            constraints.append("NOT NULL")
        if col.auto_increment:
            constraints.append("AUTO_INCREMENT")
        
        constraint_str = f" ({', '.join(constraints)})" if constraints else ""
        print(f"  {col.name:20} {col.data_type:15}{constraint_str}")
    print()


def print_help():
    """Print help message"""
    print("\n" + "="*60)
    print("SIMPLE RDBMS - COMMAND REFERENCE")
    print("="*60)
    print("\nSQL Commands:")
    print("  CREATE TABLE name (col1 TYPE [constraints], ...)")
    print("  DROP TABLE name")
    print("  INSERT INTO name (col1, col2) VALUES (val1, val2)")
    print("  SELECT * FROM name [WHERE col=val] [ORDER BY col] [LIMIT n]")
    print("  UPDATE name SET col=val WHERE condition")
    print("  DELETE FROM name WHERE condition")
    print("\nSpecial Commands:")
    print("  .tables          - List all tables")
    print("  .schema <table>  - Show table schema")
    print("  .help            - Show this help message")
    print("  .exit            - Exit REPL")
    print("\nData Types:")
    print("  INTEGER, TEXT, FLOAT, BOOLEAN, DATETIME")
    print("\nConstraints:")
    print("  PRIMARY KEY, UNIQUE, NOT NULL, AUTO_INCREMENT")
    print("="*60 + "\n")


def repl(db_path: str = "./db_data"):
    """Start interactive REPL"""
    print("=" * 60)
    print("SIMPLE RDBMS - Interactive Mode")
    print("=" * 60)
    print("Type '.help' for commands, '.exit' to quit")
    print("=" * 60)
    
    storage = StorageManager(db_path)
    db = Database(storage)
    
    while True:
        try:
            sql = input("\nSQL> ").strip()
            
            if not sql:
                continue
            
            # Special commands
            if sql == '.exit':
                print("Goodbye!")
                break
            
            elif sql == '.help':
                print_help()
                continue
            
            elif sql == '.tables':
                tables = db.list_tables()
                if tables:
                    print("\nTables:")
                    for table_name in tables:
                        row_count = len(db.tables[table_name].rows)
                        print(f"  - {table_name} ({row_count} rows)")
                else:
                    print("No tables found.")
                continue
            
            elif sql.startswith('.schema'):
                parts = sql.split()
                if len(parts) == 2:
                    print_table_schema(db, parts[1])
                else:
                    print("Usage: .schema <table_name>")
                continue
            
            # Parse and execute SQL
            cmd_type, params = SQLParser.parse(sql)
            
            if cmd_type == 'CREATE':
                db.create_table(params['table'], params['columns'])
                print(f"✓ Table '{params['table']}' created successfully.")
            
            elif cmd_type == 'DROP':
                db.drop_table(params['table'])
                print(f"✓ Table '{params['table']}' dropped successfully.")
            
            elif cmd_type == 'INSERT':
                result = db.insert(params['table'], params['data'])
                print(f"✓ 1 row inserted with ID: {result['_id']}")
            
            elif cmd_type == 'SELECT':
                results = db.select(
                    params['table'],
                    params.get('columns'),
                    params.get('where'),
                    params.get('order_by'),
                    params.get('limit')
                )
                print_results(results)
            
            elif cmd_type == 'UPDATE':
                count = db.update(params['table'], params['data'], params['where'])
                print(f"✓ {count} row(s) updated.")
            
            elif cmd_type == 'DELETE':
                count = db.delete(params['table'], params['where'])
                print(f"✓ {count} row(s) deleted.")
        
        except KeyboardInterrupt:
            print("\n\nUse '.exit' to quit")
            continue
        
        except Exception as e:
            print(f"✗ Error: {str(e)}")


if __name__ == "__main__":
    repl()