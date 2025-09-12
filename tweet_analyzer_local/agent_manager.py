# agent_manager.py
import os
import time
import pandas as pd
from dotenv import load_dotenv

load_dotenv()  # project .env

from utils import parse_datetime_safe
from gemini_wrapper import call_gemini

# Config
TWEET_CSV = os.environ.get("TWEET_CSV_PATH", "./tweets.csv")
RESULTS_PATH = os.environ.get("RESULTS_PATH", "./results.csv")
MAX_TWEETS_PER_PROMPT = int(os.environ.get("MAX_TWEETS_PER_PROMPT", "10"))
SLEEP_BETWEEN_CALLS = float(os.environ.get("SLEEP_BETWEEN_CALLS", "0.5"))
RUN_SUMMARIES = os.environ.get("RUN_SUMMARIES", "false").lower() in ("1", "true", "yes")
ALT_GEMINI_MODEL = os.environ.get("ALT_GEMINI_MODEL", "text-bison-001")

def _detect_columns(df: pd.DataFrame):
    cols = df.columns
    def find(names):
        for c in cols:
            if c.lower() in [n.lower() for n in names]:
                return c
        return None
    date_col = find(["date of the tweet", "date", "created_at", "tweet_date", "time"])
    user_col = find(["user", "username", "screen_name", "author"])
    text_col = find(["text", "tweet", "content", "message"])
    return date_col, user_col, text_col

def load_and_prepare():
    if not os.path.exists(TWEET_CSV):
        raise FileNotFoundError(f"Input CSV not found at {TWEET_CSV}")
    try:
        df = pd.read_csv(TWEET_CSV, dtype=str)
    except Exception as e:
        raise RuntimeError(f"Failed to read CSV: {e}")

    date_col, user_col, text_col = _detect_columns(df)
    if date_col is None or user_col is None:
        raise KeyError(f"Couldn't detect 'date' and 'user' columns. Found columns: {list(df.columns)}")

    df["_raw_date"] = df[date_col].astype(str)
    parsed = []
    for s in df["_raw_date"]:
        try:
            dt = parse_datetime_safe(s)
            parsed.append(pd.to_datetime(dt))
        except Exception:
            parsed.append(pd.NaT)
    df["_parsed_dt"] = pd.to_datetime(parsed)
    df["_group_date"] = df["_parsed_dt"].dt.date
    df = df.dropna(subset=[user_col, "_group_date"]).copy()
    df[user_col] = df[user_col].astype(str).str.strip()
    if text_col is None:
        df["_text_fallback"] = ""
        text_col = "_text_fallback"
    df[text_col] = df[text_col].astype(str)
    return df, user_col, text_col

def compute_counts_and_maxes():
    df, user_col, text_col = load_and_prepare()
    grouped = df.groupby([user_col, "_group_date"])
    rows = []
    for (user, gdate), gdf in grouped:
        texts = gdf[text_col].dropna().astype(str).tolist()
        rows.append({"user": user, "date": str(gdate), "num_tweets": len(texts), "texts": texts})
    result_df = pd.DataFrame(rows)
    if not result_df.empty:
        maxes = result_df.groupby("user")["num_tweets"].max().rename("max_per_user").reset_index()
        result_df = result_df.merge(maxes, on="user", how="left")
        result_df["is_max_for_user"] = result_df["num_tweets"] == result_df["max_per_user"]
    else:
        result_df["max_per_user"] = pd.NA
        result_df["is_max_for_user"] = False
    return result_df

def robust_call_gemini(prompt: str, max_output_tokens: int = 256, timeout: int = 60):
    """
    Try call_gemini once. If REST 404 (model not available), retry with ALT_GEMINI_MODEL.
    """
    # first attempt with current env/model
    out = call_gemini(prompt, max_output_tokens=max_output_tokens, timeout=timeout)
    # detect REST 404 pattern from gemini_wrapper
    if isinstance(out, str) and out.startswith("[gemini-http-error]") and "status=404" in out:
        current_model = os.environ.get("GEMINI_MODEL", "")
        alt = os.environ.get("ALT_GEMINI_MODEL", ALT_GEMINI_MODEL)
        if alt and alt != current_model:
            print(f"[fallback] primary model '{current_model}' returned 404 — retrying with '{alt}'")
            old = os.environ.get("GEMINI_MODEL")
            os.environ["GEMINI_MODEL"] = alt
            try:
                out2 = call_gemini(prompt, max_output_tokens=max_output_tokens, timeout=timeout)
            finally:
                # restore
                if old is None:
                    os.environ.pop("GEMINI_MODEL", None)
                else:
                    os.environ["GEMINI_MODEL"] = old
            return out2
    return out

def summarize_groups(df_counts: pd.DataFrame, save_results: bool = True):
    if df_counts.empty:
        return df_counts
    summaries = []
    total = len(df_counts)
    for idx, row in df_counts.iterrows():
        texts = row.get("texts") or []
        chunks = [texts[i:i+MAX_TWEETS_PER_PROMPT] for i in range(0, len(texts), MAX_TWEETS_PER_PROMPT)] or [[]]
        chunk_summaries = []
        for ch in chunks:
            if not ch:
                continue
            prompt = (
                "You are a concise analyst. Summarize these tweets in 3 short bullets. "
                "Mention main topics and sentiment briefly.\n\n" + "\n\n".join(ch) + "\n\nSummary:"
            )
            out = robust_call_gemini(prompt, max_output_tokens=256)
            chunk_summaries.append(out)
            time.sleep(SLEEP_BETWEEN_CALLS)
        summaries.append("\n\n---\n\n".join(chunk_summaries).strip() or "")
        if (idx+1) % 10 == 0 or (idx+1) == total:
            print(f"[{idx+1}/{total}] summarized user={row['user']} date={row['date']} tweets={row['num_tweets']}")
    df_counts["summary"] = summaries
    if save_results:
        out_df = df_counts.copy()
        out_df = out_df.drop(columns=["texts"], errors="ignore")
        out_df.to_csv(RESULTS_PATH, index=False)
    return df_counts

def run_full_pipeline(save_results: bool = True, run_summaries: bool = None):
    df_counts = compute_counts_and_maxes()
    run_summaries = RUN_SUMMARIES if run_summaries is None else bool(run_summaries)
    if run_summaries:
        df_counts = summarize_groups(df_counts, save_results=save_results)
    else:
        out_df = df_counts.copy()
        out_df = out_df.drop(columns=["texts"], errors="ignore")
        if save_results:
            out_df.to_csv(RESULTS_PATH, index=False)
    print(f"Pipeline finished. Results saved to {RESULTS_PATH}")
    return df_counts
