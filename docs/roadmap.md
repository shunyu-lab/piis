# Roadmap

Directions, not promises. Order may change when evidence from use says it should.

The test for every item:

> Does this improve a person’s ability to understand relevant external information with limited attention, when they choose to understand — without becoming a generic Agent, summarizer farm, or belief governor?

**V0.1.1** (this patch): still the V0.1 mock pipeline, plus product-philosophy docs and an **empty Question Bank** (no items, no engine). Everything below is **not implemented**.

---

## Capability tracks

These tracks should converge on one system (Curiosity Mode and Deep Mode sharing architecture), not a pile of unrelated tools.

### Information Acquisition

Real fetch/extract behind existing ports. Transcription. Creator/source monitoring. Cross-platform adapters.

Not: generic web crawling as a product, browser automation platforms, or notification spam.

### Knowledge State

Estimated understanding that **emerges through use** (recognition vs deeper understanding). Lightweight onboarding probes later — not personality profiling, not “build a giant KB first.”

Keep **Knowledge State** distinct from **Personal Belief**. Personal store stays user-authored; the pipeline stays conservative about inferring beliefs.

V0.1 includes only the empty **Question Bank** architecture (`data/assessment/questions/`, zero items). The bank is not the user, not the knowledge base, and not the assessment result.

```text
V0.1     Question Bank architecture (empty)
Future   Adaptive knowledge assessment
Future   Knowledge State
Future   Continuous knowledge probes
```

### Reasoning & Evidence

Stronger relation classification, evidence analysis, graded verification. Model output is never promoted to truth. Preserve uncertainty. Surface `CONFLICTING` / dissent, not only support.

### Provenance

Original source vs exposure source. Claim lineage. Optional legally constrained local snapshots (URL + metadata + hash + text; not “download the internet”).

### User Experience

**Curiosity Mode:** understanding map from a question, without a huge prior KB.

**Deep / Continuous Mode:** long-term interests, monitoring, history, evolution.

Same pipeline underneath.

### Model Portability

Real LLM/embedding providers behind ports. Rebuildable vectors. Later: Workspace Generator and Migration Assistant so a user with “ordinary LLM + RAG + manual workflow” is not forced into an Agent framework.

### Safety / Epistemic Boundaries

Human judgment remains final. No auto belief edits. No ideological profiling. No echo-chamber ranker. Categories such as EXPLORE / DISSENT / CONTRADICTION / UNCERTAINTY are design intent for later ranking and presentation — not V0.1 features.

---

## Indicative versions

A convenient narrative, not a contract:

| Version | Intent |
| --- | --- |
| **V0.1.1** | Information-processing pipeline + empty Question Bank architecture (this release) |
| **V0.2** | Real LLM / embedding providers; persistent derived index still rebuildable from JSON |
| **V0.3** | Real content acquisition / transcription behind `Extractor` |
| **V0.4** | Creator / source monitoring (new acquisition adapters) |
| **V0.5** | Personal Knowledge State product surface; still no auto-edit of beliefs |
| **V0.6** | Adaptive knowledge assessment (probes, not profiling) |
| **V0.7** | Evidence and fact verification with graded, non-oracular conclusions |
| **V0.8** | Provenance / claim lineage (original vs exposure) |
| **V0.9** | Cross-platform information acquisition |
| **V1.0** | Personal Information Intelligence System as a product — still not a truth oracle |

Beyond V1.0, still as directions: Curiosity Mode, Continuous Mode, knowledge probes, argument graphs, prediction tracking, dissent/serendipity, workflow generator, model migration assistant, optional local archival, deeper provenance.

---

## Explicitly out of the core

Do not let the project drift into:

- generic chatbot
- generic Agent platform
- generic browser automation
- generic knowledge-management software
- infinite AI summarization
- engagement / notification optimization
- automatic political or ideological profiling
- automatic belief manipulation

---

## Next implementation milestone (not started)

When implementation resumes, the smallest honest step is **V0.2: real providers behind the existing ports**, with fail-fast config, no vendor SDKs in business logic, and JSON remaining Source of Truth.

Do not start that work in a documentation change.
