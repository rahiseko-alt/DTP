# 無料ローカル構成で本人分身MVはどこまで作れるか

公式公開資料確認：2026-10-16。調査のみ。重いソフトの導入・キャラ生成・本人写真利用・有料API・購入は行っていない。

## 結論

**無料の複数工程なら、本人に似せた3D分身が飛び、本人の録音声と音楽が流れるMP4を作る構成は可能。** VRoid Studioで手作業の分身作成→VRM出力→Blender等で事前作成した飛行シーンに配置→本人録音とBGMを合成する。ソフトと生成従量費を0円にできるが、PC・準備・指導・レンダリングの費用と時間は残る。

これは**「写真1枚で本人を自動再現し、AIが飛行動画と本人歌声と音楽を全部生成する」無料サービスと同じではない。** 写真からリアル本人を再現する機能は今回のVRoid/Blender公式根拠から確認できない。無料クラウド1サービス完結の可否は本稿の調査対象外であり、完結サービスが見つかったとは報告しない。

## できる／不可／設定必要／未検証

| 要件 | 判定 | 実際の方法と限界 |
| --- | --- | --- |
| 分身作成 | できる・本人似は要手調整 | VRoidの髪・目・顔・体型・服を本人が選んで似せる。主にアニメ調3D。自動顔認識・リアル本人写真再現の実証なし。 |
| 空を飛ぶ等の全身動作 | 設定必要 | Blenderで全身を動かすキーフレーム・カメラ・背景を教員が事前作成しモデルを差し替える。VRoid単体のキャラ作成と飛行MV制作を同一機能としない。 |
| 本人の声 | できる | 本人が録音した声をそのまま合成。声学習・クローン・生成音声は不要。口パク同期は別設定で未検証。 |
| 本人の歌声 | 条件付き | 本人が歌って録音した音源を入れることと、AIに本人声で歌わせることは別。後者はこの構成ではできない。 |
| BGM | できる・権利設定必要 | 自作・利用許諾済み音楽なら合成可。AI音楽生成はVRoid/Blender/ffmpegの機能ではなく別工程。無料AI音楽の学校利用や配布許可を本稿は確認していない。 |
| MP4保存 | できる | Blenderのレンダー、またはffmpegでH.264/AAC MP4化。ffmpegの合成・出力形式だけは前日ダミー検証済み。 |
| 無料・10人分 | ソフト代は可能、当日完了未検証 | クラウドcredit枠ではなく端末/レンダー性能が制約。全員が当日一からBlenderを操作するのは別の負荷。10台へ事前準備し教員側でシーン処理する想定。 |
| 透かしなし | 出力工程では可能 | 自作のBlender/ffmpeg出力へ自動サービス透かしを入れる必要はない。ダミーは誤認防止で明示labelを付けている。第三者モデルのcredit義務は別。VRoid完成動画自体は未出力。 |
| 高校生 | 条件確認必要 | pixiv共通規約の未成年は保護者等の同意を要求。VRoid個別規約・利用方法との適合、学校の同意運用を準備。学校共有IDを10人に配る設計にはしない。 |
| 学校・商用利用 | 公式許容、資産ごと確認 | VRoid公式は法人商用・教育利用を明記。Blender公式も商用・学校利用可。追加衣装・第三者モデル・モーション・曲のライセンスは別。 |
| OC60分完成 | 未検証 | 分身調整15〜20分、教員側シーン差替え・出力、録音・合成、保存という配分は企画案。10人分のVRM取込・レンダー・保存時間の実測が必要。 |

## 公式根拠

### VRoid Studio（公式・本文200取得）

https://vroid.com/en/studio

> “VRoid Studio is free to use for anyone.”

> “Every model is exportable as VRM files and uploadable to apps that support the format.”

公式は顔・体等のパラメータ調整とテクスチャ編集を説明。Windows/macOS/iPadが掲載され、今回のLinuxクラウドでそのままGUI実行できるとは扱わない。要求仕様にはメモリ8GB、ストレージ10GB等の記載があり、会場の実端末で確認する。

https://vroid.com/en/studio/guidelines

> “Any individual or corporation may sell or use for commercial purposes any mesh, texture, or preset item provided by VRoid Studio ... provided that no special clauses are indicated in the license.”

> “You can edit and use the model data exported from VRoid Studio using software other than VRoid Studio.”

> “Instructors or students can use it for educational purposes at an educational institution.”

同ページはモデルの画像・動画を収益化する利用例を明記。一方で他者作成の素材はそのライセンスに従うと説明。無料で拾った衣装やモデルが学校広告・作品配布に自由とは限らない。

https://vroid.pixiv.help/hc/en-us/articles/4405597663385

公式Getting Started：VRoid Studioはhumanoid 3D avatarsを作るアプリ。モデルをVRMで書き出す案内あり。

https://policies.pixiv.net/en.html

共通規約は未成年等について法定代理人の同意を求める。今回取得した本文の該当表現：

> “such person must obtain the consent of a person with parental authority, guardian, or other legal representative”

同ページ内に“VRoid Studio” Terms of Useあり。無料ソフトを使うから規約・保護者同意・個別素材条件が消えるわけではない。VRoid Hubへの公開はローカル制作と分け、必須にしない。

### Blender（公式・本文200取得）

https://www.blender.org/about/license/

> “You are free to use Blender, for any purpose”

> “Blender can be used commercially ... and by students in educational institutions.”

https://docs.blender.org/manual/en/latest/getting_started/about/license.html

GPLはソフトウェアを対象とし、制作したartworkとは区別する説明あり。作品をすべてGPL公開しなければならないという意味ではない。

https://docs.blender.org/manual/en/latest/animation/introduction.html

> “Animation is typically achieved with the use of keyframes.”

https://docs.blender.org/manual/en/latest/render/output/properties/output.html

動画エンコード・出力経路とFFmpeg設定を説明。自動AI動画生成ではなく、自分で用意したシーンのアニメーションとレンダリング。

### VRMのライセンスと取込

https://vrm.dev/en/licenses/1.0/

VRM PUBLIC LICENSE 1.0は、モデルのlicense settingsに従う権利を付与。商用、avatar use、改変、再配布等を区別する。**MP4の持ち帰りとVRMモデルデータの配布は別**。自作モデルでも素材条件を引き継ぐ必要がある。

https://vrm-addon-for-blender.info/

VRM Add-on for Blenderの配布元サイトは200到達。ただし本文がJS主体で詳細設定を十分確認できず、今回addonの導入・VRoidの現行VRM取込互換性は未検証。組合せの本番採用前に実際のBlender/addon/VRMバージョンを揃える。

### 声・BGM・合成

https://ffmpeg.org/ffmpeg-filters.html

`amix` は “Mixes multiple audio inputs into a single output.” 声とBGMを混ぜる機能であり、声の複製でも音楽生成でもない。既存 [pilot](../oc-avatar-20261015/pilot/README.md) は図形とテスト音で15秒MP4を検証。本人声とVRoidの全工程は未実証。

## OCとしての現実案

最初は学校が「飛行」1シーン・カメラ・照明・BGM・出力設定を事前準備し、参加者は自分の分身の髪/顔/服を選び、本人のひと言を録音する。担当者がモデルをシーンへ差し替え、MP4を書き出して本人端末で再生する。参加者がBlenderのリギングや全身アニメーションをゼロから作る内容にはしない。

工程ごとのソフト費・従量費0円は狙える。しかし生成AI体験と呼ぶなら、どの工程をAIが担当するかを別に確定する必要がある。このローカル案だけを「AIが自分を自動生成して飛ばす」と宣伝しない。10人が完成品を持ち帰る所要時間は、1人→10人負荷のpilotが済むまで確約しない。
