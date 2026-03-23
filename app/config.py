import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "models/gemini-2.5-flash"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3