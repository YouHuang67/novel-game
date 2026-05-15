#!/usr/bin/env python3
"""Merge all batch extraction JSONs into unified lore files."""

import argparse
import json
import os
from collections import defaultdict


def load_batches(batch_dir):
    batches = []
    for i in range(1, 100):
        fname = f"batch_{i:03d}.json"
        fpath = os.path.join(batch_dir, fname)
        if not os.path.exists(fpath):
            break
        with open(fpath, encoding='utf-8') as f:
            batches.append(json.load(f))
    return batches


def build_timeline(batches):
    """Build unified timeline from all scene entries."""
    lines = ["# 剧情时间线", "", "全场景按时间顺序排列，编号可被arcs交叉引用。", ""]
    scene_idx = 0
    for b in batches:
        for s in b.get("scenes", []):
            scene_idx += 1
            ch = s.get("chapter", "?")
            loc = s.get("location", "")
            chars = ", ".join(s.get("characters", []))
            event = s.get("event", "")
            lv = s.get("level_change", "")
            ln = s.get("lines", "")
            lines.append(f"## 场景{scene_idx}")
            lines.append(f"- 章节: 第{ch}章")
            lines.append(f"- 地点: {loc}")
            lines.append(f"- 行号: {ln}")
            lines.append(f"- 人物: {chars}")
            lines.append(f"- 事件: {event}")
            if lv:
                lines.append(f"- 等级: {lv}")
            lines.append("")
    return '\n'.join(lines)


def build_all_events(batches):
    """Build flat list of all key events with batch scene range refs."""
    batch_scene_ranges = []
    scene_offset = 0
    for b in batches:
        n = len(b.get("scenes", []))
        batch_scene_ranges.append((scene_offset + 1, scene_offset + n))
        scene_offset += n

    lines = ["# 全部关键事件", "", "按batch顺序排列，每条带场景范围引用。agent在Stage 4据此提炼剧情弧线。", ""]
    for bi, b in enumerate(batches):
        events = b.get("key_events", [])
        if events:
            start, end = batch_scene_ranges[bi]
            lines.append(f"## Batch {bi + 1} [场景{start}-{end}]")
            for e in events:
                lines.append(f"- {e}")
            lines.append("")
    return '\n'.join(lines)


def build_characters(batches):
    """Merge character appearances across batches."""
    char_batches = defaultdict(list)
    char_events = defaultdict(list)

    for bi, b in enumerate(batches):
        for c in b.get("new_characters", []):
            char_batches[c].append(str(bi + 1))

    lines = ["# 人物汇总", "", f"共 {len(char_batches)} 个角色。", ""]
    # Sort by number of batch appearances (more = more important)
    sorted_chars = sorted(char_batches.items(), key=lambda x: -len(x[1]))
    for name, appearances in sorted_chars[:80]:
        lines.append(f"- **{name}** (首次: {appearances[0]})")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("batch_dir", help="Directory with batch_*.json files")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: batch_dir/../lore/plot)")
    args = parser.parse_args()

    batches = load_batches(args.batch_dir)
    print(f"Loaded {len(batches)} batches")

    output_base = args.output_dir or os.path.join(os.path.dirname(args.batch_dir), "lore", "plot")
    os.makedirs(output_base, exist_ok=True)

    files = {
        "timeline.md": build_timeline(batches),
        "all_key_events.md": build_all_events(batches),
    }
    chars_out = os.path.join(os.path.dirname(output_base), "characters", "INDEX.md")
    os.makedirs(os.path.dirname(chars_out), exist_ok=True)
    files[chars_out] = build_characters(batches)

    for fname, content in files.items():
        full_path = fname if os.path.isabs(fname) else os.path.join(output_base, fname)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        lines = content.count('\n')
        print(f"  {os.path.basename(fname)}: {lines} lines")


if __name__ == "__main__":
    main()
