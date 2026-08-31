# PIIS

**Personal Information Intelligence System**

**V0.1** is a modular information-processing pipeline: it turns external content into claims, compares those claims with separated knowledge stores, and produces traceable analysis without pretending to determine truth.

That is the current implementation, not the whole product.

The longer design direction is:

> PIIS helps people understand the information world without requiring them to personally consume the entire information stream.

It does not exist to make people consume more information. When someone **chooses** to understand something, PIIS should help them spend limited attention on information that is actually worth understanding.

That is a design direction, not a promise of efficiency or truth.

---

## Current

V0.1.1 is a patch on the frozen V0.1 architecture/prototype: replaceable provider ports, mock providers, JSON knowledge as Source of Truth, SQLite runtime state, rebuildable embeddings, a heuristic semantic-diff engine, Markdown/JSON reports, a CLI, FastAPI, and an empty Question Bank module.

It runs fully offline. It does not crawl the web, call cloud APIs, edit beliefs, or declare what is true.

```text
Content → Claim → Knowledge → Reasoning → Report
```

```text
Acquisition → Extraction → Normalization → Claim Extraction
    → Knowledge Retrieval → Semantic Diff → Evidence Analysis → Report
```

Details: [docs/architecture.md](docs/architecture.md). Concepts: [docs/concepts.md](docs/concepts.md).

---

## Problem

The motivating thesis is not merely “there is too much information.”

Information production and distribution can grow much faster than one person’s ability to inspect, compare, understand, and contextualize that information.

The scarce resources are human time, attention, and cognitive processing capacity.

So the interesting problem gradually shifts from **information retrieval** toward **selection, contextualization, comparison, and understanding**. PIIS is primarily exploring that second class of problems.

This is a product thesis, not an established economic law.

---

## Vision

Help the user understand what is going on — including disagreement, uncertainty, and sources — without forcing them to ingest the whole stream.

PIIS should optimize for understanding per unit of attention the user has **already decided** to spend, not for word count, notifications, or engagement time.

---

## Distinction

PIIS is **not**:

- a generic chatbot or LLM wrapper
- a Bilibili / web summarizer
- a browser extension
- a generic Agent platform
- a truth oracle
- an automatic belief-management system
- an attention dictator, productivity nanny, or anti-entertainment product
- a fully autonomous cognitive OS

People may rationally watch entertainment, browse social media, or spend time on content with little informational value. PIIS does not judge those choices. It assists when the user **chooses to understand**.

---

## Design philosophy

- **Deterministic when possible**, classical/statistical methods when useful, ML/DL when generalization helps, **LLM when semantic work is actually necessary**, human judgment at the final boundary.
- LLMs are **components**, not the foundation. More LLM calls is not more intelligence.
- **Model/vendor independence**: knowledge assets should outlive any provider.
- **Provenance** should become first-class (not fully implemented in V0.1).
- **Explicit uncertainty**: do not collapse fact framing, verification, similarity, relation, evidence level, and confidence into one score.
- **Anti-echo-chamber**: do not optimize only for content compatible with what the user already believes.
- **Epistemic challenger, not cognitive governor**: PIIS may surface a challenge; it must not order a belief change.
- **Question Bank ≠ user knowledge.** V0.1 includes an empty, extensible question-bank module so future assessment can estimate knowledge state gradually. It is not a profile, not personal knowledge, and not wired into the processing pipeline.

See [docs/concepts.md](docs/concepts.md).

---

## Product modes (long-term)

Both modes should share the same architecture. They are not two products. Neither is implemented as a product UX in V0.1.

**Curiosity Mode** — likely entry point. “What is this? What happened? Why does it matter? What are the competing explanations?” The user should not need to spend hours building a knowledge base first. The output is a concise understanding map plus optional deep sources, not a giant summary.

**Deep / Continuous Mode** — for people who maintain long-term interests (research, engineering, writing, analysis, serious learning). Creator monitoring, ongoing ingestion, domain and primary-source libraries, personal knowledge, claim history, provenance, conflict detection.

Onboarding should **not** be “build your knowledge base first.” A **Knowledge State** (estimated understanding) should emerge over time, and stay distinct from **Personal Belief** (what the user explicitly endorses).

V0.1 ships only the **empty Question Bank architecture** for that future path. There is no question content, no assessment engine, and no knowledge-state inference yet.

---

## V0.1 invariants (still in force)

1. Information is not knowledge. External claims are not auto-promoted into authoritative knowledge.
2. `ClaimType.FACT` is author framing, not verified truth. `FACT + UNVERIFIED` is valid.
3. Similarity is not agreement. High similarity can still be `CONFLICTING`.
4. Personal Knowledge is read-only during processing. The user decides.
5. Evidence level, extractor confidence, and verification status are not a truth score.
6. The Question Bank is an input asset for future assessment, not a representation of the user's knowledge.

---

## Current status

**V0.1.1 — architecture / prototype (V0.1 line, patch).**

Implemented:

- replaceable provider interfaces
- mock acquisition / extraction / LLM / embedding providers
- four isolated knowledge stores
- JSON knowledge persistence (Source of Truth)
- SQLite runtime state (jobs and report paths only)
- rebuildable in-memory vector layer (Derived Data)
- semantic diff engine
- heuristic relation classifier (LLM classifier port ready)
- evidence-analysis abstraction
- Markdown / JSON reports
- CLI (`piis process`)
- FastAPI
- offline demo
- test suite
- empty Question Bank architecture (`src/piis/assessment/`, `data/assessment/questions/` with no items)

V0.1 does **not**: automatic belief modification, autonomous agents, large-scale crawling, truth declarations, required cloud providers, production fact-checking, multi-agent orchestration, user profiling, adaptive knowledge assessment, question content, response evaluation, or knowledge-state inference.

The sample JSON under `examples/sample_data/` is a **lab fixture** so the pipeline can be demonstrated offline. It is not the intended product onboarding model. It does not contain a question bank.

---

## Quick Start

Python 3.12+.

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

pip install -e ".[dev]"
pytest
python examples/basic_pipeline.py
```

CLI:

```bash
piis process https://example.com/demo
piis --help
```

If `piis` is not on PATH (common with the Microsoft Store Python on Windows), use `python -m piis --help` instead.

API:

```bash
uvicorn piis.api.main:app --reload
```

```text
GET /health  →  {"status": "ok"}
POST /process  {"url": "https://example.com/demo"}
GET /reports/{id}
```

Copy `.env.example` to `.env` for local overrides. Never commit `.env` or API keys.

On Windows consoles that are not UTF-8, step markers print as `[ok]` instead of `✓`.

---

## Example

`https://example.com/demo` is a fictional transcript. Sample knowledge in `examples/sample_data/` is fictional and safe to commit.

The demo is built so a report can show:

- redundant restatement of domain knowledge
- conflict with a sample personal belief
- unrelated geography next to AI/programming knowledge
- an evidence gap on a prediction with no supporting span

Generated reports go to `data/processed/` (gitignored). SQLite runtime state is `data/runtime/piis.db` (gitignored). Real personal knowledge belongs in `data/personal/` (gitignored).

---

## Persistence

- **JSON** = Source of Truth (knowledge)
- **SQLite** = runtime state only
- **Vector index** = derived data, rebuilt from JSON text

---

## Roadmap

Future work is grouped by capability, not treated as a promise or a rigid sequence:

- information acquisition
- question bank / knowledge assessment (empty architecture in V0.1)
- knowledge state
- reasoning and evidence
- provenance
- user experience (Curiosity vs Deep Mode)
- model portability
- epistemic / safety boundaries

The intended convergence is a Personal Information Intelligence System, not a generic Agent platform.

See [docs/roadmap.md](docs/roadmap.md).

---

## License

MIT. See [LICENSE](LICENSE).
