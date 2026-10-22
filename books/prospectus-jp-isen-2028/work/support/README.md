# P10–12 photograph-only outputs

- `page-10.png`, `page-11.png`: original 2480×3508 embedded page raster, replacing isolated photograph rectangles only. All outside-photo and protected text/sign/graphic pixels are byte-identical. School-building photograph and remaining text/layout preserved.
- `p12-photo.png`: 1184×485 photograph for ONLY PDF page 12 clip `[327.9923095703125, 53.80705642700195, 564.502197265625, 150.66348266601562]` points. Do not use the wider source image bbox. Native monetary text/table is untouched by this subtask.
- `prepare.py`: extraction/contact-sheet composition from the parent-identified saved source PDF; `spec.json`: original and contact-sheet rectangles.
- `*-input.png` and `*-generated.png`: actual isolated model references and full generation outputs. `generation-jobs.json` and adjacent `.prompt.yaml` preserve exact prompts.
- `compose.py`: deterministic cut-back composition and assertions; run from repository root, then `write_metadata.py`. Generation is not deterministic; saved generated files are the fixed reproducible inputs.
- `changes.json`: SHA256, all photograph and protected rectangles, display clip, and pixel checks.

Visual inspection: sources, each isolated model reference, all five generated images and all three final outputs opened with `view_image`; full-page and enlarged faces/sign/circle checked. P10/P11 main-photo text is original, not generated. Men visually clean-shaven; headscarves converted to natural uncovered hair and ordinary clothes. Japanese-image casting describes requested artistic appearance, not identification of nationality. No independent reviewer performed by this subtask.

Limitation: AI photographic edits can alter fine background detail inside the allowed photo rectangles. No claim of documentary student identity/enrollment is made. Exact pixel preservation applies to outside-photo and protected overlay areas only.
