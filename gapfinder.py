"""
GapFinder — Automated Software Tool Gap Discovery (v3)

A research agent that autonomously discovers opportunities in software markets.

Phase 0: Discover — Find domains worth scanning (from a seed area or from scratch)
Phase 1: Scan — Find and score gaps in each domain (Stages 1-6)
Phase 2: Kill — Reality-check gaps against competition (Stages 7-8)
Phase 3: Explore — Deep-dive surviving gaps into actionable opportunities (Stage 9)

Uses Claude API with web search for data gathering and analysis.

Usage:
    # Full autonomous pipeline: discover domains → scan → kill → explore
    python gapfinder.py --discover "AI infrastructure"
    python gapfinder.py --discover "fintech" --v2 --explore

    # Scan specific domains
    python gapfinder.py "AI agent testing"
    python gapfinder.py --v2 "AI agent testing"

    # Just reality-check or explore existing results
    python gapfinder.py --reality-check
    python gapfinder.py --explore
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
            match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
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
        subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True)
        print(f"  [git] Committed: {message}")
    except subprocess.CalledProcessError:
        print("  [git] Nothing to commit or git error — skipping.")


# ===========================================================================
# PHASE 0: DOMAIN DISCOVERY
# ===========================================================================
def phase_0_discover(seed_area: str) -> list[str]:
    """Discover specific scannable domains from a broad seed area."""
    print(f"\n{'='*60}")
    print(f"  Phase 0: Domain Discovery")
    print(f"  Seed: {seed_area}")
    print(f"{'='*60}")

    prompt = f"""You are a market analyst discovering software tool domains worth investigating.

Starting from the broad area: "{seed_area}"

Your job:
1. Search for the current state of "{seed_area}" — what sub-categories exist?
2. Search for emerging trends, new funding rounds, and recent launches in this space
3. Search for pain points and complaints developers/teams have in this area
4. Search HN, Reddit, Twitter for "I wish there was a tool that..." signals
5. Search for recent YC batches, ProductHunt launches, and GitHub trending repos

From your research, identify 8-15 SPECIFIC scannable domains. Each domain should be:
- Narrow enough to have 10-30 existing tools (not "AI" — too broad)
- Broad enough to have meaningful gaps (not "Python linting for Django 4.2" — too narrow)
- Timely — something actively evolving right now
- Mix of obvious sub-domains AND non-obvious adjacent/emerging ones

Return ONLY a JSON object:
{{
  "seed_area": "{seed_area}",
  "discovery_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "domains": [
    {{
      "name": "Specific domain name",
      "why_scan": "Why this domain is worth investigating right now",
      "signals": ["Signal 1 that suggests gaps exist", "Signal 2"],
      "estimated_tools": "rough count of existing tools",
      "heat": "hot|warm|emerging|niche"
    }}
  ],
  "methodology": "What searches you ran to discover these"
}}"""

    response = call_claude(prompt, max_tokens=8000)
    data = extract_json_from_response(response)

    if not data:
        data = {"seed_area": seed_area, "raw_response": extract_text_from_response(response), "domains": []}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / "discovered_domains.json"
    out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    git_commit(f"Phase 0: Discovered domains from '{seed_area}'")

    domains = [d["name"] for d in data.get("domains", [])]
    print(f"\n  Discovered {len(domains)} domains:")
    for i, d in enumerate(data.get("domains", []), 1):
        print(f"    {i}. [{d.get('heat', '?')}] {d['name']}")
    print()

    return domains


# ===========================================================================
# PHASE 1: GAP SCANNING (Stages 1-6)
# ===========================================================================

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
  "matrix": {{"ToolName": {{"feature1": true, "feature2": false}}}},
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
5. **Pricing gaps**: Pricing models nobody offers
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

Return ONLY a JSON object:
{{
  "domain": "{domain}",
  "validated_gaps": [
    {{
      "id": "gap-1",
      "title": "...",
      "demand_signals": [
        {{"source": "reddit|hackernews|twitter|github|blog", "url": "...", "summary": "...", "date": "..."}}
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

Score each gap on three dimensions (0-10 each):
- **demand**: How many people want this? 0=nobody, 10=massive demand
- **competition**: How empty is the space? 0=crowded, 10=nobody does this
- **feasibility**: How practical to build? 0=near-impossible, 10=straightforward

Calculate: opportunity_score = demand * competition * feasibility / 100

Return ONLY a JSON object with gaps sorted by opportunity_score descending:
{{
  "domain": "{domain}",
  "ranked_gaps": [
    {{
      "rank": 1, "id": "gap-1", "title": "...", "description": "...",
      "demand_score": 0, "competition_score": 0, "feasibility_score": 0,
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


# ===========================================================================
# PHASE 2: REALITY CHECK (Stages 7-8)
# ===========================================================================

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

1. **Direct Competitor Search** — At least 5 queries:
   - "{title} tool 2025 2026"
   - "{title} open source GitHub"
   - "{title} startup funding"
   - "top {title} tools"
   - "{title} solution platform"

2. **First-Party Fix Detection** — Check Anthropic, OpenAI, Google, Cloudflare, AWS, Microsoft
   Score: None=0, Acknowledged=-10, Beta=-25, GA=-50, Multiple GA=-75

3. **Velocity Analysis** — What % of solutions shipped in last 6 months?

4. **"Top N List" Test** — Search "top 5 [category] tools 2026" or "best [category] 2026"

5. **Open-Source Saturation** — GitHub repos matching this, last 6 months

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
  "differentiation_angle": "...",
  "evidence_urls": ["..."]
}}

Scoring: Start at 100, subtract penalties (first-party 0-75, velocity 0-30, saturation 0-30, top_n 0-20). Floor at 0.
Verdicts: >60 PROCEED, 30-60 DIFFERENTIATE, 10-30 PIVOT, <10 ABANDON"""

    response = call_claude(prompt, system=REALITY_CHECK_SYSTEM)
    data = extract_json_from_response(response)
    if not data:
        data = {"gap_title": title, "raw_response": extract_text_from_response(response), "verdict": "UNKNOWN", "reality_check_score": -1}
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
        result["original_score"] = gap.get("opportunity_score", 0)
        result["domain"] = domain
        results.append(result)
        score = result.get("reality_check_score", "?")
        verdict = result.get("verdict", "?")
        print(f"    -> Reality: {score}/100 | Verdict: {verdict}")
    return results


def stage_8_final_report(reality_results: list[dict]) -> list[dict]:
    """Generate the v2 master report with reality-checked scores. Returns survivors."""
    print("\n  Stage 8: Final Report (v2)...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    rc_file = OUTPUT_DIR / "reality_checks.json"
    rc_file.write_text(json.dumps(reality_results, indent=2), encoding="utf-8")

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
    lines.append("## Full Scorecard\n")
    lines.append("| # | Gap | Domain | Original | Reality | Verdict |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for i, r in enumerate(reality_results, 1):
        lines.append(f"| {i} | {r.get('gap_title', '?')} | {r.get('domain', '?')} | {r.get('original_score', '?')} | {r.get('reality_check_score', '?')}/100 | {r.get('verdict', '?')} |")
    lines.append("")

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
            if r.get("differentiation_angle"):
                lines.append(f"- **Angle:** {r['differentiation_angle']}")
            lines.append("")

    report = "\n".join(lines)
    report_file = OUTPUT_DIR / "master_gap_report_v2.md"
    report_file.write_text(report, encoding="utf-8")
    git_commit("Stage 8: v2 reality-checked report")
    print(f"    -> {report_file}")
    return survivors


# ===========================================================================
# PHASE 3: DEEP EXPLORATION (Stage 9)
# ===========================================================================

EXPLORER_SYSTEM = """You are a startup strategist and product researcher. \
You've been given a validated market gap that survived a Competition Reality Check. \
Your job is to explore this opportunity deeply and produce an actionable brief \
that someone could use to start building tomorrow.

Be specific. Use real numbers. Cite real sources. No hand-waving."""


def stage_9_deep_explore(gap: dict) -> dict:
    """Deep-dive a surviving gap into an actionable opportunity brief."""
    title = gap.get("gap_title", gap.get("title", "Unknown"))
    domain = gap.get("domain", "Unknown")
    angle = gap.get("differentiation_angle", "")
    competitors = json.dumps(gap.get("competitors_found", []), indent=2)

    prompt = f"""Deep-dive this validated market opportunity:

**Gap:** {title}
**Domain:** {domain}
**Differentiation angle:** {angle}
**Known competitors:** {competitors}

Research and produce a comprehensive opportunity brief. Search the web for ALL of this:

## 1. TARGET USERS (search real communities)
- Search Reddit, HN, Twitter for people complaining about this exact problem
- Find specific job titles, company types, and team sizes that need this
- Find quotes from real people describing their pain
- Identify early adopters vs mainstream market

## 2. MARKET SIZING
- Search for market size data, analyst reports, funding in adjacent spaces
- Estimate TAM (total addressable market), SAM (serviceable), SOM (obtainable)
- Find pricing benchmarks from similar tools in adjacent categories

## 3. COMPETITIVE POSITIONING
- For each existing competitor, find their weaknesses (reviews, complaints, limitations)
- Search "[competitor name] alternative", "[competitor name] problems", "[competitor name] vs"
- Identify the specific angle where NO competitor is strong

## 4. DISTRIBUTION CHANNELS
- Where do target users discover tools? (HN, ProductHunt, Reddit, conferences, SEO?)
- What communities are they active in?
- What content would attract them? (blog posts, open-source tools, templates?)

## 5. BUSINESS MODEL OPTIONS
- Search for how similar tools monetize
- Open-source + cloud? Pure SaaS? Usage-based? Enterprise only?
- What's the right starting price point?

## 6. MVP SCOPE
- What's the absolute minimum to validate demand? (not full product — just proof)
- Can this start as a blog post? Open-source library? Landing page? API?
- What could you ship in 2 weeks to test the thesis?

## 7. RISKS & BLOCKERS
- What could kill this opportunity? (platform risk, regulatory, technical)
- What would make you STOP pursuing this?
- What assumptions must be true for this to work?

## 8. COMPARABLE SUCCESSES
- Search for companies that succeeded with a similar playbook
- How did they start? What was their initial wedge?
- What can you learn from their trajectory?

Return ONLY a JSON object:
{{
  "gap_title": "{title}",
  "domain": "{domain}",
  "exploration_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "target_users": {{
    "primary_persona": "...",
    "job_titles": ["..."],
    "company_types": ["..."],
    "team_sizes": "...",
    "pain_quotes": [
      {{"source": "...", "quote": "...", "url": "..."}}
    ],
    "early_adopter_profile": "..."
  }},
  "market_sizing": {{
    "tam": "...",
    "sam": "...",
    "som": "...",
    "pricing_benchmarks": ["..."],
    "adjacent_funding": "..."
  }},
  "competitive_positioning": {{
    "positioning_statement": "...",
    "competitor_weaknesses": [
      {{"competitor": "...", "weakness": "...", "source": "..."}}
    ],
    "unique_angle": "..."
  }},
  "distribution": {{
    "primary_channels": ["..."],
    "communities": ["..."],
    "content_strategy": "...",
    "launch_playbook": "..."
  }},
  "business_model": {{
    "recommended": "...",
    "pricing_strategy": "...",
    "alternatives_considered": ["..."]
  }},
  "mvp": {{
    "scope": "...",
    "two_week_version": "...",
    "validation_method": "...",
    "success_metric": "..."
  }},
  "risks": [
    {{"risk": "...", "severity": "high|medium|low", "mitigation": "..."}}
  ],
  "comparable_successes": [
    {{"company": "...", "playbook": "...", "lesson": "..."}}
  ],
  "overall_conviction": "high|medium|low",
  "one_line_pitch": "...",
  "evidence_urls": ["..."]
}}"""

    response = call_claude(prompt, system=EXPLORER_SYSTEM, max_tokens=16000)
    data = extract_json_from_response(response)
    if not data:
        data = {"gap_title": title, "raw_response": extract_text_from_response(response)}
    return data


def run_explorations(survivors: list[dict]):
    """Run Stage 9 deep exploration on surviving gaps."""
    print(f"\n{'='*60}")
    print(f"  Phase 3: Deep Exploration ({len(survivors)} opportunities)")
    print(f"{'='*60}")

    explorations = []
    for i, gap in enumerate(survivors, 1):
        title = gap.get("gap_title", gap.get("title", "Unknown"))
        print(f"\n  [{i}/{len(survivors)}] Exploring: {title}")
        result = stage_9_deep_explore(gap)
        explorations.append(result)

        conviction = result.get("overall_conviction", "?")
        pitch = result.get("one_line_pitch", "")
        print(f"    -> Conviction: {conviction}")
        if pitch:
            print(f"    -> Pitch: {pitch}")

    # Save all explorations
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    exp_file = OUTPUT_DIR / "explorations.json"
    exp_file.write_text(json.dumps(explorations, indent=2), encoding="utf-8")

    # Generate exploration report
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# GapFinder v3 — Opportunity Exploration Report",
        f"Generated: {now}",
        f"Deep-dived **{len(explorations)}** surviving opportunities\n",
        "---\n",
    ]

    for exp in explorations:
        title = exp.get("gap_title", "Unknown")
        conviction = exp.get("overall_conviction", "?")
        pitch = exp.get("one_line_pitch", "N/A")

        lines.append(f"## {title}")
        lines.append(f"**Conviction:** {conviction} | **Pitch:** {pitch}\n")

        # Target users
        users = exp.get("target_users", {})
        if users.get("primary_persona"):
            lines.append(f"**Target:** {users['primary_persona']}")
        if users.get("pain_quotes"):
            lines.append("\n**Pain quotes:**")
            for q in users["pain_quotes"][:3]:
                lines.append(f'> "{q.get("quote", "")}" — {q.get("source", "")}')
            lines.append("")

        # Market
        market = exp.get("market_sizing", {})
        if market.get("tam"):
            lines.append(f"**TAM:** {market['tam']} | **SAM:** {market.get('sam', '?')} | **SOM:** {market.get('som', '?')}")

        # Positioning
        pos = exp.get("competitive_positioning", {})
        if pos.get("unique_angle"):
            lines.append(f"\n**Unique angle:** {pos['unique_angle']}")

        # MVP
        mvp = exp.get("mvp", {})
        if mvp.get("two_week_version"):
            lines.append(f"\n**2-week MVP:** {mvp['two_week_version']}")
        if mvp.get("validation_method"):
            lines.append(f"**Validate by:** {mvp['validation_method']}")
        if mvp.get("success_metric"):
            lines.append(f"**Success metric:** {mvp['success_metric']}")

        # Business model
        biz = exp.get("business_model", {})
        if biz.get("recommended"):
            lines.append(f"\n**Business model:** {biz['recommended']}")
        if biz.get("pricing_strategy"):
            lines.append(f"**Pricing:** {biz['pricing_strategy']}")

        # Distribution
        dist = exp.get("distribution", {})
        if dist.get("launch_playbook"):
            lines.append(f"\n**Launch playbook:** {dist['launch_playbook']}")

        # Risks
        risks = exp.get("risks", [])
        if risks:
            lines.append("\n**Risks:**")
            for r in risks:
                lines.append(f"- [{r.get('severity', '?')}] {r.get('risk', '')} — {r.get('mitigation', '')}")

        # Comparables
        comps = exp.get("comparable_successes", [])
        if comps:
            lines.append("\n**Comparable successes:**")
            for c in comps:
                lines.append(f"- **{c.get('company', '?')}:** {c.get('lesson', '')}")

        lines.append("\n---\n")

    report = "\n".join(lines)
    report_file = OUTPUT_DIR / "exploration_report.md"
    report_file.write_text(report, encoding="utf-8")
    git_commit("Phase 3: Deep exploration of surviving opportunities")
    print(f"\n    -> {report_file}")


# ===========================================================================
# PIPELINE ORCHESTRATION
# ===========================================================================

def scan_domain(domain: str) -> dict:
    """Run the full 6-stage gap analysis on a single domain."""
    print(f"\n{'='*60}")
    print(f"  Domain: {domain}")
    print(f"{'='*60}")

    out_dir = ensure_output_dir(domain)

    landscape = stage_1_landscape(domain, out_dir)
    git_commit(f"Stage 1: Landscape scan for '{domain}'")

    matrix = stage_2_feature_matrix(domain, landscape, out_dir)
    git_commit(f"Stage 2: Feature matrix for '{domain}'")

    gaps = stage_3_gaps(domain, landscape, matrix, out_dir)
    git_commit(f"Stage 3: Gap identification for '{domain}'")

    validated = stage_4_validate(domain, gaps, out_dir)
    git_commit(f"Stage 4: Demand validation for '{domain}'")

    ranked = stage_5_score(domain, gaps, validated, out_dir)
    git_commit(f"Stage 5: Scoring & ranking for '{domain}'")

    stage_6_report(domain, ranked, out_dir)
    git_commit(f"Stage 6: Gap report for '{domain}'")

    return ranked


def run_full_scan(domains: list[str] | None = None, run_v2: bool = False, run_explore: bool = False):
    """Scan domains and optionally run reality check + exploration."""
    domains = domains or DOMAINS_TO_SCAN
    all_gaps = []

    phase_label = "v1"
    if run_v2 and run_explore:
        phase_label = "v3 (full pipeline)"
    elif run_v2:
        phase_label = "v2"

    print(f"GapFinder {phase_label} — Scanning {len(domains)} domain(s)")
    print(f"Model: {MODEL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Phase 1: Scan all domains
    for domain in domains:
        result = scan_domain(domain)
        for gap in result.get("ranked_gaps", []):
            gap["domain"] = domain
            all_gaps.append(gap)

    all_gaps.sort(key=lambda g: g.get("opportunity_score", 0), reverse=True)

    # Master report
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
        lines.append(f"- **What to build:** {gap.get('what_to_build', 'N/A')}")
        lines.append(f"- **Who needs it:** {gap.get('who_needs_it', 'N/A')}")
        lines.append("")

    (OUTPUT_DIR / "master_gap_report.md").write_text("\n".join(lines), encoding="utf-8")
    (OUTPUT_DIR / "all_gaps_ranked.json").write_text(json.dumps(all_gaps, indent=2), encoding="utf-8")
    git_commit("Master gap report across all domains")

    print(f"\n  Phase 1 DONE — {len(all_gaps)} gaps across {len(domains)} domains")

    # Phase 2: Reality Check
    survivors = []
    if run_v2:
        top_gaps = all_gaps[:TOP_N_GAPS]
        reality_results = run_reality_checks(top_gaps)
        survivors = stage_8_final_report(reality_results)

        proceed = sum(1 for r in reality_results if r.get("verdict") == "PROCEED")
        diff = sum(1 for r in reality_results if r.get("verdict") == "DIFFERENTIATE")
        abandon = sum(1 for r in reality_results if r.get("verdict") == "ABANDON")
        print(f"\n  Phase 2 DONE — PROCEED: {proceed} | DIFFERENTIATE: {diff} | ABANDON: {abandon}")

    # Phase 3: Deep Exploration
    if run_explore and survivors:
        run_explorations(survivors)
        print(f"\n  Phase 3 DONE — {len(survivors)} opportunities explored")
    elif run_explore and not survivors:
        print("\n  Phase 3 SKIPPED — No survivors to explore. Run with --v2 first.")


def run_reality_check_only():
    """Run Phase 2 on existing v1 output."""
    raw_file = OUTPUT_DIR / "all_gaps_ranked.json"
    if not raw_file.exists():
        print(f"ERROR: {raw_file} not found. Run v1 scan first.")
        sys.exit(1)

    all_gaps = json.loads(raw_file.read_text(encoding="utf-8"))
    print(f"Loaded {len(all_gaps)} gaps from {raw_file}")

    top_gaps = all_gaps[:TOP_N_GAPS]
    reality_results = run_reality_checks(top_gaps)
    survivors = stage_8_final_report(reality_results)
    return survivors


def run_explore_only():
    """Run Phase 3 on existing reality check output."""
    rc_file = OUTPUT_DIR / "reality_checks.json"
    if not rc_file.exists():
        print(f"ERROR: {rc_file} not found. Run --v2 first.")
        sys.exit(1)

    reality_results = json.loads(rc_file.read_text(encoding="utf-8"))
    survivors = [r for r in reality_results if r.get("verdict") in ("PROCEED", "DIFFERENTIATE")]

    if not survivors:
        print("No survivors to explore. All gaps were ABANDON/PIVOT.")
        sys.exit(0)

    print(f"Found {len(survivors)} surviving gaps to explore")
    run_explorations(survivors)


# ===========================================================================
# CLI
# ===========================================================================
def main():
    args = sys.argv[1:]

    run_v2 = "--v2" in args
    reality_only = "--reality-check" in args
    explore_only = "--explore" in args and "--v2" not in args and "--discover" not in args
    run_explore = "--explore" in args
    discover_seed = None

    # Extract --discover value
    if "--discover" in args:
        idx = args.index("--discover")
        if idx + 1 < len(args) and not args[idx + 1].startswith("--"):
            discover_seed = args[idx + 1]
        else:
            print("ERROR: --discover requires a seed area. Example: --discover \"AI infrastructure\"")
            sys.exit(1)

    # Remove flags from args to get bare domain names
    flags = {"--v2", "--reality-check", "--explore", "--discover"}
    domains = [a for a in args if a not in flags and a != discover_seed]

    if reality_only:
        survivors = run_reality_check_only()
        if run_explore and survivors:
            run_explorations(survivors)
    elif explore_only:
        run_explore_only()
    elif discover_seed:
        # Full autonomous pipeline: discover → scan → kill → explore
        discovered = phase_0_discover(discover_seed)
        if not discovered:
            print("ERROR: No domains discovered. Try a different seed area.")
            sys.exit(1)
        run_full_scan(discovered, run_v2=run_v2, run_explore=run_explore)
    elif domains:
        run_full_scan(domains, run_v2=run_v2, run_explore=run_explore)
    else:
        run_full_scan(run_v2=run_v2, run_explore=run_explore)


if __name__ == "__main__":
    main()
