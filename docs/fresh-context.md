# 台帳の入口

読み書き・開始・終了の手順は [運用ルール台帳](../company-data/rules-ledger.md) に集約しました。

Sで毎回読むのは [確定台帳](../company-data/ledger.md) の全文です。

```bash
python3 system/scripts/read-ledger.py
```

`--local` は未マージ作業版の検証専用です。共通版の取得成功とは区別します。
