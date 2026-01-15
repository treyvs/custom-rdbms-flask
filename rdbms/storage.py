"""
rdbms/storage.py
File-based storage manager using JSON
"""

import json
import os
from typing import Dict, Any


class StorageManager:
    """Manages persistent storage of tables as JSON files"""
    
    def __init__(self, db_path: str = "./db_data"):
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
    
    def _get_table_path(self, table_name: str) -> str:
        """Get file path for a table"""
        return os.path.join(self.db_path, f"{table_name}.json")
    
    def save_table(self, table_name: str, table_data: Dict[str, Any]):
        """Save table data to JSON file"""
        filepath = self._get_table_path(table_name)
        with open(filepath, 'w') as f:
            json.dump(table_data, f, indent=2)
    
    def load_table(self, table_name: str) -> Dict[str, Any]:
        """Load table data from JSON file"""
        filepath = self._get_table_path(table_name)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Table '{table_name}' not found")
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def load_all_tables(self) -> Dict[str, Dict[str, Any]]:
        """Load all tables from storage"""
        tables = {}
        for filename in os.listdir(self.db_path):
            if filename.endswith('.json'):
                table_name = filename[:-5]
                with open(os.path.join(self.db_path, filename), 'r') as f:
                    tables[table_name] = json.load(f)
        return tables
    
    def delete_table(self, table_name: str):
        """Delete table file"""
        filepath = self._get_table_path(table_name)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table file exists"""
        return os.path.exists(self._get_table_path(table_name))
    
    def get_all_table_names(self) -> list:
        """Get list of all table names"""
        tables = []
        for filename in os.listdir(self.db_path):
            if filename.endswith('.json'):
                tables.append(filename[:-5])
        return tables