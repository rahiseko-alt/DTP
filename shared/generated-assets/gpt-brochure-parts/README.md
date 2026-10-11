# GPT制作画像から作る写真パーツ

元画像: `references/user-gpt/lecturer-spread/page_001.png`。出典は同じフォルダの `source.yaml`。

画像はImageGenで元画像から文字・数字・ロゴ・帯・カード・枠を取り除いた生成写真素材です。人物の細部は再生成で変化しています。本校の実在教員・在校生の写真として登録・掲載する素材ではありません。実写真の正本は `company-data/photos/` です。

| ファイル | 元画像の領域 | 状態 |
| --- | --- | --- |
| teacher-students-photo.png | 左ページの講師と学生の写真 | 2026-10-11 人間が承認 |
| use-ai.png | 右ページ6ステップ・上段左 | 作成中 |
| research.png | 上段中央 | 作成中 |
| create.png | 上段右 | 作成中 |
| analyze.png | 下段左 | 作成中 |
| present.png | 下段中央 | 作成中 |
| work.png | 下段右 | 作成中 |
| marketing.png | 活用例の1枚目 | 作成中 |
| web-production.png | 活用例の2枚目 | 作成中 |
| business-report.png | 活用例の3枚目 | 作成中 |
| video-production.png | 活用例の4枚目 | 作成中 |

各画像の隣の `.prompt.yaml` に編集指示と参照入力を記録します。写真を載せる枠・帯・ラベル・正確な文字・正式ロゴはコード側で配置します。BOOKへの組込みと印刷用の配置サイズ確認は未実施です。