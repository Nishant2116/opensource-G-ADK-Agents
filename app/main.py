import logging
from contextlib import asynccontextmanager
import os
import uuid

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from google.adk.runners import InMemoryRunner
from google.adk.events.event import Event
from google.genai.types import Content, Part

from . import agent_setup
import sqlite3
from pydantic import BaseModel
from typing import List

from .agents.agent import root_agent

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

file_handler = logging.FileHandler("agent.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")

app = FastAPI(title="G-ADK Agents", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return FileResponse("app/static/index.html")

@app.get("/data-manager")
async def data_manager():
    return FileResponse("app/static/data_manager.html")

def get_db_connection():
    conn = sqlite3.connect('demo.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/tables")
async def list_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return {"tables": tables}

@app.get("/api/table/{table_name}")
async def get_table_data(table_name: str):
    if not table_name.isidentifier():
        return {"error": "Invalid table name"}
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT rowid, * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        data = [dict(row) for row in rows]
        conn.close()
        return {"columns": columns, "data": data}
    except Exception as e:
        conn.close()
        return {"error": str(e)}

@app.delete("/api/table/{table_name}")
async def drop_table(table_name: str):
    if not table_name.isidentifier():
        return {"error": "Invalid table name"}
    conn = get_db_connection()
    try:
        conn.execute(f"DROP TABLE {table_name}")
        conn.commit()
        conn.close()
        return {"message": f"Table {table_name} deleted"}
    except Exception as e:
        conn.close()
        return {"error": str(e)}

@app.delete("/api/table/{table_name}/row/{rowid}")
async def delete_row(table_name: str, rowid: int):
    if not table_name.isidentifier():
        return {"error": "Invalid table name"}
    conn = get_db_connection()
    try:
        conn.execute(f"DELETE FROM {table_name} WHERE rowid = ?", (rowid,))
        conn.commit()
        conn.close()
        return {"message": "Row deleted"}
    except Exception as e:
        conn.close()
        return {"error": str(e)}

class InsertRowRequest(BaseModel):
    data: dict

@app.post("/api/table/{table_name}/insert")
async def insert_row(table_name: str, request: InsertRowRequest):
    if not table_name.isidentifier():
        return {"error": "Invalid table name"}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        columns = list(request.data.keys())
        values = list(request.data.values())
        placeholders = ", ".join(["?"] * len(values))
        cols_str = ", ".join(columns)
        
        query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return {"message": "Row inserted successfully"}
    except Exception as e:
        conn.close()
        return {"error": str(e)}

class ColumnDef(BaseModel):
    name: str
    type: str
    primary_key: bool = False
    not_null: bool = False

class CreateTableRequest(BaseModel):
    name: str
    columns: List[ColumnDef]

@app.post("/api/create-table")
async def create_table(request: CreateTableRequest):
    if not request.name.isidentifier():
        return {"error": "Invalid table name"}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cols_sql = []
        for col in request.columns:
            cname = col.name
            if not cname.isidentifier():
                 raise ValueError(f"Invalid column name: {cname}")

            ctype = col.type.upper()
            allowed_types = ["TEXT", "INTEGER", "REAL", "DATE", "BLOB"]
            if ctype not in allowed_types:
                ctype = "TEXT"
            
            definition = f"{cname} {ctype}"
            if col.primary_key:
                definition += " PRIMARY KEY"
                if ctype == "INTEGER":
                    definition += " AUTOINCREMENT"
            elif col.not_null:
                definition += " NOT NULL"
                
            cols_sql.append(definition)
        
        query = f"CREATE TABLE {request.name} ({', '.join(cols_sql)})"
        cursor.execute(query)
        conn.commit()
        conn.close()
        return {"message": f"Table '{request.name}' created successfully"}
    except Exception as e:
        conn.close()
        return {"error": str(e)}

@app.post("/agent/query")
async def query_agent(prompt: str):
    logger.info(f"Received query: {prompt}")
    try:
        local_runner = InMemoryRunner(agent=root_agent, app_name="agents")
        session = await local_runner.session_service.create_session(user_id="user", app_name="agents")
        session_id = session.id
        logger.info(f"Session created: {session_id}")
        
        content = Content(parts=[Part(text=prompt)], role="user")
        response_obj = local_runner.run_async(user_id="user", session_id=session_id, new_message=content)
        
        full_response = ""
        if hasattr(response_obj, '__aiter__'):
            async for chunk in response_obj:
                if hasattr(chunk, 'content') and chunk.content and chunk.content.parts:
                    for part in chunk.content.parts:
                        if part.text:
                            full_response += part.text
                elif hasattr(chunk, 'text') and chunk.text:
                        full_response += chunk.text
                elif hasattr(chunk, 'delta') and chunk.delta:
                        full_response += chunk.delta
        else:
            response = await response_obj
            full_response = str(response)
        
        logger.info(f"\n[RAW_AGENT_OUTPUT_START]\n{full_response}\n[RAW_AGENT_OUTPUT_END]\n")
        cleaned_output = clean_response(full_response)
        logger.info(f"\n[CLEANED_OUTPUT_START]\n{cleaned_output}\n[CLEANED_OUTPUT_END]\n")
        
        return {"response": cleaned_output}

    except Exception as e:
        error_msg = str(e)
        
        # Rate limit handling
        if "RateLimitError" in error_msg or "429" in error_msg:
             logger.warning(f"Rate limit: {e}")
             import re
             match = re.search(r"try again in (\d+(\.\d+)?)s", error_msg)
             wait_time = match.group(1) if match else "20"
             return {"response": f"⚠️ **System Busy**: Rate limit reached. Please try again in **{wait_time} seconds**."}
        
        # Tool validation / BadRequest handling (e.g., exec_python missing)
        if "Tool call validation failed" in error_msg or "exec_python" in error_msg:
             logger.warning(f"Tool validation error (likely hallucinations): {e}")
             return {"response": "⚠️ **System Busy**: The AI is momentarily overwhelmed. Please wait 10-15 seconds and try asking again."}

        logger.error(f"Error processing query: {e}")
        import traceback
        traceback.print_exc()
        
        # Generic user-friendly error
        return {"response": "⚠️ **System Busy**: An internal error occurred. Please wait a moment and try again."}

def clean_response(text: str) -> str:
    lower_text = text.lower()
    end_tag = "</answer>"
    start_tag = "<answer>"
    
    end_idx = lower_text.rfind(end_tag)
    
    if end_idx != -1:
        start_idx = lower_text.rfind(start_tag, 0, end_idx)
        
        if start_idx != -1:
            return text[start_idx : end_idx + len(end_tag)]
    
    logger.warning("No <answer>...</answer> block pair found in output.")
    lines = text.split('\n')
    cleaned_lines = []
    banned_starts = ["WE NEED TO", "I WILL NOW", "LET'S CALL", "FOLLOWING THE", "STEP 1"]
    for line in lines:
        stripped = line.strip().upper()
        if not any(stripped.startswith(b) for b in banned_starts):
            cleaned_lines.append(line)
            
    return '\n'.join(cleaned_lines).strip()
