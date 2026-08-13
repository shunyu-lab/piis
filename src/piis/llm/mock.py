import json
import re

from piis.llm.base import LLMProvider

_DEMO_CLAIMS = {
    "claims": [
        {
            "content": "Python is a programming language created by Guido van Rossum.",
            "claim_type": "FACT",
            "confidence": 0.9,
            "topics": ["python", "programming"],
            "evidence": [
                {
                    "text": "The speaker says Python is a programming language created by Guido van Rossum.",
                    "credibility": "CREATOR_CONTENT",
                }
            ],
        },
        {
            "content": (
                "AI will completely eliminate the need for software engineers within two years."
            ),
            "claim_type": "PREDICTION",
            "confidence": 0.55,
            "topics": ["ai", "software-engineers"],
            "evidence": [],
        },
        {
            "content": "Companies should ban all use of coding assistants.",
            "claim_type": "VALUE_JUDGMENT",
            "confidence": 0.4,
            "topics": ["coding-assistants", "policy"],
            "evidence": [],
        },
        {
            "content": "Large language models can assist programmers with boilerplate.",
            "claim_type": "FACT",
            "confidence": 0.7,
            "topics": ["llm", "programming"],
            "evidence": [
                {
                    "text": (
                        "The speaker also notes that large language models "
                        "can assist programmers with boilerplate."
                    ),
                    "credibility": "CREATOR_CONTENT",
                }
            ],
        },
        {
            "content": "The capital of France is Paris.",
            "claim_type": "FACT",
            "confidence": 0.95,
            "topics": ["geography"],
            "evidence": [
                {
                    "text": "the speaker remarks that the capital of France is Paris",
                    "credibility": "CREATOR_CONTENT",
                }
            ],
        },
    ]
}


class MockLLMProvider(LLMProvider):
    """Deterministic stand-in. Swap for OpenAI/Gemini/Anthropic later."""

    @property
    def name(self) -> str:
        return "mock"

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        task = (system or "").lower()
        if "extract claims" in task:
            if "example.com/demo" in prompt or "future of programming" in prompt.lower():
                return json.dumps(_DEMO_CLAIMS)
            return json.dumps(
                {
                    "claims": [
                        {
                            "content": prompt.strip().splitlines()[-1][:240],
                            "claim_type": "UNKNOWN",
                            "confidence": 0.3,
                            "topics": [],
                            "evidence": [],
                        }
                    ]
                }
            )
        if "classify the relation" in task:
            return json.dumps(self._classify(prompt))
        return "mock-llm: no handler for this prompt"

    def _classify(self, prompt: str) -> dict[str, str]:
        """Fixture-aware labels so LLMRelationClassifier is a real swap target."""
        claim = _field(prompt, "CLAIM")
        knowledge = _field(prompt, "KNOWLEDGE")
        if claim == knowledge:
            return {
                "label": "redundant",
                "rationale": "Mock LLM: statements are identical.",
            }
        if "eliminate" in claim and "change" in knowledge and "eliminate" in knowledge:
            return {
                "label": "conflicting",
                "rationale": "Mock LLM: elimination vs change-not-eliminate.",
            }
        if "boilerplate" in claim and "boilerplate" in knowledge:
            return {
                "label": "supporting",
                "rationale": "Mock LLM: same directional claim about assistance.",
            }
        if "will replace" in claim and "not replace" in knowledge:
            return {
                "label": "conflicting",
                "rationale": "Mock LLM: replace vs will not replace.",
            }
        if "paris" in claim or "france" in claim:
            return {
                "label": "unrelated",
                "rationale": "Mock LLM: geography vs AI/programming knowledge.",
            }
        return {
            "label": "unknown",
            "rationale": "Mock LLM: no fixture match.",
        }


def _field(prompt: str, name: str) -> str:
    match = re.search(rf"{name}:\s*(.+)", prompt)
    return match.group(1).strip().lower() if match else ""
