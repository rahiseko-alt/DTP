# 全14指示原文の比較：パーツ担当

14指示原文の全文を読了。長文は行範囲で分割、重複2対はSHAとバイト同一を確認。支持指標を評価に使わない。原文は変更しない。

## 結論

パーツ用途ではImage Prompt Engineerが主候補。ただし今回の最大問題の紙面密度をパーツだけで直せない。主役・脇役・密度・疎密を具体化するImpeccable Layoutと、素材に役目を求めるBolderの方が全体制作の欠陥には直接効く。

## 全件比較

| 原文 | 判断 | 理由 |
|---|---|---|
| additional/voltagent-ui-designer.md | 補助 | 仕様と素材引継ぎを担当する指示は有益。UIの状態/操作/性能が中心で、人物切抜き・写真ディレクション・冊子密度は具体化していない。 |
| critique/impeccable-bolder.md | 推奨補助 | 既存の視覚世界の強い表現を増幅し、素材には役目と証拠を求める。空白を画像で埋めるだけにしない、素材だけで全冊を変更しない責務境界に有効。 |
| critique/impeccable-critique.md | 審査へ | 意匠判断と機械検査を独立させ、具体的問題/理由/修正を返す。制作素材の具体仕様はない。パーツ担当の主プロンプトより独立審査向け。 |
| critique/impeccable-distill.md | 今回の主軸には不適 | 情報・装飾を削減する指示。必要情報を消さない保護条項はあるが、今回の薄い紙面を増強する素材設計の主軸にはならない。 |
| critique/impeccable-layout.md | 推奨補助 | 主役と脇役、意図した密度、詰まった間隔と広い間隔のリズムを制作前に決める。パーツの寸法・役目の受注条件と審査に有効。 |
| critique/taste-SKILL.md | 部分的に有益/原文一括採用不可 | 実画像を要求し、反復構図を点検する。生成優先、写真上のラベル禁止、雑誌=余白広めという既定値、架空の端数推奨が今回の実写真・文字重なり・密度・事実に衝突。 |
| critique/taste-redesign-SKILL.md | 部分的に有益/原文一括採用不可 | 重なりや奥行き、実写真の採用、空白だけの面の不完成を指摘する。ただし余白倍増、端数データへの置換、架空名・日付の変更の指示が実冊子に危険。 |
| editorial/agency-brand-guardian.md | 補助 | 素材ライブラリ、ロゴ使用規則、ブランド一貫性を整える。ブランド再設計・監視まで拡張するため、今回の限定パーツ制作役を超える。 |
| editorial/agency-image-prompt-engineer.md | パーツ主候補 | 参照分解、主役の位置/大きさ/背景との関係、構図/縦横比/照明を具体的な生成指示へ落とす。候補中で素材の指示手順が最も具体的。実写真選定・透明切抜き・文字を載せる領域・生成と実在の区別・印刷解像度の実測は別途不足。 |
| editorial/agency-ui-designer.md | 補助 | 精密な仕様と複数形式の素材供給を明示。UI部品の再利用・数学的間隔が中心で、誌面の非均一な写真と文字の構成を担当する原文ではない。 |
| editorial/agency-visual-storyteller.md | 写真方針の補助 | 写真アートディレクション、写真のスタイリング、コンセプト開発を明示。物語のリズムから素材の役目を決められるが、具体的な切抜き/構図検証/納品仕様はImage Prompt Engineerほど明示しない。全冊編集向けの責務も混在。 |
| production/anthropic-frontend-design.md | 意匠の補助 | 依頼の指示を優先、題材固有の表現、文字を視覚要素として使う、画像を見て批評する。素材の制作手順ではなく意匠全体。静かにする/削るを余白増加と解釈しない条件が必要。 |
| production/taste-redesign.md | 部分的に有益/原文一括採用不可 | critique/taste-redesign-SKILL.mdと同内容。独立候補として加点しない。 |
| production/taste-v2.md | 部分的に有益/原文一括採用不可 | critique/taste-SKILL.mdと同内容。独立候補として加点しない。 |

## 根拠原文（引用）

### editorial/agency-image-prompt-engineer.md：45–45行

```text
- Consider aspect ratio and composition in every prompt
```

### editorial/agency-image-prompt-engineer.md：61–62行

```text
- **Subject Interaction**: Relationship with environment or other elements
- **Scale & Proportion**: Size relationships and spatial positioning
```

### editorial/agency-image-prompt-engineer.md：138–151行

```text

### Step 1: Concept Intake
- Understand the visual goal and intended use case
- Identify target AI platform and its prompt syntax preferences
- Clarify style references, mood, and brand requirements
- Determine technical requirements (aspect ratio, resolution intent)

### Step 2: Reference Analysis
- Analyze visual references for lighting, composition, and style elements
- Identify key photographers or photographic movements to reference
- Extract specific technical details that create the desired effect
- Note color palettes, textures, and atmospheric qualities

### Step 3: Prompt Construction
```

### editorial/agency-visual-storyteller.md：27–31行

```text
### Multimedia Design Excellence
- Create video content, animations, interactive media, and motion graphics
- Design infographics, data visualizations, and complex information simplification
- Provide photography art direction, photo styling, and visual concept development
- Develop custom illustrations, iconography, and visual metaphor creation
```

### editorial/agency-visual-storyteller.md：55–60行

```text
- **Visual Pacing**: Rhythm and timing of visual elements for optimal engagement

### Multimedia Content Creation
- **Video Storytelling**: Storyboard development, shot selection, visual pacing
- **Animation & Motion Graphics**: Principle animation, micro-interactions, explainer animations
- **Photography Direction**: Concept development, mood boards, styling direction
```

### critique/impeccable-bolder.md：18–24行

```text
- **Keep content true.** Existing claims are part of the scope: preserve them unless the user supplies replacements. If real evidence is essential to the direction but absent, ask for it.
- **Commit, then clarify.** Half-measures read as noise. Make the one decisive move completely, then quiet everything around it so the move is legible. If every element got louder, the section got flatter.
- **Give it its own rhythm.** The target should read as a peak in the scroll, a shift in density or pace from what surrounds it, not simply more of the same.

## The skeleton test

Strip the copy out of your planned section and study the bare structure. Does the skeleton still say what this section is and why it matters, through hierarchy and the system's devices alone? If it only works once the words return, the boldness is in the text size, not the design. A placeholder for an image or artifact names a job, an anchor and a piece of evidence, not a cue to drop in a decorative photo; fill that job with whatever the subject actually has.
```

### critique/impeccable-layout.md：18–23行

```text
   - **Reading order:** Apply the squint test. With detail blurred, can you still identify the primary element, the secondary element, and the major groups in order?
   - **Grouping:** Are related items close and distinct groups separated, or are containers compensating for weak proximity?
   - **Rhythm:** Do tight and generous intervals create a deliberate cadence, or is one spacing value repeated until everything has equal weight?
   - **Structure:** Does the topology match the content and task? Are repeated cards, columns, or sections genuinely equivalent, or merely a framework default?
   - **Density:** Does the amount of information per region fit use frequency, decision complexity, and visitor mode?
   - **Adaptation:** At narrow, intermediate, wide, zoomed, and localized states, what reorders, collapses, wraps, scrolls, or remains fixed? Does DOM and focus order still agree with the visual order?
```

### critique/impeccable-layout.md：35–41行

```text
Before editing, name:

- the primary reading or task path;
- what belongs together and what must separate;
- which element leads and which supports;
- the intended density and spacing rhythm;
- how the structure changes across containers, viewports, input modes, and content extremes.
```

### critique/taste-redesign-SKILL.md：58–58行

```text
- **Missing whitespace.** Double the spacing. Let the design breathe. Dense layouts work for data dashboards, not for marketing pages.
```

### critique/taste-redesign-SKILL.md：82–82行

```text
- **Fake round numbers like `99.99%`, `50%`, `$100.00`.** Use organic, messy data: `47.2%`, `$99.00`, `+1 (312) 847-1928`.
```

### critique/taste-SKILL.md：267–267行

```text
1. **Image-generation tool first.** If ANY image-gen tool is available in the environment (`generate_image`, MCP image tool, IDE-integrated gen, OpenAI image tools, etc.) you MUST use it to create section-specific assets: hero photography, product shots, texture backgrounds, mood images. Generate at the right aspect ratio for the section. Do not skip this step because hand-rolled CSS feels faster.
```

### critique/taste-SKILL.md：689–689行

```text
* **NO pills/labels/tags overlaid on images.** No `<span>` overlays on photos with tags like `Brand · 02`, `PLATE · BRAND`, `Field notes - journal`. Either let the image speak alone, or add a caption directly below (outside the image).
```

## 責務境界

主役/密度/視線/重なりの全冊方針は編集長・編集者が決め、パーツ担当は指定された役目と配置に合う素材を供給する。パーツの出来栄えだけで全冊を合格にしない。

## 原文に足りない事項

- 既存人物・実写真の棚卸しと生成素材との区別
- 透過切抜き、文字が重なる領域、背景透かしとしての供給
- 配置後の実寸トリミング、顔・手・文字の干渉確認
- 実使用サイズでの解像度と権利の確認
- 架空の数値・実績・学生像を事実として創作しない

原文全体の採用、役割設定変更、台帳更新、紙面修正は行っていない。
