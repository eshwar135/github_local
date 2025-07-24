import requests

class LLMAssistant:
    def __init__(self, model: str = "llama3"):
        self.url = "http://localhost:11434/api/generate"
        self.model = model

    def ask(self, task_list: list, question: str) -> str:
        task_context = "\n".join([f"- {t['title']} ({t['status']})" for t in task_list])
        prompt = f"Here are my tasks:\n{task_context}\n\nQuestion: {question}"
        try:
            response = requests.post(self.url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            })
            return response.json().get("response", "").strip()
        except Exception as e:
            return f"Error: {e}"
