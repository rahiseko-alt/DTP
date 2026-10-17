# 高校生10人のMV制作：声・音楽の公式料金と利用条件

取得日：2026-10-15（日本時間）。USD・税別。契約も生成も行っていない。公式公開本文と公式料金ページの埋込planデータを確認。会社ログインを高校生へ貸せるとは推測していない。

## 判断の要点

**18歳未満を含む本人声クローンにElevenLabsは採用できない。** 現行利用規約は18歳未満の利用を認めず、禁止用途ポリシーは18歳未満の声の録音をモデル作成・学習のために提出すること自体を禁止。成人教員のアカウントによる代行でも、この入力禁止は解消しない。学校体験で本人がしゃべった音声を録音し、そのファイルを動画編集でそのまま合成すれば、声クローン契約は不要（音声生成費$0）。この録音・編集案は本調査の設計提案であり、ElevenLabsの機能ではない。

音楽はSuno有料契約で生成したオリジナル曲を使う案が検討できるが、**学校組織利用と参加者へのアカウント貸与は別問題**。現行規約のenterprise連絡条項、権限、未成年同意を満たす運用は確認が必要。単一法人アカウントを10人へ配ればよい、とは結論しない。

## ElevenLabs

公式料金：https://elevenlabs.io/pricing

| プラン | 月払い | 年払い月換算／年総額 | 今回に関係する機能 |
| --- | --- | --- | --- |
| Free | $0 | $0 | 10k credits、商用不可、Instant Voice Cloningなし |
| Starter | $6 | $5／$60 | 30k credits、商用ライセンス、Instant Voice Cloning、custom voice slots 10 |
| Creator | $22 | 約$18.33／$220 | 121k credits、Professional Voice Cloning、custom slots 30、PVC 1 |
| Pro | $99 | $82.50／$990 | 600k credits、custom slots 160、PVC 1 |
| Scale | $299 | 約$249.17／$2,990 | 1.8M credits、3 workspace席、PVC 3 |
| Business | $990 | $825／$9,900 | 6M credits、10 workspace席、PVC 10 |
| Enterprise | 個別見積 | 個別見積 | 追加席・voice・同時実行等 |

料金FAQは年払いを月額の10か月分と明記。期間限定のStarter初月$1（Oct 18まで表示）、Creator初月$11は一時割引なので継続費用の基準から除外。価格表示はCreator 121kであり、過去の100kという一般情報を採用しない。TTSはおおむね1文字1credit、Flash等APIは0.5〜1credit/文字。voice slotsとworkspace席は別。10 slotsは10人のログイン許可を意味しない。

### 年齢・同意・アカウント

規約：https://elevenlabs.io/terms-of-use （最終更新2026-10-09）

> If you are under 18 years of age (or the age of legal majority where you live), you may not use our Services

> You may not share or permit others to use your individual account credentials.

ポリシー：https://elevenlabs.io/use-policy （最終更新2026-10-09）

> You may not submit voice recordings of anyone under 18 to create or train a voice model.

> Apps, products, or experiences directed at individuals under 18 are prohibited unless we have assessed and approved them in writing.

> You may not use our Services to create a voice, avatar or other content that uses the likeness of, or is designed to be recognised as, a specific real minor.

本人・保護者の同意だけでは上記禁止の解除とはならない。明示的で十分な説明を受けた同意のない存命者の声・肖像の複製も禁止。規約は権限を得た他者の声のモデルを一般に扱うが、次のPVC固有制約が優先される。

PVC公式ヘルプ：https://help.elevenlabs.io/hc/en-us/articles/36842751624209-Can-I-create-a-Professional-Voice-Clone-of-someone-else-s-voice

> Even with their consent, you cannot clone someone else’s voice.

PVCは本人アカウントで本人が確認・作成し、必要ならprivate sharing linkで共有する方式。教員が高校生10人の声をPVCとして一括登録する設計は不可。Instant Voice Cloningについても未成年の入力禁止は適用される。

### ログイン・席・APIの違い

- 単一個人ログインを参加者へ貸与：規約で禁止。
- Scale/Businessのworkspace席：公式のチーム席。ただし席を買っても年齢・未成年声入力禁止は変わらない。教員1人＋参加者10人なら10席では11人を収容しない。
- 教員だけがAPIを扱う集中運用：credential貸与とは別。ただし未成年向け体験の書面承認、未成年声入力禁止はAPIにも及ぶ。安価なAPIプランなら回避できるという解釈はしない。サービス別条件は https://elevenlabs.io/service-specific-terms から適用される。

## Suno

公式料金：https://suno.com/pricing 。初期表示は年払い。月払い額は同ページ内の公式`monthly_price_usd`・`annual_price_usd`を確認し、`raw-audio-cost/suno-plan-data-excerpts.txt`へ保存。

| プラン | 月払い | 年払い月換算／年総額 | credits | ダウンロード枠 | 商用 |
| --- | --- | --- | --- | --- | --- |
| Free | $0 | $0 | 50/日 | 現行ページはNo monthly song downloads | 不可 |
| Pro | $10 | $8／$96 | 2,500/月 | 20曲/月 | 対象出力で可 |
| Premier | $30 | $24／$288 | 10,000/月 | 60曲/月 | 対象出力で可 |

年契約$8を単月$8で買えるとは扱わない。現行公開ページには生成creditsとdownload枠が別記され、追加credit/download購入可だが追加downloadの単価は未確認。

公式プラン説明：https://help.suno.com/en/articles/2410049 は50creditsで10songs、Pro2,500、Premier10,000と説明。ただしモデル・機能ごとの消費は変動しうるため、10〜20秒なら必ず何creditsと断定しない。

### 10人×2〜3試行の概算

音楽の候補数を1人2〜3曲＝全20〜30曲と仮定すると、上記ヘルプの単純比率では100〜150credits相当（**試行が常に1曲だけを返すと保証しない**）。Proの2,500creditsは候補数の目安を十分上回るが、ダウンロード枠は別に確認する必要がある。

- 最終採用曲10曲だけを正規ダウンロード：Proの20曲枠内。個人用の単月プラン価格基準は$10、10人あたり単純按分$1。ただし学校での集中利用可否は未確定で、確定見積ではない。
- 20候補をすべてダウンロード：Proの20曲枠と一致。
- 30候補をすべてダウンロード：Pro20曲枠を超える。Premier60曲枠なら収まる。単月$30、単純按分$3。
- 参加者各自がProを契約：10×$10＝$100/月。個別アカウント・保護者同意・各人の商用権取得を設計する方式で、学校1契約共有とは異なる。
- 学校の法人契約・複数席：公開標準席単価は未確認。sales見積対象。上記$10/$30を学校10席の価格と表示しない。

### 年齢・同意・商用・組織

公式規約：https://suno.com/terms

> You must be at least 13 years old to use the Service.

> if you are under 18 years old, you may use the Service only with the express consent of your parent or guardian

会社等を代表して契約する権限を求め、さらに次を明記：

> If you are an enterprise user, you must contact sales to use our Service

個人ログインを10人に配布できるという許諾は確認できない。パスワード・account detailsの秘密保持と全活動への責任を規定。学校というだけで標準Pro1契約を共有できるとは判断しない。公開の公式API料金/教育席ライセンスも今回未確認。第三者の「Suno API」価格は利用しない。

商用利用は有料期間に生成し権利を得た曲について、正規の承認済みチャネルで契約枠内ダウンロードした出力を使う必要がある：

> You may not commercially exploit Output that has not been downloaded by you through an approved channel under these Terms of Service.

無料版生成曲はpersonal/non-commercial。後からProへ入っても過去無料曲へ自動で商用権が付くとは扱わない。学校の集客・SNS広告に出すMVを「授業だから非商用」と自動判断しない。公式ヘルプは有料期間生成曲の商用権が解約後も継続すると説明：https://help.suno.com/en/articles/2416769 。現行規約でユーザー同士のRemixは有料プランでもpersonal/non-commercialという固有制限があるため、他人曲Remixを自校広告用の新曲生成と同一視しない。純粋AI出力への著作権成立はSunoが保証しない。

SunoのVoice Model機能は本人自身の声のみ。会社教員アカウントに生徒の声を入れてVoice Modelを作る案は規約の本人声制約に合わない。今回の音楽案は本人声学習なしの新規BGM生成と、別途ローカル録音の合成を分ける。

## 推奨する予算上の整理

声は本人録音を動画編集へ直載せし、クローン費$0。音楽は学校としての利用条件を確認したうえで、最終10曲だけをダウンロードする運用ならSuno Proの容量が基準候補、30候補すべて持帰りならPremierまたは追加download枠を比較する。**価格が容量内でも学校利用の許諾完了を意味しない。** API集中運用・法人席・個人契約・ログイン貸与を別欄にして見積もる。

原文HTML・テキスト・SHAは`audio-cost-sources.json`および`raw-audio-cost/`。公式本文の明記がない事項は不明として残した。
