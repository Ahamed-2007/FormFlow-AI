"""Python port of includes/ollama.php.

The PHP version hand-rolled an HTTP client over a raw TCP socket because
plain PHP has no bundled HTTP client. Python's standard `requests` library
does the same job; the externally visible behaviour (URL, model, timeouts,
error messages) is kept identical.
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_CONNECT_TIMEOUT = 5
OLLAMA_REQUEST_TIMEOUT = 120


class OllamaError(RuntimeError):
    """Raised for any failure talking to the local Ollama model."""


def ensure_ollama_is_reachable():
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=OLLAMA_CONNECT_TIMEOUT)
    except requests.exceptions.Timeout as error:
        raise OllamaError("The local AI model took too long to respond. Please try again.") from error
    except requests.exceptions.RequestException as error:
        raise OllamaError("Unable to connect to the local AI model. Please make sure Ollama is running.") from error
    if not response.ok:
        raise OllamaError("The local AI model returned an HTTP error.")


def generate_ollama_response(prompt, max_tokens=700, request_timeout=OLLAMA_REQUEST_TIMEOUT):
    ensure_ollama_is_reachable()
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tokens},
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=(OLLAMA_CONNECT_TIMEOUT, request_timeout))
    except requests.exceptions.Timeout as error:
        raise OllamaError("The local AI model took too long to respond. Please try again.") from error
    except requests.exceptions.RequestException as error:
        raise OllamaError("Unable to connect to the local AI model. Please make sure Ollama is running.") from error

    if not response.ok:
        raise OllamaError("The local AI model returned an HTTP error.")

    try:
        data = response.json()
    except ValueError as error:
        raise OllamaError("The local AI model returned invalid JSON. Please try again.") from error

    answer = str(data.get("response", "")).strip()
    if answer == "":
        raise OllamaError("The local AI model returned an empty answer. Please try again.")
    return answer
