# GapFinder — Automated Software Tool Gap Discovery

## What This Is
A research pipeline that discovers unserved gaps in software domains, then reality-checks them.
Users will ask you to scan their domain — follow the methodology below.

## When a User Asks to Scan a Domain

Run the full pipeline using web search. Save all outputs as JSON + markdown.

### Phase 1: Find Gaps (Stages 1-6)

For each domain, create `output/<domain-slug>/` and run:

1. **Landscape Scan** — Search 5+ queries to find ALL tools. Save `landscape.json`
2. **Feature Matrix** — Build tool x feature comparison. Save `feature_matrix.json`
3. **Gap Identification** — Find feature/segment/workflow/integration/pricing gaps. Save `raw_gaps.json`
4. **Demand Validation** — Search Reddit, HN, Twitter, GitHub for demand signals. Save `validated_gaps.json`
5. **Scoring & Ranking** — Score each gap: `opportunity = demand * competition * feasibility / 100` (all 0-10). Save `ranked_gaps.json`
6. **Report Generation** — Top 10 gaps as markdown. Save `gap_report.md`

Commit after each stage.

### Phase 2: Kill Gaps (Stages 7-8)

For top N gaps, run Competition Reality Check. Be SKEPTICAL — try to DISPROVE each gap:

7. **Reality Check** — For each gap, search for:
   - Direct competitors (5+ queries)
   - First-party fixes (Anthropic, OpenAI, Google, AWS, Microsoft changelogs)
   - Velocity (% shipped in last 6 months)
   - "Top N [category]" comparison articles
   - GitHub repos (last 6 months)

   Score: start at 100, subtract penalties. Verdict:
   - `> 60`: PROCEED | `30-60`: DIFFERENTIATE | `10-30`: PIVOT | `< 10`: ABANDON

8. **Final Report** — Adjusted scores with verdicts. Save `master_gap_report_v2.md`

## Running Multiple Domains in Parallel
Use agents — one per domain — to parallelize. Each agent handles all 6 stages for its domain.

## Project Structure
- `gapfinder.py` — Python script version (needs ANTHROPIC_API_KEY)
- `output/` — All generated data (per-domain subdirectories)
- `GAPFINDER-SPEC.md` — v1 architecture
- `GAPFINDER-V2-SPEC.md` — v2 Competition Reality Check methodology

## Environment Variables (for gapfinder.py only)
- `ANTHROPIC_API_KEY` — Required
- `GAPFINDER_MODEL` — Override model (default: claude-sonnet-4-20250514)
- `GAPFINDER_TOP_N` — Gaps to reality-check (default: 20)
