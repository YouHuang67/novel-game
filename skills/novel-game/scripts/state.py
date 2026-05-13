#!/usr/bin/env python3
"""gamestate.json manager for novel-game skill.

Schema: lang | settings {protagonist, custom} | cast | inventory | flags |
        timeline [{turn, summary, player?, ref}] | meta {chapter, last_played}
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve_path(novel_path, save_name):
    if save_name is None:
        return os.path.join(novel_path, "gamestate.json")
    saves_dir = os.path.join(novel_path, "saves")
    os.makedirs(saves_dir, exist_ok=True)
    return os.path.join(saves_dir, f"{save_name}.json")


def _turns_dir(novel_path, save_name):
    name = save_name or "default"
    return os.path.join(novel_path, "turns", name)


def _load_state(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_state(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def cmd_init(args):
    path = _resolve_path(args.novel_path, args.save)
    if os.path.exists(path):
        print(json.dumps({"error": f"Save already exists: {path}"}))
        sys.exit(1)

    confirmed = getattr(args, "confirmed", None)
    if confirmed != "true":
        print(json.dumps({
            "error": "MISSING --confirmed true. You must complete AskUserQuestion customization (language + supplementary definitions) and the player must choose 'start game' before calling init. Re-run with --confirmed true."
        }, ensure_ascii=False))
        sys.exit(1)

    protagonist = args.protagonist or ""
    if not protagonist.strip():
        print(json.dumps({
            "error": "MISSING --protagonist. You must describe the protagonist before initializing. This comes from the lore extraction, supplemented by player customization."
        }, ensure_ascii=False))
        sys.exit(1)

    state = {
        "novel": os.path.basename(os.path.abspath(args.novel_path)),
        "save": args.save or "default",
        "lang": args.lang or "",
        "settings": {
            "protagonist": protagonist,
            "custom": args.custom or "",
        },
        "cast": args.cast or "",
        "inventory": args.inventory or "",
        "flags": args.flags or "",
        "timeline": [],
        "meta": {
            "chapter": args.chapter or 1,
            "pending_guidance": False,
            "created_at": datetime.now().isoformat(),
            "last_played": datetime.now().isoformat(),
        },
    }

    _save_state(path, state)
    print(json.dumps({"ok": True, "path": path}, ensure_ascii=False))


def cmd_load(args):
    path = _resolve_path(args.novel_path, args.save)
    if not os.path.exists(path):
        print(json.dumps({"error": f"Save not found: {path}"}))
        sys.exit(1)
    state = _load_state(path)
    state["meta"]["last_played"] = datetime.now().isoformat()
    _save_state(path, state)
    state["NEXT_STEP"] = "After presenting the scene, output AskUserQuestion with 3 options (last: free input)."
    print(json.dumps(state, ensure_ascii=False, indent=2))


def cmd_set(args):
    path = _resolve_path(args.novel_path, args.save)
    if not os.path.exists(path):
        print(json.dumps({"error": f"Save not found: {path}"}))
        sys.exit(1)

    state = _load_state(path)
    field = args.field
    value = args.value

    if field == "lang":
        state["lang"] = value
    elif field == "protagonist":
        state["settings"]["protagonist"] = value
    elif field == "custom":
        state["settings"]["custom"] = value
    elif field in ("cast", "inventory", "flags"):
        state[field] = value
    elif field == "chapter":
        state["meta"]["chapter"] = int(value)
    else:
        print(json.dumps({"error": f"Unknown field: {field}"}))
        sys.exit(1)

    state["meta"]["last_played"] = datetime.now().isoformat()
    _save_state(path, state)
    print(json.dumps({"ok": True, "field": field}, ensure_ascii=False))


def cmd_save_content(args):
    """Step 1: save story text. Options must be saved separately via save-options."""
    path = _resolve_path(args.novel_path, args.save)
    if not os.path.exists(path):
        print(json.dumps({"error": f"Save not found: {path}"}))
        sys.exit(1)

    state = _load_state(path)
    if state["meta"].get("pending_guidance"):
        print(json.dumps({
            "error": "BLOCKED. Previous turn still needs AskUserQuestion options. Run save-options first, then retry save-content."
        }, ensure_ascii=False))
        sys.exit(1)

    turn_num = len(state["timeline"])

    turns_dir = _turns_dir(args.novel_path, args.save)
    os.makedirs(turns_dir, exist_ok=True)
    ref_filename = f"{turn_num:03d}.txt"
    ref_path = os.path.join(turns_dir, ref_filename)
    if args.content:
        with open(ref_path, "w", encoding="utf-8") as f:
            f.write(args.content)

    save_name = args.save or "default"
    rel_ref = os.path.join("turns", save_name, ref_filename)

    entry = {
        "turn": turn_num,
        "summary": args.summary,
        "ref": rel_ref,
    }
    if args.player:
        entry["player"] = args.player

    state["timeline"].append(entry)

    # Save thinking trace if provided
    if getattr(args, "thinking", None):
        think_filename = f"{turn_num:03d}_think.txt"
        think_path = os.path.join(turns_dir, think_filename)
        with open(think_path, "w", encoding="utf-8") as f:
            f.write(args.thinking)

    state["meta"]["pending_guidance"] = True
    state["meta"]["last_played"] = datetime.now().isoformat()
    _save_state(path, state)

    print(json.dumps({
        "ok": True,
        "turn": turn_num,
        "ref": rel_ref,
        "NEXT": "OUTPUT AskUserQuestion with 3 options (last: free input). Then run: state.py save-options --guidance-text '...'"
    }, ensure_ascii=False))


def cmd_save_options(args):
    """Step 2: validate and save the guidance options."""
    path = _resolve_path(args.novel_path, args.save)
    if not os.path.exists(path):
        print(json.dumps({"error": f"Save not found: {path}"}))
        sys.exit(1)

    state = _load_state(path)
    if not state["meta"].get("pending_guidance"):
        print(json.dumps({
            "error": "No pending guidance. Run save-content first, output options, then save-options."
        }, ensure_ascii=False))
        sys.exit(1)

    guidance = getattr(args, "guidance_text", "") or ""
    if not guidance:
        print(json.dumps({
            "error": "MISSING --guidance-text. Pass the exact guidance text you output to the player."
        }, ensure_ascii=False))
        sys.exit(1)

    has_options = bool(re.search(r'\(\d\)', guidance))
    has_free = bool(re.search(r'自由输入|free input', guidance))
    has_summary = len(guidance.strip().split('\n')) >= 2

    if not (has_options and has_free and has_summary):
        missing = []
        if not has_options:
            missing.append("numbered options like (1) (2) (3)")
        if not has_free:
            missing.append('free-input option ("自由输入" or "free input")')
        if not has_summary:
            missing.append("at least 2 lines (summary + options)")
        print(json.dumps({
            "error": f"GUIDANCE INCOMPLETE. Missing: {', '.join(missing)}. Fix and re-run save-options."
        }, ensure_ascii=False))
        sys.exit(1)

    state["meta"]["pending_guidance"] = False
    state["meta"]["last_played"] = datetime.now().isoformat()
    _save_state(path, state)
    print(json.dumps({"ok": True, "turn_complete": True}, ensure_ascii=False))


def cmd_timeline_truncate(args):
    path = _resolve_path(args.novel_path, args.save)
    if not os.path.exists(path):
        print(json.dumps({"error": f"Save not found: {path}"}))
        sys.exit(1)

    state = _load_state(path)
    after = args.after_turn
    original_len = len(state["timeline"])
    state["timeline"] = [e for e in state["timeline"] if e["turn"] <= after]
    removed = original_len - len(state["timeline"])
    state["meta"]["last_played"] = datetime.now().isoformat()
    _save_state(path, state)
    print(json.dumps({"ok": True, "removed": removed}, ensure_ascii=False))


def cmd_list(args):
    saves = []
    default_path = os.path.join(args.novel_path, "gamestate.json")
    if os.path.exists(default_path):
        s = _load_state(default_path)
        tl = s.get("timeline", [])
        saves.append((
            "default",
            s["meta"].get("chapter", "?"),
            len(tl),
            s["meta"].get("last_played", "")[:16],
        ))

    saves_dir = os.path.join(args.novel_path, "saves")
    if os.path.isdir(saves_dir):
        for fname in sorted(os.listdir(saves_dir)):
            if fname.endswith(".json"):
                fpath = os.path.join(saves_dir, fname)
                s = _load_state(fpath)
                tl = s.get("timeline", [])
                saves.append((
                    fname.replace(".json", ""),
                    s["meta"].get("chapter", "?"),
                    len(tl),
                    s["meta"].get("last_played", "")[:16],
                ))

    if saves:
        print(f"{'Save':<20} {'Chapter':>8} {'Turns':>6}  Last Played")
        print("-" * 60)
        for name, ch, turns, ts in saves:
            print(f"{name:<20} {str(ch):>8} {str(turns):>6}  {ts}")
    else:
        print("(no saves found)")


def main():
    parser = argparse.ArgumentParser(description="Novel game state manager")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init")
    p_init.add_argument("novel_path")
    p_init.add_argument("--save", default=None)
    p_init.add_argument("--confirmed", default=None)
    p_init.add_argument("--lang", default="")
    p_init.add_argument("--chapter", type=int)
    p_init.add_argument("--protagonist", default="")
    p_init.add_argument("--custom", default="")
    p_init.add_argument("--cast", default="")
    p_init.add_argument("--inventory", default="")
    p_init.add_argument("--flags", default="")

    p_load = sub.add_parser("load")
    p_load.add_argument("novel_path")
    p_load.add_argument("--save", default=None)

    p_set = sub.add_parser("set")
    p_set.add_argument("novel_path")
    p_set.add_argument("field")
    p_set.add_argument("value")
    p_set.add_argument("--save", default=None)

    p_sc = sub.add_parser("save-content")
    p_sc.add_argument("novel_path")
    p_sc.add_argument("--save", default=None)
    p_sc.add_argument("--summary", required=True)
    p_sc.add_argument("--player", default=None)
    p_sc.add_argument("--content", default=None)
    p_sc.add_argument("--thinking", default=None)

    p_so = sub.add_parser("save-options")
    p_so.add_argument("novel_path")
    p_so.add_argument("--save", default=None)
    p_so.add_argument("--guidance-text", default=None)

    p_tt = sub.add_parser("timeline-truncate")
    p_tt.add_argument("novel_path")
    p_tt.add_argument("--save", default=None)
    p_tt.add_argument("--after-turn", type=int, required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("novel_path")

    args = parser.parse_args()

    cmds = {
        "init": cmd_init,
        "load": cmd_load,
        "set": cmd_set,
        "save-content": cmd_save_content,
        "save-options": cmd_save_options,
        "timeline-truncate": cmd_timeline_truncate,
        "list": cmd_list,
    }

    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
