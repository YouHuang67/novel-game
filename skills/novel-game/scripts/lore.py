#!/usr/bin/env python3
"""Progressive disclosure tool for novel-game skill.

Lets the agent query specific lore topics on demand,
instead of loading the entire meta.md into context.

Usage:
  python3 lore.py index <novel-path>          # Show lore tree
  python3 lore.py read <novel-path> <topic>   # Read a specific lore file
  python3 lore.py search <novel-path> <kw>    # Search across lore files
"""

import argparse
import os
import sys

LOREDIR = "lore"


def _lore_root(novel_path):
    return os.path.join(novel_path, LOREDIR)


def _walk_index(lore_root):
    """Generate a tree string of all lore files with first-line summaries."""
    lines = []
    for dirpath, dirnames, filenames in sorted(os.walk(lore_root)):
        rel = os.path.relpath(dirpath, lore_root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        prefix = "  " * depth

        # Print directory
        if rel != ".":
            lines.append(f"{prefix}{os.path.basename(dirpath)}/")

        # Print files
        for fn in sorted(filenames):
            if not fn.endswith(".md"):
                continue
            fpath = os.path.join(dirpath, fn)
            first = ""
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped and not stripped.startswith("#"):
                            first = stripped[:80]
                            break
            except Exception:
                pass
            indent = prefix + "  "
            rel_path = os.path.join(rel, fn) if rel != "." else fn
            lines.append(f"{indent}{rel_path}  -- {first}")

    return "\n".join(lines)


def cmd_index(args):
    root = _lore_root(args.novel_path)
    if not os.path.isdir(root):
        print("(no lore directory yet)")
        return
    print(_walk_index(root))


def cmd_read(args):
    root = _lore_root(args.novel_path)
    # Support both "characters/萧炎" and "characters/萧炎.md"
    topic = args.topic
    if not topic.endswith(".md"):
        topic += ".md"
    fpath = os.path.join(root, topic)
    if not os.path.isfile(fpath):
        print(f"(not found: {topic})")
        sys.exit(1)
    with open(fpath, "r", encoding="utf-8") as f:
        print(f.read())


def cmd_search(args):
    root = _lore_root(args.novel_path)
    if not os.path.isdir(root):
        print("(no lore directory yet)")
        return
    kw = args.keyword.lower()
    hits = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            fpath = os.path.join(dirpath, fn)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                if kw in content.lower():
                    rel = os.path.relpath(fpath, root)
                    # Extract matching lines
                    for i, line in enumerate(content.split("\n")):
                        if kw in line.lower():
                            hits.append(f"{rel}:{i+1}:  {line.strip()[:100]}")
            except Exception:
                pass
    if hits:
        print("\n".join(hits[:20]))
    else:
        print(f"(no matches for '{args.keyword}')")


def main():
    parser = argparse.ArgumentParser(description="Progressive disclosure lore tool")
    sub = parser.add_subparsers(dest="command")

    p_index = sub.add_parser("index")
    p_index.add_argument("novel_path")

    p_read = sub.add_parser("read")
    p_read.add_argument("novel_path")
    p_read.add_argument("topic")

    p_search = sub.add_parser("search")
    p_search.add_argument("novel_path")
    p_search.add_argument("keyword")

    args = parser.parse_args()

    if args.command == "index":
        cmd_index(args)
    elif args.command == "read":
        cmd_read(args)
    elif args.command == "search":
        cmd_search(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
