# GapFinder — Automated Software Tool Gap Discovery

## What This Is

A research agent that systematically discovers unserved gaps in any
software domain. Feed it a category, it maps the landscape, finds
what's missing, validates demand, and outputs a ranked gap report.

NOT autoresearch (no keep/revert loop).
This is a structured research pipeline with web search + analysis.

## Why Not Autoresearch?

Autoresearch needs: one file, one metric, one loop.
Gap discovery has no scalar metric — you can't score
"is this a real gap" as 0.73 vs 0.81. Verification
requires market research, not repeated experiments.

What we borrow from autoresearch:
- Systematic, tireless execution
- Agent-driven (human sleeps, agent works)
- Structured output (not vague analysis)
- Git as memory (each research session committed)

## Architecture

```
Input: "AI agent testing tools"
         │
         ▼
┌─────────────────────────────┐
│  Stage 1: LANDSCAPE SCAN     │
│  - Search for all tools       │
│  - Scrape product pages       │
│  - Extract features/pricing   │
│  - Build tool × feature matrix│
│  Output: landscape.json       │
└──────────────┬────────────────┘
               ▼
┌─────────────────────────────┐
│  Stage 2: FEATURE MATRIX     │
│  - Standardize features       │
│  - Mark: ✓ has / ✗ missing    │
│  - Identify sparse columns    │
│    (features few tools have)  │
│  - Identify empty rows        │
│    (tools nobody has built)   │
│  Output: feature_matrix.json  │
└──────────────┬────────────────┘
               ▼
┌─────────────────────────────┐
│  Stage 3: GAP IDENTIFICATION │
│  - Find missing combinations  │
│  - Find underserved segments  │
│  - Find integration gaps      │
│  - Find pricing gaps          │
│  Output: raw_gaps.json        │
└──────────────┬────────────────┘
               ▼
┌─────────────────────────────┐
│  Stage 4: DEMAND VALIDATION  │
│  - Search Reddit/HN/Twitter   │
│    for complaints/requests    │
│  - Search GitHub Issues for   │
│    feature requests           │
│  - Search Google Trends for   │
│    rising search terms        │
│  - Count demand signals       │
│  Output: validated_gaps.json  │
└──────────────┬────────────────┘
               ▼
┌─────────────────────────────┐
│  Stage 5: SCORING & RANKING  │
│  Score each gap on:           │
│  - Demand signals (0-10)      │
│  - Competition density (0-10) │
│  - Technical feasibility(0-10)│
│  - Market size estimate       │
│  - Build complexity estimate  │
│  Output: ranked_gaps.json     │
└──────────────┬────────────────┘
               ▼
┌─────────────────────────────┐
│  Stage 6: REPORT GENERATION  │
│  - Top 10 gaps with evidence  │
│  - For each: what to build,   │
│    who needs it, why now,     │
│    existing alternatives,     │
│    demand proof               │
│  Output: gap_report.md        │
└──────────────────────────────┘
```

## How to Run

### Option A: Claude Code (Recommended)

```bash
claude -p "You are a market research agent. Research the
domain: 'AI agent testing and evaluation tools'.

Execute these stages in order:

Stage 1: Search for every tool in this space. For each tool,
record: name, URL, pricing, key features, target audience,
funding/size. Search at least 5 different queries.

Stage 2: Build a feature matrix. Rows = tools, Columns = 
features. Mark each cell as supported/not supported.

Stage 3: Find gaps — features that 0-1 tools offer, 
combinations nobody provides, segments nobody targets.

Stage 4: Validate each gap. Search Reddit, Hacker News,
Twitter for people complaining about or requesting this
capability. Count the demand signals.

Stage 5: Score each gap on demand (0-10), competition (0-10
where 10 = no competition), and feasibility (0-10).

Stage 6: Write a gap_report.md with the top 10 gaps,
ranked by opportunity score = demand × (10 - competition)
× feasibility. Include evidence links for each.

Save all intermediate outputs as JSON files.
Commit after each stage." \
  --dangerously-skip-permissions
```

### Option B: Python Script with Claude API

For repeatable, scheduled gap scanning across multiple domains.

```python
# gapfinder.py — Automated gap discovery
# Uses Claude API for analysis, web search for data

import anthropic
import json
import os
from datetime import datetime

client = anthropic.Anthropic()

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

def scan_domain(domain: str) -> dict:
    """Run full gap analysis on a domain."""
    
    # Stage 1-6 in one structured prompt
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search"
        }],
        messages=[{
            "role": "user",
            "content": f"""Research the software tool landscape for: "{domain}"

Execute this analysis:

1. LANDSCAPE: Search for all major tools in this space. 
   List each with: name, URL, 3 key features, pricing model, 
   target audience.

2. FEATURE MATRIX: Create a feature comparison. 
   Identify which features are common vs rare.

3. GAPS: Identify what's missing:
   - Features 0-1 tools offer
   - User segments nobody targets well
   - Workflows nobody automates end-to-end
   - Integration gaps between tools
   - Pricing gaps (everything expensive, nothing free/open-source, etc.)

4. DEMAND SIGNALS: For each gap, search for evidence 
   that people want this. Look for Reddit posts, HN comments, 
   GitHub issues, tweets asking for this capability.

5. RANKING: Score each gap:
   - demand (0-10): how many people seem to want this
   - competition (0-10): 10 = nobody does this, 0 = crowded
   - feasibility (0-10): how hard to build
   - opportunity = demand × competition × feasibility / 100

Return as JSON:
{{
  "domain": "{domain}",
  "tools_found": [...],
  "feature_matrix": {{...}},
  "gaps": [
    {{
      "title": "...",
      "description": "...",
      "demand_score": N,
      "competition_score": N,
      "feasibility_score": N,
      "opportunity_score": N,
      "evidence": ["url1", "url2"],
      "who_needs_it": "...",
      "what_to_build": "..."
    }}
  ]
}}"""
        }]
    )
    
    return response

def run_full_scan():
    """Scan all domains and generate master report."""
    all_gaps = []
    
    for domain in DOMAINS_TO_SCAN:
        print(f"\nScanning: {domain}...")
        result = scan_domain(domain)
        # Parse and collect gaps
        # ... (extract from response)
        
    # Sort all gaps by opportunity score
    all_gaps.sort(key=lambda g: g.get("opportunity_score", 0), reverse=True)
    
    # Generate master report
    report = f"# GapFinder Report — {datetime.now().strftime('%Y-%m-%d')}\n\n"
    report += f"Scanned {len(DOMAINS_TO_SCAN)} domains\n\n"
    report += "## Top 20 Gaps by Opportunity Score\n\n"
    
    for i, gap in enumerate(all_gaps[:20], 1):
        report += f"### {i}. {gap['title']}\n"
        report += f"- **Domain:** {gap.get('domain', 'N/A')}\n"
        report += f"- **Opportunity Score:** {gap['opportunity_score']}\n"
        report += f"- **What to build:** {gap['what_to_build']}\n"
        report += f"- **Who needs it:** {gap['who_needs_it']}\n\n"
    
    with open("gap_report.md", "w") as f:
        f.write(report)
    
    print(f"\nReport saved: gap_report.md")
    print(f"Total gaps found: {len(all_gaps)}")

if __name__ == "__main__":
    run_full_scan()
```

## Domains to Scan (Starter List)

### AI/ML Tool Gaps
- AI agent testing and evaluation
- AI agent prompt optimization
- LLM cost monitoring per task/workflow
- AI agent drift detection and auto-repair
- Domain SLM training platforms
- AI agent security/guardrails
- MCP server ecosystem tools
- Multi-agent orchestration
- AI workflow debugging/replay

### Enterprise Automation Gaps
- Insurance claims automation
- HR compliance automation (UAE/GCC specific)
- Document intelligence for regulated industries
- Enterprise AI governance dashboards
- AI-powered audit trail systems

### Developer Tool Gaps
- AI code review for specific frameworks
- Automated API documentation from code
- AI-powered database migration tools
- Test data generation for regulated industries
- AI-assisted incident response

### Synergy-Adjacent Gaps
- No-code domain entity builder with AI
- AI agent marketplace/registry
- Cross-MCP-server context sharing
- Agent performance benchmarking as a service
- AI workflow template marketplace

## What Makes This Different From Googling

1. **Systematic** — covers every tool, not just the ones you've heard of
2. **Feature matrix** — visual gaps that browsing product pages won't reveal
3. **Demand validated** — not just "nobody built it" but "people actually want it"
4. **Scored** — prioritized by opportunity, not gut feeling
5. **Repeatable** — run monthly to catch emerging gaps
6. **Multi-domain** — scan 10 domains in one run, find cross-domain patterns

## Output Example

```
Gap #1: Autoresearch for AI Agent Optimization
Domain: AI agent testing
Opportunity Score: 7.2
Demand: 8/10 (multiple Reddit posts, Karpathy's autoresearch viral)
Competition: 9/10 (nobody does this)
Feasibility: 8/10 (autoresearch pattern is proven)
Evidence: [reddit.com/r/LocalLLaMA/..., x.com/karpathy/...]
What to build: Closed-loop agent optimizer that evaluates + auto-improves
Who needs it: Every team running AI agents in production
```

## Publishing This

### As an Article
"I Built an Agent That Finds Software Gaps While I Sleep"
- Show the pipeline
- Show real gaps it found
- Show demand evidence
- Let readers run it on their own domains

### As an Open-Source Tool
- GitHub repo with the scanner script
- Configurable domain list
- JSON + Markdown output
- GitHub Actions for scheduled weekly scans

### As a Synergy Feature
- Integrate into Agent Studio
- Scan for gaps in YOUR domain (insurance, HR)
- Auto-suggest new agents to build based on gaps found
