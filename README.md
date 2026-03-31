# ⚡ Volta Story Angle Generator

AI-powered PR tool that monitors EV industry news and generates ready-to-pitch story angles for Volta's communications team.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.40-red)
![Claude](https://img.shields.io/badge/AI-Claude%20API-purple)

## What it does

1. **Ingests** recent EV industry news from NewsAPI and trade publication RSS feeds
2. **Classifies** articles by theme and relevance using Claude
3. **Generates** 5-7 compelling story angles with headlines, news pegs, rationale, and outlet recommendations
4. **Surfaces** everything in a clean dashboard designed for Monday morning PR brainstorms
5. **Learns** from team feedback via blocked topics and custom instructions that shape future angle generation

## Quick start

```bash
# Clone and install
git clone https://github.com/YOUR_USERNAME/volta-story-generator.git
cd volta-story-generator
pip install -r requirements.txt

# Add your API keys
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your actual keys

# Seed with demo data (works without API keys)
python seed_data.py

# Launch the dashboard
streamlit run app.py
```

## Running the full pipeline

With API keys configured:

```bash
# Run ingestion + classification + angle generation
python -m src.pipeline
```

Or use the **Refresh** button in the dashboard sidebar.

## API keys needed

| Service | Free tier | Get it at |
|---------|-----------|-----------|
| NewsAPI | 100 requests/day | [newsapi.org](https://newsapi.org/) |
| Anthropic (Claude) | Pay-as-you-go | [console.anthropic.com](https://console.anthropic.com/) |

## Feedback loop

The tool improves over time through two feedback mechanisms in the sidebar:

**Blocked topics** — The PR team can block terms (e.g., "tesla", "crypto") so articles matching those terms are filtered out during ingestion. Each source article also has a "Block similar" button that auto-extracts a keyword and adds it to the block list.

**Custom instructions** — Free-text instructions that get injected into every angle generation prompt. Examples: "Our CEO is available for grid reliability commentary this month", "We have a product launch in Texas in April — prioritize Texas angles", "Avoid angles about Tesla unless they directly impact charging networks." These persist across sessions and shape every future run.

## Architecture

```
NewsAPI + RSS Feeds
        │
        ▼
  ┌─────────────┐
  │  Ingestion   │  Fetch, normalize, deduplicate (fuzzy title matching)
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │  Classify    │  Claude: theme tagging + relevance scoring
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │  Generate    │  Claude: story angle creation from top articles
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │   SQLite     │  Articles + angles stored locally
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │  Streamlit   │  Dashboard with filters, cards, source articles
  └─────────────┘
```

## Project structure

```
volta-story-generator/
├── app.py                 # Streamlit dashboard
├── seed_data.py           # Demo data seeder
├── requirements.txt
├── .streamlit/
│   ├── config.toml        # Streamlit theme
│   └── secrets.toml.example
├── src/
│   ├── newsapi_fetcher.py # NewsAPI integration
│   ├── rss_fetcher.py     # RSS feed parser
│   ├── database.py        # SQLite + fuzzy dedup
│   ├── ai_processor.py    # Claude classification + angle generation
│   └── pipeline.py        # End-to-end orchestrator
└── data/
    └── volta.db           # SQLite database (auto-created)
```

## Deployment

Hosted on [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push to GitHub
2. Connect repo at share.streamlit.io
3. Add API keys in the Streamlit secrets manager
4. Done — shareable URL is live

## Scaling considerations

This is a prototype. For production, I'd evolve toward:

- **PostgreSQL** for multi-user storage and better querying
- **Redis** for caching API responses and dedup state
- **Celery + scheduled jobs** for automated daily/weekly runs
- **React dashboard** with journalist-level targeting and pitch tracking
- **Feedback loop** where the PR team rates angles to improve generation over time
