import base64
import logging
import os
from datetime import date

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from .prompts import return_instructions_root
from .tools import call_alloydb_agent, generate_plot
from app.agent_setup import llm

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

def get_root_agent() -> LlmAgent:
    tools = [call_alloydb_agent, generate_plot]
    
    agent = LlmAgent(
        model=llm,
        name="data_science_root_agent",
        instruction=return_instructions_root(),
        global_instruction=(
            f"""
            You are a Data Science AI Assistant.
            Todays date: {date.today()}
            """
        ),
        tools=tools,
        generate_content_config=types.GenerateContentConfig(temperature=0),
    )
    return agent

root_agent = get_root_agent()
