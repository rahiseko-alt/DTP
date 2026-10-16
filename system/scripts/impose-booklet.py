#!/usr/bin/env python3
"""BOOK の PDF（1ページ1面、仕上がり+塗り足し）から、確認・製本用の見開き PDF を作る。

  spreads : 見開きの閲覧用。表紙／2-3／…／最終ページ。左綴じ、見開き中央で仕上がり線が接する
  saddle  : 中綴じの面付け。印刷順に重ねて両面印刷し、真ん中で折って折り目を止めると冊子になる
            （ページ数は4の倍数。左綴じ。両面印刷は「短辺とじ（短辺で反転）」）

使い方:
  python3 system/scripts/impose-booklet.py --src <book.pdf> --mode saddle --out <out.pdf> [--bleed-mm 3]

トンボ（トリムマーク）・CMYK・PDF/X は付けない（system/rules/output.md。入稿形式は印刷会社に確認）。
外側の塗り足しは残し、見開き中央（綴じ側）の塗り足しは仕上がり線で切って、反対側のページを隠さない。
"""
import argparse
import sys

from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from pypdf.generic import DecodedStreamObject, NameObject

MM = 72 / 25.4


def clipped(page, x0, y0, x1, y1):
    """内容を矩形 (x0,y0,x1,y1)（ページ座標）で切り抜く（コンテンツストリームに clip を前置する）。"""
    data = page.get_contents().get_data()
    head = f"q {x0:.3f} {y0:.3f} {x1 - x0:.3f} {y1 - y0:.3f} re W n\n".encode()
    stream = DecodedStreamObject()
    stream.set_data(head + data + b"\nQ")
    page[NameObject("/Contents")] = stream
    return page


def sheet_of(reader, left, right, bleed):
    """左右のページ番号（0 始まり、None は白紙）から、綴じ側の塗り足しを切った1面を作る。"""
    w = float(reader.pages[0].mediabox.width)
    h = float(reader.pages[0].mediabox.height)
    sheet_w = 2 * w - 2 * bleed
    out = PageObject.create_blank_page(width=sheet_w, height=h)
    if left is not None:
        p = clipped(reader.pages[left], 0, 0, w - bleed, h)  # 右側（綴じ側）の塗り足しを切る
        out.merge_transformed_page(p, Transformation())
    if right is not None:
        p = clipped(reader.pages[right], bleed, 0, w, h)  # 左側（綴じ側）の塗り足しを切る
        out.merge_transformed_page(p, Transformation().translate(sheet_w - w, 0))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=["spreads", "saddle"], required=True)
    ap.add_argument("--bleed-mm", type=float, default=3.0)
    a = ap.parse_args()

    bleed = a.bleed_mm * MM
    n = len(PdfReader(a.src).pages)
    reader = PdfReader(a.src)  # 面を切り抜くので、使う面ごとに内容を書き換える（各面は1回だけ使う）
    w = PdfWriter()
    if a.mode == "spreads":
        w.add_page(sheet_of(reader, None, 0, bleed))
        for i in range(1, n - 1, 2):
            w.add_page(sheet_of(reader, i, i + 1, bleed))
        if n % 2 == 0:
            w.add_page(sheet_of(reader, n - 1, None, bleed))
    else:
        if n % 4:
            sys.exit(f"中綴じはページ数が4の倍数である必要があります（現在 {n} ページ）")
        # 外側の紙から内側へ。紙 k（0 始まり）の表は [n-1-2k | 2k]、裏は [2k+1 | n-2-2k]
        for k in range(n // 4):
            w.add_page(sheet_of(reader, n - 1 - 2 * k, 2 * k, bleed))
            w.add_page(sheet_of(reader, 2 * k + 1, n - 2 - 2 * k, bleed))
    w.add_metadata({"/Title": f"{a.mode} imposition of {a.src}"})
    w.write(a.out)
    print(f"{a.mode}: {len(w.pages)} 面 → {a.out}")


if __name__ == "__main__":
    main()
