"""Run the V0.1 mock pipeline without an API key."""

from pathlib import Path

from piis.config.settings import Settings
from piis.console import print_step
from piis.runtime import build_pipeline

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    settings = Settings(
        knowledge_dir=ROOT / "examples" / "sample_data",
        data_dir=ROOT / "data",
        database_url=f"sqlite:///{(ROOT / 'data' / 'runtime' / 'piis.db').as_posix()}",
    )
    pipeline = build_pipeline(settings, on_step=print_step)
    report = pipeline.process_url("https://example.com/demo")
    print()
    print(f"Markdown: {report.markdown_path}")
    print(f"JSON:     {report.json_path}")


if __name__ == "__main__":
    main()
