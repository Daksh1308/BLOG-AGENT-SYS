# Blog Writing Agent (BWA)

An **AI-powered blog writing agent** built with **LangGraph**, **LangChain**, and **OpenRouter**. It generates full technical blog posts from a single topic prompt through a stateful agent graph pipeline.

Given a topic, it decides whether web research is needed, optionally searches the web, plans a structured outline, writes each section in parallel, and generates diagrams — all producing a final Markdown file.

---

## Architecture

```
Topic
  │
  ▼
┌──────────┐
│  Router  │ ◄── decides closed_book / hybrid / open_book
└────┬─────┘
     │ needs_research?
     ├── No  ──► ┌──────────────┐
     │            │ Orchestrator │ ◄── generates Plan (5-9 tasks)
     │            └──────┬───────┘
     │                   │ fanout
     │            ┌──────▼───────┐
     │            │   Workers    │ ◄── each writes one section (parallel)
     │            └──────┬───────┘
     │                   │
     ▼ Yes               │
┌──────────┐             │
│ Research │ ◄── Tavily / Google search + LLM synthesis
└────┬─────┘             │
     └──► Orchestrator   │
                        ▼
              ┌─────────────────────┐
              │  Reducer Subgraph   │
              │  ┌──────────────┐   │
              │  │ merge_content│   │
              │  └──────┬───────┘   │
              │         ▼          │
              │  ┌──────────────┐   │
              │  │ decide_images│   │ ◄── LLM places [[IMAGE_N]] placeholders
              │  └──────┬───────┘   │
              │         ▼          │
              │  ┌────────────────┐│
              │  │generate_images ││ ◄── Pillow local diagram generation
              │  └────────────────┘│
              └─────────────────────┘
                        │
                        ▼
                   Final .md file
```

### Graph Nodes

| Node | Description |
|------|-------------|
| **Router** | LLM decides if web research is needed (closed_book / hybrid / open_book) and generates search queries |
| **Research** | Fetches web results via Tavily (if API key set) or Google search, deduplicates, filters by recency |
| **Orchestrator** | Generates a structured `Plan` with 5-9 task sections, each with goal, bullets, target word count |
| **Worker** | Each worker writes one Markdown section in parallel using `Send` fanout |
| **Reducer** | 3-node subgraph: merge sections → decide on image placeholders → generate & place images |

---

## Features

- **Three research modes**: closed_book (evergreen), hybrid (some research), open_book (news roundup)
- **Web research via Tavily** (optional API key) or **Google search** (free, no API key)
- **Image generation** via Pillow: generates clean local diagram images — no API key required
- **Recency filtering**: automatically filters evidence by date for news/open_book modes
- **Evidence-grounded writing**: workers cite provided URLs for factual claims
- **Structured output**: all LLM calls use Pydantic schemas for reliable parsing
- **Streamlit UI**: tabs for Plan, Evidence, Markdown Preview, Images, Logs
- **Download options**: `.md` file, `.zip` bundle (MD + images)
- **Past blog viewer**: browse and load previously generated blogs

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip / venv

### Installation

```bash
# Clone or navigate to the project
cd blog-agent-system

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### API Setup

The project uses **OpenRouter** as the LLM provider (free tier available, no credit card required).

1. Sign up at https://openrouter.ai
2. Generate an API key
3. Create `.env` file:

```env
OPENAI_API_KEY=sk-or-v1-...
```

**Optional** — Tavily for higher-quality web search (falls back to free Google search if unset):

```env
TAVILY_API_KEY=tvly-...
```

Get one at https://tavily.com

### Run

```bash
# CLI test
python -c "from bwa_backend import app; print('App ready:', app)"

# Streamlit UI
streamlit run bwa_frontend.py
```

Opens at `http://localhost:8501`.

---

## Usage

1. Enter a blog topic (e.g., "Self Attention in Transformers" or "Latest AI news this week")
2. Set the "As-of date" (for recency filtering in news mode)
3. Click **Generate Blog**
4. View results across tabs:
   - **Plan**: structured outline with tasks and metadata
   - **Evidence**: web sources used (if research was needed)
   - **Markdown Preview**: rendered blog with any generated images
   - **Images**: generated diagram files
   - **Logs**: detailed event trace

### Download

- **Markdown**: download the `.md` file
- **Bundle**: download `.zip` containing markdown + all images

---

## Project Structure

```
blog-agent-system/
├── bwa_backend.py          # LangGraph agent pipeline (production)
├── bwa_frontend.py         # Streamlit UI
├── api/index.py            # FastAPI serverless handler (Vercel)
├── public/index.html       # Static frontend (Vercel)
├── vercel.json             # Vercel deployment config
├── 1_bwa_basic.ipynb       # v1: minimal orchestrator→workers
├── 2_bwa_improved_prompting.ipynb  # v2: richer prompts + audience/tone
├── 3_bwa_research.ipynb    # v3: router + Tavily research
├── 4_bwa_research_fine_tuned.ipynb # v4: recency + date filtering
├── 5_bwa_image.ipynb       # v5: Gemini image generation
├── tavily_test.ipynb       # Tavily API smoke test
├── .env                    # API keys
├── images/                 # Generated images
├── requirements.txt        # Python dependencies
├── run.sh                  # Convenience startup script
└── *.md                    # Generated blog files
```

---

## Notebooks (Incremental Development)

| Notebook | Features Added |
|----------|----------------|
| `1_bwa_basic.ipynb` | Orchestrator → fanout → workers → reducer (no research, no images) |
| `2_bwa_improved_prompting.ipynb` | Rich prompts, section types, audience/tone |
| `3_bwa_research.ipynb` | Router + Tavily research + evidence-grounded citations |
| `4_bwa_research_fine_tuned.ipynb` | Recency filtering, `as_of` dates, `blog_kind` enum, open_book mode |
| `5_bwa_image.ipynb` | ReducerWithImages subgraph (Gemini image generation) |

`bwa_backend.py` is the consolidated production version combining all features.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `langgraph` | Stateful agent graph framework |
| `langchain-openai` | OpenAI-compatible LLM (OpenRouter) |
| `langchain-core` | LangChain abstractions (messages, tools) |
| `pydantic` | Structured data schemas |
| `python-dotenv` | Environment variable loading |
| `tavily-python` | Optional — Tavily web search API |
| `googlesearch-python` | Free Google search fallback |
| `Pillow` | Local diagram image generation |
| `streamlit` | Web UI |
| `pandas` | DataFrame display in UI |

### Install All at Once

```bash
pip install -r requirements.txt
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `404` model not found | Model name changed on OpenRouter. Run `curl -s https://openrouter.ai/api/v1/models \| jq '.data[].id' \| grep gemini` to list available models |
| No research results | If no `TAVILY_API_KEY`, Google search fallback is used. Ensure topic queries are specific |
| Image generation fails | Pillow fallback always works locally — check `images/` directory permissions |
| `429` rate limit | Wait and retry. Free tiers have per-minute limits |
| Streamlit won't start | Ensure all deps installed: `pip install -r requirements.txt` |
| Venv not found | Recreate: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` |

---

## License

MIT
