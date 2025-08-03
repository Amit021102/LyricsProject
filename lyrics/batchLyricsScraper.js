const { scrapeLyrics } = require('./scraper');  // assumes scraper.js exports the function

// List of songs to scrape
const songs = [
  { artist: 'J Cole', song: 'friday night lights' },
  { artist: 'J Cole', song: 'too deep for the intro' },
  { artist: 'J Cole', song: 'before im gone' },
  { artist: 'J Cole', song: 'back to the topic' },
  { artist: 'J Cole', song: 'you got it' },
  { artist: 'J Cole', song: 'villematic' },
  { artist: 'J Cole', song: 'enchanted' },
  { artist: 'J Cole', song: 'blow up' },
  { artist: 'J Cole', song: 'higher' },
  { artist: 'J Cole', song: 'in the morning' },
];

(async () => {
  for (const { artist, song } of songs) {
    console.log(`\nScraping: ${artist} - ${song}`);
    await scrapeLyrics(artist, song);
  }
})();