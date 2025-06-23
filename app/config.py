import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Server Configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Model Configuration
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'mixtral-8x7b-32768')
DEFAULT_TEMPERATURE = float(os.getenv('DEFAULT_TEMPERATURE', 0.7))
DEFAULT_MAX_TOKENS = int(os.getenv('DEFAULT_MAX_TOKENS', 2048))

# Conversation Settings
CONVERSATIONS_DIR = os.getenv('CONVERSATIONS_DIR', 'conversations')

# API Settings
API_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

# Headers configuration
def get_headers():
    return {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
