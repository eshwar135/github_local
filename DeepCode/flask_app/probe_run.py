import os, traceback
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
API_KEY = os.getenv("GOOGLE_API_KEY")

print("MODEL:", MODEL)
print("GOOGLE_API_KEY present:", bool(API_KEY))

try:
    import google.generativeai as ggen
    ggen.configure(api_key=API_KEY) if API_KEY else None
    print("Calling get_model() ...")
    m = ggen.get_model(MODEL)
    print("get_model() returned:", type(m).__name__)
    if hasattr(m, "model_name"):
        print("model_name:", m.model_name)
except Exception as e:
    print("ERROR:", repr(e))
    traceback.print_exc()
