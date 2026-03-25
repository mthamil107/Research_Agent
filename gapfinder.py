"""
GapFinder — Automated Software Tool Gap Discovery

A research agent that systematically discovers unserved gaps in any
software domain. Feed it a category, it maps the landscape, finds
what's missing, validates demand, and outputs a ranked gap report.

Uses Claude API with web search for data gathering and analysis.
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

MODEL = "claude-sonnet-4-20250514"
OUTPUT_DIR = Path("output")

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


def call_claude(prompt: str, max_tokens: int = 16000) -> anthropic.types.Message:
    """Call Claude with web search enabled."""
    return client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 20}],
        messages=[{"role": "user", "content": prompt}],
    )


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
        # Fallback: save raw text
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
      "feature2": false,
      ...
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
        lines.append(
            f"| Dimension | Score |"
        )
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


def run_full_scan(domains: list[str] | None = None):
    """Scan all domains and generate a master report."""
    domains = domains or DOMAINS_TO_SCAN
    all_gaps = []

    print(f"GapFinder — Scanning {len(domains)} domain(s)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    for domain in domains:
        result = scan_domain(domain)
        for gap in result.get("ranked_gaps", []):
            gap["domain"] = domain
            all_gaps.append(gap)

    # Sort all gaps across domains by opportunity score
    all_gaps.sort(key=lambda g: g.get("opportunity_score", 0), reverse=True)

    # Master report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# GapFinder Master Report",
        f"Generated: {now}",
        f"Scanned **{len(domains)}** domains | Found **{len(all_gaps)}** total gaps\n",
        "---\n",
        "## Top 20 Gaps by Opportunity Score\n",
    ]

    for i, gap in enumerate(all_gaps[:20], 1):
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
    print(f"  DONE — {len(all_gaps)} gaps found across {len(domains)} domains")
    print(f"  Master report: {master_file}")
    print(f"  Raw data: {raw_file}")
    print(f"{'='*60}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Scan specific domains from CLI arguments
        domains = sys.argv[1:]
        run_full_scan(domains)
    else:
        # Scan all default domains
        run_full_scan()
