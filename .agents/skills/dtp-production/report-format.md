# 同じPDFへのレビューと編集長判断

レポートは `books/<id>/reviews/production/<pdf-sha256>/` に保存する技術検査の実体。全体の状態台帳ではない。

独立レビュアーの返答を `review.json` に保存する。以下は形式例であり、未検査でpassを埋めてはならない。

```json
{
  "pdf_sha256": "実PDFのsha256",
  "mode": "preview",
  "page_count": 12,
  "binding": "left",
  "editor_session": "実際の制作エージェントID",
  "reviewer_session": "実際の独立レビュアーID",
  "pages_seen": [1,2,3,4,5,6,7,8,9,10,11,12],
  "spreads_seen": [[1],[2,3],[4,5],[6,7],[8,9],[10,11],[12]],
  "dimensions": {
    "content": "pass", "audience": "pass", "spreads": "pass", "rhythm": "pass",
    "legibility": "pass", "assets": "pass", "output": "pass"
  },
  "checks": {"validate":"pass", "render":"pass", "visual_pages":"pass", "visual_spreads":"pass"},
  "findings": [],
  "evidence": {"見開き画像": ["実際に開いた画像パス"], "検証": ["実行結果の参照"]}
}
```

未検査は`uninspected`、不合格は`fail`。指摘には`severity`、`pages`、`issue`、`evidence`、`required_fix`を記入する。
releaseではchecksに`pinned_browser`・`print_dimensions`・`effective_resolution`が必要。

編集長の返答を `decision.json` に保存する。review_sha256は保存したreview.jsonのバイト列のsha256。

```json
{
  "pdf_sha256": "同じ実PDFのsha256",
  "review_sha256": "実review.jsonのsha256",
  "mode": "preview",
  "chief_session": "実際の編集長エージェントID",
  "decision": "submit",
  "quality": {"intent":"pass", "coherence":"pass", "design":"pass", "usable":"pass"},
  "reason": "依頼と現物に基づく提出理由"
}
```

```bash
python3 system/scripts/dtp-quality-gate.py --pdf <PDF> --review <review.json> --decision <decision.json> --mode preview
```

重大指摘、未検査、見開き不足、版の不一致、自己レビュー、編集長差し戻しでは非zero終了。minorは編集長が用途に対して許容する理由を判断に残す。

ゲートは実PDFのページ数とハッシュを確認する。報告内容が本当か、IDが実際の起動者か、紙面が美しいかを単独で証明する機能ではない。親が起動IDとツール実行/目視の証拠を確認する。人間の最終採用・マージ・入稿承認とは別。

デザイン審査ではdesign-contract.mdに従い、evidenceに「参照構成比較」「依頼条件照合」を追加する。原本と出力の具体的画像パス・比較結果を記載し、spreads/rhythm/assets/audienceの合否と一致させる。必須指示違反をminorとして許容しない。
