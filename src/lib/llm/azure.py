import logging

from langchain_openai import AzureChatOpenAI

from settings import AZURE_OPENAI_API_VERSION, AZURE_OPENAI_CHAT_DEPLOYMENT_NAME, AZURE_MODEL_TEMPERATURE

logger = logging.getLogger(__name__)

llm = AzureChatOpenAI(
    openai_api_version=AZURE_OPENAI_API_VERSION,
    azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
    temperature=AZURE_MODEL_TEMPERATURE
)
logger.info(f"Model Azure {AZURE_OPENAI_CHAT_DEPLOYMENT_NAME} loaded")
