# 国際ビジネスAI科・原画保持パーツ

9点すべて元画素と一致。写真単体8点、後付け文字/帯/ロゴが重なる1点は分離未完了です。

顔・服装・背景・色・人数・構図を再生成していません。原画の矩形抽出であり、全身透過切抜きではありません。写真内の衣服文字・モニターUI・制作物の文字は、被写体の一部として原画どおり保持します。

原本: references/user-gpt/faithful-parts-20261013/international-ai.png

推定配置寸法は幅だけA4相当として参考換算し、高さは元画像の縦横比を保持。実配置/印刷品質の合格値ではありません。個別PNGは無拡縮、contact-sheetだけ縮小確認用です。

| ID | 状態 | 元画素サイズ |
| --- | --- | --- |
| hero-original | restoration_required | 745×478px |
| learning-01-generative-ai | ready_exact | 218×133px |
| learning-02-international-business | ready_exact | 218×133px |
| learning-03-marketing | ready_exact | 218×133px |
| learning-04-cultural-communication | ready_exact | 355×138px |
| learning-05-presentation | ready_exact | 311×138px |
| feature-01-practical-ai | ready_exact | 218×129px |
| feature-02-collaboration | ready_exact | 213×129px |
| feature-03-pbl | ready_exact | 207×129px |

全詳細・出典・切り出し矩形・制約はmanifest.jsonと各.prompt.yamlを確認。既存の生成文字除去候補は顔等の変化があるため不採用。試行画像はGit対象外の.cache/gpt-faithful-parts-20261013/rejected/へ保管し、完成パーツへ混ぜていません。

各extractスクリプトで再抽出後、親フォルダのbuild-catalog.mjsで分類・寸法・画素を再検証します。
