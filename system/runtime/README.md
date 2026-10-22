# PDF抽出の固定ランタイム

`poppler-linux-64.lock` はLinux x86_64用Poppler 26.05.0と全推移依存の配布URL・SHA256を固定するexplicit lockです。micromambaも2.9.0-0の実体SHA256を検証して取得します。通常の導入で依存解決や最新版への更新は行いません。

```bash
bash system/scripts/setup-extraction-runtime.sh
export PATH="$PWD/.cache/extraction-runtime/env/bin:$PATH"
npm run asset:check
```

GitHub Actionsも同じ導入スクリプトとlockを使います。Ubuntu 24.04へ固定し、`pdftoppm`と`pdfinfo`をこのprefixから実行。元の抽出recipe、版一致、原本SHA、再抽出PNGのSHA検査は維持しています。

クラウド付属の26.05.0とconda-forge版26.05.0で、管理中の原本9cropがすべて同じSHA256になることを実測しました。紙面・写真・登録済みcropの内容と役割は変更しません。検証は `docs/audits/extraction-runtime-20261022/`。

lockの更新は意図的なランタイム変更として行い、対象cropの再抽出SHAと必須asset-integrityの両方で確認します。版文字列だけを書き換えて既存recipeへ合わせません。
