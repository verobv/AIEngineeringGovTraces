from langchain_openai import ChatOpenAI
from src.config import OPENAI_API_KEY, OPENROUTER_API_KEY
import os

def get_llm(model_name: str, temperature: float = 0.0):
    """
    Factory to return the correct LLM client (OpenAI or OpenRouter).
    Handles parameter compatibility for GPT-5 vs older models.
    """
    
    # Define base parameters (common to all models, without 'temperature')
    params = {
        "model": model_name,
    }

    # Determine if it is a GPT-5 series / Reasoning model
    # List all new models that do not support 'temperature'
    reasoning_models = ["gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-5.1-codex", "o3-mini"]
    is_reasoning_model = any(rm in model_name.lower() for rm in reasoning_models)
    
    if is_reasoning_model:
        # === For GPT-5 / High Reasoning Mode ===
        # Must remove parameters like temperature, top_p, etc.
        # Add reasoning parameters
        #params["reasoning_effort"] = "high" # Uncomment to use high reasoning
        pass
    else:
        # === For Traditional Models (GPT-4) ===
        # Retain temperature to control randomness
        params["temperature"] = temperature

    if any(x in model_name.lower() for x in ["gpt", "o1", "o3"]):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY is missing in environment variables!")
            
        return ChatOpenAI(
            api_key=api_key,
            **params
        )
    else:
        # OpenRouter
        return ChatOpenAI(
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            **params
        )