# Excuse Generator (Streamlit)

A simple, professional UI to generate context-aware excuses quickly.

## Quickstart

1. Create and activate a virtual environment (recommended)
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Features
- Scenario, audience, tone, specificity, and length controls
- Optional custom context
- Rephrase button for variations
- History with optional JSONL persistence

## Notes
- Templates are defined in `src/generator.py` and can be extended.
- No external models required; works fully offline.
