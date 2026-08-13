# PIIS

**Personal Information Intelligence System**

A modular information-processing system that turns external content into claims, compares those claims with separated knowledge stores, and produces traceable analysis without pretending to determine truth.

> Do not optimize for consuming more information. Optimize for consuming the information that matters.

---

## What is PIIS?

Modern Internet users consume large amounts of information, but acquisition is often passive, repetitive, and hard to compare with what they already know.

PIIS explores a different workflow:

```text
external information
    ↓
structured claims
    ↓
knowledge retrieval
    ↓
semantic comparison
    ↓
evidence gaps / conflicts / relations
    ↓
human-readable report
```

**V0.1 is an information-processing pipeline with replaceable ports.** It is not a generic chatbot, not a Bilibili summarizer, not a browser extension, not an autonomous agent, not a truth oracle, not an automatic belief-management system, and not a fully autonomous cognitive OS.

```text
Content → Claim → Knowledge → Reasoning → Report
```

The long-term direction is a personal information-intelligence system. V0.1 keeps that scope small on purpose.

---

## Core Architecture

| Layer | Meaning |
| --- | --- |
| **Content** | Raw internet payload (video, article, post, …). Not a claim. Not knowledge. |
| **Claim** | A proposition extracted from Content. Not knowledge. |
| **Knowledge** | Stored items in four isolated stores: domain, primary, personal, external. |
| **Reasoning** | Analysis of claims against knowledge (relations, gaps, reports). Not knowledge. |

Implementation pipeline:

```text
Acquisition → Extraction → Normalization → Claim Extraction
    → Knowledge Retrieval → Semantic Diff → Evidence Analysis → Report
```

Details: [docs/architecture.md](docs/architecture.md).

---

## Design Principles

1. **Information is not knowledge.** External content is raw. Claims are extracted, then compared with existing knowledge. The pipeline does not promote external claims into authoritative knowledge.
2. **FACT is framing, not truth.** `ClaimType.FACT` means the author presented a proposition as fact. `FACT + UNVERIFIED` is a valid state.
3. **Similarity is not agreement.** Embedding similarity is a signal. Classification decides the relation. High similarity can still be `CONFLICTING`.
4. **Personal beliefs are not automatically changed.** The V0.1 pipeline is read-only toward Personal Knowledge. The user decides.
5. **Evidence is not truth.** Evidence level, extractor confidence, and verification status are separate. They are not collapsed into a truth score.

See [docs/concepts.md](docs/concepts.md).

---

## Current Status

**V0.1.0 — architecture / prototype (frozen).**

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

---

## What V0.1 Does NOT Do

- no automatic belief modification
- no real autonomous agents
- no large-scale crawling
- no automatic truth oracle
- no cloud provider required
- no production-grade fact checking
- no multi-agent orchestration
- no browser extension
- no generic chatbot

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

## Architecture

See [docs/architecture.md](docs/architecture.md).

Persistence freeze:

- **JSON** = Source of Truth (knowledge)
- **SQLite** = runtime state only
- **Vector index** = derived data, rebuilt from JSON text

---

## Roadmap

V0.1.0 is frozen. Later versions may add real LLM/embedding providers, transcription, and richer personal-knowledge tooling — still without auto-editing beliefs or declaring truth.

See [docs/roadmap.md](docs/roadmap.md).

---

## License

MIT. See [LICENSE](LICENSE).
