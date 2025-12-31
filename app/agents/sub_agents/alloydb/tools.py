import sqlite3
import logging
from google.adk.agents import LlmAgent

DB_FILE = "demo.db"
logger = logging.getLogger(__name__)

def get_schema():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        full_schema_info = []
        
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
            
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cursor.fetchall()
            
            table_info = f"""
            Table: {table}
            Columns: {', '.join(columns)}
            Sample Rows: {rows}
            """
            full_schema_info.append(table_info)
            
        conn.close()
        
        if not full_schema_info:
            return "No tables found in database."
            
        return "\n".join(full_schema_info)
        
    except Exception as e:
        return f"Error loading schema: {e}"

def execute_sql(query: str):
    logger.info(f"Executing SQL: {query}")
    try:
        query = query.replace("```sql", "").replace("```", "").strip()
        
        if query.strip().upper().startswith("SELECT") and "LIMIT" not in query.upper():
            query += " LIMIT 10"

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        result = [dict(zip(columns, row)) for row in rows]
        result_str = str(result)
        if len(result_str) > 2000:
             return result_str[:2000] + "... (truncated)"
        return result_str
    except Exception as e:
        return f"Error executing SQL: {e}"

from app.agent_setup import llm

alloydb_agent = LlmAgent(
    model=llm,
    name="alloydb_agent",
    instruction="""
    You are a SQL expert. Your task is to answer user questions by querying the local SQLite database.
    
    CRITICAL: DO NOT assume table names. You must discover them.
    
    1. FIRST, call the `get_schema` tool to inspect the database structure.
    2. Based on the schema, generate a valid SQLite query (Always include descriptive columns!).
    3. Use the `execute_sql` tool.
    4. Return the results.

    <CONSTRAINTS>
    - Focus on accurate SQL generation.
    - Return the tool output directly.
    </CONSTRAINTS>
    """,
    tools=[get_schema, execute_sql]
)
