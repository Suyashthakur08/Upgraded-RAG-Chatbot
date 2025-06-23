import requests
import json
from .config import (
    get_headers,
    API_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS
)

def chat_with_groq(user_input, conversation_history=None):
    if conversation_history is None:
        conversation_history = []
    
    # Add system message for coding assistance
    if not conversation_history:
        conversation_history.append({
            "role": "system",
            "content": """You are an expert coding assistant specialized in code generation and development. Your primary focus is to:

1. Generate clean, efficient, and well-documented code
2. Provide code explanations and best practices
3. Suggest optimizations and improvements
4. Help with debugging and error resolution
5. Implement design patterns and architectural solutions
6. Ensure concise and to the point answers

When generating code:
- Use clear and consistent naming conventions
- Include helpful comments and documentation
- Follow language-specific best practices
- Consider edge cases and error handling
- Provide usage examples when relevant

For code-related questions:
- Explain the logic and reasoning behind the code
- Suggest alternative approaches when applicable
- Highlight potential performance implications
- Recommend relevant libraries or tools
- Include testing strategies

Please provide detailed, accurate, and practical coding assistance."""
        })
    
    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    payload = {
        "model": DEFAULT_MODEL,
        "messages": conversation_history,
        "temperature": DEFAULT_TEMPERATURE,
        "max_tokens": DEFAULT_MAX_TOKENS
    }

    try:
        response = requests.post(
            API_BASE_URL,
            headers=get_headers(),
            json=payload
        )
        response.raise_for_status()
        assistant_message = response.json()["choices"][0]["message"]["content"]
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        return assistant_message, conversation_history
    except requests.exceptions.HTTPError as e:
        # Print the full error response for debugging
        print("Groq API error:", response.text)
        return f"Error: {str(e)} | {response.text}", conversation_history
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}", conversation_history

def save_conversation(conversation_history, filename="conversation_history.json"):
    """Save the conversation history to a file"""
    with open(filename, 'w') as f:
        json.dump(conversation_history, f, indent=2)

def load_conversation(filename="conversation_history.json"):
    """Load conversation history from a file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
