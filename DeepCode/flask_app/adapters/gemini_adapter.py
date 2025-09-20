import os
from .base import ModelAdapter

class GeminiAdapter(ModelAdapter):
    def __init__(self, api_key=None, api_key_file=None, model=None):
        self.api_key = api_key
        self.api_key_file = api_key_file
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        self.backend = None
        self.client = None

        # Try google.generativeai first
        try:
            import google.generativeai as ggen
            if self.api_key:
                ggen.configure(api_key=self.api_key)
            elif self.api_key_file and os.path.exists(self.api_key_file):
                with open(self.api_key_file) as f:
                    ggen.configure(api_key=f.read().strip())
            self.backend = "google.generativeai"
            self.client = ggen
        except Exception:
            pass

        # Try google.genai fallback
        if not self.backend:
            try:
                import google.genai as gapi
                if self.api_key:
                    gapi.configure(api_key=self.api_key)
                elif self.api_key_file and os.path.exists(self.api_key_file):
                    with open(self.api_key_file) as f:
                        gapi.configure(api_key=f.read().strip())
                self.backend = "google.genai"
                self.client = gapi
            except Exception:
                pass

    def info(self):
        return {
            "model": self.model,
            "backend": self.backend,
            "configured": bool(self.client),
        }

    def _coerce_response_to_text(self, resp):
        """Extract text from SDK response objects if possible."""
        if resp is None:
            return None
        if hasattr(resp, "text") and resp.text:
            return resp.text
        if hasattr(resp, "candidates") and resp.candidates:
            cand = resp.candidates[0]
            if hasattr(cand, "content") and cand.content:
                return str(cand.content)
            return str(cand)
        if isinstance(resp, dict):
            if "text" in resp:
                return str(resp["text"])
            if "candidates" in resp and resp["candidates"]:
                return str(resp["candidates"][0])
        return str(resp)

    def generate(self, prompt, max_tokens=256, temperature=0.0):
        if not self.client:
            raise RuntimeError("No Gemini client configured")

        if self.backend == "google.generativeai":
            ggen = self.client
            try:
                # Preferred modern API: GenerativeModel.generate_content
                if hasattr(ggen, "GenerativeModel"):
                    model = ggen.GenerativeModel(self.model)
                    resp = model.generate_content(prompt)
                    text = self._coerce_response_to_text(resp)
                    if text:
                        return text
                    return str(resp)

                # Fallback: get_model path
                if hasattr(ggen, "get_model"):
                    model_obj = ggen.get_model(self.model)
                    if hasattr(model_obj, "generate_content"):
                        resp = model_obj.generate_content(prompt)
                        text = self._coerce_response_to_text(resp)
                        if text:
                            return text
                        return str(resp)

                raise RuntimeError("No supported generation method found in google.generativeai")

            except Exception as e:
                raise RuntimeError(f"GeminiAdapter (google.generativeai) call failed: {e}")

        if self.backend == "google.genai":
            gapi = self.client
            try:
                return gapi.generate_text(
                    model=self.model,
                    prompt=prompt,
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ).result
            except Exception as e:
                raise RuntimeError(f"GeminiAdapter (google.genai) call failed: {e}")

        raise RuntimeError("Unsupported backend")
