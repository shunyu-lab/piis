# Concepts

PIIS (Personal Information Intelligence System) treats information, claims, knowledge, and reasoning as different things.

## Five principles

### 1. Information is not knowledge

External content is raw information. The system extracts Claims, then compares them with existing Knowledge. It does not automatically promote external claims into authoritative knowledge.

### 2. FACT is framing, not truth

`ClaimType.FACT` means the author presented the proposition as a factual statement. It does not mean PIIS verified it. `FACT + UNVERIFIED` is valid.

### 3. Similarity is not agreement

Embedding similarity is a signal. Two statements can be highly similar while contradicting each other. Semantic Diff is: embed → signal, classify → decision, aggregate → analysis result.

### 4. Personal beliefs are not automatically changed

Personal Knowledge is the user's cognitive state. The V0.1 pipeline is read-only toward it. PIIS may flag support, opposition, contradictions, and gaps. It must not modify, delete, or create beliefs, or change belief confidence.

### 5. Evidence is not truth

Evidence level, source class, extractor confidence, and verification status stay separate. They are not a single truth score.

## Content

Raw internet payload: URL, type, title, author, `raw_text`. Not yet claims. Not knowledge.

## Claim

A proposition extracted from Content.

- `FACT` — presented as fact by the author; **unverified**
- `OPINION` / `VALUE_JUDGMENT` — evaluative
- `PREDICTION` — about the future
- `INTERPRETATION` — a reading of something else
- `QUESTION` — not an assertion

Do not store a “summary” in place of claims.

## Knowledge

An item that lives in a store:

- Domain knowledge
- Primary sources
- Personal knowledge (belief / hypothesis / question)
- External claims (cached, optional)

Personal beliefs may have confidence, evidence for/against, and revision history. The system may **suggest** re-evaluation. It may not silently edit the belief.

Embeddings are not stored on knowledge items. They are derived at runtime.

## Reasoning (analysis result)

`KnowledgeRelation`, `ClaimAnalysis`, `SemanticDiffResult`, `EvidenceAnalysis`.

These objects answer: how does this claim sit next to what we already store?

They are not stored as knowledge in V0.1. Reports present them to the user.

## Labels that are not truth

These fields are easy to misread. They do **not** mean “how true is this?”

| Field | Meaning |
| --- | --- |
| `Claim.confidence` | Extractor confidence that the proposition was identified. Not P(true). |
| `EvidenceSpan.evidence_level` (JSON alias: `credibility`) | Source class of a span. A primary source can be wrong. |
| `EvidenceLevel` | Same: source class, not verification. |
| `VerificationStatus` | Whether PIIS has checked the claim. Independent of `ClaimType`. V0.1 is always `UNVERIFIED`. |
| `PersonalBelief.confidence` | How strongly the user currently holds the belief. |
| `KnowledgeRelation.confidence` | Confidence in the relation label (conflict vs redundant, …). |
| `KnowledgeRelation.similarity` | Embedding neighborhood. Never the relation verdict. |

`ClaimType.FACT` + `VerificationStatus.UNVERIFIED` is the normal V0.1 state for fact-framed claims.

## Evidence level

`PRIMARY_SOURCE` … `SOCIAL_MEDIA` … `UNKNOWN` describe source class. A primary source can be wrong. A forum post can be right. The label is one input to later evidence analysis, not a truth bit.
