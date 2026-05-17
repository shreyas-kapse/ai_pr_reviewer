# AI PR Reviewer — Automated Pull Request Review using LangGraph Agents

> **AI-powered GitHub pull request reviewer** that automatically analyzes code for security vulnerabilities, bug risks, and performance issues using multi-agent LangGraph pipelines and posts structured reviews directly to GitHub.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)](https://langchain-ai.github.io/langgraph/)
[![LangChain](https://img.shields.io/badge/LangChain-Powered-blue)](https://langchain.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black)](https://ollama.com)
[![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## What Is This?

**AI PR Reviewer** is a GitHub App that automatically reviews pull requests the moment they are opened or updated. It runs three specialized AI agents in parallel — security, bug risk, and performance — then aggregates their findings into a single structured review comment posted back to the PR.

No manual triggering. No copy-pasting code into ChatGPT. Just open a PR and get an AI review in seconds.

---

## Features

- **Parallel multi-agent review** — Security, bug risk, and performance agents run simultaneously using LangGraph's parallel node execution, cutting review time by ~3x vs sequential
- **Multi-LLM support** — Switch between local Ollama models (fully private, no API cost) and Google Gemini with a single config change
- **GitHub App integration** — Installs on any repo via GitHub App, authenticates with JWT, verifies webhook signatures with HMAC-SHA256
- **Structured Pydantic output** — Every agent returns typed `ReviewSchema` objects with `severity`, `file_name`, `line_number`, `issue`, and `suggestion` fields — not freeform text
- **Configurable review rules** — Control `max_files`, `skip_extensions`, `max_patch_chars` via `config.yaml` without touching code
- **Human-in-the-loop gate** — Optional approval step before the review is posted; toggled via config
- **Large PR protection** — Automatically skips files over `max_patch_chars`, ignores non-code files (`.md`, `.json`, `.lock`), and caps at `max_files` to prevent token overflow
- **LangSmith tracing** — Full agent trace visibility when `LANGCHAIN_API_KEY` is set; zero overhead when it's not
- **Persistent checkpointing** — Every review is stored in SQLite via LangGraph's `AsyncSqliteSaver`, enabling replay and audit

---

## Architecture

```
GitHub PR Event (webhook)
        │
        ▼
  FastAPI /webhook/github
  (signature verification)
        │
        ▼
  LangGraph StateGraph
        │
   ┌────┴─────────────────┐
   │           │           │
   ▼           ▼           ▼
Security    Bug Risk   Performance
 Agent       Agent       Agent
   │           │           │
   └────┬──────┘───────────┘
        ▼
   Aggregator Node
   (FinalReviewSchema)
        │
        ▼
   GitHub Formatter Node
   (Markdown review body)
        │
        ▼
   [Optional] Human-in-the-Loop
        │
        ▼
   Post Review to GitHub
```

Each agent independently analyzes the PR diff and returns structured findings. The aggregator merges all three into a `FinalReviewSchema` with `overall_severity`, `merge_recommendation`, and `top_issues`.

---

## Tech Stack

| Layer               | Technology                          |
| ------------------- | ----------------------------------- |
| API server          | FastAPI + Uvicorn (async)           |
| Agent orchestration | LangGraph (parallel StateGraph)     |
| LLM framework       | LangChain                           |
| LLM providers       | Ollama (local) / Google Gemini      |
| GitHub integration  | PyGithub + GitHub App JWT auth      |
| Diff parsing        | unidiff                             |
| Data validation     | Pydantic v2                         |
| Checkpointing       | LangGraph AsyncSqliteSaver (SQLite) |
| Observability       | LangSmith tracing                   |

---

## Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed locally (if using `ollama` provider)
- A GitHub App with webhook configured (see [GitHub App Setup](#github-app-setup) below)

### 1. Clone and install

```bash
git clone https://github.com/shreyas-kapse/ai_pr_reviewer.git
cd ai_pr_reviewer
pip install -r requirements.txt
```

### 2. Set up environment variables

Create a `.env` file in the project root:

```env
# GitHub App credentials
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY_PATH=path/to/private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# LLM provider (only needed for Gemini)
GOOGLE_API_KEY=your_google_api_key

# Optional: LangSmith tracing
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=ai-pr-reviewer
```

### 3. Configure the LLM provider

Edit `app/config.yaml`:

```yaml
llm:
  provider: ollama # switch to "gemini" for Gemini

  ollama:
    model: qwen2.5-coder:7b-instruct-q4_K_M
    temperature: 0
    num_ctx: 2048
    device: cpu

  gemini:
    model: gemini-2.0-flash
    temperature: 0
```

For Ollama, pull the model first:

```bash
ollama pull qwen2.5-coder:7b-instruct-q4_K_M
```

### 4. Run the server

```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Expose locally for webhook (development)

```bash
ngrok http 8000
```

Set the ngrok URL as your GitHub App webhook URL: `https://<ngrok-url>/webhook/github`

---

## GitHub App Setup

1. Go to **GitHub → Settings → Developer Settings → GitHub Apps → New GitHub App**
2. Set **Webhook URL** to your server's `/webhook/github` endpoint
3. Set a **Webhook Secret** — save it as `GITHUB_WEBHOOK_SECRET` in your `.env`
4. Required **permissions**:
   - Pull Requests: Read & Write
   - Contents: Read
5. Subscribe to **Pull Request** events
6. After creation, generate a **Private Key** — save the `.pem` file path as `GITHUB_PRIVATE_KEY_PATH`
7. Note your **App ID** — save it as `GITHUB_APP_ID`
8. Install the app on your target repositories

---

## Configuration Reference

All review behavior is controlled via `app/config.yaml` — no code changes needed.

```yaml
post-review:
  human-in-loop: false # set true to approve each review before posting

llm:
  provider: ollama # "ollama" or "gemini"

review:
  max_files: 20 # max files reviewed per PR
  max_patch_chars: 15000 # files with larger diffs are skipped
  skip_extensions: # file types ignored entirely
    - ".md"
    - ".txt"
    - ".json"
    - ".lock"
```

---

## Review Output Example

When a PR is opened, the bot posts a review comment like this:

```
## 🤖 AI Code Review

**Overall Severity:** 🔴 High
**Recommendation:** Changes Requested

### Summary
The PR introduces a new authentication endpoint with critical security issues. SQL injection vulnerability detected in the query builder. Performance concern with N+1 query in the user fetch loop.

### Top Issues

| Severity | Type | File | Line | Issue |
|---|---|---|---|---|
| 🔴 High | Security | auth/login.py | 42 | Unsanitized input passed directly to SQL query |
| 🟡 Medium | Bug Risk | users/service.py | 87 | Missing null check before attribute access |
| 🔵 Low | Performance | users/service.py | 103 | N+1 query inside loop — consider batch fetch |
```

---

## How It Works

1. **GitHub sends a webhook** when a PR is opened, reopened, or synchronized
2. **Signature is verified** using HMAC-SHA256 to ensure the payload is from GitHub
3. **Diff is fetched and parsed** using `unidiff`; large files and non-code files are filtered out
4. **Three LangGraph agents run in parallel**: each receives the diff and returns structured `ReviewSchema` objects with Pydantic validation
5. **Aggregator node** merges all findings into a `FinalReviewSchema` with `overall_severity` and `merge_recommendation`
6. **Formatter node** converts the schema into a GitHub-flavored markdown review body
7. **Optional human approval** gate checks config before posting
8. **Review is posted** to the PR via GitHub Reviews API with the correct event type (`APPROVE` / `REQUEST_CHANGES` / `COMMENT`)

---

## Project Structure

```
ai_pr_reviewer/
├── app/
│   ├── main.py                          # FastAPI app, webhook handler
│   ├── config.yaml                      # All runtime configuration
│   ├── enums.py
│   ├── graph/
│   │   ├── graph_builder.py             # LangGraph StateGraph definition
│   │   ├── state.py                     # ReviewState TypedDict
│   │   └── nodes/
│   │       ├── security_review_node.py
│   │       ├── bug_risk_review_node.py
│   │       ├── performance_review_node.py
│   │       ├── pr_review_node.py        # Aggregator
│   │       ├── final_review_node.py     # GitHub formatter
│   │       └── post_review_node.py      # Posts to GitHub
│   └── services/
│       ├── llm_service.py               # Multi-LLM factory (Ollama / Gemini)
│       ├── config_service.py            # Singleton config loader
│       ├── github_auth_service.py       # JWT auth + webhook verification
│       ├── github_review_service.py     # GitHub Reviews API
│       ├── schema/
│       │   └── review_schema.py         # Pydantic models
│       ├── reviewers/                   # Agent business logic
│       └── prompts/                     # LLM prompt templates
├── requirements.txt
└── .env                                 # (not committed)
```

---

## Roadmap

- [ ] Inline diff comments on specific lines
- [ ] Review history API endpoint
- [ ] PR size estimation before review
- [ ] Custom review rules per repository via `.pr-reviewer.yml`

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## License

[MIT](LICENSE)

---

_Built with LangGraph, LangChain, FastAPI, and the GitHub Apps API._
