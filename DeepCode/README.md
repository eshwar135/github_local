# DeepCode — JupyterLab + Gemini scaffold

Project path: `D:\agenic_arhitecture\5`

This scaffold runs JupyterLab plus a lightweight Flask service that demonstrates calling Gemini (`gemini-1.5-flash`) via the Google GenAI SDK. It uses docker-compose for quick local runs. **This setup expects your .env to live at `D:\gemini\.env`.**

## Quick start (Windows)

1. Copy `.env.example` to `D:\gemini\.env` and either set:
   - `GEMINI_API_KEY=sk-...` (paste key), or
   - `GEMINI_API_KEY_FILE=D:\\gemini\\gemini_key` and save the key at `D:\gemini\gemini_key`.

2. Ensure `D:\gemini` contains your key file (if using `GEMINI_API_KEY_FILE`).

3. From the project root run:
   ```powershell
   docker-compose up --build
