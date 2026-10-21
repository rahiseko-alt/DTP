import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const book = path.dirname(fileURLToPath(import.meta.url));
const assembly = JSON.parse(await fs.readFile(path.join(book, 'reviews/assembly-proof.json'), 'utf8'));
const cover = path.resolve(book, '../..', assembly.inputs.find(x => x.page === 1).file);
const { revision } = JSON.parse(await fs.readFile(path.join(path.dirname(cover), 'provenance.json'), 'utf8'));
// Capture the rendered PDF page, rather than the pre-assembly cover artwork.
const png = await fs.readFile(path.join(book, 'output/pages/page-01.png'));
const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', headless: true, args: ['--no-sandbox'] });
try {
  const page = await browser.newPage({ viewport: { width: 744, height: 1053 }, deviceScaleFactor: 1 });
  await page.setContent(`<style>html,body{margin:0;width:744px;height:1053px;overflow:hidden}img{display:block;width:744px;height:1053px}</style><img src="data:image/png;base64,${png.toString('base64')}">`);
  await page.locator('img').evaluate(img => img.decode());
  const target = path.join(book, `reviews/cover-revision${revision}-screenshot.png`);
  await page.screenshot({ path: target });
  process.stdout.write(target + '\n');
} finally {
  await browser.close();
}
