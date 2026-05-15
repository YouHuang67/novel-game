#!/usr/bin/env python3
"""Split novel into chapter batches for parallel LLM extraction."""

import argparse
import os
import re
import json

EXTRACTION_PROMPT = """Extract structured data from these novel chapters. Output ONLY valid JSON, no explanation.

{
  "scenes": [
    {
      "chapter": <N>,
      "lines": "L<start>-L<end>",
      "location": "<specific place>",
      "characters": ["<name1>", "<name2>"],
      "event": "<one sentence: who did what, what happened>",
      "level_change": "<character: old -> new, skip if none>"
    }
  ],
  "key_events": ["<3-5 most important plot events>"],
  "new_characters": ["<first-time appearances in this batch>"],
  "new_locations": ["<first-time locations in this batch>"],
  "power_progression": "<summary of level/ability changes across batch>"
}

Rules:
- One scene per major location change or event shift within a chapter
- characters: list ALL named characters appearing in the scene
- event: include who did what AND the result
- lines: use the L<num> markers in the text
- Only list genuinely new characters/locations in new_characters/new_locations
"""


def find_chapters(lines):
    chapters = []
    pat = re.compile(r'^第[\d一二三四五六七八九十百千]+\s*章\s')
    for i, line in enumerate(lines):
        if pat.match(line.strip()):
            chapters.append((i + 1, line.strip()))
    return chapters


def split_batches(novel_path, batch_size=20, output_dir=None):
    with open(novel_path, encoding='utf-8') as f:
        lines = f.readlines()

    chapters = find_chapters(lines)
    total = len(chapters)
    novel_dir = output_dir or os.path.dirname(os.path.abspath(novel_path))
    batch_dir = os.path.join(novel_dir, "_batches")
    os.makedirs(batch_dir, exist_ok=True)

    batches = []
    for i in range(0, total, batch_size):
        batch_chapters = chapters[i:i + batch_size]
        if not batch_chapters:
            break
        batch_id = f"{i // batch_size + 1:03d}"
        first_ch = batch_chapters[0]
        last_ch = batch_chapters[-1]
        start_line = first_ch[0]
        end_line = chapters[i + batch_size][0] - 1 if i + batch_size < total else len(lines)
        end_line = min(end_line, len(lines))

        # Write batch text
        batch_text = ''.join(lines[start_line - 1:end_line])
        batch_txt = os.path.join(batch_dir, f"batch_{batch_id}.txt")
        with open(batch_txt, 'w', encoding='utf-8') as f:
            f.write(batch_text)

        # Write extraction prompt
        prompt_file = os.path.join(batch_dir, f"batch_{batch_id}_prompt.md")
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(EXTRACTION_PROMPT)
            f.write(f"\n\n# Batch {batch_id}: Chapters {batch_chapters[0][1]} to {batch_chapters[-1][1]}\n")
            f.write(f"# Lines L{start_line} to L{end_line}\n\n")
            f.write(batch_text)

        batch_info = {
            "batch_id": batch_id,
            "chapters": f"{batch_chapters[0][1]} to {batch_chapters[-1][1]}",
            "lines": f"L{start_line}-L{end_line}",
            "txt": batch_txt,
            "prompt": prompt_file,
            "chapter_count": len(batch_chapters),
        }
        batches.append(batch_info)
        print(f"  batch_{batch_id}: {batch_chapters[0][1]} ... {batch_chapters[-1][1]} ({len(batch_chapters)}章, {end_line - start_line + 1}行)")

    # Write batch index
    index = {"total_chapters": total, "batch_size": batch_size, "batches": batches}
    with open(os.path.join(batch_dir, "index.json"), 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    batch_count = (total + batch_size - 1) // batch_size
    print(f"\n{batch_count} batches ({batch_size} ch each) -> {batch_dir}")
    return batches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("novel_path")
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    split_batches(args.novel_path, args.batch_size, args.output_dir)


if __name__ == "__main__":
    main()
