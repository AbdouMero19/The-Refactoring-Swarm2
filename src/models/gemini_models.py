import os
from dotenv import load_dotenv , find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables (looks for GOOGLE_API_KEY in .env)
load_dotenv(find_dotenv())

def get_llm(model_type="flash"):
    """
    Returns the configured Gemini Model.
    
    Args:
        model_type (str): 'flash' for speed (Auditor/Fixer), 'pro' for reasoning (Judge).
    
    Returns:
        ChatGoogleGenerativeAI: The configured LangChain model object.
    """
    # Select the specific model version
    # 'flash' -> Faster, cheaper, higher rate limits (Good for loops)
    # 'pro'   -> Smarter, better logic, lower rate limits (Good for one-off complex tasks)
    model_name = "gemini-1.5-flash" if model_type == "flash" else "gemini-1.5-pro"
    
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0,      # CRITICAL: Keep it 0 for deterministic code generation
        max_retries=2,      # Auto-retry if Google's API has a hiccup
        
    )