import logging

from langchain_groq import ChatGroq

from settings import GROQ_MODEL, GROQ_API_KEY

logger = logging.getLogger(__name__)

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
)

logger.info(f"Groq Model {GROQ_MODEL} loaded")
