# GapFinder — Automated Software Tool Gap Discovery

**Find market gaps in any software domain. Then kill the ones that aren't real.**

GapFinder is a research methodology + pipeline that:
1. **Scans** a domain for every existing tool
2. **Identifies** what's missing (feature gaps, segment gaps, pricing gaps)
3. **Validates** demand via Reddit, HN, Twitter, GitHub signals
4. **Scores** gaps by opportunity (demand x competition x feasibility)
5. **Reality-checks** each gap against actual competition (v2)

Of our top 20 gaps across 10 AI domains, **12 were already dead** after reality checking. Zero received a clean "PROCEED."

> The most valuable output of GapFinder is not the gaps it finds — it's the gaps it kills.

---

## How to Use This

There are two ways to run GapFinder. **Pick the one that fits you.**

### Option A: Claude Code (Recommended)

This is how we built the results in this repo. No API key needed — just a Claude Code subscription.

```bash
# 1. Clone this repo
git clone https://github.com/YOUR_USERNAME/GapFinder.git
cd GapFinder

# 2. Open with Claude Code
claude

# 3. Tell it to scan your domain
```

Then just say:

```
Scan the domain "your domain here" using the GapFinder methodology in GAPFINDER-SPEC.md.
Run all 6 stages: landscape scan, feature matrix, gap identification,
demand validation, scoring, and report generation.
Save output to output/<your-domain>/. Use web search for every stage.
```

For the v2 reality check, follow up with:

```
Now run a Competition Reality Check on the top 5 gaps using the methodology
in GAPFINDER-V2-SPEC.md. Be skeptical — try to DISPROVE each gap exists.
Search for direct competitors, first-party fixes, GitHub repos, and "top N" articles.
```

**Why this works well:**
- Claude Code has built-in web search — no API key setup
- Can run multiple domain scans in parallel via agents
- Results go straight into the repo with git commits
- You can ask follow-up questions about specific gaps

### Option B: Python Script (Automated / Scheduled)

For repeatable, scheduled scans. Requires an Anthropic API key with web search access.

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/GapFinder.git
cd GapFinder
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# Edit .env with your key, then:
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Scan a single domain
python gapfinder.py "your domain here"

# 4. Scan with reality check (v2)
python gapfinder.py --v2 "your domain here"

# 5. Scan all default domains
python gapfinder.py --v2
```

**Estimated API costs:**
- Single domain (v1, 6 stages): ~$2-5
- Single domain (v2, 8 stages): ~$5-10
- All 10 default domains (v2): ~$50-100

### Option C: Manual (No Code)

You don't need any tool. For any gap you're considering:

- [ ] Search `"[problem] tool 2026"` — found < 3 direct competitors?
- [ ] Search `"[problem] open source GitHub"` — found < 5 repos in 6 months?
- [ ] Check Anthropic, OpenAI, Cloudflare, AWS changelogs — no first-party fix?
- [ ] Search `"top [N] [category] 2026"` — no comparison articles?
- [ ] Check HN/Reddit — no "Show HN" posts solving this?
- [ ] Check YCombinator portfolio — no funded startup here?

**If any check fails, do not proceed without explicit justification.**

---

## Scanning Your Own Domain

### Step 1: Pick a specific domain

Good: `"AI-powered contract analysis for legal teams"`
Bad: `"AI tools"` (too broad)

The more specific the domain, the better the results. GapFinder works best on domains narrow enough to have 10-30 existing tools.

### Step 2: Run v1 (find gaps)

Using Claude Code:
```
Scan the domain "AI-powered contract analysis for legal teams"
using the GapFinder methodology. Run all 6 stages with web search.
Save to output/ai-contract-analysis/.
```

Or using the script:
```bash
python gapfinder.py "AI-powered contract analysis for legal teams"
```

### Step 3: Run v2 (kill gaps)

This is the critical step. Don't skip it.

Using Claude Code:
```
Run a Competition Reality Check on the top 5 gaps from
output/ai-contract-analysis/ranked_gaps.json.
For each gap, search for direct competitors, first-party fixes,
GitHub saturation, and "top N" comparison articles.
Save results to output/ai-contract-analysis/reality_check.json.
```

Or using the script:
```bash
python gapfinder.py --v2 "AI-powered contract analysis for legal teams"
```

### Step 4: Read the verdicts

Check `output/<your-domain>/gap_report.md` for v1 results and `output/master_gap_report_v2.md` for reality-checked results.

| Verdict | What to do |
|---------|-----------|
| PROCEED | Rare. Build it. |
| DIFFERENTIATE | Gap exists but needs a sharp unique angle |
| PIVOT | Core thesis dead. Look at adjacent gaps |
| ABANDON | Market solved. Move on. |

---

## The Pipeline

```
Phase 1: Find Gaps (Stages 1-6)
  Stage 1: Landscape Scan — Find all tools via web search
  Stage 2: Feature Matrix — Build tool x feature comparison
  Stage 3: Gap Identification — Find missing features, segments, workflows
  Stage 4: Demand Validation — Search Reddit/HN/Twitter/GitHub for signals
  Stage 5: Scoring & Ranking — Score: demand x competition x feasibility / 100
  Stage 6: Report Generation — Markdown report with top gaps

Phase 2: Kill Gaps (Stages 7-8)
  Stage 7: Competition Reality Check — Try to DISPROVE each gap
  Stage 8: Final Report — Adjusted scores with verdicts
```

### Stage 7: The Competition Reality Check

The Reality Check agent runs 5 checks per gap:

| Check | What it does | Penalty |
|-------|-------------|---------|
| Direct Competitor Search | 5+ queries for existing solutions | Proportional |
| First-Party Fix Detection | Are Anthropic/OpenAI/Google solving it? | -10 to -75 |
| Velocity Analysis | % of solutions shipped in last 6 months | Up to -30 |
| "Top N List" Test | Do comparison articles exist? | -20 |
| Open-Source Saturation | GitHub repos in last 6 months | Up to -30 |

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
  master_gap_report.md          # v1 cross-domain report
  master_gap_report_v2.md       # v2 reality-checked report
  all_gaps_ranked.json          # All gaps sorted by score
  reality_checks.json           # Raw reality check data
  <domain-slug>/
    landscape.json              # Stage 1: All tools found
    feature_matrix.json         # Stage 2: Tool x feature grid
    raw_gaps.json               # Stage 3: Identified gaps
    validated_gaps.json         # Stage 4: Demand signals
    ranked_gaps.json            # Stage 5: Scored gaps
    gap_report.md               # Stage 6: Human-readable report
```

## Sample Results (March 2026)

We scanned 10 AI/software domains. Results after reality checking:

| # | Gap | v1 Score | v2 Score | Verdict |
|---|-----|----------|----------|---------|
| 1 | Domain Data Pipeline | 58.43 | 22.43 | ABANDON |
| 2 | MCP Context Optimization | 57.00 | 24.00 | ABANDON |
| 3 | Unified Security SDK | 56.10 | 16.10 | ABANDON |
| 7 | Domain-Specific Eval | 49.14 | 38.14 | DIFFERENTIATE |
| 8 | MCP Security Gateway | 48.30 | 1.30 | ABANDON |

The MCP Security Gateway dropped from 48.3 to **1.3** — 41 competing projects found.

Full results in `output/`.

## Default Domains

Edit `DOMAINS_TO_SCAN` in `gapfinder.py` or pass your own:

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

## Methodology Docs

- [`GAPFINDER-SPEC.md`](GAPFINDER-SPEC.md) — v1 architecture and design
- [`GAPFINDER-V2-SPEC.md`](GAPFINDER-V2-SPEC.md) — v2 Competition Reality Check methodology

## Limitations

- **Scoring is subjective.** Different weights produce different rankings
- **Search is incomplete.** Misses stealth startups, internal tools, non-English ecosystems
- **Results expire fast.** AI infrastructure has ~6-month gap-to-saturation cycles. Re-run monthly
- **No outcome validation yet.** We don't know if DIFFERENTIATE gaps produce successful products
- **API costs.** Full 10-domain v2 scan uses significant API credits via the Python script

## License

MIT
