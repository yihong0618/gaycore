import os
import sys

if __package__:
    from .cli import run
else:
    # Support direct execution of this file (e.g. via uv run).
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from gaycore.cli import run


if __name__ == "__main__":
    # make_playlist_dict()
    sys.exit(run())
