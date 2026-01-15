"""
rdbms/parser.py
SQL-like parser using regex
Credits: Regex patterns optimized with AI assistance
"""

import re
from typing import Tuple, Dict, Any, List
from rdbms.engine import Column


class SQLParser:
    """Parse SQL-like commands"""
    
    @staticmethod
    def parse(sql: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse SQL command and return (command_type, parameters)
        
        Supported commands:
        - CREATE TABLE
        - DROP TABLE
        - INSERT INTO
        - SELECT
        - UPDATE
        - DELETE
        """
        sql = sql.strip().rstrip(';')
        
        # CREATE TABLE
        create_match = re.match(
            r'CREATE\s+TABLE\s+(\w+)\s*\((.*)\)', 
            sql, 
            re.IGNORECASE | re.DOTALL
        )
        if create_match:
            table_name = create_match.group(1)
            cols_str = create_match.group(2)
            columns = SQLParser._parse_columns(cols_str)
            return 'CREATE', {'table': table_name, 'columns': columns}
        
        # DROP TABLE
        drop_match = re.match(r'DROP\s+TABLE\s+(\w+)', sql, re.IGNORECASE)
        if drop_match:
            return 'DROP', {'table': drop_match.group(1)}
        
        # INSERT INTO
        insert_match = re.match(
            r'INSERT\s+INTO\s+(\w+)\s*\((.*?)\)\s*VALUES\s*\((.*?)\)',
            sql, 
            re.IGNORECASE
        )
        if insert_match:
            table = insert_match.group(1)
            columns = [c.strip() for c in insert_match.group(2).split(',')]
            values = SQLParser._parse_values(insert_match.group(3))
            data = dict(zip(columns, values))
            return 'INSERT', {'table': table, 'data': data}
        
        # SELECT
        select_match = re.match(
            r'SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*?))?(?:\s+ORDER\s+BY\s+([\w-]+))?(?:\s+LIMIT\s+(\d+))?$',
            sql, 
            re.IGNORECASE
        )
        if select_match:
            cols = select_match.group(1).strip()
            columns = None if cols == '*' else [c.strip() for c in cols.split(',')]
            table = select_match.group(2)
            where = SQLParser._parse_where(select_match.group(3)) if select_match.group(3) else None
            order_by = select_match.group(4)
            limit = int(select_match.group(5)) if select_match.group(5) else None
            
            return 'SELECT', {
                'table': table,
                'columns': columns,
                'where': where,
                'order_by': order_by,
                'limit': limit
            }
        
        # UPDATE
        update_match = re.match(
            r'UPDATE\s+(\w+)\s+SET\s+(.*?)\s+WHERE\s+(.*)',
            sql, 
            re.IGNORECASE
        )
        if update_match:
            table = update_match.group(1)
            set_clause = SQLParser._parse_set(update_match.group(2))
            where = SQLParser._parse_where(update_match.group(3))
            return 'UPDATE', {'table': table, 'data': set_clause, 'where': where}
        
        # DELETE
        delete_match = re.match(
            r'DELETE\s+FROM\s+(\w+)\s+WHERE\s+(.*)',
            sql, 
            re.IGNORECASE
        )
        if delete_match:
            table = delete_match.group(1)
            where = SQLParser._parse_where(delete_match.group(2))
            return 'DELETE', {'table': table, 'where': where}
        
        raise ValueError(f"Unable to parse SQL: {sql}")
    
    @staticmethod
    def _parse_columns(cols_str: str) -> List[Column]:
        """Parse column definitions from CREATE TABLE"""
        columns = []
        
        # Split by comma, but handle commas inside constraints
        col_defs = []
        current = []
        paren_depth = 0
        
        for char in cols_str + ',':
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == ',' and paren_depth == 0:
                col_defs.append(''.join(current).strip())
                current = []
                continue
            current.append(char)
        
        for col_def in col_defs:
            if not col_def:
                continue
            
            col_def = col_def.strip()
            parts = col_def.split()
            
            if len(parts) < 2:
                continue
            
            name = parts[0]
            data_type = parts[1]
            
            col_def_upper = col_def.upper()
            primary_key = 'PRIMARY' in col_def_upper and 'KEY' in col_def_upper
            unique = 'UNIQUE' in col_def_upper
            not_null = 'NOT' in col_def_upper and 'NULL' in col_def_upper
            auto_inc = 'AUTO_INCREMENT' in col_def_upper
            
            columns.append(Column(
                name=name,
                data_type=data_type,
                nullable=not not_null,
                primary_key=primary_key,
                unique=unique,
                auto_increment=auto_inc
            ))
        
        return columns
    
    @staticmethod
    def _parse_values(values_str: str) -> List[Any]:
        """Parse VALUES clause"""
        values = []
        current = []
        in_string = False
        
        for char in values_str:
            if char == "'" and (not current or current[-1] != '\\'):
                in_string = not in_string
                current.append(char)
            elif char == ',' and not in_string:
                values.append(SQLParser._convert_value(''.join(current).strip()))
                current = []
            else:
                current.append(char)
        
        if current:
            values.append(SQLParser._convert_value(''.join(current).strip()))
        
        return values
    
    @staticmethod
    def _convert_value(val: str) -> Any:
        """Convert string value to appropriate Python type"""
        val = val.strip()
        
        if val.startswith("'") and val.endswith("'"):
            return val[1:-1]
        elif val.lower() == 'null':
            return None
        elif val.lower() in ['true', 'false']:
            return val.lower() == 'true'
        elif '.' in val:
            try:
                return float(val)
            except:
                return val
        else:
            try:
                return int(val)
            except:
                return val
    
    @staticmethod
    def _parse_where(where_str: str) -> Dict[str, Any]:
        """Parse WHERE clause (simple equality with AND only)"""
        if not where_str:
            return {}
        
        where = {}
        conditions = re.split(r'\s+AND\s+', where_str, flags=re.IGNORECASE)
        
        for condition in conditions:
            match = re.match(r'(\w+)\s*=\s*(.+)', condition.strip())
            if match:
                col = match.group(1)
                val = SQLParser._convert_value(match.group(2))
                where[col] = val
        
        return where
    
    @staticmethod
    def _parse_set(set_str: str) -> Dict[str, Any]:
        """Parse SET clause"""
        data = {}
        
        for assignment in set_str.split(','):
            match = re.match(r'(\w+)\s*=\s*(.+)', assignment.strip())
            if match:
                col = match.group(1)
                val = SQLParser._convert_value(match.group(2))
                data[col] = val
        
        return data