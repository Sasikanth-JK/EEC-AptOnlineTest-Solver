import asyncio
import google.generativeai as gemini
from google.api_core.exceptions import ResourceExhausted
from logger import LOGGER
from config import Config

def initialize_gemini(api_key: str) -> gemini.GenerativeModel:
    gemini.configure(api_key=api_key)
    
    response_schema = {
        "type": "object",
        "properties": {
            "option_id": {"type": "string"},
            "explanation": {"type": "string"}
        },
        "required": ["option_id", "explanation"]
    }
    
    model = gemini.GenerativeModel(
        model_name = Config.MODEL_NAME,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": response_schema,
        }
    )
    LOGGER.info("Gemini model initialized.")
    return model

async def safe_gen_wrapper(model, prompt, retries=3, delay=30):
    try:
        return await asyncio.wait_for(safe_generate(model, prompt, retries, delay), timeout=92)
    except asyncio.TimeoutError:
        LOGGER.error("Model response timed out.")
        return None
    
async def safe_generate(model, prompt, retries=3, delay=30):
    for attempt in range(retries):
        try:
            return model.generate_content(prompt)
        except ResourceExhausted:
            if attempt < retries - 1:
                print(f"Quota exceeded, retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                raise