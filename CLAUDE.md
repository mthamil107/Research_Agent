# GapFinder — Automated Software Tool Gap Discovery

## What This Is
A research agent that discovers unserved gaps in software domains using Claude API + web search.
See `GAPFINDER-SPEC.md` for the full architecture and design rationale.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Scan all default domains
python gapfinder.py

# Scan specific domains
python gapfinder.py "AI agent testing" "MCP server tools"
```

## Project Structure
- `gapfinder.py` — Main pipeline (6 stages: landscape -> matrix -> gaps -> validate -> score -> report)
- `output/` — Generated reports and intermediate JSON (per-domain subdirectories)
- `GAPFINDER-SPEC.md` — Full specification and domain list

## Pipeline Stages
1. **Landscape Scan** — Find all tools via web search
2. **Feature Matrix** — Build tool x feature comparison
3. **Gap Identification** — Find missing features, segments, workflows
4. **Demand Validation** — Search Reddit/HN/Twitter/GitHub for demand signals
5. **Scoring & Ranking** — Score gaps on demand/competition/feasibility
6. **Report Generation** — Markdown report with top 10 gaps per domain

Each stage saves JSON output and commits to git automatically.
