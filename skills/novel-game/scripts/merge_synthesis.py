#!/usr/bin/env python3
"""Merge all batch extraction JSONs into unified lore files."""

import argparse
import json
import os
import re
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
    lines = ["# 剧情时间线", "", "全场景按时间顺序排列。", ""]
    for b in batches:
        for s in b.get("scenes", []):
            ch = s.get("chapter", "?")
            loc = s.get("location", "")
            chars = ", ".join(s.get("characters", []))
            event = s.get("event", "")
            lv = s.get("level_change", "")
            ln = s.get("lines", "")
            lines.append("---")
            lines.append(f"- 第{ch}章 | {loc} | {ln}")
            lines.append(f"  人物: {chars}")
            lines.append(f"  {event}")
            if lv:
                lines.append(f"  等级: {lv}")
            lines.append("")
    return '\n'.join(lines)


def build_arcs(batches):
    """Detect map arcs from key events."""
    map_sigs = [
        ("磐石城", ["磐石城", "老虎帮", "老鼠巷", "废墟"]),
        ("黑石城", ["黑石城", "赤沙帮", "玉门镇", "方家"]),
        ("十二盟会", ["十二盟会", "武盟", "白石城", "人榜", "郡城", "三拳之约"]),
        ("洞天世界", ["洞天", "天人合一", "法天象地", "内景", "外圣", "黑魔山", "天贵山"]),
        ("黑暗战争", ["黑暗", "黑暗世界", "百日诛魔令", "邪神"]),
        ("太皇域/新域", ["太皇", "域城", "新域", "造化", "至尊", "神光", "神火", "神庭", "神榜"]),
    ]

    lines = ["# 剧情弧线", ""]
    for map_name, keywords in map_sigs:
        events = []
        for b in batches:
            for e in b.get("key_events", []):
                if any(kw in e for kw in keywords):
                    events.append(e)
        if events:
            lines.append(f"## {map_name}")
            for e in events[:8]:
                lines.append(f"- {e}")
            lines.append("")
    return '\n'.join(lines)


def build_characters(batches):
    """Merge character appearances across batches."""
    char_batches = defaultdict(list)
    char_events = defaultdict(list)

    for b in batches:
        batch_id = b.get("batch_id", os.path.basename(b.get("_source", "")))
        for c in b.get("new_characters", []):
            char_batches[c].append(batch_id)

    lines = ["# 人物汇总", "", f"共 {len(char_batches)} 个角色。", ""]
    # Sort by number of batch appearances (more = more important)
    sorted_chars = sorted(char_batches.items(), key=lambda x: -len(x[1]))
    for name, appearances in sorted_chars[:80]:
        lines.append(f"- **{name}** (首次: {appearances[0]})")
    return '\n'.join(lines)


def build_map_transitions(batches):
    """Identify map transition events."""
    trans_keywords = ["前往", "进入", "抵达", "踏入", "传送至", "离去", "离开", "出发"]
    lines = ["# 地图切换", ""]
    for b in batches:
        for e in b.get("key_events", []):
            if any(kw in e for kw in trans_keywords):
                lines.append(f"- {e}")
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
        "arcs.md": build_arcs(batches),
        "map_transitions.md": build_map_transitions(batches),
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
