# GapFinder — Automated Software Tool Gap Discovery

## What This Is
A research agent that discovers unserved gaps in software domains using Claude API + web search,
then reality-checks them against actual competition. See README.md for full documentation.

## Quick Start

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

python gapfinder.py "AI agent testing"       # v1: find gaps
python gapfinder.py --v2 "AI agent testing"  # v2: find + reality-check
python gapfinder.py --reality-check          # v2: reality-check existing results
```

## Project Structure
- `gapfinder.py` — Main pipeline (8 stages: landscape -> matrix -> gaps -> validate -> score -> report -> reality check -> final report)
- `output/` — Generated reports and intermediate JSON (per-domain subdirectories)
- `GAPFINDER-SPEC.md` — v1 specification and domain list
- `GAPFINDER-V2-SPEC.md` — v2 Competition Reality Check methodology

## Pipeline
- **Phase 1 (Stages 1-6):** Find and score gaps
- **Phase 2 (Stages 7-8):** Kill gaps with Competition Reality Check

Each stage saves JSON output and commits to git automatically.

## Environment Variables
- `ANTHROPIC_API_KEY` — Required
- `GAPFINDER_MODEL` — Override model (default: claude-sonnet-4-20250514)
- `GAPFINDER_TOP_N` — Number of top gaps to reality-check (default: 20)
