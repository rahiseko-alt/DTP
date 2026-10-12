# 編集長視点：全件評価

14ファイル全文、実SHA確認。2対が完全同一で、異なる本文は12。技術README5件は対象外。支持数での選別なし。

## 結論

中心候補は Impeccable Critique。紙面構成の判定補助は Impeccable Layout、方向照合は Anthropic Frontend Design。Visual Storytellerは内容編集の補助として有益だが、編集長の差戻しと審査統合を具体化しておらず中心推薦を撤回。

原文を勝手に改変した案ではなく、適用候補の評価。原本の人物写真・図・文字の関係や内容の十分性を比較し、薄い誌面を止める印刷編集長プロンプトは収集内に完成形として存在しない。

## 全件と根拠

### additional/voltagent-ui-designer.md

補助のみ：文脈取得と引継ぎは明示するが、品質審査は項目列挙で誌面の差戻し基準にならない。

読了 174行、SHA `60b69fc6d3da170b5570b29332d6000ee8f26f4b1df4e9bc680a44f57a37478c`。

根拠 L14：Always begin by requesting design context from the context-manager. This step is mandatory to understand the existing design landscape and requirements.

### critique/impeccable-bolder.md

局所修正用：既存世界の強い表現・密度・ペースを使う指示は有益。全冊の判定や独立審査の責任は持たない。

読了 33行、SHA `a4e4d986f74ef5f3c8218dfcfd5b04fe103b47182cf1e16aeb979e5703d5cd87`。

根拠 L13：A section usually reads flat for reasons its neighbors have already solved. Look at what the rest of the page does that this section does not: the display type at full strength, the structural devices that carry meaning, the signature motif, the density and pacing. A flat section is typically one that quietly opts out of the system's own strongest moves. The most reliable bolder pass brings the target up to the expressive level its neighbors already reach, in the system's own vocabulary rather than a new one.

### critique/impeccable-critique.md

推奨1：編集長の審査統合：独立した見た目評価と機械証拠を隔離し、原本と文脈を持たせ、単なる連結ではなく統合する。追認問題への最も具体的な対策。Web操作・Nielsen得点だけでは誌面充実度を止められないため、そのまま編集長として採用不可。

読了 841行、SHA `8d2cdf4f583a0caf7685620069069354b4fb81582fb63c349783298454140a0e`。

根拠 L33：Delegate Assessment A and Assessment B to separate sub-agents. They must not see each other's output. Do not show findings to the user until synthesis.

### critique/impeccable-distill.md

中心にしない：必要情報を消すなとはあるが、短文化と大きな余白・単純線形配置へ強く誘導する。今回の雑誌紙面で一括適用は不適合。

読了 111行、SHA `048e5a7671024592cba6cd4ede70b6c535db0c1be84d6837638e40f51fb3fad7`。

根拠 L63：- **Generous white space**: Let content breathe, don't pack everything tight

### critique/impeccable-layout.md

推奨2：紙面構成の判定：主従・近接・疎密・内容と構造の対応・密度を質問ごとに証拠で答える指示。技術検査が階層やリズムを証明しないことを明示。固定の空白増量を求めない。冊子見開き・HAL比較・提出拒否権は追加の適用契約が必要。

読了 84行、SHA `14ba132b6168bf0a7498f8c3fbbb41b73ff704da5dc3688fd842807446e54a05`。

根拠 L31：Also inspect arbitrary spacing, overflow, stacking, and container behavior the detector cannot resolve. Keep mechanical evidence out of the first assessment, then synthesize both passes before editing. A clean scan cannot prove hierarchy or rhythm.

### critique/taste-SKILL.md

部分参考／一括採用不可：依頼・既存素材・既存密度を起点にする改修手順と原文チェックは有益。しかし低密度既定、内容制限、生成画像優先、架空データを自然な数へ変える指示が同居し、冊子用に丸ごと採用すべきでない。

読了 1228行、SHA `2136ed83016bfada39f7b8013b2aafd9f78fcbd9799110ed222a79c6419ba5fb`。

根拠 L640：* **NO fake-perfect numbers.** Avoid `99.99%`, `50%`, `1234567`. Use organic, messy data (`47.2%`, `+1 (312) 847-1928`).

### critique/taste-redesign-SKILL.md

一括採用不可：重なり・弱い見出し・空虚な面の検出は具体的。ただし余白倍増・架空値を自然な値にする指示が今回の指示と衝突。

読了 181行、SHA `a75d547d04595fe97a5d377dddf145d029d51487a4f2a0a5a9d3b532ca3b84cd`。

根拠 L58：- **Missing whitespace.** Double the spacing. Let the design breathe. Dense layouts work for data dashboards, not for marketing pages.

### editorial/agency-brand-guardian.md

補助：ブランド整合：ブランド遵守監査と是正は責務として明示されるが、誌面密度・写真選定・原本比較・独立審査統合は具体化されない。ブランド全体系再構築は今回過大。

読了 322行、SHA `d1d5c78af85d4d35be94b93d5c011d17e3cf5dcb69b2037a3ebf3059803b893e`。

根拠 L30：- Audit brand compliance and provide corrective guidance

### editorial/agency-image-prompt-engineer.md

部品担当用：参照の構図・光・主役の分解が具体的。誌面編集の合否判定、情報配分、全冊連続性を担当しない。

読了 236行、SHA `63a564d01dc5812c494cd8aa034ce1217031d8fe8b3eca1323316879769ff13f`。

根拠 L146：- Analyze visual references for lighting, composition, and style elements

### editorial/agency-ui-designer.md

UI用途／編集長にしない：トークン・コンポーネント・状態・開発引継ぎ中心。視覚階層は述べるが、今回の冊子を止める審査手順は弱い。

読了 383行、SHA `3130768958d3b3d38178aaec91cf789e01ecca4984c8674d4aaea446b6cba240`。

根拠 L43：- Establish component foundations before creating individual screens

### editorial/agency-visual-storyteller.md

補助：全冊の内容編集：写真ディレクション、物語展開、視覚ペース、情報階層は冊子編集に有益。しかし判定・差戻し・独立レビュー統合が具体的でなく、これを編集長の中心とする前提は撤回。

読了 149行、SHA `f4950c9d65b5d105ec48ebce4b7621154e3bf89871dbbf07af245476930eb4dd`。

根拠 L55：- **Visual Pacing**: Rhythm and timing of visual elements for optimal engagement

### production/anthropic-frontend-design.md

推奨3：方向照合：依頼優先、実内容、制作前計画照合と現物自己批評が具体的。quiet/cutを空白増量と読み替えてはいけない。独立レビュー・差戻し責任は別途必要。

読了 71行、SHA `d91970639e9f5c37682ac7ab60094d35f1c7c1f38d731bd56396563aee10c1d3`。

根拠 L45：All traits are legitimate for some briefs, but they are defaults rather than choices, and they appear regardless of subject. Where the brief pins down a visual direction, follow it exactly — the brief's own words always win, including when it asks for one of these looks. Where it leaves an axis free, don't spend that freedom on one of these defaults. As with a hired human designer, there's often a careful balance between doing what you're good at and taking each project as a chance to experiment and learn.

### production/taste-redesign.md

一括採用不可：重なり・弱い見出し・空虚な面の検出は具体的。ただし余白倍増・架空値を自然な値にする指示が今回の指示と衝突。

読了 181行、SHA `a75d547d04595fe97a5d377dddf145d029d51487a4f2a0a5a9d3b532ca3b84cd`。同一本文：critique/taste-redesign-SKILL.md。

根拠 L58：- **Missing whitespace.** Double the spacing. Let the design breathe. Dense layouts work for data dashboards, not for marketing pages.

### production/taste-v2.md

部分参考／一括採用不可：依頼・既存素材・既存密度を起点にする改修手順と原文チェックは有益。しかし低密度既定、内容制限、生成画像優先、架空データを自然な数へ変える指示が同居し、冊子用に丸ごと採用すべきでない。

読了 1228行、SHA `2136ed83016bfada39f7b8013b2aafd9f78fcbd9799110ed222a79c6419ba5fb`。同一本文：critique/taste-SKILL.md。

根拠 L640：* **NO fake-perfect numbers.** Avoid `99.99%`, `50%`, `1234567`. Use organic, messy data (`47.2%`, `+1 (312) 847-1928`).
