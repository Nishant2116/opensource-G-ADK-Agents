from app.agents.sub_agents.alloydb.tools import get_schema
import logging
logging.basicConfig(level=logging.INFO)

s = get_schema()
print(f"--- SCHEMA SIZE ---")
print(f"Characters: {len(s)}")
print(f"Estimated Tokens (char/4): {len(s)/4}")
print(f"First 500 chars:\n{s[:500]}")
