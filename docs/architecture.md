# Architecture

**V0.1.0 is frozen.** This document describes the architecture that ships in this release. Do not expand it for V0.1.

V0.1 is an information-processing pipeline with replaceable ports. It is not a cognitive OS.

Frozen conceptual layers:

```text
Content → Claim → Knowledge → Reasoning
```

Frozen implementation pipeline:

```text
Acquisition → Extraction → Normalization → Claim Extraction
    → Knowledge Retrieval → Semantic Diff → Evidence Analysis → Report
```

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

`PERSONAL_BELIEF` is cognitive state. The pipeline is read-only toward personal knowledge.

## Persistence

Three categories. Do not mix them.

**JSON = Source of Truth**

Knowledge lives in JSON files (`examples/sample_data/` in the repo; `data/personal/` locally and gitignored). SQLite does not store knowledge content.

**SQLite = Runtime State**

`data/runtime/piis.db` stores jobs, status, report ids, and file paths. Gitignored.

**Vector index = Derived Data**

`MemoryVectorStore` is rebuilt from JSON `content` text on startup. Embeddings are **not** stored on `KnowledgeItem` and must never be written into knowledge JSON. The index is never the only copy of a belief, source, claim, or knowledge item.

`KnowledgeRepository` is the swap point for PostgreSQL later. `VectorStore` is the swap point for Qdrant later.

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

V0.1 implements mocks only. Unknown `LLM_PROVIDER` values fail fast rather than pretending to call a cloud API.

### Semantic Diff

The engine is a reasoning module with a stable inner pipeline:

1. Embed the claim and retrieved knowledge items (`EmbeddingProvider`) — **signal**
2. Classify each pair (`RelationClassifier`) — **decision**
3. Aggregate `ClaimAnalysis` / `SemanticDiffResult` — **analysis result**

V0.1 default classifier is `HeuristicRelationClassifier` (explicitly labeled). `LLMRelationClassifier` uses the same method signature so V0.2 can switch without changing the engine.

Similarity is stored on `KnowledgeRelation.similarity` as a feature. Tests require that a **conflict** still classifies as `conflicting` when topical overlap (and therefore similarity) is high.

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

## Cognitive constraints

- No auto-update of personal beliefs
- Reports must label fact / opinion / prediction / unverified
- Evidence level ≠ truth
- Personal knowledge is not uploaded anywhere in V0.1 (there is no cloud provider)
