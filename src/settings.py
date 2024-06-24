import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-70b-8192"

AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"]
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
AZURE_MODEL_TEMPERATURE = os.environ.get("AZURE_OPENAI_TEMPERATURE", 0.5)
