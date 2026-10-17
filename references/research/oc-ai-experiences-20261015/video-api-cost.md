# 高校生10人の短いMV制作：画像・動画・音楽APIの料金調査

公式本文取得日：2026-10-15。USD、税・為替・編集作業・保存・転送を含まない。月額個人プランとは分けたAPI従量料金。実際の生成、支払、アカウント設定は行っていない。

## 結論

画像はOpenAI GPT Image、動画と音楽はGoogleのAPIに現行価格がある。ただし**高校生本人のリアルな分身を飛ばす体験には、年齢・人物生成条件が料金より先に必要**。Gemini APIは18歳未満向けAPI Clientを禁じ、Vertex画像→動画は人物生成が成人限定。スタッフが会社ログインを貸せばよい、APIキーを隠せば無条件で適法・許可、と判断できない。Sora APIは既に終了している。

## 1. OpenAI：静止画の分身素材。Sora動画APIは候補外

[画像生成公式](https://developers.openai.com/api/docs/guides/image-generation) の1024×1024 GPT Image 2出力参考料金：Low $0.006、Medium $0.053、High $0.211/枚。入力テキスト・参照画像トークンは別。10人各2〜3案=20〜30枚なら、Mediumの**出力のみ$1.06〜1.59**、High $4.22〜6.33。元写真から編集する場合は画像入力費を足す必要があり、これを総額とは呼ばない。

引用：「The final cost is the sum of: input text tokens input image tokens if using the edits endpoint image output tokens」。[API価格](https://platform.openai.com/docs/pricing) はモデル別入力・出力トークン表。ChatGPTの月額契約がAPI料金を含むとの根拠にはならない。

[Sora 2モデル公式](https://developers.openai.com/api/docs/models/sora-2) は「The Sora 2 models and Videos API were shut down on September 24, 2026 and are no longer available. There is no one-to-one replacement API.」と明記。古い$0.10/秒の表も同ページに残るが**歴史料金であって今回の購入候補ではない**。[旧動画ガイド](https://developers.openai.com/api/docs/guides/video-generation) 冒頭も終了と歴史資料であることを明示。旧ガイドの人顔画像拒否等も現行サービスの許可には使わない。

## 2. Gemini API：Veo動画とLyria音楽

[公式価格](https://ai.google.dev/gemini-api/docs/pricing) は「Paid Tier, per second in USD」と明記。

| 音声付き動画 | 720p生成1秒 | 200〜600生成秒の試算 |
| --- | ---: | ---: |
| Veo 3.1 Lite Preview | $0.05 | $10〜30 |
| Veo 3.1 Fast Preview | $0.10 | $20〜60 |
| Veo 3.1 Standard Preview | $0.40 | $80〜240 |

計算前提：10人×完成尺10〜20秒×2〜3試行=200〜600生成秒。**完成尺と請求生成尺は一致しないことがある**。4/6/8秒等の対応尺、カット数、作り直しに応じて請求尺が増える。例えば1人8秒×2カット×3案なら全体480秒、Lite $24 / Fast $48 / Standard $192。余った4秒を切っても生成代は消えない。

音楽：Lyria 3 Clip Preview 30秒$0.04/曲、Lyria 3 Pro Preview全曲$0.08/曲、Lyria 3.5全曲$0.08/曲。各人2〜3曲なら30秒版20〜30曲で$0.80〜1.20。歌詞・本人声クローン・任意歌声への対応はこの料金表から確認できない。音声付きVeoの価格は同期音声の生成価格であり、**本人声の再現を保証する機能や権利ではない**。

価格表引用：「You will only be charged if your video is successfully generated.」失敗の分類や音楽・他モデルに同一条件が適用されると一般化しない。

**利用年齢条件**：[Gemini API追加規約](https://ai.google.dev/gemini-api/terms) は「You must be 18 years of age or older to use the APIs.」さらに「You also will not use the Services as part of a website, application, or other service ... that is directed towards or is likely to be accessed by individuals under the age of 18.」。高校生向けセルフ操作UIの採用を安易に勧められない。職員だけの集中処理がこの企画で許されるかは、処理内容と提供形態について正式確認が必要。

## 3. Google Cloud（Vertex由来の公式URL）：組織運用候補

[公式モデル仕様](https://cloud.google.com/vertex-ai/generative-ai/docs/models/veo/3-1-generate) はVeo 3.1の動画長4/6/8秒、最大4出力/プロンプト、画像→動画、テキスト→動画を記載。Veo3.1/FastのGA開始2025-11-17、Lite Preview開始2026-04-02。API利用権・クォータ・地域を当日までに実機で確認する必要がある。

[Cloud価格](https://cloud.google.com/vertex-ai/generative-ai/pricing) は取得時公式リダイレクト先が `cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing`。Veo3.1 720p音声付き$0.40、Fast $0.10、Lite $0.05、音声なしは順に$0.20/$0.08/$0.03と掲載。ただしこの本文表記は「/ 1 count」であり、本調査ではCloudのcount単位を独自に秒と読み替えて請求総額を確定しない。上の秒単価試算は単位が明確なGemini API表に基づく。Cloud契約を採用する際はCloud SKUと課金単位を確認する。

[画像→動画公式](https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-an-image) の `personGeneration` は `allow_adult`（成人の人物・顔のみ）と `disallow` を示し、デフォルト `allow_adult`。引用：「Only allow generation of adult people and faces.」。このルートで**18歳未満本人のリアル顔を使えるとは説明できない**。アニメ化すれば必ず許可されるとの根拠もない。2D架空キャラクター、本人以外の架空成人、顔を使わない抽象MV等を検討できるが、希望する本人分身案を勝手にその代替で確定しない。

## 学校での運用と見積り範囲

- **個人月額ログインの共有**：今回調べたAPI料金から許可を導けない。参加者へ会社ID・パスワードやAPIキーを配らない。
- **法人seat**：人数分ユーザー権限を付与する契約方式。今回のAPI単価とは別見積りで、10人の席が含まれるとは扱わない。
- **スタッフ集中API実行**：学校の課金プロジェクトで職員が要求を実行し、結果を参加者へ渡す設計。参加者の会社ログイン不要にできるが、未成年向け利用条件・人物生成条件を自動で解消する方式ではない。
- **本人の声**：本人が別途録音した声を編集で重ねる方法と、声をAIで複製する方法を区別。後者の価格・同意・未成年条件は今回未調査。
- **音楽**：生成音楽の費用は上記。本人声で歌わせるモデル、歌詞、商用公開や配布の権利は別確認。同期音声付き動画と完成MVのBGMも別。

条件が満たされる場合の純生成費用の一例は、Lite動画480秒$24＋30秒音楽30曲$1.20＋GPT Image2 Medium画像30枚出力$1.59＝**$26.79＋画像入力等**。これは未成年本人分身企画の実施可否を承認する見積りではなく、従量料金の算術例。再試行・尺増加・追加音声API・編集ソフト・法人seat・保存等は別。遅延と失敗を含めた実機試行を行わず当日10人同時完成は保証できない。

取得HTML・抽出本文・URL・取得日・SHA256は `video-api-cost-sources.json` と `raw-video-api-cost/` に保存。調査のみで、チラシBOOK・自社情報・台帳は変更していない。
