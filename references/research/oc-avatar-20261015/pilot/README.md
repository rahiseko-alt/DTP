# 合成・形式だけのダミー

`dummy-compositing-only.mp4` は幾何図形と合成テスト音の15秒動画。画面にも DUMMY / NO PERSON / NO AI GENERATION と明示。本人似アバター、AI画像・動画・音楽、本人声、飛行動作、スマホ保存を実証するものではない。

- 再現: `bash make-dummy.sh`（ffmpeg/ffprobeが必要）。同ディレクトリのダミーと `ffprobe.json` を再生成。
- 検証済み: H.264/AAC、720×1280、24fps、15秒MP4をローカル作成。ffprobe証跡を同梱。
- `compose-local.sh`: `bash compose-local.sh avatar.png voice.wav music.wav new-output.mp4`。既に用意した静止画と録音・BGMを15秒へ合成するだけ。人物への変換・飛行動作・声複製は行わない。BGMは短ければ繰り返す。出力既存時は上書きしない。
- 補助スクリプトも単色画像・合成音のみで実行。本人素材では未実行。人物画像や本人録音を同梱していない。
- 本番運用とAI工程はtechnical.md参照。
