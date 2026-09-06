import os
import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


class OllamaError(RuntimeError):
    """AI service error."""


def ensure_ollama_is_reachable():
    if not GROQ_API_KEY:
        raise OllamaError(
            "AI service is not configured. Please set GROQ_API_KEY."
        )


def generate_ollama_response(prompt, max_tokens=700, request_timeout=120):
    if not GROQ_API_KEY:
        raise OllamaError(
            "AI service is not configured. Please set GROQ_API_KEY."
        )

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=request_timeout
        )
    except requests.exceptions.Timeout as error:
        raise OllamaError(
            "The AI service took too long to respond. Please try again."
        ) from error
    except requests.exceptions.RequestException as error:
        raise OllamaError(
            "Unable to connect to the AI service. Please try again."
        ) from error

    if not response.ok:
        raise OllamaError(
            f"The AI service returned an HTTP error ({response.status_code})."
        )

    try:
        data = response.json()
        answer = data["choices"][0]["message"]["content"].strip()
    except (ValueError, KeyError, IndexError, TypeError) as error:
        raise OllamaError(
            "The AI service returned an invalid answer. Please try again."
        ) from error

    if not answer:
        raise OllamaError(
            "The AI service returned an empty answer. Please try again."
        )

    return answer