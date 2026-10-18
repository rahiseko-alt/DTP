import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';
import { chromium } from 'playwright';

function getArg(name, defaultValue) {
  const idx = process.argv.indexOf(name);
  if (idx !== -1 && idx + 1 < process.argv.length) return process.argv[idx + 1];
  return defaultValue;
}

const legacyBrainDir = 'C:/Users/user/.gemini/antigravity/brain/6689cedc-bb2a-4cdb-8bf2-514e68d71a0d';
const workDir = path.resolve(getArg('--work-dir', process.env.BOOKLET_WORK_DIR || '.cache/build_full_booklet_pdf'));
const flatDir = path.resolve(
  getArg(
    '--input-dir',
    process.env.FLAT_PAGES_DIR ||
      (fs.existsSync(path.join(legacyBrainDir, 'flat_pages'))
        ? path.join(legacyBrainDir, 'flat_pages')
        : path.resolve('.cache/flat_pages')),
  ),
);
const finalPdfPath = path.resolve(
  getArg('--output', 'output/pdf/AIビジネス専門学校_学校案内_2028_白版_20P.pdf'),
);
const outPdfDir = path.dirname(finalPdfPath);
if (!fs.existsSync(outPdfDir)) fs.mkdirSync(outPdfDir, { recursive: true });
if (!fs.existsSync(workDir)) fs.mkdirSync(workDir, { recursive: true });
if (!fs.existsSync(flatDir)) fs.mkdirSync(flatDir, { recursive: true });

async function main() {
  console.log('1. Generating P20 back cover...');
  const svg = `
<svg width="2480" height="3508" viewBox="0 0 2480 3508" xmlns="http://www.w3.org/2000/svg">
  <rect width="2480" height="3508" fill="#ffffff"/>
  <rect x="150" y="180" width="2180" height="8" fill="#24476b"/>
  
  <text x="1240" y="600" font-family="Noto Sans JP, sans-serif" font-size="84" font-weight="900" fill="#24476b" text-anchor="middle" letter-spacing="6">AIビジネス専門学校</text>
  <text x="1240" y="680" font-family="Noto Sans JP, sans-serif" font-size="38" font-weight="500" fill="#57606a" text-anchor="middle" letter-spacing="8">AI BUSINESS VOCATIONAL SCHOOL</text>
  <text x="1240" y="820" font-family="Noto Sans JP, sans-serif" font-size="46" font-weight="700" fill="#24476b" text-anchor="middle">学校法人 海鵬学園</text>
  <rect x="1120" y="880" width="240" height="4" fill="#e0245e"/>

  <rect x="280" y="1080" width="1920" height="420" rx="24" fill="#f4f6f9" stroke="#d0d7de" stroke-width="3"/>
  <text x="360" y="1190" font-family="Noto Sans JP, sans-serif" font-size="52" font-weight="800" fill="#24476b">設置学科（2年制・商業実務専門課程）</text>
  <text x="360" y="1290" font-family="Noto Sans JP, sans-serif" font-size="44" font-weight="700" fill="#1f2328">■ 国際ビジネスAI科</text>
  <text x="960" y="1290" font-family="Noto Sans JP, sans-serif" font-size="36" font-weight="400" fill="#57606a">AI活用 / データ分析 / グローバルビジネス実務</text>
  <text x="360" y="1390" font-family="Noto Sans JP, sans-serif" font-size="44" font-weight="700" fill="#1f2328">■ 総合ビジネス科</text>
  <text x="960" y="1390" font-family="Noto Sans JP, sans-serif" font-size="36" font-weight="400" fill="#57606a">販売・サービス / 経営 / 事務 / マーケティング / IT</text>

  <rect x="280" y="1600" width="1920" height="1050" rx="24" fill="#ffffff" stroke="#24476b" stroke-width="4"/>
  <rect x="280" y="1600" width="1920" height="120" rx="20" fill="#24476b"/>
  <text x="1240" y="1680" font-family="Noto Sans JP, sans-serif" font-size="50" font-weight="800" fill="#ffffff" text-anchor="middle">お問い合わせ・入学相談窓口</text>
  
  <text x="380" y="1850" font-family="Noto Sans JP, sans-serif" font-size="44" font-weight="700" fill="#57606a">【お電話でのお問い合わせ】</text>
  <text x="380" y="1960" font-family="Noto Sans JP, sans-serif" font-size="76" font-weight="900" fill="#24476b">TEL. 052-451-3821</text>
  
  <text x="380" y="2100" font-family="Noto Sans JP, sans-serif" font-size="44" font-weight="700" fill="#57606a">【メールでのお問い合わせ】</text>
  <text x="380" y="2190" font-family="Noto Sans JP, sans-serif" font-size="52" font-weight="700" fill="#1f2328">ai-nyushi@jp-academy.net</text>
  
  <text x="380" y="2320" font-family="Noto Sans JP, sans-serif" font-size="44" font-weight="700" fill="#57606a">【学校所在地・交通アクセス】</text>
  <text x="380" y="2410" font-family="Noto Sans JP, sans-serif" font-size="44" font-weight="600" fill="#1f2328">〒453-0015 愛知県名古屋市中村区椿町12-19</text>
  <text x="380" y="2490" font-family="Noto Sans JP, sans-serif" font-size="42" font-weight="700" fill="#e0245e">JR・名鉄・近鉄・地下鉄「名古屋駅」太閤通口（西口）より徒歩10分</text>

  <text x="1240" y="2850" font-family="Noto Sans JP, sans-serif" font-size="46" font-weight="700" fill="#24476b" text-anchor="middle">学校公式サイト・最新募集要項はこちら</text>
  <text x="1240" y="2930" font-family="Noto Sans JP, sans-serif" font-size="38" font-weight="500" fill="#57606a" text-anchor="middle">https://kaihougakuen.my.canva.site/</text>
  
  <text x="1240" y="3200" font-family="Noto Sans JP, sans-serif" font-size="56" font-weight="900" fill="#24476b" text-anchor="middle" letter-spacing="4">学びを、未来の力に。</text>
  <rect x="150" y="3320" width="2180" height="8" fill="#24476b"/>
</svg>
`;

  const p20Path = path.join(flatDir, 'P20_back_cover.png');
  await sharp(Buffer.from(svg)).png().toFile(p20Path);
  console.log('P20 generated at:', p20Path);

  // 20ページの順序定義
  const pages = [
    'P01_cover.png',
    'P02_multicultural_left.png',
    'P03_multicultural_right.png',
    'P04_overview_left.png',
    'P05_overview_right.png',
    'P06_international_ai_left.png',
    'P07_international_ai_right.png',
    'P08_general_business_left.png',
    'P09_general_business_right.png',
    'P10_lecturer_ai_left.png',
    'P11_lecturer_ai_right.png',
    'P12_school_pr_left.png',
    'P13_school_pr_right.png',
    'P14_support_faculty.png',
    'P15_parents_guide.png',
    'P16_tuition_guide.png',
    'P17_payment_timing.png',
    'P18_admissions_guide.png',
    'P19_facility_access.png',
    'P20_back_cover.png'
  ];

  console.log('2. Building combined PDF via Playwright...');
  let html = `<!DOCTYPE html><html><head><meta charset="utf-8">
  <style>
    @page { size: A4 portrait; margin: 0; }
    html, body { margin: 0; padding: 0; background: #fff; }
    .page {
      width: 210mm;
      height: 297mm;
      page-break-after: always;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }
    .page:last-child {
      page-break-after: avoid;
    }
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
  </style>
  </head><body>`;

  for (const p of pages) {
    const fullPath = path.join(flatDir, p).replace(/\\/g, '/');
    html += `<div class="page"><img src="file:///${fullPath}"></div>`;
  }
  html += `</body></html>`;

  const htmlPath = path.join(workDir, 'booklet_print.html');
  fs.writeFileSync(htmlPath, html, 'utf-8');

  const browser = await chromium.launch({
    executablePath: process.env.STUDIO_CHROMIUM_PATH || undefined,
    headless: true,
  });
  const page = await browser.newPage();
  await page.goto(`file:///${htmlPath.replace(/\\/g, '/')}`, { waitUntil: 'load' });

  await page.pdf({
    path: finalPdfPath,
    format: 'A4',
    printBackground: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 }
  });

  // ユーザー提示用ディレクトリが環境変数で指定されていればコピー
  if (process.env.BRAIN_DIR && fs.existsSync(process.env.BRAIN_DIR)) {
    const brainPdfPath = path.join(process.env.BRAIN_DIR, path.basename(finalPdfPath));
    fs.copyFileSync(finalPdfPath, brainPdfPath);
  }

  await browser.close();
  console.log('PDF successfully created at:', finalPdfPath);
  console.log('File size:', fs.statSync(finalPdfPath).size, 'bytes');
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
