from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Text generation port. Business code must not import vendor SDKs."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def generate(self, prompt: str, *, system: str | None = None) -> str:
        """Return model text. Structured callers are responsible for parsing JSON."""
