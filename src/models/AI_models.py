import os
from dotenv import load_dotenv , find_dotenv
from langchain_mistralai import ChatMistralAI
# from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables (looks for GOOGLE_API_KEY in .env)
load_dotenv(find_dotenv())

# def get_llm(model_type="flash"):
#     """
#     Returns the configured Gemini Model.
    
#     Args:
#         model_type (str): 'flash' for speed (Auditor/Fixer), 'pro' for reasoning (Judge).
    
#     Returns:
#         ChatGoogleGenerativeAI: The configured LangChain model object.
#     """
#     # Select the specific model version
#     # 'flash' -> Faster, cheaper, higher rate limits (Good for loops)
#     # 'pro'   -> Smarter, better logic, lower rate limits (Good for one-off complex tasks)
#     model_name = "gemini-2.0-flash" if model_type == "flash" else "gemini-2.0-pro"
    
#     return ChatGoogleGenerativeAI(
#         model=model_name,
#         temperature=0,      # CRITICAL: Keep it 0 for deterministic code generation
#         max_retries=2,      # Auto-retry if Google's API has a hiccup
        
#     )


def get_llm(model_type="medium"):
    """
    Returns the Mistral LLM instance.
    """
    
    # Map your "flash" or "pro" keywords to specific Mistral models
    if model_type == "small":
        # Fast model for quick tasks 
        model_name = "mistral-small-latest" 
    elif model_type == "medium":
        # Powerful model for coding (Fixer/Judge)
        model_name = "mistral-medium-latest"
    elif model_type == "large":
        # Most powerful model for complex reasoning
        model_name = "mistral-large-latest"    

    print(f"🔌 Loading LLM: {model_name}")

    llm = ChatMistralAI(
        model=model_name,
        temperature=0,
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        max_retries=5,
        timeout=60
        # Mistral handles context windows automatically, usually 32k or 128k
    )

    return llm