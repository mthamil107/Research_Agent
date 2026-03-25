# GapFinder — Automated Software Tool Gap Discovery

**Find market gaps in any software domain. Then kill the ones that aren't real.**

GapFinder is a multi-agent research pipeline that:
1. **Scans** a software domain for every existing tool
2. **Identifies** what's missing (feature gaps, segment gaps, pricing gaps, etc.)
3. **Validates** demand via Reddit, HN, Twitter, GitHub signals
4. **Scores** gaps by opportunity (demand x competition x feasibility)
5. **Reality-checks** each gap against actual competition (v2)

The v1-to-v2 transition is where all the value lives. Of our top 20 gaps across 10 AI domains, **12 were already dead** after reality checking. Zero received a clean "PROCEED."

> The most valuable output of GapFinder is not the gaps it finds — it's the gaps it kills.

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/GapFinder.git
cd GapFinder

# Install
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...

# Scan a single domain (v1 — find gaps)
python gapfinder.py "AI agent testing"

# Scan with reality check (v2 — find AND kill gaps)
python gapfinder.py --v2 "AI agent testing"

# Scan all 10 default domains
python gapfinder.py

# Run reality check on existing v1 results
python gapfinder.py --reality-check
```

## The Pipeline

```
Phase 1: Find Gaps (Stages 1-6)
  Stage 1: Landscape Scan — Find all tools via web search
  Stage 2: Feature Matrix — Build tool x feature comparison
  Stage 3: Gap Identification — Find missing features, segments, workflows
  Stage 4: Demand Validation — Search Reddit/HN/Twitter/GitHub for demand signals
  Stage 5: Scoring & Ranking — Score gaps on demand/competition/feasibility
  Stage 6: Report Generation — Markdown report with top gaps per domain

Phase 2: Kill Gaps (Stages 7-8)
  Stage 7: Competition Reality Check — Disprove each gap exists
  Stage 8: Final Report — Adjusted scores with verdicts
```

## Stage 7: The Competition Reality Check

This is the contribution. The Reality Check agent has one job: **disprove that the gap exists.**

It runs 5 checks per gap:

| Check | What it does | Penalty |
|-------|-------------|---------|
| Direct Competitor Search | 5+ search queries for existing solutions | Proportional to competitors found |
| First-Party Fix Detection | Check if Anthropic/OpenAI/Google/AWS are solving it | -10 to -75 depending on status |
| Velocity Analysis | % of solutions shipped in last 6 months | Up to -30 |
| "Top N List" Test | Do comparison articles already exist? | -20 if yes |
| Open-Source Saturation | GitHub repos matching problem, last 6 months | Up to -30 |

### Verdicts

| Verdict | Reality Score | Meaning |
|---------|--------------|---------|
| PROCEED | > 60 | Few competitors, no first-party fixes, go build it |
| DIFFERENTIATE | 30-60 | Gap exists but needs a unique angle |
| PIVOT | 10-30 | Core thesis dead, adjacent angle might work |
| ABANDON | < 10 | Market solved or saturated, move on |

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Your Anthropic API key |
| `GAPFINDER_MODEL` | `claude-sonnet-4-20250514` | Claude model to use |
| `GAPFINDER_TOP_N` | `20` | Number of top gaps to reality-check |

## Output Structure

```
output/
  master_gap_report.md          # v1 cross-domain report
  master_gap_report_v2.md       # v2 reality-checked report
  all_gaps_ranked.json          # All gaps sorted by score
  reality_checks.json           # Raw reality check data
  ai-agent-testing-and-evaluation/
    landscape.json              # Stage 1: All tools found
    feature_matrix.json         # Stage 2: Tool x feature grid
    raw_gaps.json               # Stage 3: Identified gaps
    validated_gaps.json         # Stage 4: Demand signals
    ranked_gaps.json            # Stage 5: Scored gaps
    gap_report.md               # Stage 6: Human-readable report
  ...per domain...
```

## Sample Results (March 2026 Scan)

We scanned 10 AI/software domains and found 141+ gaps. After reality checking the top 20:

| Original Rank | Gap | v1 Score | v2 Score | Verdict |
|---------------|-----|----------|----------|---------|
| #1 | Domain Data Pipeline | 58.43 | 22.43 | ABANDON |
| #2 | MCP Context Optimization | 57.00 | 24.00 | ABANDON |
| #3 | Unified Security SDK | 56.10 | 16.10 | ABANDON |
| #8 | MCP Security Gateway | 48.30 | 1.30 | ABANDON |
| #7 | Domain-Specific Eval | 49.14 | 38.14 | DIFFERENTIATE |

The MCP Security Gateway dropped from 48.3 to **1.3** — we found 41 competing projects.

Full results are in the `output/` directory.

## Default Domains

The pipeline ships with 10 domains to scan:

1. AI agent testing and evaluation
2. AI agent prompt optimization
3. LLM cost monitoring and optimization
4. AI workflow orchestration for enterprises
5. AI agent security and guardrails
6. MCP server ecosystem tools
7. AI agent observability
8. Domain-specific SLM training platforms
9. AI-powered document processing for insurance
10. Multi-agent collaboration frameworks

Edit the `DOMAINS_TO_SCAN` list in `gapfinder.py` or pass domains as CLI arguments.

## Manual Reality Check (No Code Required)

You don't need this script to use the methodology. For any gap:

- [ ] Search `"[problem] tool 2026"` — found < 3 direct competitors?
- [ ] Search `"[problem] open source GitHub"` — found < 5 repos in 6 months?
- [ ] Check Anthropic, OpenAI, Cloudflare, AWS changelogs — no first-party fix?
- [ ] Search `"top [N] [category] 2026"` — no comparison articles?
- [ ] Check HN/Reddit — no "Show HN" posts solving this?
- [ ] Check YCombinator portfolio — no funded startup here?
- [ ] Velocity < 50%?

**If any check fails, do not proceed without explicit justification.**

## Methodology Docs

- [`GAPFINDER-SPEC.md`](GAPFINDER-SPEC.md) — v1 architecture and design
- [`GAPFINDER-V2-SPEC.md`](GAPFINDER-V2-SPEC.md) — v2 Competition Reality Check methodology

## Limitations

- **Scoring is subjective.** The multiplicative formula and reality check penalties are hand-tuned. Different weights produce different rankings.
- **Search-based discovery is incomplete.** Misses stealth startups, internal tools, non-English ecosystems.
- **Results expire fast.** AI infrastructure has ~6-month gap-to-saturation cycles. Re-run monthly.
- **No outcome validation.** We don't yet know if DIFFERENTIATE gaps produce successful products.
- **API costs.** A full 10-domain v2 scan uses significant Claude API credits (web search + analysis across 80+ calls).

## License

MIT
