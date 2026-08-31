# Concepts

This document is the philosophical and technical foundation of PIIS (Personal Information Intelligence System).

V0.1 implements a small offline pipeline. The concepts below explain **why** that pipeline is shaped the way it is, and which extensions belong later. They are not a claim that V0.1 already does all of this.

When adding a feature, ask:

> Does this improve a person's ability to understand relevant external information with limited attention — when they have chosen to understand?

If not, it probably does not belong in the core.

Two further constraints:

> PIIS should reduce the initial burden of personalization by allowing user knowledge state to emerge gradually through interaction, rather than requiring users to manually construct a complete knowledge base before receiving value.

> The Question Bank is an input asset for future assessment, not a representation of the user's knowledge.

---

## 1. The problem PIIS is trying to solve

The motivating thesis is not merely “there is too much information.”

Information production and distribution can grow much faster than an individual’s ability to inspect, compare, understand, and contextualize that information.

Scarce resources:

- human time
- human attention
- cognitive processing capacity

This is a **product thesis**, not an established economic law.

---

## 2. Information abundance and finite attention

When production outruns inspection, the bottleneck is no longer “can we fetch a document?” It is “which documents, claims, and disagreements are worth the next unit of attention?”

PIIS should **not** assume everyone must maximize attention efficiency.

A person may rationally:

- watch entertainment
- browse social media
- relax
- consume repetitive content
- spend time on activities with little measurable informational value

PIIS does not judge those choices. It is not an anti-entertainment product, a productivity dictator, a digital nanny, or a system that decides what people ought to care about.

> PIIS should assist people when they **choose** to understand something.

---

## 3. Information selection vs information retrieval

The interesting problem class shifts from:

```text
Information Retrieval
```

toward:

```text
Information Selection
Information Contextualization
Information Comparison
Information Understanding
```

PIIS is primarily exploring the second class.

It should not optimize for:

- longer summaries
- more notifications
- more AI-generated text
- maximum daily engagement
- maximum content consumption

It should optimize for (qualitatively, without fake precision):

- information gain relative to the user
- relevance
- novelty (user-relative)
- contextual usefulness
- evidence quality
- contradiction detection
- uncertainty visibility
- source traceability
- user understanding

Do not claim a universal numeric “information gain” unless it is rigorously defined.

**Novelty is user-relative.** The same statement may be new to user A, redundant to user B, and basic to expert C. Long-term PIIS should approximate `Value(content | user knowledge state)`, not a single importance score for the whole world.

---

## 4. Understanding vs summarization

A giant summary is not the product.

Curiosity Mode should answer “help me understand what is going on,” including competing explanations — not “give me more text.”

Optimize for **understanding per unit of user attention**, not word count.

---

## 5. Content → Claim → Knowledge → Reasoning

These layers must not be collapsed.

```text
Content   →  Claim  →  Knowledge  →  Reasoning
 raw          extracted   stored         analysis
```

**Content** — internet payload (URL, type, title, author, `raw_text`). Not a claim. Not knowledge.

**Claim** — a proposition extracted from Content. Do not store a “summary” in place of claims.

- `FACT` — presented as fact by the author; **unverified** in V0.1
- `OPINION` / `VALUE_JUDGMENT` — evaluative
- `PREDICTION` — about the future
- `INTERPRETATION` — a reading of something else
- `QUESTION` — not an assertion

**Knowledge** — an item in an isolated store: domain, primary, personal, or external. Embeddings are derived at runtime and must not become the Source of Truth.

**Reasoning** — `KnowledgeRelation`, `ClaimAnalysis`, `SemanticDiffResult`, `EvidenceAnalysis`. These answer how a claim sits next to stored knowledge. In V0.1 they are presented in reports, not written back as knowledge JSON.

The long-term **product loop** is not one-way summarization:

```text
External World
      ↓
   Content
      ↓
    Claims
      ↓
Knowledge Retrieval
      ↓
Semantic Comparison
      ↓
Evidence / Reasoning
      ↓
  Understanding
      ↓
    User
      ↓
User feedback / learning
      ↓
 Knowledge State
      ↓
better future analysis
```

---

## 6. Personal Knowledge vs Knowledge State

Keep these separate.

**Personal Belief** — what the user **explicitly** claims to believe or endorse. In V0.1 this lives in the personal store. The processing pipeline is **read-only** toward it. PIIS may flag support, opposition, contradictions, and gaps. It must not modify, delete, or create beliefs, or change belief confidence.

**Knowledge State** (future) — what the system **estimates** the user currently understands or recognizes: likely known, likely unknown, uncertainty, familiarity, hypotheses, open questions, recently learned concepts, possibly outdated knowledge.

A Knowledge State should **emerge over time**. Do not make “manually build a large knowledge base first” the default product philosophy. V0.1’s seeded `examples/sample_data/` is a demo fixture, not onboarding.

A correct quiz answer must **not** imply:

- mastery of an entire topic, or
- that the user **believes** a related proposition.

Recognition is not conceptual understanding, application, comparison, or critical evaluation. Adaptive assessment is a future direction, not personality profiling, and is not in V0.1.

---

## 6b. Question Bank (architecture only in V0.1)

PIIS should not force a new user to spend many hours building a personal knowledge base before personalization can start. A future system may estimate boundaries, familiarity, uncertainty, coverage, and depth through lightweight onboarding, adaptive questions, occasional probes, explicit feedback, and observed use.

The first architectural step is a dedicated **Question Bank**. V0.1 provides the module and an **empty** storage location. It does not contain questions, an engine, grading, or Knowledge State inference.

Keep these separate:

```text
Question Bank
    ↓
Assessment Item
    ↓
Assessment Session
    ↓
User Response
    ↓
Assessment Result
    ↓
Knowledge State
```

| Concept | Meaning |
| --- | --- |
| Question Bank | Repository of candidate questions the system *could* ask |
| Assessment Item | One question plus metadata (`src/piis/assessment/`) |
| Assessment Session | A concrete sitting (future) |
| User Response | An answer to one item (future; sensitive; keep local) |
| Assessment Result | Analysis of a response (future) |
| Knowledge State | Estimate of what the user likely knows (future) |

```text
Question Bank  ≠  Personal Knowledge  ≠  Knowledge State
```

Do not write bank items into personal knowledge JSON. Do not write assessment results into the bank. A correct answer is not automatic mastery of a topic (`recognizing a concept ≠ deep conceptual understanding`). Cognitive-level labels (`RECOGNITION` … `CRITICAL_EVALUATION`) describe intended item depth; they are not a scoring framework or a measure of intelligence.

The processing pipeline does not use the bank:

```text
PIIS Core
   │
   ├── Information Pipeline   (V0.1)
   ├── Knowledge System       (V0.1)
   └── Assessment System      (empty bank only)
```

Future engine (not implemented):

```text
Question Bank
      ↓
Assessment Engine
      ↓
Question Selection
      ↓
User Response
      ↓
Response Evaluation
      ↓
Knowledge State Update
```

An answer may be evidence about **understanding**. It must not be treated as evidence of belief, personality, ideology, values, or what the user “should” know. No cloud sync, analytics, or profiling of responses in V0.1.

---

## 7. Provenance

**Knowledge Provenance** should become first-class: where did this come from, what content produced the claim, when did the user encounter it, was it observed or derived, what primary source does it trace to, which video/article/post caused the encounter?

Distinguish:

```text
original source   ≠   user exposure source
```

Example:

```text
Paper A
   ↓
Creator B discusses Paper A
   ↓
User sees Video B
   ↓
PIIS extracts Claim C
```

`original source = Paper A`, `exposure source = Video B`.

Possible future metadata: `source_content_id`, `source_url`, `source_span`, timestamps, content hash, source type, derivation chain. V0.1 already has some of these hooks (`Content.source_url`, `Claim.source_content_id`, `Claim.source_span`, `KnowledgeItem.source` / `metadata`). Do not require a full provenance graph in V0.1.

**Local archival** (future, optional, legally constrained): some URLs rot. A safer hierarchy is URL + metadata + content hash + transcript/text snapshot where appropriate + optional permitted local archive. Do **not** assume that downloading and permanently storing every internet source is acceptable. Not implemented in V0.1.

---

## 8. Evidence vs truth

Never reduce claims to a single `TRUE / FALSE`.

Keep separate:

- factual **framing** (`ClaimType`)
- **verification** status
- opinion / prediction / interpretation / value judgment
- **similarity**
- **relation** label
- **evidence level** (source class)
- model / extractor **confidence**

| Field | Meaning |
| --- | --- |
| `Claim.confidence` | Extractor confidence that the proposition was identified. Not P(true). |
| `EvidenceSpan.evidence_level` (JSON alias: `credibility`) | Source class of a span. A primary source can be wrong. |
| `VerificationStatus` | Whether PIIS has checked the claim. Independent of `ClaimType`. V0.1 is always `UNVERIFIED`. |
| `PersonalBelief.confidence` | How strongly the user currently holds the belief. |
| `KnowledgeRelation.confidence` | Confidence in the relation label. |
| `KnowledgeRelation.similarity` | Embedding neighborhood. Never the relation verdict. |

`ClaimType.FACT` + `VerificationStatus.UNVERIFIED` is the normal V0.1 state for fact-framed claims.

`PRIMARY_SOURCE` … `SOCIAL_MEDIA` … `UNKNOWN` describe source class, not truth.

---

## 9. Similarity vs relation

Embedding similarity is a **signal**. Two statements can be highly similar while contradicting each other.

Semantic Diff:

```text
embed → signal
classify → decision
aggregate → analysis result
```

High similarity can still be `CONFLICTING`. Similarity is not agreement.

---

## 10. LLM as capability, not foundation

> LLMs are components of PIIS, not the foundation of PIIS.

Prefer the simplest reliable mechanism that actually solves the problem. Conceptual preference (not a rigid runtime stack):

```text
Deterministic logic
    ↓
Classical algorithms
    ↓
Statistical methods
    ↓
ML / DL models
    ↓
LLM reasoning
    ↓
Human judgment
```

Use deterministic methods when they are sufficient. Use ML/DL where statistical generalization is useful. Use LLMs where semantic interpretation, language generation, ambiguity, or complex reasoning is genuinely necessary. Do not invoke an LLM merely because it *can* perform a task.

V0.1 already follows this in Semantic Diff: a **heuristic** classifier is the default; an LLM classifier is a replaceable port.

---

## 11. Deterministic-first engineering

This preference is for:

- lower cost and latency
- better reproducibility and debuggability
- less hallucination exposure
- easier testing
- easier vendor migration
- longer system lifespan
- less dependence on transient model tricks

Mature workflows should look like **pipeline + learned components + selective reasoning**, not Agent → LLM → Agent → LLM → LLM.

“More LLM calls” is not a measure of intelligence.

The stable core should eventually include: content normalization, schemas, provenance, storage, retrieval, hashing, deduplication, caching, scheduling, workflow state, evaluation, report structure.

Replaceable intelligence: LLM, embedding model, relation classifier, claim extractor, reranker, ASR, OCR, other specialized models.

The long-term asset is **knowledge representation + provenance + user knowledge state + workflow + evaluation + reasoning interfaces** — not dependence on model X.

---

## 12. Model independence

Pursue **minimal migration cost** between AI providers (OpenAI, Anthropic, Google, local models, future vendors).

```text
Knowledge Assets
      ⟂
Model Vendor
```

The same knowledge should operate with different providers. Users should not need an Agent framework merely to express a PIIS workflow.

**PIIS Workspace Generator** (future): scaffolding for people who only have an ordinary conversational LLM + RAG + a manually triggered workflow — directory structure, schemas, retrieval strategy, prompts, templates, validation, migration config.

**Migration Assistant** (future): inspect a model, generate RAG/prompt/workflow assets, run compatibility checks, switch providers. The objective is low migration cost, not automatic magic. Not in V0.1.

---

## 13. Anti-echo-chamber principle

A highly personalized filter can become a bubble.

Do **not** optimize only for “content most compatible with what the user already believes.”

Preserve room for disagreement, competing explanations, contradictory evidence, minority positions, unexpected discoveries, and serendipity.

Conceptual attention categories (future, not V0.1 labels):

```text
EXPLORE
DISSENT
CONTRADICTION
UNCERTAINTY
```

A piece of information can be worth attention **because** it challenges an existing belief.

---

## 14. Human judgment boundary

PIIS should evolve toward **attention allocator + epistemic challenger**, not **attention controller + cognitive governor**.

It may say: “This challenges your current view.” It must not say: “Your view must be changed.”

It may say: “You have not encountered evidence X.” It must not say: “Therefore you must believe Y.”

Human judgment remains the final authority. Personal beliefs are never auto-edited.

---

## 15. Curiosity Mode vs Deep Mode

Same architecture, two uses.

**Curiosity Mode** (likely broad-user entry):

```text
User curiosity
    ↓
PIIS
    ↓
lightweight user knowledge estimation
    ↓
external information acquisition
    ↓
claim extraction
    ↓
contextualization
    ↓
fact / interpretation / opinion / prediction separation
    ↓
disagreement / uncertainty analysis
    ↓
concise understanding map
    ↓
optional deep sources
```

**Deep / Continuous Mode**: creator monitoring, continuous ingestion, domain and primary libraries, personal knowledge, claim history, predictions, provenance, conflict detection, long-term evolution — for researchers, students, engineers, writers, analysts, serious learners.

Do not implement these product modes in V0.1. Do not split into two codebases.

---

## V0.1 five principles (frozen)

1. **Information is not knowledge.** External content is raw. Claims are extracted, then compared with existing knowledge. The pipeline does not promote external claims into authoritative knowledge.
2. **FACT is framing, not truth.** `FACT + UNVERIFIED` is valid.
3. **Similarity is not agreement.** Classification decides the relation.
4. **Personal beliefs are not automatically changed.** Read-only personal store during processing.
5. **Evidence is not truth.** Do not collapse labels into a truth score.

---

## What does not belong

Do not drift toward: generic chatbot, generic Agent platform, generic browser automation, generic knowledge-management software, infinite AI summarization, notification spam, engagement optimization, automatic ideological/political profiling, or automatic belief manipulation.

---

## Success (long-term questions)

Do not define success as documents processed, tokens generated, AI calls, summaries, or time-on-app.

Ask instead:

- Can the system reduce **unnecessary** information consumption **when the user is trying to understand**?
- Can it surface genuinely new information **for that user**?
- Can it identify meaningful contradictions?
- Can it adapt explanation depth to knowledge state?
- Can the user trace important information to sources?
- Can the user switch models without losing knowledge assets?
- Does it preserve uncertainty instead of fabricating certainty?
- Does it challenge the user when appropriate, without governing beliefs?
- Does it avoid becoming another algorithmic echo chamber?
- Does it help the user understand something faster without pretending to think for them?
