# AGENTS.md — publishing-studio 作業指示（Codex / Claude Code 共通）

このファイルは、このリポジトリで作業するすべての AI エージェント（Codex、Claude Code）と人間に共通の指示の正本です。
Claude Code は `CLAUDE.md` 経由でこのファイルを読み込みます。どちらのエージェントでも、**同じルール・同じリポジトリ・同じデータ・同じレンダリング・同じテスト・同じレビュー基準**で作業します（docs/concept.md §10）。
エージェント固有の事情でルールを変えないでください。共通のルールはこのファイルと `system/rules/` に書きます。

## 1. このリポジトリについて

AIビジネス専門学校のパンフレット・募集要項・チラシ・ポスター等の紙面（BOOK）を、複数の他校・他社の参考資料からデザイン構造を分析・再構成し、自社の正本データだけを使って制作・更新し続けるための「AI支援型DTP制作基盤」のモノレポです。
ページは「AI 生成の背景（Layer 1）＋ HTML/CSS/SVG の構造（Layer 2）＋ コードで正確に配置する文字（Layer 3）」で組み立て、Playwright（Chromium）で PNG / PDF に出力します。
構想の原本は [docs/concept.md](docs/concept.md)（**編集禁止**）、仕組みの詳細は [docs/architecture.md](docs/architecture.md) です。

## 2. 4台帳の共通入口

人間の最新指定により記録は次の4台帳に集約する。台帳と原本・制作物のフォルダは別物。

| 台帳 | 用途 |
| --- | --- |
| [確定台帳](company-data/ledger.md) | 最新の最有力情報。記載または空欄 |
| [引継ぎ台帳](company-data/handoff-ledger.md) | 再開位置・次作業・注意点 |
| [経緯台帳](company-data/history-ledger.md) | 判断・変更の理由 |
| [運用ルール台帳](company-data/rules-ledger.md) | 読み書き・担当・作業手順 |

S・開始・再開時は `python3 system/scripts/read-ledger.py` で確定台帳を全文読み、同じsha256の開始・終了マーカーを確認する。続けて引継ぎ台帳も必ず全文読む（省略不可）。会話中は台帳更新を認識した時と全文を保持していない時だけ再読する。毎回答・毎編集の再読は不要。

具体的な開始・終了・更新・マージ手順は運用ルール台帳を参照する。引継ぎ・経緯・原本は必要時に参照する。Gitは保存・共有・変更管理の手段であり、現在情報を把握するため履歴を読む必要はない。

確定台帳の更新は人間の明確な指示で作業ブランチに書き込み、人間が承認したマージでmainの共通版に反映する。原本・画像・コード・制作設定は各フォルダに保存する。制作用YAMLはレンダリング入力であり、別の把握用台帳にしない。

## 紙面制作の起動

「紙面を作れ」「冊子を作れ」や紙面品質の改善依頼では [dtp-productionスキル](.agents/skills/dtp-production/SKILL.md) を適用し、編集制作・独立レビュー・編集長を別エージェントで行う。これは人間が指定した制作体制。部品の生成・編集依頼では [dtp-partsスキル](.agents/skills/dtp-parts/SKILL.md) を適用する。登録役割とホストの対応はスキルの公式設定説明を確認する。

## 3. 制作の現在情報

現在情報は確定台帳、再開事項は引継ぎ台帳を読む。このファイルに進捗表を複製しない。

## 4. ディレクトリマップ

```text
.
├─ AGENTS.md / CLAUDE.md / README.md
├─ docs/
│  ├─ concept.md             構想の原本（編集禁止）
│  └─ architecture.md        データの流れ・形式・CLI・テスト
├─ system/
│  ├─ rules/                 制作ルール（まず 00-principles.md）
│  ├─ prompts/               作業用プロンプト（解析・背景生成・完コピ・変換・レビュー・日常編集）
│  ├─ templates/             new:book / new:page / ref:ingest が使う雛形、review.md、background.prompt.yaml
│  ├─ scripts/               CLI（render / compare / validate / new-book / new-page / ingest-reference / ref-prep / gen-inputs / doctor / setup.sh）
│  ├─ design-engine/         ページ合成・スキーマ・テンプレート（Handlebars）・Vite プレビュー
│  ├─ devcontainer/          Dockerfile と環境の説明
│  └─ fixtures/studio/       テスト用のミニスタジオ（架空の「サンプル学園」）
├─ company-data/             自社情報の唯一の正本（facts / brand / photos / copy）
├─ references/               他校・他社の参考資料（<source>/<kind>/）
├─ books/                    制作する BOOK（<bookId>/）
├─ shared/
│  ├─ components/            共通パーシャル（*.hbs）
│  ├─ layouts/               共通 CSS（grid / typography / components）
│  └─ generated-assets/      再利用する AI 生成ビジュアル（+ .prompt.yaml）
├─ .devcontainer/  .claude/settings.json
└─ package.json  tsconfig.json  vitest.config.ts
```

## 5. コマンド

すべて `npm run <名前>` で実行します。引数は `--` の後に書きます。CLI（render / compare / validate / new:book / new:page / ref:ingest / doctor）は `--root <dir>`（既定: リポジトリルート）を受け付けます。`dev` は Vite のため `--root` ではなく環境変数で指定します（`STUDIO_ROOT=system/fixtures/studio npm run dev`、ポートは `PORT`）。

| コマンド | 用途 |
| --- | --- |
| `npm run setup` | 環境の初期化（`bash system/scripts/setup.sh`。`-- --quiet` で問題だけ表示） |
| `npm run doctor` | 環境診断（Node 22、Chromium、フォント、sharp、git-lfs、poppler の pdfinfo / pdftoppm） |
| `npm run dev` | プレビュー（Vite）。`/` に BOOK・ページ一覧、`/preview/<bookId>/<pageId>`（`?guides=1` でガイド）、`/preview/<bookId>` で BOOK 全体 |
| `npm run new:book -- <bookId> [--kind brochure] [--title "..."] [--size A4] [--orientation portrait] [--pages 4]` | BOOK を作成 |
| `npm run new:page -- --book <id> [--after <pageId>] [--type other] [--title "..."]` | ページを追加 |
| `npm run ref:ingest -- --source <name> --kind <kind> (--pdf <file> \| --images <dir>) [--dpi 150] [--format jpg\|png]` | 参考資料を取り込み（PDF のページ画像は既定 JPEG） |
| `npm run ref:prep -- (--spec <references/.../prep/<name>.yaml> \| --all)` | 写真・スキャンの参考ページを比較用に正立・単ページ・台形補正（`.cache/ref-prep/` に出力。`compare` の参照に指定ファイルを書けば自動で行う） |
| `npm run photo:add -- --file <画像> --id <写真ID> --rights "<使用条件・肖像の同意>" --tags a,b` | 学校の写真を `company-data/photos/` に取り込み `photos.yaml` に登録（タグ必須、向きの補正・EXIF除去・長辺6000pxまで） |
| `npm run photo:search -- (--query <語句> | --tag <タグ[,タグ...]>)` | 写真のID・キャプション・タグを絞り込み、一致分だけのコンタクトシートを `.cache/photo-search/` に作る |
| `npm run gen:inputs -- (--book <id> ... \| --all)` | Layer 1 の生成指示（`backgrounds/layer1-orders.yaml`）から、生成モデルへ入力する参考ページの切り出し（`.cache/gen-inputs/`）と必要な画素数の一覧を作る |
| `npm run render -- --book <id> [--page <id> ...] [--format png\|pdf\|both] [--dpi N] [--guides] [--release] [--out <dir>]` | PNG / PDF 出力 |
| `npm run compare -- --book <id> --page <id> [--reference <path>] [--rendered <png>] [--threshold 0.1]` | 参考ページとの比較（diff / side-by-side / overlay / report.yaml） |
| `npm run validate [-- --strict]` | データ・BOOK・参考資料・テンプレートの検証、直書き・禁止語・生成記録の確認 |
| `npm run typecheck` | TypeScript の型チェック |
| `npm run test` | テスト（vitest） |
| `npm run check` | `typecheck` → `validate` → `test` |

よく使う例:

```bash
npm run render -- --book brochure --page page_016 --format png
npm run compare -- --book brochure --page page_016
npm run render -- --book brochure --release
npm run validate -- --strict
```

## 6. ページの 3 層構造

最終ページを 1 枚の画像で作りません。**表現力は画像生成、正確性はコード**（詳細: system/rules/page-layers.md）。

| 層 | 作り方 | 置くもの | 書く場所 |
| --- | --- | --- | --- |
| Layer 1: BASE VISUAL | AI 画像生成・写真 | 背景、写真、生成ビジュアル、グラデーション、光、テクスチャ、複雑な装飾、写真と背景の融合 | `books/<id>/backgrounds/` + `page.yaml` の `background`、`shared/generated-assets/`、`company-data/photos/` |
| Layer 2: STRUCTURE | HTML / CSS / SVG | カード、枠、罫線、半透明パネル、単純図形、マスク、色面、本文量で大きさが変わる領域 | `page.html`、`page.css`、`shared/layouts/`、`shared/components/` |
| Layer 3: CONTENT | HTML（コード） | 見出し、本文、数字、学科名、氏名、企業名、URL、ページ番号、QR、キャプション | `page.html`（事実は `{{facts...}}` で参照） |

- 文字は画像に入れない。文章量で変わる枠は背景に焼き込まない
- Layer 1 の生成では、参考ページ画像を画像生成モデルへ直接入力してよい（image prompt / image reference / composition reference / style・visual reference / img2img 系など）。構図・背景・質感・視覚密度を高精度に再現または参考にし、その上にコードで正確な文字を載せる（system/rules/image-generation.md §3）
- 座標は `.trim`（仕上がり線基準、mm）。文字は安全領域の内側、色面・写真は塗り足しまで

## 7. 絶対に守るルール

docs/concept.md §14 の最重要原則（詳細と具体的な行動: system/rules/00-principles.md）:

1. GitHub を唯一の正本にする — 成果は commit / push して初めて完了
2. 自社データは 1 か所だけに持つ — `company-data/` だけ。BOOK には `{{facts...}}` などの参照だけを書き、値を書き写さない
3. 参考資料と自社情報を混同しない — 参考資料の固有情報を books / company-data / shared に持ち込まない
4. 画像生成に文字の正確性を求めない — 生成画像に文字・数字・ロゴ・QR を入れない
5. コードだけで全デザインを描こうとしない — 質感・光・複雑な装飾は Layer 1
6. 背景画像・構造・テキストを分離する
7. 初期制作と日常編集を分ける — 日常編集でデザインを作り直さない
8. AI の会話履歴ではなくファイルに状態を残す
9. 確定データは技術的に保護する — Phase 7 で導入予定（現在は未導入）
10. 一度作ったデザインを再利用可能な資産にする — 共通部品は `shared/` へ

このリポジトリでの追加ルール:

- **事実を作らない**: company-data にない情報を推測・Web 検索・参考資料で補わない。不明な値は `"TODO: ..."` のまま残して人間に確認する。実績の数値には `as_of` と `source` を付ける
- **参考資料の分離**: Phase 8 で流用禁止の 10 項目（学校名・実績・数字・人物・企業名・ロゴ・学科名・インタビュー・写真・固有コピー）は完コピ検証の段階からページ・company-data・shared に書き写さない（参考資料の写真・ロゴをそのまま貼る・切り出すのも不可。Layer 1 の画像生成への参考ページ画像の直接入力は可）。参考資料ごとに `source.yaml` の `forbidden_terms` を必ず埋める（`npm run validate` が books / company-data / shared での出現をエラーにする）
- **生成画像には記録**: 画像の隣に同じベース名の `.prompt.yaml`。生成に入力した参考画像と方式は `reference_inputs` に書く（system/rules/image-generation.md）
- **見て確認する**: 参考ページ・出力 PNG は画像として開いて目視する。OCR やテキスト抽出だけで判断しない
- **完コピ検証は最低 2 ラウンド**: Phase 5 では `npm run compare` による視覚比較と修正を 2 回以上行い、`review.md` に記録する（system/rules/review.md）
- **docs/concept.md を編集しない**
- **バイナリは Git LFS**: png / jpg / jpeg / pdf / webp / tif / psd / ai は `.gitattributes` で LFS 管理
- **検証を通す**: マージ前に、セッション内で `npm run doctor`・`npm run check`・変更した BOOK の `npm run render`・出力 PNG の目視を行う（自動 CI はないため、これが唯一の検証）。未完了・不合格の途中保存は§2に従い、合格とは扱わない。`approved` のページを変えたら理由をコミットメッセージに書く
- **保護機構（Phase 7）はまだ導入しない**: PreToolUse フック・権限設定・Git 差分チェックは Phase 6 の baseline 確定後に導入する（system/rules/protection.md）

## 8. どこに何を置くか

| もの | 置き場所 | 備考 |
| --- | --- | --- |
| 学校名・住所・連絡先・アクセス | `company-data/facts/school.yaml` | |
| 学科・教員・実績・問い合わせ先 | `company-data/facts/{courses,teachers,results,contacts}.yaml` | 新しい種類は `facts/<名前>.yaml` |
| ブランドカラー・書体 | `company-data/brand/colors/colors.yaml`、`brand/fonts/fonts.yaml` | CSS 変数 `--color-*` `--font-*` になる |
| ロゴ | `company-data/brand/logo/`（+ `logo.yaml`） | 正式データのみ |
| 学校の写真 | `company-data/photos/`（+ `photos.yaml`） | 権利確認済みのみ。AI 生成画像は不可 |
| 複数 BOOK 共通のコピー | `company-data/copy/*.yaml` | |
| 参考資料（PDF・ページ画像） | `references/<source>/<kind>/` | `npm run ref:ingest` |
| 参考資料の禁止語 | `references/<source>/<kind>/source.yaml` の `forbidden_terms` | |
| 参考資料の解析結果 | `references/<source>/<kind>/analysis/{book,page_NNN}.yaml` | |
| 比較用の補正指定（Phase 5） | `references/<source>/<kind>/prep/<name>.yaml` | `npm run ref:prep`。補正画像は `.cache/ref-prep/`（コミットしない） |
| BOOK の設定・ページ順 | `books/<id>/config/book.yaml` | |
| BOOK が使う参考資料 | `books/<id>/references.yaml` | パスで指定（コピーしない） |
| ページの構造と文字 | `books/<id>/pages/<pageId>/page.html`（+ `page.css`、`page.yaml`） | |
| ページの背景（生成） | `books/<id>/backgrounds/<pageId>.png` + `<pageId>.prompt.yaml` | |
| Layer 1 の生成指示（生成前） | `books/<id>/backgrounds/layer1-orders.yaml` | 素材ごとの大きさ・切り出し範囲・プロンプト。生成画像は `<素材 id>.png` + `.prompt.yaml`。未生成は `validate` が警告 |
| BOOK 固有の部品 | `books/<id>/components/*.hbs` | `{{> book/<名前>}}` |
| 共通の部品・CSS | `shared/components/*.hbs`、`shared/layouts/*.css` | |
| 再利用する生成ビジュアル | `shared/generated-assets/` + `.prompt.yaml` | |
| レビュー記録・比較出力 | `books/<id>/reviews/<pageId>/review.md`、`compare-<日時>/report.yaml` | 比較画像（`*.png`）は参考ページの画素を含むためコミットしない（`.gitignore` 済み） |
| 出力 | `books/<id>/output/png/<pageId>.png`、`output/pdf/<BOOK 名>.pdf` | |
| BOOK・ページの状態、次にやること | `book.yaml` / `page.yaml` の `notes`、`review.md` | 会話に残さない |
| ルール | `system/rules/` | |
| 作業プロンプト | `system/prompts/` | |
| 雛形 | `system/templates/` | |

## 9. 作業別の入口

| 作業 | プロンプト | 主なルール |
| --- | --- | --- |
| 参考資料の取り込み・解析 | system/prompts/analyze-reference.md | references.md、naming.md |
| 背景・ビジュアルの生成 | system/prompts/generate-background.md | image-generation.md |
| 完コピ検証 | system/prompts/replicate-page.md | page-layers.md、review.md、typography-ja.md |
| 自社版への変換 | system/prompts/convert-to-company.md | references.md、company-data.md |
| 視覚レビュー | system/prompts/visual-review.md | review.md、output.md |
| 日常編集 | system/prompts/daily-edit.md | company-data.md |

## 10. 担当・並行作業

担当・担当外・並行作業の確認は [運用ルール台帳](company-data/rules-ledger.md) を正本とする。

## 11. 困ったとき

- テンプレートのエラー「キー "..." がデータに存在しません」: company-data・page.yaml・book.yaml のキー名を確認。任意項目なら `{{#if}}` で囲む。値がないからといって値を作らない
- 画像が表示されない・比較が壊れる: LFS の実体が未取得の可能性。「Git LFS のポインタです（実体が未取得）」と出たら確実なので `git lfs pull`
- 「画像を読めません」、または `render` の「画像を表示できません: <パス>」に LFS の案内が付かない: ポインタではない（ファイルが壊れている・形式が対応していないなど）。`git lfs pull` では直らないので、元の画像を確かめる
- Chromium が起動しない・フォントがおかしい: `npm run doctor` → `bash system/scripts/setup.sh`。Playwright 指定版の Chromium を取得できない環境では、手元の Chromium を `STUDIO_CHROMIUM_PATH` に指定すれば確認用の出力はできる（`--release` は不可。system/devcontainer/README.md）
- ルールが矛盾している・判断できない: 作業を止め、論点を `notes` / `review.md` に書いて人間に確認する
