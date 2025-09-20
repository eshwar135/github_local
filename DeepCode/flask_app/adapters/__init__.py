# app/__init__.py
import os
from dotenv import load_dotenv
from flask import Flask

def create_app():
    load_dotenv()  # load .env
    app = Flask(__name__)
    app.config.from_mapping(
        GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY"),
    )

    # configure google.generativeai
    try:
        import google.generativeai as ggen
        api_key = app.config.get("GOOGLE_API_KEY")
        if api_key:
            ggen.configure(api_key=api_key)
            app.logger.info("google.generativeai configured.")
        else:
            app.logger.warning("GOOGLE_API_KEY missing; ggen will try ADC.")
    except Exception:
        app.logger.exception("Failed to import/configure google.generativeai")

    # register blueprints, etc.
    return app
