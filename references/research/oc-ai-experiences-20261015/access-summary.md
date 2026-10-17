# 外部OCのAI体験調査：アクセス診断

**再開後の現状：** 2026-10-15、正規設定変更後にruntime `unrestricted / enforced` を確認。公式本文の取得に成功し調査を完了。成果は`report.md`。以下は設定変更前の診断履歴であり、現在の調査件数0や接続不可を意味しない。

取得日：2026-10-15。専門学校と大学の実例を公式本文から調べる依頼に対し、学校種別で2サブを起動した。現時点の公式本文取得・AI体験実例確認は0件。以下は調査先候補であり、実施校一覧ではない。

## 確認した環境

cloud-environment-runtimeのnetworking参考と`/etc/codex/network-policy.json`を再読。startup policyはrestricted、VPN未設定。runtime metadataはobservations_current:true、network state:unknown、custom allowed_hosts空。read_environment_config_draftで編集ドラフトもcustom egress空・package_managers presetのみと確認。draft保存とruntime適用は別。

専用Web検索・ブラウズツールは現在のALL_TOOLSに存在しない。通常HTTPSで学校10host、検索3hostへ接続したが全て`Tunnel connection failed: 403 Forbidden`または同義CONNECT403。TLS検証を無効にせず、proxy変更・他ドメイン経由の取得で制限を迂回していない。

## 必要な追加接続先候補

| 用途 | host |
| --- | --- |
| 専門学校公式 | www.hal.ac.jp, www.ncs.ac.jp, www.tokyo-ec.ac.jp, www.jec.ac.jp, www.denpa.ac.jp |
| 大学公式 | www.meijo-u.ac.jp, www.nucba.ac.jp, www.ait.ac.jp, www.tuis.ac.jp, www.it-chiba.ac.jp |
| 実際の企画ページの発見 | www.google.com, www.bing.com, search.yahoo.co.jp |

学校別URL・観測は`vocational-access.json`と`university-access.json`。検索クエリは「専門学校 大学 OC 生成AI 体験」をURLエンコードして通常HTTPS送信。本文は取得できていない。

## 再開時に集める情報

公式URL、開催日、対象、参加者が入力・操作する内容、制作物・持帰りの明記、所要時間、使用AI・ツール、講義/体験の区分、予約・保護者・費用。未記載は不明、本文未取得は未確認として区別する。画像、動画、音楽、ゲーム/アプリ、データ分析、ビジネス活用に分類するが、実例を収集するまでは分類に企画を創作して埋めない。

正規ネットワーク設定が適用されたら、上記接続を再試行し実際の公式企画本文・公開PDFを収集する。現段階では他校の具体的AI体験や集客効果を根拠付きで提案できない。
