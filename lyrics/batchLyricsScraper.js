const { scrapeLyrics } = require('./scraper');  // assumes scraper.js exports the function

// List of songs to scrape
const songs = [
  { artist: 'Kendrick Lamar', song: 'wacced out murals' },
  { artist: 'Kendrick Lamar', song: 'squabble up' },
  { artist: 'Kendrick Lamar', song: 'man at the garden' },
  { artist: 'Kendrick Lamar', song: 'hey now' },
  { artist: 'Kendrick Lamar', song: 'reincarnated' },
  { artist: 'Kendrick Lamar', song: 'tv off' },
  { artist: 'Kendrick Lamar', song: 'dodger blue' },
  { artist: 'Kendrick Lamar', song: 'peekaboo' },
  { artist: 'Kendrick Lamar', song: 'heart pt. 6' },
  { artist: 'Kendrick Lamar', song: 'gnx' },
  { artist: 'Kendrick Lamar', song: 'gloria' }
];

(async () => {
  for (const { artist, song } of songs) {
    console.log(`\nScraping: ${artist} - ${song}`);
    await scrapeLyrics(artist, song);
  }
})();