from langchain.chat_models import init_chat_model
from config.settings import settings

llm = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai",
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.1,
    max_tokens=4000,
    max_retries=3
)
