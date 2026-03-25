# GapFinder v2: Competition Reality Check Stage

## Problem Statement

GapFinder v1 identifies market gaps using demand signals, competition scoring, and feasibility analysis. However, it **does not validate whether identified gaps have already been filled or are actively being closed** by the time you act on them. This leads to a critical failure mode:

> **A gap that scored 57/100 six months ago may be a crowded market today.**

## Solution: Stage 7 — Competition Reality Check

Add a mandatory validation stage **after** gap scoring and **before** any build decision.

### Updated Pipeline
```
Stage 1-6: (unchanged)
Stage 7: Competition Reality Check  <- NEW
Stage 8: Final Recommendation       <- NEW
```

### Stage 7 Methodology
1. Direct Competitor Search (5+ queries per gap)
2. First-Party Fix Detection (Anthropic, OpenAI, Cloudflare, Google, AWS, etc.)
3. Velocity Analysis (solutions shipped in last 6 months)
4. "Top N Lists" Test (do comparison articles exist?)
5. Open-Source Saturation Check (GitHub repos in last 6 months)
6. HN/Reddit Signal Check ("I built X" posts)

### Scoring
```
Reality_Check starts at 100, subtract:
- First_Party_Modifier: 0 to -75
- Velocity_Penalty: -(velocity_score * 0.3)
- Saturation_Penalty: -(github_repos_6mo * 3, max -30)
- Top_N_Penalty: -20 if comparison articles exist
- Floor at 0
```

### Verdicts
- PROCEED: Adjusted > 40, Reality > 60
- DIFFERENTIATE: Adjusted > 30, Reality 30-60
- PIVOT: Adjusted > 20, Reality 10-30
- ABANDON: Adjusted < 20, Reality < 10
