"""
GapFinder — Automated Software Tool Gap Discovery (v2)

A research agent that systematically discovers unserved gaps in any
software domain, then reality-checks them against actual competition.

Phase 1 (Stages 1-6): Find and score gaps
Phase 2 (Stage 7-8): Kill gaps with Competition Reality Check

Uses Claude API with web search for data gathering and analysis.

Usage:
    python gapfinder.py                          # Scan all default domains (v1 only)
    python gapfinder.py --v2                     # Full pipeline with reality check
    python gapfinder.py "AI agent testing"       # Scan specific domain
    python gapfinder.py --v2 "MCP server tools"  # Specific domain + reality check
    python gapfinder.py --reality-check          # Run Stage 7 on existing v1 output
"""

import anthropic
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

client = anthropic.Anthropic()

MODEL = os.environ.get("GAPFINDER_MODEL", "claude-sonnet-4-20250514")
OUTPUT_DIR = Path("output")
TOP_N_GAPS = int(os.environ.get("GAPFINDER_TOP_N", "20"))

DOMAINS_TO_SCAN = [
    "AI agent testing and evaluation",
    "AI agent prompt optimization",
    "LLM cost monitoring and optimization",
    "AI workflow orchestration for enterprises",
    "AI agent security and guardrails",
    "MCP server ecosystem tools",
    "AI agent observability",
    "Domain-specific SLM training platforms",
    "AI-powered document processing for insurance",
    "Multi-agent collaboration frameworks",
]


def ensure_output_dir(domain: str) -> Path:
    """Create and return output directory for a domain."""
    slug = re.sub(r"[^a-z0-9]+", "-", domain.lower()).strip("-")
    path = OUTPUT_DIR / slug
    path.mkdir(parents=True, exist_ok=True)
    return path


def extract_json_from_response(response) -> dict | None:
    """Extract JSON from a Claude API response, handling text and tool use blocks."""
    for block in response.content:
        if block.type == "text":
            text = block.text
            # Try to find JSON in code fences first
            match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            # Try parsing the whole text as JSON
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
    return None


def extract_text_from_response(response) -> str:
    """Extract all text content from a Claude API response."""
    parts = []
    for block in response.content:
        if block.type == "text":
            parts.append(block.text)
    return "\n".join(parts)


def call_claude(prompt: str, system: str = "", max_tokens: int = 16000) -> anthropic.types.Message:
    """Call Claude with web search enabled."""
    kwargs = dict(
        model=MODEL,
        max_tokens=max_tokens,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 20}],
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        kwargs["system"] = system
    return client.messages.create(**kwargs)


def git_commit(message: str):
    """Stage all changes and commit."""
    try:
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", message],
            check=True,
            capture_output=True,
        )
        print(f"  [git] Committed: {message}")
    except subprocess.CalledProcessError:
        print("  [git] Nothing to commit or git error — skipping.")


# ---------------------------------------------------------------------------
# Stage 1: Landscape Scan
# ---------------------------------------------------------------------------
def stage_1_landscape(domain: str, out_dir: Path) -> dict:
    """Search for every tool in the domain and record details."""
    print("  Stage 1: Landscape Scan...")
    prompt = f"""You are a market research analyst. Research the software tool landscape for: "{domain}"

Search using at least 5 different queries to find ALL tools in this space — established players, startups, open-source projects, and emerging tools.

For each tool, record:
- name
- url
- description (1-2 sentences)
- key_features (list of 3-5)
- pricing (free / freemium / paid / enterprise — with details if available)
- target_audience
- maturity (established / growing / early-stage / beta)

Return ONLY a JSON object (no other text) in this format:
{{
  "domain": "{domain}",
  "scan_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "tools": [
    {{
      "name": "...",
      "url": "...",
      "description": "...",
      "key_features": ["...", "..."],
      "pricing": "...",
      "target_audience": "...",
      "maturity": "..."
    }}
  ],
  "queries_used": ["query1", "query2", ...]
}}"""

    response = call_claude(prompt)
    data = extract_json_from_response(response)

    if not data:
        data = {"domain": domain, "raw_response": extract_text_from_response(response)}

    out_file = out_dir / "landscape.json"
    out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"    -> {out_file} ({len(data.get('tools', []))} tools found)")
    return data


# ---------------------------------------------------------------------------
# Stage 2: Feature Matrix
# ---------------------------------------------------------------------------
def stage_2_feature_matrix(domain: str, landscape: dict, out_dir: Path) -> dict:
    """Build a tool x feature matrix."""
    print("  Stage 2: Feature Matrix...")
    tools_summary = json.dumps(landscape.get("tools", []), indent=2)

    prompt = f"""You are a market research analyst. Given these tools in the "{domain}" space:

{tools_summary}

Build a comprehensive feature matrix:
1. Identify ALL distinct features/capabilities across all tools
2. For each tool, mark whether it supports each feature

Return ONLY a JSON object:
{{
  "domain": "{domain}",
  "features": ["feature1", "feature2", ...],
  "matrix": {{
    "ToolName": {{
      "feature1": true,
      "feature2": false
    }}
  }},
  "common_features": ["features most tools have"],
  "rare_features": ["features 0-1 tools have"],
  "analysis": "Brief summary of patterns observed"
}}"""

    response = call_claude(prompt)
    data = extract_json_from_response(response)

    if not data:
        data = {"domain": domain, "raw_response": extract_text_from_response(response)}

    out_file = out_dir / "feature_matrix.json"
    out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"    -> {out_file}")
    return data


# ---------------------------------------------------------------------------
# Stage 3: Gap Identification
# ---------------------------------------------------------------------------
def stage_3_gaps(domain: str, landscape: dict, matrix: dict, out_dir: Path) -> dict:
    """Find gaps in the market."""
    print("  Stage 3: Gap Identification...")
    prompt = f"""You are a market research analyst. Analyze the "{domain}" tool landscape.

Tools found:
{json.dumps(landscape.get('tools', []), indent=2)}

Feature matrix summary:
- Common features: {json.dumps(matrix.get('common_features', []))}
- Rare features: {json.dumps(matrix.get('rare_features', []))}
- Analysis: {matrix.get('analysis', 'N/A')}

Identify ALL gaps:
1. **Feature gaps**: Features that 0-1 tools offer
2. **Segment gaps**: User segments nobody targets well
3. **Workflow gaps**: End-to-end workflows nobody automates
4. **Integration gaps**: Missing integrations between tools
5. **Pricing gaps**: Pricing models nobody offers (e.g., everything is enterprise-only, nothing open-source)
6. **Quality gaps**: Areas where existing tools are weak/buggy

Return ONLY a JSON object:
{{
  "domain": "{domain}",
  "gaps": [
    {{
      "id": "gap-1",
      "title": "...",
      "category": "feature|segment|workflow|integration|pricing|quality",
      "description": "What is missing and why it matters",
      "affected_users": "Who suffers from this gap",
      "closest_alternatives": ["What exists but falls short"]
    }}
  ]
}}"""

    response = call_claude(prompt)
    data = extract_json_from_response(response)

    if not data:
        data = {"domain": domain, "raw_response": extract_text_from_response(response)}

    out_file = out_dir / "raw_gaps.json"
    out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"    -> {out_file} ({len(data.get('gaps', []))} gaps found)")
    return data


# ---------------------------------------------------------------------------
# Stage 4: Demand Validation
# ---------------------------------------------------------------------------
def stage_4_validate(domain: str, gaps: dict, out_dir: Path) -> dict:
    """Validate demand for each gap via web search."""
    print("  Stage 4: Demand Validation...")
    gaps_summary = json.dumps(gaps.get("gaps", []), indent=2)

    prompt = f"""You are a market research analyst validating demand for software gaps in "{domain}".

Gaps to validate:
{gaps_summary}

For EACH gap, search the web for demand signals:
- Reddit posts/comments requesting this capability
- Hacker News discussions about this need
- Twitter/X posts complaining about the lack of this
- GitHub issues requesting related features
- Blog posts discussing this unmet need
- Forum threads asking for recommendations

Return ONLY a JSON object:
{{
  "domain": "{domain}",
  "validated_gaps": [
    {{
      "id": "gap-1",
      "title": "...",
      "demand_signals": [
        {{
          "source": "reddit|hackernews|twitter|github|blog|forum",
          "url": "...",
          "summary": "What the person said/requested",
          "date": "approximate date if known"
        }}
      ],
      "signal_count": 0,
      "demand_summary": "Overall assessment of demand"
    }}
  ]
}}"""

    response = call_claude(prompt, max_tokens=16000)
    data = extract_json_from_response(response)

    if not data:
        data = {"domain": domain, "raw_response": extract_text_from_response(response)}

    out_file = out_dir / "validated_gaps.json"
    out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"    -> {out_file}")
    return data


# ---------------------------------------------------------------------------
# Stage 5: Scoring & Ranking
# ---------------------------------------------------------------------------
def stage_5_score(domain: str, gaps: dict, validated: dict, out_dir: Path) -> dict:
    """Score and rank each gap."""
    print("  Stage 5: Scoring & Ranking...")
    prompt = f"""You are a market research analyst scoring software gaps in "{domain}".

Raw gaps:
{json.dumps(gaps.get('gaps', []), indent=2)}

Demand validation:
{json.dumps(validated.get('validated_gaps', []), indent=2)}

Score each gap on three dimensions:
- **demand** (0-10): How many people want this? 0=nobody, 10=massive demand
- **competition** (0-10): How empty is the space? 0=crowded market, 10=nobody does this
- **feasibility** (0-10): How practical to build? 0=near-impossible, 10=straightforward

Calculate: opportunity_score = demand * competition * feasibility / 100

Return ONLY a JSON object with gaps sorted by opportunity_score descending:
{{
  "domain": "{domain}",
  "ranked_gaps": [
    {{
      "rank": 1,
      "id": "gap-1",
      "title": "...",
      "description": "...",
      "demand_score": 0,
      "competition_score": 0,
      "feasibility_score": 0,
      "opportunity_score": 0.0,
      "what_to_build": "Concrete product/feature description",
      "who_needs_it": "Target user persona",
      "why_now": "Why this gap exists now / why timing is right",
      "evidence": ["url1", "url2"],
      "build_complexity": "low|medium|high",
      "market_size_estimate": "small|medium|large"
    }}
  ]
}}"""

    response = call_claude(prompt)
    data = extract_json_from_response(response)

    if not data:
        data = {"domain": domain, "raw_response": extract_text_from_response(response)}

    out_file = out_dir / "ranked_gaps.json"
    out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"    -> {out_file}")
    return data


# ---------------------------------------------------------------------------
# Stage 6: Report Generation
# ---------------------------------------------------------------------------
def stage_6_report(domain: str, ranked: dict, out_dir: Path) -> str:
    """Generate a human-readable gap report."""
    print("  Stage 6: Report Generation...")

    gaps = ranked.get("ranked_gaps", [])
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# Gap Report: {domain}",
        f"Generated: {now}\n",
        f"## Summary",
        f"Found **{len(gaps)}** gaps ranked by opportunity score.\n",
        "---\n",
    ]

    for gap in gaps[:10]:
        score = gap.get("opportunity_score", "N/A")
        lines.append(f"## #{gap.get('rank', '?')}. {gap.get('title', 'Untitled')}")
        lines.append(f"**Opportunity Score:** {score}\n")
        lines.append("| Dimension | Score |")
        lines.append("| --- | --- |")
        lines.append(f"| Demand | {gap.get('demand_score', '?')}/10 |")
        lines.append(f"| Competition (10=empty) | {gap.get('competition_score', '?')}/10 |")
        lines.append(f"| Feasibility | {gap.get('feasibility_score', '?')}/10 |")
        lines.append(f"| Build Complexity | {gap.get('build_complexity', '?')} |")
        lines.append(f"| Market Size | {gap.get('market_size_estimate', '?')} |\n")

        if gap.get("description"):
            lines.append(f"**What's missing:** {gap['description']}\n")
        if gap.get("what_to_build"):
            lines.append(f"**What to build:** {gap['what_to_build']}\n")
        if gap.get("who_needs_it"):
            lines.append(f"**Who needs it:** {gap['who_needs_it']}\n")
        if gap.get("why_now"):
            lines.append(f"**Why now:** {gap['why_now']}\n")

        evidence = gap.get("evidence", [])
        if evidence:
            lines.append("**Evidence:**")
            for url in evidence:
                lines.append(f"- {url}")
            lines.append("")

        lines.append("---\n")

    report = "\n".join(lines)
    out_file = out_dir / "gap_report.md"
    out_file.write_text(report, encoding="utf-8")
    print(f"    -> {out_file}")
    return report


# ---------------------------------------------------------------------------
# Stage 7: Competition Reality Check (v2)
# ---------------------------------------------------------------------------
REALITY_CHECK_SYSTEM = """You are a skeptical market analyst. Your job is to DISPROVE \
that a gap exists, not confirm it. Search aggressively for:
1. Existing solutions (commercial, open-source, first-party)
2. Announced solutions (blog posts, changelogs, roadmaps)
3. Adjacent solutions that could expand into this space
4. Platform owners fixing it themselves

Assume every gap is already being solved until proven otherwise.
Your value is in preventing wasted effort, not in optimism."""


def stage_7_reality_check(gap: dict, domain: str) -> dict:
    """Run Competition Reality Check on a single gap."""
    title = gap.get("title", gap.get("name", "Unknown"))
    description = gap.get("description", gap.get("what_to_build", ""))

    prompt = f"""Run a Competition Reality Check on this gap:

**Gap:** {title}
**Domain:** {domain}
**Thesis:** {description}

Execute these 5 checks:

1. **Direct Competitor Search** — Search at least 5 queries:
   - "{title} tool 2025 2026"
   - "{title} open source GitHub"
   - "{title} startup funding"
   - "top {title} tools"
   - "{title} solution platform"

2. **First-Party Fix Detection** — Check if platform owners are solving this:
   - Anthropic, OpenAI, Google, Cloudflare, AWS, Microsoft changelogs/blogs
   - Score: None=0, Acknowledged=-10, Beta=-25, GA=-50, Multiple GA=-75

3. **Velocity Analysis** — What % of solutions shipped in last 6 months?

4. **"Top N List" Test** — Search for "top 5 [category] tools 2026" or "best [category] 2026"

5. **Open-Source Saturation** — Search GitHub for repos matching this, last 6 months

Return ONLY a JSON object:
{{
  "gap_title": "{title}",
  "competitors_found": [
    {{"name": "...", "type": "first-party|startup|oss|enterprise", "maturity": "pre-launch|beta|GA|established", "key_metric": "...", "backed_by": "...", "launch_date": "..."}}
  ],
  "competitor_count": 0,
  "first_party_fix_status": "none|acknowledged|beta|GA|multiple_GA",
  "first_party_details": "...",
  "velocity": "slow|accelerating|rapid|solved",
  "solutions_shipped_6mo": "N/M",
  "top_n_list_exists": false,
  "top_n_source": "",
  "github_repos_6mo": 0,
  "oss_saturation": "open|early|crowded|saturated",
  "reality_check_score": 0,
  "verdict": "PROCEED|DIFFERENTIATE|PIVOT|ABANDON",
  "differentiation_angle": "If DIFFERENTIATE or PIVOT, what angle would work?",
  "evidence_urls": ["..."]
}}

Scoring for reality_check_score:
  Start at 100
  Subtract first_party_modifier (0 to -75)
  Subtract velocity_penalty: -(percentage of solutions from last 6mo * 0.3)
  Subtract saturation_penalty: -(github_repos_6mo * 3, max -30)
  Subtract top_n_penalty: -20 if comparison articles exist
  Floor at 0

Verdicts:
  reality_check_score > 60: PROCEED
  reality_check_score 30-60: DIFFERENTIATE
  reality_check_score 10-30: PIVOT
  reality_check_score < 10: ABANDON"""

    response = call_claude(prompt, system=REALITY_CHECK_SYSTEM)
    data = extract_json_from_response(response)

    if not data:
        data = {
            "gap_title": title,
            "raw_response": extract_text_from_response(response),
            "verdict": "UNKNOWN",
            "reality_check_score": -1,
        }

    return data


def run_reality_checks(top_gaps: list[dict]) -> list[dict]:
    """Run Stage 7 reality checks on top gaps."""
    print(f"\n{'='*60}")
    print(f"  Stage 7: Competition Reality Check ({len(top_gaps)} gaps)")
    print(f"{'='*60}")

    results = []
    for i, gap in enumerate(top_gaps, 1):
        title = gap.get("title", gap.get("name", "Unknown"))
        domain = gap.get("domain", "Unknown")
        print(f"\n  [{i}/{len(top_gaps)}] Reality-checking: {title}")
        result = stage_7_reality_check(gap, domain)

        # Carry forward original scoring
        result["original_score"] = gap.get("opportunity_score", 0)
        result["domain"] = domain
        results.append(result)

        score = result.get("reality_check_score", "?")
        verdict = result.get("verdict", "?")
        print(f"    -> Reality: {score}/100 | Verdict: {verdict}")

    return results


# ---------------------------------------------------------------------------
# Stage 8: Final Report (v2)
# ---------------------------------------------------------------------------
def stage_8_final_report(reality_results: list[dict]):
    """Generate the v2 master report with reality-checked scores."""
    print("\n  Stage 8: Final Report (v2)...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Save raw reality check data
    rc_file = OUTPUT_DIR / "reality_checks.json"
    rc_file.write_text(json.dumps(reality_results, indent=2), encoding="utf-8")

    # Count verdicts
    verdicts = {"PROCEED": 0, "DIFFERENTIATE": 0, "PIVOT": 0, "ABANDON": 0, "UNKNOWN": 0}
    for r in reality_results:
        v = r.get("verdict", "UNKNOWN")
        verdicts[v] = verdicts.get(v, 0) + 1

    lines = [
        "# GapFinder v2 — Competition Reality Check Report",
        f"Generated: {now}",
        f"Reality-checked **{len(reality_results)}** top gaps\n",
        "## Verdict Summary\n",
        "| Verdict | Count |",
        "| --- | --- |",
    ]
    for v, c in verdicts.items():
        if c > 0:
            lines.append(f"| {v} | {c} |")
    lines.append("")

    # Scorecard table
    lines.append("## Full Scorecard\n")
    lines.append("| # | Gap | Domain | Original | Reality | Verdict |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for i, r in enumerate(reality_results, 1):
        title = r.get("gap_title", "Unknown")
        domain = r.get("domain", "?")
        orig = r.get("original_score", "?")
        rc = r.get("reality_check_score", "?")
        verdict = r.get("verdict", "?")
        lines.append(f"| {i} | {title} | {domain} | {orig} | {rc}/100 | {verdict} |")
    lines.append("")

    # Detail cards for non-ABANDON gaps
    survivors = [r for r in reality_results if r.get("verdict") in ("PROCEED", "DIFFERENTIATE")]
    if survivors:
        lines.append("## Survivors (PROCEED / DIFFERENTIATE)\n")
        for r in survivors:
            lines.append(f"### {r.get('gap_title', 'Unknown')}")
            lines.append(f"- **Domain:** {r.get('domain', '?')}")
            lines.append(f"- **Reality Score:** {r.get('reality_check_score', '?')}/100")
            lines.append(f"- **Verdict:** {r.get('verdict', '?')}")
            lines.append(f"- **Competitors found:** {r.get('competitor_count', len(r.get('competitors_found', [])))}")
            lines.append(f"- **First-party fix:** {r.get('first_party_fix_status', '?')}")
            lines.append(f"- **Velocity:** {r.get('velocity', '?')}")
            if r.get("differentiation_angle"):
                lines.append(f"- **Angle:** {r['differentiation_angle']}")
            lines.append("")

    report = "\n".join(lines)
    report_file = OUTPUT_DIR / "master_gap_report_v2.md"
    report_file.write_text(report, encoding="utf-8")
    git_commit("Stage 8: v2 reality-checked report")
    print(f"    -> {report_file}")


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------
def scan_domain(domain: str) -> dict:
    """Run the full 6-stage gap analysis on a single domain."""
    print(f"\n{'='*60}")
    print(f"  Domain: {domain}")
    print(f"{'='*60}")

    out_dir = ensure_output_dir(domain)

    # Stage 1
    landscape = stage_1_landscape(domain, out_dir)
    git_commit(f"Stage 1: Landscape scan for '{domain}'")

    # Stage 2
    matrix = stage_2_feature_matrix(domain, landscape, out_dir)
    git_commit(f"Stage 2: Feature matrix for '{domain}'")

    # Stage 3
    gaps = stage_3_gaps(domain, landscape, matrix, out_dir)
    git_commit(f"Stage 3: Gap identification for '{domain}'")

    # Stage 4
    validated = stage_4_validate(domain, gaps, out_dir)
    git_commit(f"Stage 4: Demand validation for '{domain}'")

    # Stage 5
    ranked = stage_5_score(domain, gaps, validated, out_dir)
    git_commit(f"Stage 5: Scoring & ranking for '{domain}'")

    # Stage 6
    report = stage_6_report(domain, ranked, out_dir)
    git_commit(f"Stage 6: Gap report for '{domain}'")

    return ranked


def run_full_scan(domains: list[str] | None = None, run_v2: bool = False):
    """Scan all domains and generate master report. Optionally run v2 reality check."""
    domains = domains or DOMAINS_TO_SCAN
    all_gaps = []

    print(f"GapFinder {'v2' if run_v2 else 'v1'} — Scanning {len(domains)} domain(s)")
    print(f"Model: {MODEL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    for domain in domains:
        result = scan_domain(domain)
        for gap in result.get("ranked_gaps", []):
            gap["domain"] = domain
            all_gaps.append(gap)

    # Sort all gaps across domains by opportunity score
    all_gaps.sort(key=lambda g: g.get("opportunity_score", 0), reverse=True)

    # Master report (v1)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# GapFinder Master Report",
        f"Generated: {now}",
        f"Scanned **{len(domains)}** domains | Found **{len(all_gaps)}** total gaps\n",
        "---\n",
        f"## Top {TOP_N_GAPS} Gaps by Opportunity Score\n",
    ]

    for i, gap in enumerate(all_gaps[:TOP_N_GAPS], 1):
        lines.append(f"### {i}. {gap.get('title', 'Untitled')}")
        lines.append(f"- **Domain:** {gap.get('domain', 'N/A')}")
        lines.append(f"- **Opportunity Score:** {gap.get('opportunity_score', 'N/A')}")
        lines.append(
            f"- **Scores:** Demand {gap.get('demand_score', '?')}, "
            f"Competition {gap.get('competition_score', '?')}, "
            f"Feasibility {gap.get('feasibility_score', '?')}"
        )
        lines.append(f"- **What to build:** {gap.get('what_to_build', 'N/A')}")
        lines.append(f"- **Who needs it:** {gap.get('who_needs_it', 'N/A')}")
        if gap.get("why_now"):
            lines.append(f"- **Why now:** {gap['why_now']}")
        lines.append("")

    master_report = "\n".join(lines)
    master_file = OUTPUT_DIR / "master_gap_report.md"
    master_file.write_text(master_report, encoding="utf-8")
    git_commit("Master gap report across all domains")

    # Save raw ranked data
    raw_file = OUTPUT_DIR / "all_gaps_ranked.json"
    raw_file.write_text(json.dumps(all_gaps, indent=2), encoding="utf-8")
    git_commit("All gaps ranked data (JSON)")

    print(f"\n{'='*60}")
    print(f"  Phase 1 DONE — {len(all_gaps)} gaps found across {len(domains)} domains")
    print(f"  Master report: {master_file}")
    print(f"{'='*60}")

    # Phase 2: Reality Check (v2)
    if run_v2:
        top_gaps = all_gaps[:TOP_N_GAPS]
        reality_results = run_reality_checks(top_gaps)
        stage_8_final_report(reality_results)

        proceed = sum(1 for r in reality_results if r.get("verdict") == "PROCEED")
        diff = sum(1 for r in reality_results if r.get("verdict") == "DIFFERENTIATE")
        abandon = sum(1 for r in reality_results if r.get("verdict") == "ABANDON")
        print(f"\n{'='*60}")
        print(f"  Phase 2 DONE — Reality Check Complete")
        print(f"  PROCEED: {proceed} | DIFFERENTIATE: {diff} | ABANDON: {abandon}")
        print(f"{'='*60}")


def run_reality_check_only():
    """Run Stage 7-8 on existing v1 output (all_gaps_ranked.json)."""
    raw_file = OUTPUT_DIR / "all_gaps_ranked.json"
    if not raw_file.exists():
        print(f"ERROR: {raw_file} not found. Run v1 scan first.")
        sys.exit(1)

    all_gaps = json.loads(raw_file.read_text(encoding="utf-8"))
    print(f"Loaded {len(all_gaps)} gaps from {raw_file}")

    top_gaps = all_gaps[:TOP_N_GAPS]
    reality_results = run_reality_checks(top_gaps)
    stage_8_final_report(reality_results)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    args = sys.argv[1:]

    run_v2 = "--v2" in args
    reality_only = "--reality-check" in args

    # Remove flags from args
    domains = [a for a in args if not a.startswith("--")]

    if reality_only:
        run_reality_check_only()
    elif domains:
        run_full_scan(domains, run_v2=run_v2)
    else:
        run_full_scan(run_v2=run_v2)


if __name__ == "__main__":
    main()
