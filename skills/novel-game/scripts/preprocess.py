#!/usr/bin/env python3
"""Preprocess a novel .txt: generate timeline stub and extraction checklist."""

import argparse
import os
import re
import sys
from collections import Counter


def find_chapters(lines):
    """Return list of (line_number_1based, title)."""
    chapters = []
    pattern = re.compile(r'^第[\d一二三四五六七八九十百千]+\s*章\s')
    for i, line in enumerate(lines):
        if pattern.match(line.strip()):
            chapters.append((i + 1, line.strip()))
    return chapters


def extract_scenes(lines, chapters):
    """Within each chapter, find scene breaks (2+ blank lines). Return list of (start_line, chapter_title, scene_index)."""
    scenes = []
    for idx, (ch_start, ch_title) in enumerate(chapters):
        ch_end = chapters[idx + 1][0] if idx + 1 < len(chapters) else len(lines) + 1
        scene_idx = 0
        blank_count = 0
        scene_start = ch_start
        for i in range(ch_start, min(ch_end, len(lines) + 1)):
            li = i - 1
            if li >= len(lines):
                break
            if lines[li].strip() == '':
                blank_count += 1
            else:
                if blank_count >= 2 and i - scene_start > 10:
                    scenes.append((scene_start, ch_title, scene_idx))
                    scene_idx += 1
                    scene_start = i
                blank_count = 0
        scenes.append((scene_start, ch_title, scene_idx))
    return scenes


def extract_names(lines):
    """Extract character names: surname-filtered candidates near speech verbs."""

    # Top 200 Chinese surnames as a set of single chars
    surname_chars = set('赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张'
                        '孔曹严华金魏陶姜戚谢邹喻水云苏潘葛奚范彭郎鲁韦昌马'
                        '苗凤花方俞任袁柳鲍史唐费薛雷贺倪汤滕殷罗毕郝邬安常'
                        '乐于时傅卞齐康伍余元卜顾孟穆萧尹姚邵湛汪祁毛禹狄米'
                        '贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮席季麻强'
                        '贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞'
                        '万柯管卢莫经房解应宗丁宣贲邓单杭洪包诸左石崔吉钮龚'
                        '程嵇邢滑裴陆荣翁羊惠甄家封芮羿储靳邴松井富巫乌焦巴'
                        '弓牧山谷车侯伊宁仇祖武符刘景詹束龙叶幸司韶黎乔苍双'
                        '闻党翟谭贡劳姬申冉雍桑桂牛寿通边燕冀尚温庄晏柴瞿阎'
                        '文欧聂晁勾敖冷辛阚那简饶空曾沙须丰游荆')

    # Compound surnames (2-char)
    compound = {'欧阳','上官','司马','诸葛','慕容','皇甫','端木','令狐','夏侯','长孙','独孤','东方','西门','南宫','北冥','拓跋','尉迟','公羊','公冶','太史','申屠'}

    # Longest speech verb alternatives first to avoid partial matches
    speech_verbs = ('冷笑道|淡淡道|沉声道|怒声道|平静道|开口道|微笑道|'
                    '喝道|问道|说道|笑道|冷喝|大喝|怒喝|沉喝|低喝|'
                    '轻声|低声|寒声|厉声|大声|小声|高声道|'
                    '冷冷道|道|说|问|喊|喝|叫|笑|骂|吼|冷|淡|沉|叹|怒|斥|嚷')
    speech_pat = re.compile(r'([一-龥]{2,3})(?:' + speech_verbs + ')')
    raw = Counter()
    for line in lines:
        for m in speech_pat.finditer(line):
            w = m.group(1)
            if re.match(r'^[一-龥]+$', w):
                raw[w] += 1

    # Step 2: filter aggressively
    result = []
    for w, count in raw.most_common():
        if count < 3:
            break
        # Must be 2 chars starting with surname, or 3 chars with compound surname
        if len(w) == 2 and w[0] in surname_chars:
            result.append((w, count))
        elif len(w) == 3 and (w[:2] in compound or w[0] in surname_chars):
            result.append((w, count))

    # Step 3: also collect names introduced via naming patterns
    name_intro = re.compile(r'(?:名叫|叫做|名为|姓[一-龥]|叫[一-龥]|我是|我叫|在下|老夫|本座|贫道|贫僧|老衲|妾身|奴婢|奴才|洒家|咱家|老娘|本[一-龥])([一-龥]{2,4})')
    intro_names = Counter()
    for line in lines:
        for m in name_intro.finditer(line):
            n = m.group(1)
            if re.match(r'^[一-龥]{2,4}$', n):
                intro_names[n] += 1

    # Merge, deduplicate (intro names usually high quality)
    seen = {n for n, _ in result}
    for n, c in intro_names.most_common(50):
        if n not in seen and c >= 1:
            result.append((n, c))
            seen.add(n)

    # Step 4: post-process — merge fragments into base names
    merged = {}
    sorted_names = sorted(result, key=lambda x: -x[1])
    for name, count in sorted_names:
        if len(name) == 2:
            merged[name] = merged.get(name, 0) + count
        elif len(name) == 3:
            prefix = name[:2]
            suffix = name[2]
            # Case A: "陈玄询/说/微" → merge to "陈玄"
            speech_suffixes = '说问道叫喊喝笑骂怒吼斥冷淡沉叹微轻声平冰暗狞厉暴怒似的大询'
            if suffix in speech_suffixes:
                if prefix in merged:
                    merged[prefix] += count
                else:
                    merged[prefix] = merged.get(prefix, 0) + count
            # Case B: "山河微/山河询" → merge to "楚山河" (chars 1,2 match)
            else:
                # Check if any existing 3-char key shares chars 1-2 with this one
                matched = False
                for existing in list(merged.keys()):
                    if len(existing) == 3 and existing[1:] == name[1:] and existing != name:
                        merged[existing] += count
                        matched = True
                        break
                if not matched:
                    merged[name] = merged.get(name, 0) + count
        else:
            merged[name] = merged.get(name, 0) + count

    # Step 5: final filter — remove common words that aren't names
    not_names = {
        '废物', '前辈', '过来', '起来', '那天', '那就', '那几',
        '冷淡', '冷漠', '冷声', '冷声说', '冷漠说',
        '那你', '那谁知', '那不知', '那还用',
        '么名字', '有理会', '有理会他', '经不知', '应该知',
        '空间通', '马恭敬', '方不知',
        '双眸子', '屈辱大', '时发出', '苍凉的', '万法灭',
        '出来', '不出来', '你爹', '不是一个', '无辜的',
        '面阎王', '解析天', '一声', '一道', '阵阵',
    }
    result = [(n, c) for n, c in sorted(merged.items(), key=lambda x: -x[1])
              if n not in not_names and c >= 3]

    return result


def extract_locations(lines):
    """Extract location names by suffix pattern across full text."""
    suffixes = '(?:城|镇|村|山|河|谷|林|街|巷|楼|阁|殿|堂|帮|派|门|宗|府|院|庄|寨|堡|关|口|铺|坊|市|县|岭|峰|湖|海|岛|寺|庙|观|宫|塔|台|亭|桥|崖|渊|坡|岗|丘|洞|窟)'
    pattern = re.compile(r'([一-龥]{2,5}' + suffixes + r')')
    blacklist = {'不过如此', '怎么回事', '怎么回事呢', '什么地方', '什么地方呢', '什么门派'}
    locs = Counter()
    for line in lines:
        for m in pattern.finditer(line):
            name = m.group(1)
            if name not in blacklist:
                locs[name] += 1
    return [(l, c) for l, c in locs.most_common(100) if c >= 3]


def extract_techniques(lines):
    """Extract martial arts / skill names across full text."""
    suffixes = '(?:拳|掌|腿|指|爪|刀|剑|枪|棍|鞭|功|法|诀|经|术|劲|步|身|气|罡|罩|体|印|斩|劈|刺|扫|崩|裂|碎|破|杀)'
    pattern = re.compile(r'([一-龥]{2,5}' + suffixes + r')')
    blacklist = {'不过如此', '怎么回事', '怎么回事呢', '什么功夫', '什么功法', '这种功夫', '那种功法'}
    techs = Counter()
    for line in lines:
        for m in pattern.finditer(line):
            name = m.group(1)
            if name not in blacklist:
                techs[name] += 1
    return [(t, c) for t, c in techs.most_common(150) if c >= 3]


def build_timeline_stub(scenes, chapters):
    """Generate timeline_stub.md content."""
    lines_out = ["# 剧情时间线", "", "按场景顺序排列，每个字段留空由 agent 填写。", ""]
    for start_line, ch_title, scene_idx in scenes:
        lines_out.append("---")
        lines_out.append("")
        lines_out.append(f"## 场景")
        lines_out.append(f"- 时间: [填写]")
        lines_out.append(f"- 地点: [填写]")
        lines_out.append(f"- 人物: [填写]")
        lines_out.append(f"- 事件: [填写]")
        lines_out.append(f"- 等级变化: [填写]")
        lines_out.append(f"- 章节: {ch_title}" if scene_idx == 0 else f"- 章节: {ch_title} (续)")
        lines_out.append(f"- 原文行号: L{start_line}")
        lines_out.append("")
    return '\n'.join(lines_out)


def build_checklist(names, locations, techniques):
    """Generate CHECKLIST.md content."""
    lines_out = ["# 提取清单", "", "每项按模板填写 lore 文件后勾选。", ""]
    lines_out.append("## 人物")
    lines_out.append("")
    for n, c in names:
        lines_out.append(f"- [ ] {n} (出现{c}次)")
    lines_out.append("")
    lines_out.append("## 地点")
    lines_out.append("")
    for l, c in locations:
        lines_out.append(f"- [ ] {l} (出现{c}次)")
    lines_out.append("")
    lines_out.append("## 功法/技能")
    lines_out.append("")
    for t, c in techniques:
        lines_out.append(f"- [ ] {t} (出现{c}次)")
    return '\n'.join(lines_out)


def main():
    parser = argparse.ArgumentParser(description="Preprocess novel for novel-game skill")
    parser.add_argument("novel_path", help="Path to novel .txt")
    args = parser.parse_args()

    novel_path = args.novel_path
    novel_dir = os.path.dirname(os.path.abspath(novel_path))

    with open(novel_path, encoding='utf-8') as f:
        lines = f.readlines()

    print(f"全书: {len(lines)}行, {sum(len(l) for l in lines)}字符")

    # 1. Chapter detection
    chapters = find_chapters(lines)
    print(f"章节: {len(chapters)}")

    # 2. Scene detection
    scenes = extract_scenes(lines, chapters)
    print(f"场景: {len(scenes)}")

    # 3. Name extraction (full text)
    print("扫描人物...")
    names = extract_names(lines)
    print(f"人物候选: {len(names)}")

    # 4. Location extraction (full text)
    print("扫描地点...")
    locations = extract_locations(lines)
    print(f"地点候选: {len(locations)}")

    # 5. Technique extraction (full text)
    print("扫描功法...")
    techniques = extract_techniques(lines)
    print(f"功法候选: {len(techniques)}")

    # Build output
    lore_dir = os.path.join(novel_dir, "lore")
    plot_dir = os.path.join(lore_dir, "plot")
    os.makedirs(plot_dir, exist_ok=True)

    # Timeline stub
    timeline_path = os.path.join(plot_dir, "timeline_stub.md")
    timeline_content = build_timeline_stub(scenes, chapters)
    with open(timeline_path, "w", encoding="utf-8") as f:
        f.write(timeline_content)
    print(f"时间线骨架: {timeline_path} ({len(scenes)} 场景)")

    # Checklist
    checklist_path = os.path.join(lore_dir, "CHECKLIST.md")
    checklist_content = build_checklist(names, locations, techniques)
    with open(checklist_path, "w", encoding="utf-8") as f:
        f.write(checklist_content)
    print(f"提取清单: {checklist_path}")

    # Stats
    print(f"\n---")
    print(f"章节: {len(chapters)}")
    print(f"场景: {len(scenes)}")
    print(f"人物候选(全书扫描): {len(names)}")
    print(f"地点候选(全书扫描): {len(locations)}")
    print(f"功法候选(全书扫描): {len(techniques)}")


if __name__ == "__main__":
    main()
