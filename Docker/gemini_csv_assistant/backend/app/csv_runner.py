import pandas as pd
import traceback
from typing import Any, Dict

ALLOWED_GLOBALS = {
    "pd": pd,
}


def run_pandas_snippet(csv_path, code_snippet: str) -> Dict[str, Any]:
    """
    Runs a **restricted** pandas-only snippet safely and returns serializable result.

    Expectations: The snippet should load the CSV using pandas (pd.read_csv) into a variable named `df`
    and then produce a variable named `output` which is either a DataFrame or a serializable object.

    We execute in a restricted namespace with only `pd` available.
    """
    try:
        local_ns = {"__file__": str(csv_path)}
        # pre-load df variable for convenience
        local_ns["df"] = pd.read_csv(csv_path)

        # Build a small wrapper to limit what user code can do
        exec_env = {k: v for k, v in ALLOWED_GLOBALS.items()}
        exec_env.update(local_ns)

        # Only execute the snippet; it must set `output`.
        exec(code_snippet, {}, exec_env)

        if "output" not in exec_env:
            return {"error": "Snippet did not set `output` variable."}

        out = exec_env["output"]
        # If it's a DataFrame, return head as dict; else try to serialize
        if hasattr(out, "to_dict"):
            return {"type": "dataframe", "data": out.head(100).to_dict(orient="records")}
        else:
            return {"type": "object", "data": out}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}
