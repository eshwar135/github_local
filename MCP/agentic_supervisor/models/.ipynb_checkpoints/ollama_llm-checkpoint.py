# models/ollama_llm.py
import subprocess

MODEL_NAME = "gemma:2b"  # Local Ollama model must be pulled already

def query_ollama(prompt: str) -> str:
    """
    Run local inference with Ollama CLI.
    Requires `ollama pull gemma:2b` already done.
    """
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL_NAME],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        response = result.stdout.decode().strip()
        if not response:
            return "[LLM] Empty response."
        return response
    except Exception as e:
        return f"[LLM Error] {str(e)}"
