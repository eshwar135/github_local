import os
from dotenv import load_dotenv

print("Loading .env ...")
load_dotenv()

print("GEMINI_MODEL =", os.getenv("GEMINI_MODEL"))
print("GOOGLE_API_KEY present?", bool(os.getenv("GOOGLE_API_KEY")))
