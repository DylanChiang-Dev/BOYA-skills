#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-skills.py — 博雅 skill 防呆檢查器（維護輔助，非 build 依賴）

定位：唯讀、只報告、不改檔。把 CONVENTIONS 的「SKILL.md 寫作契約」與
「以 SKILL.md 為準」的 ROUTER 同步，從口頭約定變成跑一下就能驗證的事。

只用標準函式庫。對人文社科維護者友善：純文字報告、可手動介入。

用法：
    python3 scripts/check-skills.py            # 印報告
    python3 scripts/check-skills.py --check    # 有 WARN/ERROR 時回傳非 0（給未來選用的 CI）

檢查項：
  契約（依 CONVENTIONS「SKILL.md 寫作契約」）
    - frontmatter 僅 name / description 兩欄，無版本欄
    - name 為 kebab-case 且與目錄同名
    - description 含「時使用」與至少一個「」觸發語
    - SKILL.md 行數 > 200 提醒檢查是否該拆（CONVENTIONS §8）
    - 誠信聲明（不編造／查無標註）存在與否（僅提示，由作者判斷是否誠信類）
  ROUTER 同步（依 ROUTER「以 SKILL.md 為準」）
    - 每個 skill 目錄都有對應 ROUTER 列
    - 每個指向 skill 的 ROUTER 列都對得上既有目錄（抓改名／錯字）
    - ROUTER 列裡的觸發語都能在該 skill 的 description 找到（抓 ROUTER 殘留舊觸發語）
"""

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO, "skills")
ROUTER = os.path.join(REPO, "ROUTER.md")

KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# 中文角括號觸發語：「...」
QUOTE = re.compile(r"「([^」]+)」")
ALLOWED_FM_KEYS = {"name", "description"}
SPLIT_LINE_LIMIT = 200

# ROUTER 表中合法但「非 skill 目錄」的 skill 欄目標（工具列），不應被當成漏目錄
NON_SKILL_TARGETS = {"templates/", "knowledge/venues.md", "VERIFICATION.md"}

ERRORS, WARNS, INFOS = [], [], []


def err(s):
    ERRORS.append(s)


def warn(s):
    WARNS.append(s)


def info(s):
    INFOS.append(s)


def parse_frontmatter(path):
    """回傳 (keys_in_order, dict, line_count)；非 --- 開頭則 keys 為 None。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, {}, len(lines)
    keys, data = [], {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            break
        m = re.match(r"^([A-Za-z0-9_]+):\s?(.*)$", lines[i])
        if m:
            keys.append(m.group(1))
            data[m.group(1)] = m.group(2).strip()
    return keys, data, len(lines)


def check_skill(name):
    sk_path = os.path.join(SKILLS_DIR, name, "SKILL.md")
    if not os.path.isfile(sk_path):
        err(f"[{name}] 找不到 skills/{name}/SKILL.md")
        return None
    keys, fm, n_lines = parse_frontmatter(sk_path)

    if keys is None:
        err(f"[{name}] SKILL.md 開頭不是 frontmatter（--- 區塊）")
        return None

    # 僅 name / description
    extra = [k for k in keys if k not in ALLOWED_FM_KEYS]
    if extra:
        err(f"[{name}] frontmatter 多出欄位 {extra}（契約：僅 name / description，版本走 git tag）")
    for need in ("name", "description"):
        if need not in fm:
            err(f"[{name}] frontmatter 缺 {need}")

    # name kebab-case 且與目錄同名
    fm_name = fm.get("name", "")
    if fm_name and not KEBAB.match(fm_name):
        err(f"[{name}] name「{fm_name}」非 kebab-case")
    if fm_name and fm_name != name:
        err(f"[{name}] name「{fm_name}」與目錄名「{name}」不一致")

    # description 觸發語契約
    desc = fm.get("description", "")
    triggers = [q.strip() for q in QUOTE.findall(desc)]
    if desc:
        if "時使用" not in desc:
            warn(f"[{name}] description 未見「……時使用」句型（契約：須寫明觸發語境）")
        if not triggers:
            warn(f"[{name}] description 未見任何「」觸發語")

    # 誠信聲明（提示，不判定誰是誠信類）：偵測「不編造／查無標註」這類具體字樣，
    # 而非泛用的「絕不／不得」（那幾乎每個 description 都有，會失去鑑別力）。
    integrity_markers = (
        "編造", "捏造", "查無", "查不到", "待人工", "待補", "需補", "真偽", "如實",
    )
    if desc and not any(m in desc for m in integrity_markers):
        info(f"[{name}] description 未含誠信聲明字樣（若屬誠信類技能，契約要求聲明「絕不編造／查無標註」）")

    # 行數提醒
    if n_lines > SPLIT_LINE_LIMIT:
        info(f"[{name}] SKILL.md {n_lines} 行 > {SPLIT_LINE_LIMIT}，CONVENTIONS §8 要求檢查是否該拆 references/")

    return {"name": name, "triggers": triggers}


def parse_router():
    """從 ROUTER.md 表格抽 (skill欄文字, 觸發語cell文字)；回傳 list[(skill, trigger_cell)]。"""
    rows = []
    if not os.path.isfile(ROUTER):
        err("找不到 ROUTER.md")
        return rows
    with open(ROUTER, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            trig, skill = cells[0], cells[1]
            # 跳過表頭與分隔列
            if set(skill) <= set("-: ") or skill in ("skill",):
                continue
            rows.append((skill, trig))
    return rows


def router_skill_token(skill_cell):
    """ROUTER skill 欄可能含反引號或附註，抽出主 token。"""
    m = re.search(r"`?([A-Za-z0-9_./-]+)`?", skill_cell)
    return m.group(1) if m else skill_cell.strip("`")


def main():
    if not os.path.isdir(SKILLS_DIR):
        err(f"找不到 skills/ 目錄：{SKILLS_DIR}")
        report()
        return 2

    skill_names = sorted(
        d for d in os.listdir(SKILLS_DIR)
        if os.path.isdir(os.path.join(SKILLS_DIR, d)) and not d.startswith(".")
    )

    parsed = {}
    for name in skill_names:
        r = check_skill(name)
        if r:
            parsed[name] = r

    router_rows = parse_router()
    router_targets = {router_skill_token(s): trig for (s, trig) in router_rows}

    # 每個 skill 目錄都有 ROUTER 列
    for name in skill_names:
        if name not in router_targets:
            warn(f"[{name}] skills/ 有此目錄，ROUTER.md 卻無對應列")

    # 每個指向 skill 的 ROUTER 列都對得上目錄
    for tok, trig in router_targets.items():
        if tok in NON_SKILL_TARGETS or tok.endswith("/") or "." in tok:
            continue
        if tok not in skill_names:
            warn(f"[ROUTER] 列指向「{tok}」，但 skills/ 沒有此目錄（改名或錯字？）")

    # ROUTER 觸發語應能回溯到 description（抓殘留舊觸發語）
    for name, data in parsed.items():
        trig_cell = router_targets.get(name)
        if not trig_cell:
            continue
        router_trigs = [q.strip() for q in QUOTE.findall(trig_cell)]
        desc_blob = "".join(data["triggers"])
        for rt in router_trigs:
            # 寬鬆：ROUTER 觸發語的關鍵詞是否出現在 description 觸發語裡
            core = re.split(r"[／/]", rt)[0].strip()
            if core and core not in desc_blob:
                info(f"[{name}] ROUTER 觸發語「{rt}」未在 description 觸發語中找到（ROUTER 為摘要，請人工確認非殘留）")

    return report()


def report():
    line = "─" * 56
    print(line)
    print("博雅 skill 防呆檢查報告  check-skills.py")
    print(line)
    for tag, bucket in (("ERROR", ERRORS), ("WARN", WARNS), ("INFO", INFOS)):
        print(f"\n{tag}（{len(bucket)}）")
        if not bucket:
            print("  （無）")
        for s in bucket:
            print(f"  • {s}")
    print("\n" + line)
    print(f"ERROR {len(ERRORS)}　WARN {len(WARNS)}　INFO {len(INFOS)}")
    print("註：ERROR=違反契約硬規；WARN=結構漂移待修；INFO=供人工確認，非必修。")
    print(line)
    if "--check" in sys.argv:
        return 1 if (ERRORS or WARNS) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
