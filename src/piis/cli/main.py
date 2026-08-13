import argparse
import sys

from piis.config.settings import Settings
from piis.console import print_step
from piis.runtime import build_pipeline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="piis",
        description="Personal Information Intelligence System (PIIS) - process a URL through the mock pipeline",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    process = sub.add_parser("process", help="Acquire a URL and run the pipeline")
    process.add_argument("url")
    args = parser.parse_args(argv)

    if args.command == "process":
        return _process(args.url)
    return 1


def _process(url: str) -> int:
    print("Processing...")
    pipeline = build_pipeline(Settings(), on_step=print_step)
    report = pipeline.process_url(url)
    print()
    print("Report:")
    print(report.markdown_path or "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
