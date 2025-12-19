import os
import sys


def run():
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("gaycore needs a TTY. Run it in a real terminal.", file=sys.stderr)
        return 1
    term = os.environ.get("TERM", "")
    if not term or term == "dumb":
        print("gaycore needs a valid TERM (try xterm-256color).", file=sys.stderr)
        return 1

    from gaycore.gcore_box import GcoreBox, MENU_DICT

    try:
        gcore_box = GcoreBox()
    except Exception as exc:
        print(f"gaycore failed to initialize the TUI: {exc}", file=sys.stderr)
        return 1
    gcore_box.pick(list(MENU_DICT.keys()))


if __name__ == "__main__":
    run()
