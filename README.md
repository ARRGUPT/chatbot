# Chatbot

A small example chatbot built with LangGraph and LangChain components, using Groq LLM (via `langchain_groq`) and a Streamlit frontend. It demonstrates tool-enabled chat flows (web search, simple calculator, and a stock-price fetcher) and persisted conversation checkpoints using SQLite.

## Table of contents

- Project overview
- Requirements
- Environment variables / API keys
- Install and run
- Key files
- How conversation threads are stored
- Notes & troubleshooting
- License

## Project overview

This repository contains a minimal chatbot example wired together with:

- `langgraph` for stateful graph-based chat flows and checkpointing
- `langchain_groq` to connect to the Groq LLM
- `streamlit` for a quick web UI (`streamlit_frontend.py`)
- A few simple tools (DuckDuckGo search, a Python `calculator` tool, and a stock price lookup) bound to the LLM

The app persists conversation checkpoints to an SQLite database (`chatbot.db`) via LangGraph's `SqliteSaver`.

## Requirements

- Python 3.10+ (recommended)
- Git (optional)

Required Python packages are declared in `requirements.txt` inside this folder. Key packages include `langgraph`, `langchain`, `langchain_groq`, `streamlit`, and `langchain-community`.

## Environment variables / API keys

You must provide credentials for the LLM and (optionally) external APIs.

- GROQ API key: place it in a `.env` file at the project root (or system env) as `GROQ_API_KEY`. The code uses `python-dotenv` to load this value.
- Alpha Vantage API key: `langgraph_backend.py` currently uses an Alpha Vantage key in the HTTP URL. Replace the hardcoded key with your own key, or update the code to read from an environment variable (recommended). If you want to use Alpha Vantage, sign up at https://www.alphavantage.co/ to get an API key.

Example `.env`:

GROQ_API_KEY=your_groq_api_key_here
ALPHAVANTAGE_API_KEY=your_alpha_vantage_key_here

Note: The repository currently expects `GROQ_API_KEY` to be present. If the backend cannot authenticate to Groq, the chatbot will not generate responses.

## Version
```bash
python --version
3.11.8
```

## Install and run (Windows PowerShell)

1. Create and activate a virtual environment (optional but recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Add your `.env` file or set environment variables (see above).

4. Run the Streamlit frontend:

```powershell
streamlit run streamlit_frontend.py
```

The Streamlit app will open in your browser. Use the sidebar to create a new chat or switch between existing threads.

## Key files

- `streamlit_frontend.py` — Streamlit frontend that renders the chat UI, keeps an in-memory message history in `st.session_state`, and streams LLM responses.
- `langgraph_backend.py` — The backend graph and node definitions. It configures the Groq LLM, binds tools, sets up `SqliteSaver` checkpointing, and compiles the LangGraph `chatbot` object used by the frontend.
- `requirements.txt` — Python package dependencies for this example.
- `chatbot.db` — SQLite database created at runtime (in the current working directory) used to persist chat checkpoints.

## How conversation threads are stored

The LangGraph `SqliteSaver` stores checkpoints which include a `config` object with a `thread_id`. The Streamlit frontend lists the distinct `thread_id`s and allows switching between them. If you want to clear history, delete `chatbot.db` or remove specific rows from the database (SQLite clients or `sqlite3` can be used).

## Notes & troubleshooting

- If you see authentication errors, confirm `GROQ_API_KEY` is present and valid.
- The stock-price tool currently calls Alpha Vantage with a hardcoded key — replace it with your own or refactor the code to use an environment variable like `ALPHAVANTAGE_API_KEY`.
- If the DuckDuckGo search tool fails, ensure the `langchain-community` extra tools are installed (`ddgs` and `langchain-community` are listed in `requirements.txt`).
- On first run, `chatbot.db` will be created. If you run into schema or locked-db errors, ensure no other process is holding the file and try again.
- For local development, you may want to pin exact package versions in `requirements.txt` to avoid breaking changes in transitive dependencies.

## Security / privacy

- This example stores conversations in plain SQLite on disk. Do not use it to store sensitive or personal data in production.
- Be mindful when connecting external APIs (search, finance) — responses and logs may contain private or third-party data.

## Contributing & next steps

- Consider moving the Alpha Vantage key into an environment variable and updating `langgraph_backend.py` to read it (more secure and configurable).
- Add unit tests for tool functions (calculator, stock fetcher) and a simple integration test for the graph flow.

## License

This example is provided as-is for learning and demonstration purposes. Add your preferred open-source license if you plan to publish.

---

If you'd like, I can:

- update `langgraph_backend.py` to read the Alpha Vantage API key from an environment variable and remove the hardcoded key
- add a small `.env.example` and a `Makefile`/PowerShell script to simplify setup

Tell me which of those follow-ups you'd like me to do next.

🚀 **Live App:** [Try it on Streamlit](https://arrgupt-chatbot-streamlit-frontend-h4fnyi.streamlit.app/)