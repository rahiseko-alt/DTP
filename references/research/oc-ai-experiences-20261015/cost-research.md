# Avatar OC：10名の料金・組織利用調査

公式取得日2026-10-15。USD、円は**1 USD=150円の試算仮定**。為替の実勢値ではない。税・決済手数料・開発・編集・スタッフ費を含まない。購入・契約・実装・生成テストは未実施。

## 推奨：学校管理API＋本人声の録音合成

10名がそれぞれ10〜20秒の本人分身MVを作る。動画を1人最大3回生成する予算で、20秒×3×10人=600生成秒。短い生成カットを結合する前提で、20秒の単発生成可否とは分ける。

| 内訳 | 公式単価と試算 |
| --- | --- |
| Runway Gen-4 Turbo動画 | 5credit/秒、1credit=$0.01→$0.05/秒。600秒=$30=4,500円、1名450円 |
| Runway Gen-4.5動画 | 12credit/秒→600秒=$72=10,800円、1名1,080円 |
| 分身画像の例 | Gen-4 Image 1080p=8credit/枚=$0.08。4候補×10人=$3.20=480円。参照本人画像の同一性保持は性能未検証 |
| 本人声 | 新規録音をローカル編集で動画へ載せるなら声AI料金0。歌唱クローン/リップシンクとは別 |
| 音楽 | 別途。Runway seed_audioは0.25credit/秒・最低5creditだが、望むBGM生成と配布ライセンスへの適合未確認のため音楽総額を確定しない。Suno/ElevenLabs等はaudio-cost.md参照 |

10秒×2試行×10人=200秒ならTurbo $10、20秒×3なら$30。20秒を全員もう1回作り直すごとにTurbo $10、Gen-4.5 $24追加。画像/音楽込みの初期生成費予算は**1回10名で約5,000〜15,000円の仮枠**。上限保証・納品保証ではない。

公式：https://docs.dev.runwayml.com/guides/pricing/

引用：『Credits can be purchased for $0.01 per credit』『gen4_turbo 5 credits per second』『gen4.5 12 credits per second』。税が加算される場合あり。Webの月額creditとAPI請求を同じ財布と仮定しない。API自動補充は最低1000credit/$10、https://docs.dev.runwayml.com/usage/autobilling/ 。APIcredit有効期限・通常手動購入の最低額はこの調査では未確定。

## 会社アカウントで複数人：3方式の区別

| 方式 | 判定と費用 |
| --- | --- |
| 会社の単一ログイン/パスワード/APIキーを10人へ貸す | **不可**。Runway規約2.1『You may not share your Account, password, or API keys with anyone』 |
| Runway法人Teamの各自席 | 2〜9人、$69/席/月。年払い月換算$55（年契約）。最低2席=$138/月=20,700円、1席6900credit/月を共有、24並列生成。10人全員各自ログインは9席超のためEnterprise見積り。10×69と断定不可 |
| 学校管理APIを専用画面から使う | APIを自社アプリへ組込みend usersへ提供する規約上の方式あり。キーをサーバー保持し、参加者へ配らない。生成従量費＋専用画面の開発/運用費。未成年/本人素材条件とEULA等を満たす必要がある |

法人公式：https://runwayml.com/team-plan 。引用『groups of two to nine people』『$69 a month, or $55 a month billed yearly』『Each seat adds 6,900 credits a month』。月creditは1か月繰越、追加購入creditは期限なしと記載。教員2名が各自席で操作するなら2席の案だが、参加者にログインを渡す案ではない。

API規約：https://runwayml.com/terms-of-use/ §1.1/2.5。自社アプリへ統合しend usersに機能提供可、適切なEULAと規約準拠が必要。API projectに職員を招待するrolesも公式に存在：https://docs.dev.runwayml.com/usage/organizations-and-roles/ 。課金管理権限とAPIキー権限を分ける。

## 年齢・本人素材・待ち時間

- Runway §2.2は13歳以上、18歳未満は親/保護者許可を要求。13歳以上という一般条件から、未成年本人のリアル顔を特定モデルへ入力できると一律に断定しない。モデル固有条件と許諾をpilot前に確認する。
- Runway Usage Policy https://runwayml.com/coc は他人の画像/動画/音声の無許可使用を禁止し、子どもの有害/危険行為表現を禁止、子どもの表現には厳しい基準と記載。幻想的な『空を飛ぶ』が希望どおり通るかは一般年齢条件だけでは保証できず、2D/リアルの各モデルで企画適合を確認する。
- API同時実行はTier依存。https://docs.dev.runwayml.com/usage/tiers/ は初期Tierの制限と$50購入後Tier2等を掲載するが、モデル別表の値を実アカウントで確認して使う。10名同時に即完了とは約束せず、キューで順番処理。実待ち時間は未検証。
- ElevenLabsは現行18歳以上、未成年録音によるvoice model作成を禁止。教員代行で回避できない。本人声は録音そのまま合成を優先。
- Google Gemini APIは18歳以上/未成年向けclient制限、Vertex画像→動画は成人人物のみの設定があり、安価でも高校生本人顔企画の適合を推測しない。Sora旧APIは終了案内があり現役候補に使わない。詳細video-api-cost.md。
- 音楽は生成費と商用/ダウンロード/動画への組込・配布権を別確認。『有料なら何でも学校配布可』とはしない。

## 固定費の判断

初回は学校API方式の小規模pilotで、本人分身・非日常動作・録音合成・短いBGM・ダウンロードまで確認するのが費用面で有力。学校専用画面を作らない運用なら、教員が個別席で操作する法人Teamの最低月$138が比較対象。どちらも契約条件とモデル適合確認前の購入指示ではない。

根拠原文：raw-runway-cost/、runway-cost-sources.json。音声/音楽はaudio-cost.mdとsources、API代替はvideo-api-cost.mdとsources。生成性能・本人同一性・音楽適合・実待ち時間・保存方法は未検証。
