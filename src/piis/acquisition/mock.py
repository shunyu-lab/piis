from piis.acquisition.base import AcquisitionProvider
from piis.ids import new_id
from piis.models.content import Content
from piis.models.enums import SourceType

DEMO_URL = "https://example.com/demo"

DEMO_TRANSCRIPT = """\
Demo creator video on AI and programming work.

The speaker says Python is a programming language created by Guido van Rossum.

The speaker predicts that AI will completely eliminate the need for software engineers within two years.

The speaker argues that companies should ban all use of coding assistants.

The speaker also notes that large language models can assist programmers with boilerplate.

Separately, the speaker remarks that the capital of France is Paris.
"""


class MockAcquisition(AcquisitionProvider):
    """In-memory acquisition. Replace with platform adapters later."""

    def acquire(self, url: str) -> Content:
        if url.rstrip("/") == DEMO_URL:
            return Content(
                id=new_id("content"),
                source_url=DEMO_URL,
                source_type=SourceType.VIDEO,
                title="Demo: AI and the future of programming work",
                author="Mock Creator",
                raw_text=DEMO_TRANSCRIPT,
                language="en",
                metadata={"acquisition": "mock", "fixture": "demo"},
            )
        return Content(
            id=new_id("content"),
            source_url=url,
            source_type=SourceType.UNKNOWN,
            title=f"Mock content for {url}",
            author="Unknown",
            raw_text=f"Placeholder body acquired from {url}.",
            language="en",
            metadata={"acquisition": "mock"},
        )


MockAcquisitionProvider = MockAcquisition
