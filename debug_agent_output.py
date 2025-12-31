import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.agents.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.adk.events.event import Event
from google.genai.types import Content, Part

async def debug_query():
    print("--- STARTING DEBUG SESSION ---")
    
    # 1. Setup Runner
    runner = InMemoryRunner(agent=root_agent, app_name="DebugRunner")
    session = await runner.session_service.create_session(user_id="debug_user", app_name="DebugRunner")
    print(f"Session ID: {session.id}")

    # 2. Prepare Input
    prompt = "Display a pie chart of sales by product"
    content = Content(parts=[Part(text=prompt)], role="user")
    
    # 3. Execute Run
    print(f"Sending Query: '{prompt}'")
    response_obj = runner.run_async(user_id="debug_user", session_id=session.id, new_message=content)
    
    print("\n--- RAW CHUNKS ---")
    full_text = ""
    
    async for chunk in response_obj:
        # print(f"Chunk Type: {type(chunk)}")
        
        chunk_text = ""
        if hasattr(chunk, 'content') and chunk.content and chunk.content.parts:
            for part in chunk.content.parts:
                if part.text:
                    chunk_text += part.text
        elif hasattr(chunk, 'text') and chunk.text:
             chunk_text += chunk.text
        
        if chunk_text:
            print(f"RAW TEXT CHUNK: {repr(chunk_text)}")
            full_text += chunk_text

    print("\n--- FULL RESPONSE ---")
    print(full_text)
    print("---------------------")

if __name__ == "__main__":
    asyncio.run(debug_query())
