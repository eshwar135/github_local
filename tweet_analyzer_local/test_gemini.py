# test_gemini.py
from gemini_wrapper import call_gemini

prompt = "Summarize: One short sentence saying hello and that this is a test."
out = call_gemini(prompt, max_output_tokens=64)
print("OUTPUT:\n", out)
