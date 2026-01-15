"""
rdbms/engine.py
Core Database Engine - Handles tables, columns, indexes, and operations
Author: Built with AI assistance (Claude)
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import copy


class DataType:
    """Supported column data types"""
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    DATETIME = "DATETIME"
    
    @staticmethod
    def validate(value: Any, data_type: str) -> bool:
        """Validate if value matches data type"""
        if value is None:
            return True
        
        try:
            if data_type == DataType.INTEGER:
                int(value)
                return True
            elif data_type == DataType.TEXT:
                return isinstance(value, str)
            elif data_type == DataType.FLOAT:
                float(value)
                return True
            elif data_type == DataType.BOOLEAN:
                return isinstance(value, bool) or value in [0, 1, "true", "false"]
            elif data_type == DataType.DATETIME:
                if isinstance(value, str):
                    datetime.fromisoformat(value)
                return True
        except:
            return False
        return False
    
    @staticmethod
    def convert(value: Any, data_type: str) -> Any:
        """Convert value to appropriate type"""
        if value is None:
            return None
            
        if data_type == DataType.INTEGER:
            return int(value)
        elif data_type == DataType.TEXT:
            return str(value)
        elif data_type == DataType.FLOAT:
            return float(value)
        elif data_type == DataType.BOOLEAN:
            if isinstance(value, bool):
                return value
            return value in [1, "true", "True"]
        elif data_type == DataType.DATETIME:
            if isinstance(value, str):
                return value
            return datetime.now().isoformat()
        return value


class Column:
    """Represents a table column with constraints"""
    def __init__(self, name: str, data_type: str, nullable: bool = True, 
                 primary_key: bool = False, unique: bool = False, 
                 auto_increment: bool = False):
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.primary_key = primary_key
        self.unique = unique
        self.auto_increment = auto_increment
    
    def to_dict(self) -> Dict:
        """Serialize column to dictionary"""
        return {
            'name': self.name,
            'data_type': self.data_type,
            'nullable': self.nullable,
            'primary_key': self.primary_key,
            'unique': self.unique,
            'auto_increment': self.auto_increment
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Column':
        """Deserialize column from dictionary"""
        return Column(**data)


class Index:
    """Simple hash-based index for faster lookups"""
    def __init__(self, column_name: str):
        self.column_name = column_name
        self.index_map: Dict[Any, List[int]] = {}
    
    def add(self, value: Any, row_id: int):
        """Add value to index"""
        if value not in self.index_map:
            self.index_map[value] = []
        self.index_map[value].append(row_id)
    
    def remove(self, value: Any, row_id: int):
        """Remove value from index"""
        if value in self.index_map:
            if row_id in self.index_map[value]:
                self.index_map[value].remove(row_id)
    
    def lookup(self, value: Any) -> List[int]:
        """Find row IDs with this value - O(1) average"""
        return self.index_map.get(value, [])


class Table:
    """Represents a database table with rows and indexes"""
    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = {col.name: col for col in columns}
        self.rows: List[Dict[str, Any]] = []
        self.next_id = 1
        self.indexes: Dict[str, Index] = {}
        
        # Create indexes for primary and unique keys
        for col in columns:
            if col.primary_key or col.unique:
                self.indexes[col.name] = Index(col.name)
    
    def _get_next_auto_increment(self, col_name: str) -> int:
        """Get next auto-increment value"""
        max_val = 0
        for row in self.rows:
            if row.get(col_name) is not None:
                max_val = max(max_val, row[col_name])
        return max_val + 1
    
    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a row into the table"""
        row = {'_id': self.next_id}
        
        for col_name, col in self.columns.items():
            value = data.get(col_name)
            
            # Handle auto-increment
            if col.auto_increment:
                value = self._get_next_auto_increment(col_name)
            
            # Check nullable constraint
            if value is None and not col.nullable and not col.auto_increment:
                raise ValueError(f"Column '{col_name}' cannot be NULL")
            
            # Validate and convert type
            if value is not None:
                if not DataType.validate(value, col.data_type):
                    raise ValueError(f"Invalid type for column '{col_name}'. Expected {col.data_type}")
                value = DataType.convert(value, col.data_type)
            
            # Check unique constraint
            if col.unique or col.primary_key:
                if col_name in self.indexes:
                    existing = self.indexes[col_name].lookup(value)
                    if existing:
                        raise ValueError(f"Duplicate value for unique column '{col_name}'")
            
            row[col_name] = value
        
        # Add to indexes
        for col_name, index in self.indexes.items():
            if col_name in row:
                index.add(row[col_name], self.next_id)
        
        self.rows.append(row)
        self.next_id += 1
        return row
    
    def select(self, columns: Optional[List[str]] = None, 
               where: Optional[Dict[str, Any]] = None,
               order_by: Optional[str] = None,
               limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select rows from the table"""
        results = []
        
        for row in self.rows:
            # Apply WHERE clause
            if where:
                match = True
                for col, val in where.items():
                    if row.get(col) != val:
                        match = False
                        break
                if not match:
                    continue
            
            # Select columns
            if columns:
                result_row = {col: row.get(col) for col in columns if col in row}
                result_row['_id'] = row['_id']
            else:
                result_row = row.copy()
            
            results.append(result_row)
        
        # Apply ORDER BY
        if order_by:
            reverse = False
            if order_by.startswith('-'):
                reverse = True
                order_by = order_by[1:]
            results.sort(key=lambda x: x.get(order_by, ''), reverse=reverse)
        
        # Apply LIMIT
        if limit:
            results = results[:limit]
        
        return results
    
    def update(self, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Update rows in the table"""
        updated_count = 0
        
        for row in self.rows:
            # Check WHERE clause
            match = True
            for col, val in where.items():
                if row.get(col) != val:
                    match = False
                    break
            
            if match:
                # Remove from indexes
                for col_name, index in self.indexes.items():
                    if col_name in row:
                        index.remove(row[col_name], row['_id'])
                
                # Update row
                for col_name, value in data.items():
                    if col_name in self.columns:
                        col = self.columns[col_name]
                        
                        # Validate
                        if value is not None:
                            if not DataType.validate(value, col.data_type):
                                raise ValueError(f"Invalid type for column '{col_name}'")
                            value = DataType.convert(value, col.data_type)
                        
                        row[col_name] = value
                
                # Re-add to indexes
                for col_name, index in self.indexes.items():
                    if col_name in row:
                        index.add(row[col_name], row['_id'])
                
                updated_count += 1
        
        return updated_count
    
    def delete(self, where: Dict[str, Any]) -> int:
        """Delete rows from the table"""
        to_delete = []
        
        for i, row in enumerate(self.rows):
            match = True
            for col, val in where.items():
                if row.get(col) != val:
                    match = False
                    break
            
            if match:
                # Remove from indexes
                for col_name, index in self.indexes.items():
                    if col_name in row:
                        index.remove(row[col_name], row['_id'])
                to_delete.append(i)
        
        # Delete in reverse order to maintain indices
        for i in reversed(to_delete):
            del self.rows[i]
        
        return len(to_delete)
    
    def to_dict(self) -> Dict:
        """Serialize table to dictionary for storage"""
        return {
            'name': self.name,
            'columns': [col.to_dict() for col in self.columns.values()],
            'rows': self.rows,
            'next_id': self.next_id
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Table':
        """Deserialize table from dictionary"""
        columns = [Column.from_dict(col) for col in data['columns']]
        table = Table(data['name'], columns)
        table.rows = data['rows']
        table.next_id = data['next_id']
        
        # Rebuild indexes
        for row in table.rows:
            for col_name, index in table.indexes.items():
                if col_name in row:
                    index.add(row[col_name], row['_id'])
        
        return table


class Database:
    """Main database engine coordinating tables and operations"""
    def __init__(self, storage_manager):
        self.storage = storage_manager
        self.tables: Dict[str, Table] = {}
        self._load_tables()
    
    def _load_tables(self):
        """Load all tables from storage"""
        for table_name, table_data in self.storage.load_all_tables().items():
            self.tables[table_name] = Table.from_dict(table_data)
    
    def _save_table(self, table_name: str):
        """Save a table to storage"""
        if table_name in self.tables:
            self.storage.save_table(table_name, self.tables[table_name].to_dict())
    
    def create_table(self, name: str, columns: List[Column]) -> Table:
        """Create a new table"""
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")
        
        table = Table(name, columns)
        self.tables[name] = table
        self._save_table(name)
        return table
    
    def drop_table(self, name: str):
        """Delete a table"""
        if name not in self.tables:
            raise ValueError(f"Table '{name}' does not exist")
        
        del self.tables[name]
        self.storage.delete_table(name)
    
    def get_table(self, name: str) -> Table:
        """Get a table by name"""
        if name not in self.tables:
            raise ValueError(f"Table '{name}' does not exist")
        return self.tables[name]
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert into table"""
        table = self.get_table(table_name)
        result = table.insert(data)
        self._save_table(table_name)
        return result
    
    def select(self, table_name: str, columns: Optional[List[str]] = None,
               where: Optional[Dict[str, Any]] = None,
               order_by: Optional[str] = None,
               limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select from table"""
        table = self.get_table(table_name)
        return table.select(columns, where, order_by, limit)
    
    def update(self, table_name: str, data: Dict[str, Any], 
               where: Dict[str, Any]) -> int:
        """Update table"""
        table = self.get_table(table_name)
        count = table.update(data, where)
        self._save_table(table_name)
        return count
    
    def delete(self, table_name: str, where: Dict[str, Any]) -> int:
        """Delete from table"""
        table = self.get_table(table_name)
        count = table.delete(where)
        self._save_table(table_name)
        return count
    
    def join(self, left_table: str, right_table: str, 
             on_left: str, on_right: str,
             join_type: str = "INNER") -> List[Dict[str, Any]]:
        """Join two tables"""
        left = self.get_table(left_table)
        right = self.get_table(right_table)
        results = []
        
        if join_type == "INNER":
            for left_row in left.rows:
                for right_row in right.rows:
                    if left_row.get(on_left) == right_row.get(on_right):
                        # Merge rows with prefixed column names
                        merged = {}
                        for k, v in left_row.items():
                            merged[f"{left_table}.{k}"] = v
                        for k, v in right_row.items():
                            merged[f"{right_table}.{k}"] = v
                        results.append(merged)
        
        return results
    
    def list_tables(self) -> List[str]:
        """Get list of all table names"""
        return list(self.tables.keys())