# GapFinder v2 — Competition Reality Check Report
Generated: 2026-03-30
Reality-checked **20** top gaps across **15 domains** (241 total gaps from v1)

---

## Verdict Summary

| Verdict | Count | Meaning |
|---------|-------|---------|
| PROCEED | **0** | None survived clean |
| DIFFERENTIATE | **1** | Narrow window with unique angle required |
| PIVOT | **3** | Core thesis dead, adjacent angle might work |
| ABANDON | **16** | Market solved or saturated |

**Again: zero clean green lights.** Same pattern as our first 10-domain scan.

---

## Full Scorecard

| # | Gap | Domain | v1 Score | Reality | Verdict |
|---|-----|--------|----------|---------|---------|
| 1 | Unified Context Budget Manager | Context Engineering | 6.48 | 0 | ABANDON |
| 2 | HITL Browser Agent Orchestration | Browser Automation | 6.48 | 0 | ABANDON |
| 3 | Model Conversion & Optimization Hub | On-Device/Edge SLM | 6.48 | 0 | ABANDON |
| 4 | Unified FC Data Format & Converter | Function Call Training | 6.48 | 8 | ABANDON |
| 5 | Reward Function Marketplace | RL for SLM Reasoning | 5.76 | 30 | DIFFERENTIATE |
| 6 | Quantization-Aware Reasoning Eval | SLM Reasoning Eval | 5.76 | 0 | ABANDON |
| 7 | Browser Agent Security & Sandboxing | Browser Automation | 5.76 | 0 | ABANDON |
| 8 | KG-SLM Agentic Workflows | Knowledge Graph + SLM | 5.76 | ~25 | PIVOT |
| 9 | SLM-Optimized RM Training Toolkit | Reward Model Training | 5.76 | 0 | ABANDON |
| 10 | Multi-Step Agentic Workflow Router | Model Routing | 5.76 | 0 | ABANDON |
| 11 | End-to-End SLM FC Toolkit | Function Call Training | 5.76 | 0 | ABANDON |
| 12 | Tool-Use Agentic Data Generator | Synthetic Data | 5.67 | 0 | ABANDON |
| 13 | Edge-Native SLM Cascading Router | Model Routing | 5.67 | 0 | ABANDON |
| 14 | On-Device RAG Pipeline | On-Device/Edge SLM | 5.67 | 0 | ABANDON |
| 15 | Custom Domain Verifier Training | Reward Model Training | 5.40 | 14 | PIVOT |
| 16 | Budget-Constrained Adaptive Router | Model Routing | 5.12 | 0 | ABANDON |
| 17 | End-to-End Distillation Pipeline | Reasoning Distillation | 5.04 | 11 | PIVOT |
| 18 | Plug-and-Play Reasoning Layer | Test-Time Compute | 5.04 | 0 | ABANDON |
| 19 | Difficulty-Calibrated Curriculum | Synthetic Data | 5.04 | 8 | ABANDON |
| 20 | Context Quality Scoring Dashboard | Context Engineering | 5.04 | 0 | ABANDON |

---

## The Sole Survivor: DIFFERENTIATE

### Reward Function Marketplace / Curated Verifier Registry (Score: 30)
- **Domain:** RL for SLM Reasoning
- **What survived:** TRL has only 4 built-in reward functions. No community registry of domain-specific RLVR verifiers exists.
- **What's dead:** Eureka and Text2Reward show LLMs can auto-generate rewards, undermining the "marketplace" model.
- **Required angle:** Curated, benchmarked registry of RLVR verifiers for NON-math/code domains (legal, medical, finance). The "verifier problem" for custom domains remains unsolved.
- **Window:** 6-12 months before auto-generation matures

---

## PIVOT Opportunities (Narrow Adjacent Angles)

### 1. Custom Domain Verifier Training (Score: 14)
- **Dead thesis:** Platform for training domain verifiers
- **Why dead:** Labelbox, Nebius offer white-glove services; Databricks published methodology; HuggingFace TRL commoditizing
- **Pivot to:** Self-serve no-code verifier builder for non-ML teams in regulated industries. The domain expertise barrier (needing actual doctors/lawyers) matters more than the software.

### 2. End-to-End Distillation Pipeline (Score: 11)
- **Dead thesis:** Unified platform for teacher-student reasoning transfer
- **Why dead:** OpenAI's Model Distillation API, Predibase RFT, DeepSeek open weights all cover this
- **Pivot to:** Visual pipeline builder specifically for distilling proprietary models into edge-deployable SLMs. The "visual builder" is a UI feature gap, not a capability gap.

### 3. KG-SLM Agentic Workflows (Score: ~25)
- **Dead thesis:** SLM-optimized KG memory for agents
- **Why dead:** Microsoft GraphRAG, Neo4j GenAI, FalkorDB GraphRAG all exist
- **Pivot to:** Lightweight KG that runs ON-DEVICE alongside SLMs for offline agentic reasoning. No existing GraphRAG solution works without cloud.

---

## The Graveyard: What v1 Got Wrong (Again)

### Most Inflated Gaps

| Gap | v1 Score | v2 Score | Delta | Why Dead |
|-----|----------|----------|-------|----------|
| Context Budget Manager | 6.48 | 0 | **-6.48** | Anthropic & OpenAI both shipped in their Agent SDKs |
| HITL Browser Orchestration | 6.48 | 0 | **-6.48** | Stagehand, OpenAI Agents SDK, LangGraph, Vercel all have HITL |
| Model Conversion Hub | 6.48 | 0 | **-6.48** | HuggingFace Optimum IS the hub |
| On-Device RAG | 5.67 | 0 | **-5.67** | Google AI Edge RAG SDK, Microsoft Foundry Local |
| Edge Cascading Router | 5.67 | 0 | **-5.67** | vLLM Semantic Router shipped Jan 2026 |
| Plug-and-Play Reasoning | 5.04 | 0 | **-5.04** | LLM Reasoners library, AG2 ReasoningAgent |

### Root Causes (Consistent with First Scan)
1. **First-party fixes:** Anthropic, OpenAI, Google, HuggingFace are shipping fast
2. **Academic-to-production pipeline:** Research papers from 6 months ago are now shipped tools
3. **v1 doesn't check existing SDKs:** Many "gaps" are features already in LangChain, TRL, HuggingFace
4. **"Unified" is a weak thesis:** Developers use 1-2 tools, not universal converters

---

## Cross-Scan Comparison

| Metric | First Scan (10 AI infra domains) | This Scan (15 AI pipeline + SLM domains) |
|--------|----------------------------------|------------------------------------------|
| Total gaps | 141+ | 241 |
| Top 20 reality-checked | 20 | 20 |
| PROCEED | 0 | 0 |
| DIFFERENTIATE | 4 | 1 |
| PIVOT | 3 | 3 |
| ABANDON | 12 | 16 |

**This scan is even more brutal.** SLM reasoning and agent pipeline tooling are moving faster than the general AI infra market. The gap-to-saturation cycle appears to be **3-4 months**, not 6.

---

## What's Actually Still Open (March 2026)

Based on both scans (25 domains, 380+ gaps, 40 reality-checked):

1. **The verifier/reward function problem for non-math/code domains** — The only gap that survived as DIFFERENTIATE in this scan. Building custom verifiers for legal, medical, and finance reasoning is genuinely unsolved.

2. **On-device KG for offline agentic reasoning** — Every GraphRAG solution requires cloud. A lightweight KG that runs alongside SLMs on-device is a real gap.

3. **Self-serve domain verifier builder** — The tools exist for ML engineers, but not for domain experts (doctors, lawyers) who actually know what "correct" looks like.

4. **Cross-domain themes from first scan still valid:**
   - Regulated industry tooling (compliance-first SLM training)
   - Radical simplification for small teams
   - Vendor-neutral infrastructure

---

## The Meta-Lesson (Reinforced)

> **The AI infrastructure market's gap-to-saturation cycle is accelerating.** In our first scan, it was ~6 months. In this scan, we found gaps that went from "wide open" to "multiple GA solutions" in 3-4 months.

> **The highest-scoring v1 gaps are the most likely to be dead.** High scores mean high demand + high feasibility + low competition. But high demand + high feasibility means *everyone else* sees it too. The best opportunities may be the ones that score 3-4, not 6+.

> **Zero PROCEED in 40 reality checks.** This doesn't mean nothing is buildable — it means everything requires a sharp differentiation angle. The era of "build the obvious tool nobody built" is over for AI infrastructure.

---

*GapFinder v2 — 15 domains, 241 gaps, 20 reality-checked, 0 PROCEED, 1 DIFFERENTIATE*
*The most valuable output is still the gaps it kills.*
