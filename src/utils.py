from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, OPENROUTER_API_KEY
import re
from time import sleep
from openai import RateLimitError

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
        
        if not OPENAI_API_KEY:
            raise ValueError("❌ OPENAI_API_KEY is missing in environment variables!")
            
        return ChatOpenAI(
            api_key=OPENAI_API_KEY,
            **params
        )
    else:
        # OpenRouter
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not found.")

        return ChatOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            **params
        )
    
def extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found.")

    return match.group(0)

def invoke_structured(llm, prompt, schema, retries=3):
    """for attempt in range(retries):
        try:
            response = llm.invoke(prompt).content

            json_str = extract_json(response)

            return schema.model_validate_json(json_str)

        except RateLimitError as e:

            wait = 5 * (attempt + 1)

            print(f"Rate limited. Waiting {wait}s...")

            sleep(wait)

        except Exception as e:

            if attempt == retries - 1:
                raise

            print(f"Retry {attempt+1}: {e}")

            sleep(2)"""
    try:
        response = llm.invoke(prompt).content
        return schema.model_validate_json(extract_json(response))

    except RateLimitError as e:
        print(e)
        raise