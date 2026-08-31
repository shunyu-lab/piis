# Architecture

**V0.1 architecture is frozen.** This document describes the architecture that ships in **V0.1.1**. Do not expand it into V0.2.

V0.1 is an information-processing pipeline with replaceable ports. It is not a cognitive OS, Agent platform, or product UX for Curiosity/Deep modes.

Product philosophy lives in [docs/concepts.md](concepts.md). This file records **how that philosophy constrains the code**.

---

## Philosophy → engineering

```text
Product philosophy
      ↓
Knowledge boundaries
      ↓
Provider abstraction
      ↓
deterministic pipeline
      ↓
replaceable intelligence
      ↓
provenance hooks
      ↓
human decision boundary
```

| Philosophy | Engineering consequence in V0.1 |
| --- | --- |
| Understand, don’t amplify consumption | Pipeline ends in a **report**, not a feed, chatbot, or notification loop. |
| Assist only when the user chooses to understand | CLI/`POST /process` is **on-demand**. No background engagement optimizer. |
| Information ≠ knowledge ≠ reasoning | Separate models: `Content`, `Claim`, `KnowledgeItem`, analysis types. Pipeline must not write `SemanticDiffResult` into knowledge JSON. |
| FACT is framing | `ClaimType` independent of `VerificationStatus`. V0.1 always `UNVERIFIED`. |
| Similarity ≠ agreement | Semantic Diff is embed → **signal**, classify → **decision**. Heuristic classifier by default. |
| Personal belief ≠ estimated knowledge state | Personal store is **read-only** in the pipeline (`PermissionError` on save). No inferred “the user believes Y” from processing. Knowledge State is **not** a V0.1 type. |
| LLM is a capability, not the foundation | Business logic talks to ports (`LLMProvider`, `EmbeddingProvider`, …). Default relation classifier is **heuristic**. Unknown provider names **fail fast**. No vendor SDK in pipeline code. |
| Knowledge assets ⟂ model vendor | JSON is Source of Truth. Embeddings are derived and rebuildable. Swap providers in `runtime.py` without rewriting knowledge files. |
| Provenance will matter | Do not store vectors as the only copy of a claim or belief. Keep `source_url` / `source_content_id` / `source_span` / `metadata` extensible. Do not implement a provenance graph in V0.1. |
| Human judgment is final | Reports may show conflict and gaps. They must not auto-edit beliefs or declare truth. |
| Anti-echo-chamber (future) | Relation labels already include `conflicting`, not only `supporting` / `redundant`. Do not add a “maximize belief compatibility” ranker. |
| Knowledge state should emerge | Empty Question Bank module (`src/piis/assessment/`). Not wired into the pipeline. No items, engine, or inference in V0.1. |

Future Curiosity Mode and Deep Mode **share this pipeline**. Do not fork two architectures.

Assessment is a **sibling** of the pipeline, not a stage inside it:

```text
PIIS Core
   │
   ├── Information Pipeline
   ├── Knowledge System
   └── Assessment System
```

---

## Frozen conceptual layers

```text
Content → Claim → Knowledge → Reasoning
```

## Frozen implementation pipeline

```text
Acquisition → Extraction → Normalization → Claim Extraction
    → Knowledge Retrieval → Semantic Diff → Evidence Analysis → Report
```

---

## Four layers (do not collapse these)

```text
Content   →  Claim  →  Knowledge  →  Reasoning
 raw          extracted   stored         analysis result
```

| Layer | Module | Meaning |
| --- | --- | --- |
| Content | `models/content.py` | Internet payload (video, article, …) |
| Claim | `models/claim.py` | Propositions extracted from content |
| Knowledge | `models/knowledge.py` | Items in domain / primary / personal / external stores |
| Reasoning | `models/analysis.py` | Semantic diff, relations, evidence gaps, reports |

A `Claim` is not a `KnowledgeItem`. A `SemanticDiffResult` is not knowledge and must not be written into a knowledge JSON file by the pipeline.

`ClaimType.FACT` is **framing** (the author spoke as if stating a fact). It is not verification.

`PERSONAL_BELIEF` is explicit cognitive state. The pipeline is read-only toward personal knowledge.

---

## Persistence

Three categories. Do not mix them.

**JSON = Source of Truth**

Knowledge lives in JSON files (`examples/sample_data/` in the repo; `data/personal/` locally and gitignored). SQLite does not store knowledge content.

**SQLite = Runtime State**

`data/runtime/piis.db` stores jobs, status, report ids, and file paths. Gitignored.

**Vector index = Derived Data**

`MemoryVectorStore` is rebuilt from JSON `content` text on startup. Embeddings are **not** stored on `KnowledgeItem` and must never be written into knowledge JSON. The index is never the only copy of a belief, source, claim, or knowledge item.

`KnowledgeRepository` is the swap point for PostgreSQL later. `VectorStore` is the swap point for Qdrant later.

This split is what makes **model-agnostic knowledge assets** possible: a new embedding model rebuilds derived data; it does not own the beliefs.

---

## Stable core vs replaceable intelligence

**Keep stable** (evolve carefully): schemas, layer boundaries, JSON SoT, runtime job/report metadata, pipeline order, report structure, evaluation hooks.

**Replace at the port**: acquisition, extraction (including future ASR), LLM, embeddings, vector store, relation classifier, claim extractor, evidence analyzer.

V0.1 implements mocks only. Composition root: `src/piis/runtime.py`.

---

## Module map

```text
Acquisition  → raw Content
Extraction   → transcript / body text (not claims)
Normalization→ NormalizedContent
Claim extract→ Claims via LLMProvider
Knowledge    → four isolated repositories + retriever
Analysis     → SemanticDiffEngine + EvidenceAnalyzer
Reports      → Markdown / JSON
API / CLI    → composition root in runtime.py
```

### Why the ports exist

Vendor SDKs change. The pipeline should not. Business code calls `llm.generate`, `embeddings.embed`, `store.query`, `acquisition.acquire`.

Unknown `LLM_PROVIDER` values fail fast rather than pretending to call a cloud API.

### Semantic Diff

The engine is a reasoning module with a stable inner pipeline:

1. Embed the claim and retrieved knowledge items (`EmbeddingProvider`) — **signal**
2. Classify each pair (`RelationClassifier`) — **decision**
3. Aggregate `ClaimAnalysis` / `SemanticDiffResult` — **analysis result**

V0.1 default classifier is `HeuristicRelationClassifier` (explicitly labeled). `LLMRelationClassifier` uses the same method signature so a later version can switch without changing the engine.

Similarity is stored on `KnowledgeRelation.similarity` as a feature. Tests require that a **conflict** still classifies as `conflicting` when topical overlap (and therefore similarity) is high.

### Provenance hooks (do not explode in V0.1)

Present today, enough to extend later:

- `Content.source_url`, `published_at`, `metadata`
- `Claim.source_content_id`, `source_span`, `evidence`
- `KnowledgeItem.source`, `metadata`

Not present, and not required for V0.1: derivation graphs, original-vs-exposure source objects, content-hash archival, local media stores.

### Directory notes

Aligned with the approved V0.1 layout. Small names:

- `extraction/mock.py` — `MockExtractionProvider` (text only; claims stay in `extraction/claims.py`)
- `normalization/default.py` — `DefaultNormalizer`
- `knowledge/repository.py` — protocol; `json_repository.py` is the V0.1 implementation
- `knowledge/primary.py` and `external.py` — store-specific JSON repos
- `analysis/evidence.py` — `EvidenceAnalyzer` + heuristic implementation
- `persistence/database.py` + `repositories.py` — SQLite engine and job/report metadata
- `console.py` — UTF-8 terminals print `✓`; GBK Windows consoles print `[ok]`

Claim extraction remains a separate step after normalization. Extraction never returns Claims.

### Question Bank (empty)

`src/piis/assessment/` stores **candidate items**, not knowledge and not user answers.

- `models.py` — `AssessmentItem` plus `CognitiveLevel` / `QuestionType` metadata
- `repository.py` — replaceable `AssessmentItemRepository` (JSON directory in V0.1)
- `bank.py` — `QuestionBank` facade
- `data/assessment/questions/` — empty (`.gitkeep` only)

The pipeline (`runtime.py`, `pipeline/processor.py`) must not import this package. Future sessions/responses/results are not stored. If they appear later, they stay local and gitignored (`data/assessment/responses/`, `data/assessment/results/`).

---

## Cognitive constraints

- No auto-update of personal beliefs
- Reports must label fact / opinion / prediction / unverified
- Evidence level ≠ truth
- Personal knowledge is not uploaded anywhere in V0.1 (there is no cloud provider)
- No user profiling, knowledge probes, or Agent orchestration in this release
- Question Bank exists as empty architecture only: no question content, no assessment engine, no Knowledge State object
