import sys


def print_step(message: str) -> None:
    encoding = (getattr(sys.stdout, "encoding", None) or "utf-8").lower()
    mark = "✓" if "utf" in encoding else "[ok]"
    print(f"{mark} {message}")
