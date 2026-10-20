#!/usr/bin/env python3
"""Show delivery identities and pending editions without substituting a similar book."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description="資料の名前・タグ・制作状態を表示")
parser.add_argument("--tag", action="append", default=[], help="完全一致のタグ（複数指定はAND）")
parser.add_argument("--id", help="資料IDまたは制作作業ID")
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
data = json.loads((root / "downloads/latest-materials.json").read_text())
rows = [dict(item_type="current", **v) for v in data["documents"].values()]
rows += [dict(item_type="planned", **v) for v in data["production_targets"]]
rows = [v for v in rows
        if (not args.id or args.id == v.get("material_id", v.get("work_id")))
        and all(tag in v["tags"] for tag in args.tag)]
if not rows:
    parser.exit(1, "NO_MATCH: 該当資料なし。別資料で代用しない。\n")
print(json.dumps(rows, ensure_ascii=False, indent=2))
