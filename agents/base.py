import os
from agno.models.openai import OpenAIChat


def get_model(temperature: float = 0.5):
    """
    LLM model factory. To swap providers, edit only this file.
    Reads OPENAI_MODEL_ID and OPENAI_API_KEY from environment.
    """
    model_id = os.getenv("OPENAI_MODEL_ID", "gpt-4o")
    return OpenAIChat(
        id=model_id,
        temperature=temperature,
        max_tokens=4096,
    )
