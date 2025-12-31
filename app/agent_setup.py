import os
from dotenv import load_dotenv

import litellm
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("WARNING: Missing GROQ_API_KEY in .env")
    GROQ_API_KEY = "dummy_key"

litellm.api_key = GROQ_API_KEY
litellm.api_base = "https://api.groq.com/openai/v1"
litellm.num_retries = 10

MODEL_NAME = "openai/openai/gpt-oss-120b"

llm = LiteLlm(
    model=MODEL_NAME,
    api_key=GROQ_API_KEY,
    api_base="https://api.groq.com/openai/v1",
)
