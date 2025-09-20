# probe_generate.py -- safe, non-destructive probe to find available generation methods
import importlib, traceback, json, os, sys

MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def try_import(name):
    try:
        mod = importlib.import_module(name)
        print(f"Imported {name} OK")
        return mod
    except Exception as e:
        print(f"Import {name} FAILED: {e!r}")
        return None

def list_attrs(obj, label):
    attrs = sorted(a for a in dir(obj) if not a.startswith("_"))
    print(f"\n--- {label} attrs ({len(attrs)}) ---")
    print(json.dumps(attrs, indent=2)[:8000])

def safe_call(obj, call_name, *args, **kwargs):
    print(f"\nTRY: {call_name} (args={args}, kwargs keys={list(kwargs.keys())})")
    try:
        fn = getattr(obj, call_name)
    except Exception as e:
        print(f"  NO_ATTR: {e!r}")
        return None
    try:
        res = fn(*args, **kwargs)
        print("  OK -> type:", type(res))
        # Don't print huge objects; just a short repr
        s = repr(res)
        print("  repr:", s[:1000])
        return res
    except Exception as e:
        print("  CALL ERROR:")
        traceback.print_exc(limit=5)
        return None

def main():
    print("ENV MODEL:", MODEL)
    ggen = try_import("google.generativeai")
    if ggen:
        list_attrs(ggen, "google.generativeai module")
        # Try get_model
        if hasattr(ggen, "get_model"):
            print("\nCalling get_model(MODEL)...")
            try:
                m = ggen.get_model(MODEL)
                print("get_model() returned type:", type(m))
                list_attrs(m, f"model object ({type(m)})")
                # candidate method names to try
                candidates = ["generate", "predict", "respond", "complete", "run", "chat", "create", "stream", "call"]
                for cand in candidates:
                    safe_call(m, cand, prompt="Hello from probe", max_output_tokens=64)
            except Exception as e:
                print("get_model() raised:", repr(e))
        # Try GenerativeModel class
        if hasattr(ggen, "GenerativeModel"):
            print("\nInspecting GenerativeModel class...")
            GM = ggen.GenerativeModel
            list_attrs(GM, "GenerativeModel class")
            # try constructing in safe ways
            for attempt in ("from_pretrained", "__call__", "__init__"):
                if hasattr(GM, attempt):
                    print(f"GenerativeModel HAS: {attempt}")
            # try instantiate with different signatures
            for args in ((), (MODEL,),):
                try:
                    print(f"Trying instantiate GenerativeModel args={args}")
                    inst = GM(*args) if args else GM()
                    print("  instantiated OK:", type(inst))
                    list_attrs(inst, "GenerativeModel instance")
                    for cand in ["generate","predict","respond","complete","run","chat","create"]:
                        safe_call(inst, cand, "Hello from probe", max_output_tokens=32)
                    break
                except Exception as e:
                    print("  instantiate failed:", repr(e))
    # try google.genai if present
    ggen2 = try_import("google.genai")
    if ggen2:
        list_attrs(ggen2, "google.genai module")
        if hasattr(ggen2, "generate_text"):
            try:
                print("\nCalling google.genai.generate_text(...):")
                r = ggen2.generate_text(model=MODEL, prompt="Hello from probe", max_output_tokens=64)
                print(" -> OK type", type(r), "repr:", repr(r)[:1000])
            except Exception:
                traceback.print_exc()
    print("\nPROBE DONE")

if __name__ == "__main__":
    main()
