# GapFinder — Automated Software Tool Gap Discovery

**Discover market opportunities in any software domain. Autonomously.**

GapFinder is a research pipeline that:
1. **Discovers** domains worth scanning (from a broad area like "fintech")
2. **Scans** each domain for every existing tool
3. **Identifies** what's missing (feature, segment, workflow, pricing gaps)
4. **Validates** demand via Reddit, HN, Twitter, GitHub signals
5. **Scores** gaps by opportunity (demand x competition x feasibility)
6. **Reality-checks** each gap against actual competition
7. **Deep-dives** survivors into actionable opportunity briefs

Of our top 20 gaps across 10 AI domains, **12 were already dead** after reality checking. Zero received a clean "PROCEED."

> The most valuable output of GapFinder is not the gaps it finds — it's the gaps it kills.

---

## How to Use This

### Option A: Claude Code (Recommended)

No API key needed — just a Claude Code subscription.

```bash
git clone https://github.com/YOUR_USERNAME/GapFinder.git
cd GapFinder
claude
```

Then tell Claude what you want:

**"I know my domain"** — Scan it directly:
```
Scan "AI-powered contract analysis for legal teams" using the GapFinder pipeline.
Run all stages through reality check and exploration.
```

**"I have a broad area"** — Let it discover sub-domains:
```
Explore "fintech" — discover the most promising sub-domains,
then scan, reality-check, and explore survivors.
```

**"I have no idea where to look"** — Start from a trend:
```
What are the hottest underserved areas in developer tools right now?
Discover domains, scan them, and give me the surviving opportunities.
```

Claude reads CLAUDE.md and knows the full methodology.

### Option B: Python Script (Automated / Scheduled)

Requires an Anthropic API key with web search access.

```bash
git clone https://github.com/YOUR_USERNAME/GapFinder.git
cd GapFinder
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

# Full autonomous pipeline: discover → scan → reality-check → explore
python gapfinder.py --discover "fintech" --v2 --explore

# Scan specific domain with full pipeline
python gapfinder.py --v2 --explore "AI-powered contract analysis"

# Just scan (find gaps only)
python gapfinder.py "your domain here"

# Reality-check existing results
python gapfinder.py --reality-check

# Explore surviving gaps from existing results
python gapfinder.py --explore
```

**Estimated API costs:**
| Mode | Cost |
|------|------|
| Domain discovery | ~$1-2 |
| Single domain scan (v1) | ~$2-5 |
| Reality check per gap | ~$1-2 |
| Deep exploration per gap | ~$2-3 |
| Full pipeline, 10 domains | ~$80-150 |

### Option C: Manual (No Code)

For any gap you're considering, run this checklist:

- [ ] Search `"[problem] tool 2026"` — found < 3 direct competitors?
- [ ] Search `"[problem] open source GitHub"` — found < 5 repos in 6 months?
- [ ] Check Anthropic, OpenAI, Cloudflare, AWS changelogs — no first-party fix?
- [ ] Search `"top [N] [category] 2026"` — no comparison articles?
- [ ] Check HN/Reddit — no "Show HN" posts solving this?

**If any check fails, do not proceed without explicit justification.**

---

## The Pipeline

```
Phase 0: DISCOVER — Find domains worth scanning
  Input:  "fintech" or "AI infrastructure" (broad area)
  Output: 8-15 specific scannable sub-domains

Phase 1: SCAN — Find and score gaps (Stages 1-6)
  Stage 1: Landscape Scan — Find all tools via web search
  Stage 2: Feature Matrix — Build tool x feature comparison
  Stage 3: Gap Identification — Find what's missing
  Stage 4: Demand Validation — Search Reddit/HN/Twitter/GitHub
  Stage 5: Scoring — demand x competition x feasibility / 100
  Stage 6: Report — Markdown with top gaps per domain

Phase 2: KILL — Reality-check gaps (Stages 7-8)
  Stage 7: Competition Reality Check — Try to DISPROVE each gap
  Stage 8: Verdict Report — Adjusted scores: PROCEED/DIFFERENTIATE/PIVOT/ABANDON

Phase 3: EXPLORE — Deep-dive survivors (Stage 9)
  Stage 9: Opportunity Brief — For each surviving gap:
    - Target users (real pain quotes from forums)
    - Market sizing (TAM/SAM/SOM)
    - Competitive positioning (competitor weaknesses, unique angle)
    - Distribution channels
    - Business model & pricing
    - 2-week MVP scope
    - Risks & comparable successes
```

### How the phases connect

```
"fintech"
    → Phase 0 discovers: ["neobank infrastructure", "embedded lending",
       "AI fraud detection", "crypto tax tools", ...]
    → Phase 1 scans each, finds 80+ gaps across all domains
    → Phase 2 kills 60+ gaps (already solved/saturated)
    → Phase 3 deep-dives the 5-10 survivors into build-ready briefs
```

---

## Stage 7: The Competition Reality Check

5 checks per gap:

| Check | What it does | Penalty |
|-------|-------------|---------|
| Direct Competitor Search | 5+ queries for existing solutions | Proportional |
| First-Party Fix Detection | Are Anthropic/OpenAI/Google/AWS solving it? | -10 to -75 |
| Velocity Analysis | % of solutions shipped in last 6 months | Up to -30 |
| "Top N List" Test | Do comparison articles exist? | -20 |
| Open-Source Saturation | GitHub repos in last 6 months | Up to -30 |

### Verdicts

| Verdict | Reality Score | Meaning |
|---------|--------------|---------|
| PROCEED | > 60 | Few competitors, no first-party fixes |
| DIFFERENTIATE | 30-60 | Gap exists, needs unique angle |
| PIVOT | 10-30 | Core thesis dead, adjacent angle might work |
| ABANDON | < 10 | Market solved or saturated |

---

## Stage 9: Deep Exploration

For each surviving gap, produces an actionable opportunity brief:

| Section | What it answers |
|---------|----------------|
| Target Users | Who exactly needs this? Real pain quotes from forums |
| Market Sizing | TAM/SAM/SOM, pricing benchmarks |
| Competitive Positioning | Competitor weaknesses, your unique angle |
| Distribution | Where do these users discover tools? |
| Business Model | How to monetize, pricing strategy |
| MVP Scope | What to ship in 2 weeks to validate |
| Risks | What could kill this, and mitigations |
| Comparable Successes | Companies that used a similar playbook |

---

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required for script) | Anthropic API key |
| `GAPFINDER_MODEL` | `claude-sonnet-4-20250514` | Claude model to use |
| `GAPFINDER_TOP_N` | `20` | Number of top gaps to reality-check |

## Output Structure

```
output/
  discovered_domains.json       # Phase 0: Discovered sub-domains
  master_gap_report.md          # Phase 1: Cross-domain gap report
  all_gaps_ranked.json          # Phase 1: All gaps sorted by score
  reality_checks.json           # Phase 2: Raw reality check data
  master_gap_report_v2.md       # Phase 2: Reality-checked verdicts
  explorations.json             # Phase 3: Raw exploration data
  exploration_report.md         # Phase 3: Actionable opportunity briefs
  <domain-slug>/
    landscape.json              # All tools found
    feature_matrix.json         # Tool x feature grid
    raw_gaps.json               # Identified gaps
    validated_gaps.json         # Demand signals
    ranked_gaps.json            # Scored gaps
    gap_report.md               # Human-readable report
```

## Sample Results (March 2026)

Scanned 10 AI/software domains. After reality checking:

| # | Gap | v1 Score | v2 Score | Verdict |
|---|-----|----------|----------|---------|
| 1 | Domain Data Pipeline | 58.43 | 22.43 | ABANDON |
| 2 | MCP Context Optimization | 57.00 | 24.00 | ABANDON |
| 3 | Unified Security SDK | 56.10 | 16.10 | ABANDON |
| 7 | Domain-Specific Eval | 49.14 | 38.14 | DIFFERENTIATE |
| 8 | MCP Security Gateway | 48.30 | 1.30 | ABANDON |

Full results in `output/`.

## Methodology Docs

- [`GAPFINDER-SPEC.md`](GAPFINDER-SPEC.md) — v1 architecture
- [`GAPFINDER-V2-SPEC.md`](GAPFINDER-V2-SPEC.md) — v2 Competition Reality Check methodology

## Limitations

- **Scoring is subjective.** Different weights produce different rankings
- **Search is incomplete.** Misses stealth startups, internal tools, non-English ecosystems
- **Results expire fast.** Re-run monthly. AI infra has ~6-month gap-to-saturation cycles
- **No outcome validation yet.** We don't know if DIFFERENTIATE gaps produce successful products
- **API costs.** Full pipeline with discovery + 10 domains can cost $80-150

## License

MIT
