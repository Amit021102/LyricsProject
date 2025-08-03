const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

function formatForUrl(str) {
  return str.toLowerCase().replace(/[^a-z0-9]/g, '');
}

function sanitizeFilename(name) {
  return name.replace(/[\/\\?%*:|"<>]/g, '-');
}

async function scrapeLyrics(artist, song) {
  const artistFormatted = formatForUrl(artist);
  const songFormatted = formatForUrl(song);
  const url = `https://www.azlyrics.com/lyrics/${artistFormatted}/${songFormatted}.html`;

  console.log(`Fetching from: ${url}`);

  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    await page.goto(url, { timeout: 60000 });

    const lyricsLocator = page.locator('//div[@class="col-xs-12 col-lg-8 text-center"]/div[not(@class) and not(@id)]');

    const count = await lyricsLocator.count();
    if (count === 0) {
      console.error('Lyrics block not found.');
      await browser.close();
      return;
    }

    const lyrics = await lyricsLocator.first().innerText();

    const fileName = sanitizeFilename(song).toLowerCase() + '.txt';
    fs.writeFileSync(path.join(__dirname, fileName), lyrics);
    console.log(`Lyrics saved to ${fileName}`);

  } catch (err) {
    console.error('Error scraping lyrics:', err);
  } finally {
    await browser.close();
  }
}

module.exports = { scrapeLyrics };