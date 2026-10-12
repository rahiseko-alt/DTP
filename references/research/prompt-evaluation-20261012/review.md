# 全候補評価：独立レビュアー視点

指示原文14ファイル/内容12種。除外済技術5件、README5件は候補外。支持数不使用。

結論：主軸は **Impeccable Layout**、審査の独立性と報告は **Impeccable Critique**。Visual Storytellerは編集担当向けであり審査主軸にしない。Taste Redesignを丸ごと適用してはならない。

## additional/voltagent-ui-designer.md

全文読了。SHA256: 60b69fc6d3da170b5570b29332d6000ee8f26f4b1df4e9bc680a44f57a37478c

評価：低

有益：文脈取得・自己審査・他者審査の分離がある。

衝突・不足：文脈managerへの依存、Web部品・動作・暗色に偏る。具体的な誌面差戻し条件がない。

根拠：
- L14: `Always begin by requesting design context from the context-manager.`
- L84: `Design critique process:`

## critique/impeccable-bolder.md

全文読了。SHA256: a4e4d986f74ef5f3c8218dfcfd5b04fe103b47182cf1e16aeb979e5703d5cd87

評価：補助

有益：参照世界内で強い表現を使い、密度とペースを比較し、内容を真実のまま守る。

衝突・不足：制作修正命令であり独立審査役ではない。主役周りを静かにすることを空白増大に誤用し得る。

根拠：
- L13: `the signature motif, the density and pacing.`
- L18: `Keep content true.`
- L24: `Strip the copy out of your planned section and study the bare structure.`

## critique/impeccable-critique.md

全文読了。SHA256: 8d2cdf4f583a0caf7685620069069354b4fb81582fb63c349783298454140a0e

評価：強い補助

有益：別文脈で視覚批評と技術証拠を独立取得し、技術結果で批評を誘導しない。曖昧な称賛を防ぎ具体的問題/影響/修正を出す。

衝突・不足：WebのNielsen操作評価が主、密度不足の詳細な問いはLayoutより弱い。最高点minimalの語を空白増加へ短絡しない。必須質問・専用detectorなどは既存DTP運用へそのまま導入できない。

根拠：
- L10: `Assessment A must finish before detector findings enter the parent synthesis context.`
- L59: `could an unrelated product use it unchanged?`
- L164: `For each issue, tag with **P0-P3 severity**`
- L205: `Don't soften criticism.`

## critique/impeccable-distill.md

全文読了。SHA256: 048e5a7671024592cba6cd4ede70b6c535db0c1be84d6837638e40f51fb3fad7

評価：今回の主役に不適

有益：必要な意思決定情報を消さない禁止がある。

衝突・不足：削除・単純化が目的。余白増加/コピー半減/単列化を今回の薄い紙面に処方するのは逆。

根拠：
- L63: `Generous white space`
- L73: `Cut every sentence in half, then do it again`
- L90: `Remove information users need to make decisions`

## critique/impeccable-layout.md

全文読了。SHA256: 14ba132b6168bf0a7498f8c3fbbb41b73ff704da5dc3688fd842807446e54a05

評価：最優先

有益：全問を現物/ソース証拠付きで答える。主従、意味のまとまり、疎密のリズム、内容に合う構造、情報密度を直接検査。技術検査が階層/リズムを証明しないと明記。

衝突・不足：Web状態/端末検査・専用detector・編集命令を含む。HAL原本との比較・事実正本照合・差戻し基準は別途必要。

根拠：
- L18: `Apply the squint test.`
- L20: `Do tight and generous intervals create a deliberate cadence`
- L22: `Does the amount of information per region fit`
- L31: `A clean scan cannot prove hierarchy or rhythm.`
- L72: `Do not substitute a bare “yes” for verification.`

## critique/taste-SKILL.md

全文読了。SHA256: 2136ed83016bfada39f7b8013b2aafd9f78fcbd9799110ed222a79c6419ba5fb

評価：限定補助

有益：同型反復・空欄タイル・視覚素材不足・無意味ラベルを具体検出。読者と原本/既存資産を出発点とする。

衝突・不足：editorial低密度既定、generous whitespace、余白増加、巨大文字や重ねラベル禁止がHAL構成に衝突する。架空精密数禁止とmessy data指示が内部不整合。長大Web規則を丸ごと入れない。

根拠：
- L22: `these are starting material, not optional input`
- L250: `A bento grid has EXACTLY as many cells as you have content for.`
- L274: `A pure-text page is not minimalism. It is incomplete work.`
- L330: `Don't fake engineering precision the brand doesn't claim.`
- L640: `Use organic, messy data`
- L836: `increase section padding`

## critique/taste-redesign-SKILL.md

全文読了。SHA256: a75d547d04595fe97a5d377dddf145d029d51487a4f2a0a5a9d3b532ca3b84cd

評価：丸ごと適用不可

有益：重なり不足、主見出しの弱さ、平板な領域を具体指摘する。

衝突・不足：余白を倍増・最大化し、数値をmessy dataへ置き換え、日付をランダム化する指示が今回の指定と正本事実に直接衝突。

根拠：
- L54: `No overlap or depth.`
- L58: `Double the spacing.`
- L82: `Use organic, messy data`
- L88: `Randomize dates to appear real.`
- L146: `Whitespace maximization.`

## editorial/agency-brand-guardian.md

全文読了。SHA256: d1d5c78af85d4d35be94b93d5c011d17e3cf5dcb69b2037a3ebf3059803b893e

評価：限定補助

有益：一貫性と文脈に応じた柔軟性、監査と是正責任がある。

衝突・不足：ブランド策定/法律/商標が主。HALは他校の参照であり自校ブランドと同一視不可。現物審査手順が抽象的。

根拠：
- L30: `Audit brand compliance and provide corrective guidance`
- L47: `Balance consistency with flexibility for different contexts and applications`

## editorial/agency-image-prompt-engineer.md

全文読了。SHA256: 63a564d01dc5812c494cd8aa034ce1217031d8fe8b3eca1323316879769ff13f

評価：パーツ用

有益：参照の構図・主役・光を具体分解し、画像部品の仕様にできる。

衝突・不足：誌面完成度・全体密度・正本事実・合否を審査する役ではない。実写真を生成写真へ置換する理由にもならない。

根拠：
- L45: `Consider aspect ratio and composition in every prompt`
- L146: `Analyze visual references for lighting, composition, and style elements`

## editorial/agency-ui-designer.md

全文読了。SHA256: 3130768958d3b3d38178aaec91cf789e01ecca4984c8674d4aaea446b6cba240

評価：低

有益：階層と画像仕様、実装正確性QAを担当できる。

衝突・不足：UI部品一貫性が中核で誌面反復を正当化し得る。専門的な判断をcore trainingへ委ね、原本比較/疎密判定が弱い。

根拠：
- L37: `Establish design QA processes for implementation accuracy validation`
- L246: `consistent mathematical ratios`
- L383: `Your detailed design methodology is in your core training`

## editorial/agency-visual-storyteller.md

全文読了。SHA256: f4950c9d65b5d105ec48ebce4b7621154e3bf89871dbbf07af245476930eb4dd

評価：編集用の補助

有益：写真ディレクション・ページを通す視覚リズム・情報階層を組み立てる責務がある。

衝突・不足：独立批評/具体的な差戻し/密度不足検査がない。物語を作る担当が自分の物語を承認しない。測定未実施の成功数字は合格理由不可。

根拠：
- L30: `Provide photography art direction`
- L55: `Visual Pacing: Rhythm and timing of visual elements`
- L64: `visual hierarchy, narrative flow`

## production/anthropic-frontend-design.md

全文読了。SHA256: d91970639e9f5c37682ac7ab60094d35f1c7c1f38d731bd56396563aee10c1d3

評価：制作と依頼照合用の補助

有益：指定原本がAI臭さ禁止より優先すると明記。制作前計画の依頼照合、スクリーンショット批評。

衝突・不足：Web制作指示で独立審査の合否契約ではない。一か所だけ大胆/周囲を静かにする指示を紙面全体の空白増へ解釈しない。

根拠：
- L45: `the brief's own words always win`
- L53: `review that plan against the brief before building`
- L59: `taking screenshots to review`

## production/taste-redesign.md

全文読了（重複は全文読了済み原文とバイト一致検証）。SHA256: a75d547d04595fe97a5d377dddf145d029d51487a4f2a0a5a9d3b532ca3b84cd

評価：丸ごと適用不可

有益：重なり不足、主見出しの弱さ、平板な領域を具体指摘する。

衝突・不足：余白を倍増・最大化し、数値をmessy dataへ置き換え、日付をランダム化する指示が今回の指定と正本事実に直接衝突。

根拠：
- L54: `No overlap or depth.`
- L58: `Double the spacing.`
- L82: `Use organic, messy data`
- L88: `Randomize dates to appear real.`
- L146: `Whitespace maximization.`

## production/taste-v2.md

全文読了（重複は全文読了済み原文とバイト一致検証）。SHA256: 2136ed83016bfada39f7b8013b2aafd9f78fcbd9799110ed222a79c6419ba5fb

評価：限定補助

有益：同型反復・空欄タイル・視覚素材不足・無意味ラベルを具体検出。読者と原本/既存資産を出発点とする。

衝突・不足：editorial低密度既定、generous whitespace、余白増加、巨大文字や重ねラベル禁止がHAL構成に衝突する。架空精密数禁止とmessy data指示が内部不整合。長大Web規則を丸ごと入れない。

根拠：
- L22: `these are starting material, not optional input`
- L250: `A bento grid has EXACTLY as many cells as you have content for.`
- L274: `A pure-text page is not minimalism. It is incomplete work.`
- L330: `Don't fake engineering precision the brand doesn't claim.`
- L640: `Use organic, messy data`
- L836: `increase section padding`

## 全原文に不足している今回の審査契約

- HAL原本の該当面と制作見開きを同サイズで比較し、主役、情報まとまり、密度、疎密、文字の主従、重なりの違いを記述する。これは原文にはない今回必要な補足であり原文引用と区別する。
- 空白の目的を主役強調/読線/群分離として説明できるか、参照の内容を失って薄くしていないかを証拠付きで判定。架空の占有率や余白倍率を作らない。
- 主張/料金/年度/人数/資格/人物属性を正本資料へ照合し、根拠のない事実を差戻す。
- 制作説明・技術pass・他役合意を現物評価の代用にせず、依頼必須条件未達をmajorとして差戻す。
