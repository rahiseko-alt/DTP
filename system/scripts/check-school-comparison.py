#!/usr/bin/env python3
"""参考校台帳と学校比較表の整合を検査する（検証のみ。ファイルは書き換えない）。

エラー（終了コード1）:
  - 表の列数が不揃い（参考校台帳は4列、比較表は5列）
  - 比較表の項目が参考校台帳に存在しない／自社の確定台帳に存在しない（項目名の打ち間違い）
  - 比較表が最新でない（確定台帳・参考校台帳を読み直して作った結果と一致しない）
  - 口座番号など転記してはいけない値が含まれる
情報: 各校の【要確認】件数、「計算値」を含む行
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "system/scripts/build-school-comparison.py"
spec = importlib.util.spec_from_file_location("build_school_comparison", SCRIPT)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

FORBIDDEN = [
    (re.compile(r"普通預金\s*No\.?\s*\d{5,}"), "口座番号"),
    (re.compile(r"口座番号\s*[:：]?\s*\d{5,}"), "口座番号"),
]


def table_widths(path):
    widths = {}
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("| ") and not line.startswith("| ---"):
            widths[i] = len(line.strip()[1:-1].split("|"))
    return widths


def check(own_path=None, ref_path=None, out_path=None):
    own_path = own_path or builder.OWN
    ref_path = ref_path or builder.REF
    out_path = out_path or builder.OUT
    errors, info = [], []
    own = builder.read_table(own_path)
    ref = builder.read_table(ref_path)

    for name, path, want in (("参考校台帳", ref_path, 4), ("学校比較表", out_path, 5)):
        for line_no, w in table_widths(path).items():
            if w != want:
                errors.append(f"{name} {line_no}行目: 列数が {w}（正しくは {want}）")

    for label, rl, ol in builder.ROWS:
        if rl not in ref:
            errors.append(f"比較表の項目「{label}」に対応する参考校台帳の項目「{rl}」がありません")
        for k in ol:
            if k not in own:
                errors.append(f"比較表の項目「{label}」が参照する確定台帳の項目「{k}」がありません")

    expected = builder.render(own, ref)
    if not out_path.exists() or out_path.read_text(encoding="utf-8") != expected:
        errors.append("学校比較表が最新ではありません（python3 system/scripts/build-school-comparison.py で再生成）")

    for name, path in (("参考校台帳", ref_path), ("学校比較表", out_path)):
        text = path.read_text(encoding="utf-8")
        for pattern, what in FORBIDDEN:
            if pattern.search(text):
                errors.append(f"{name} に {what} が含まれています（転記しない）")

    for i, school in enumerate(("HAL名古屋", "国際医学技術専門学校", "名古屋医療秘書福祉&IT専門学校")):
        n = sum(cells[i].count("【要確認】") for cells in ref.values() if len(cells) > i)
        info.append(f"{school}: 【要確認】{n}件")
    calc = [k for k, cells in ref.items() if any("計算値" in c for c in cells)]
    if calc:
        info.append("計算値を含む行: " + "、".join(calc))
    return errors, info


def main():
    errors, info = check()
    for line in info:
        print("[情報] " + line)
    for line in errors:
        print("[エラー] " + line)
    print(f"結果: エラー {len(errors)} 件")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
