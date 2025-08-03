from lyricsProgram import process_song
from queries import wordInSong, wordInLineInSong, wordInVerseInSong, wordInLineInVerseInSong, findWordMatches, findLemmaMatches


readty_to_add = [
    "yellow_lyrics.txt",
    "luther_lyrics.txt"
]


# adding a song
# for song in readty_to_add:
#     process_song(f'lyrics\{song}')

# print(wordInSong(10, "luther_lyrics.txt"))

# print(wordInLineInSong(2, 4, "luther_lyrics.txt"))

# WORD-VERSE-SONG
# print(wordInVerseInSong(2,2,"luther_lyrcs.txt"))
# print(wordInVerseInSong(2,24,"luther_lyrics.txt"))
# print(wordInVerseInSong(56,2,"luther_lyrics.txt"))
# print(wordInVerseInSong(5,7,"luther_lyrics.txt"))

# WORD-LINE-VERSE-SONG
# print(wordInLineInVerseInSong(1,2,3,"luther_lyrcs.txt"))
# print(wordInLineInVerseInSong(1,2,30,"luther_lyrics.txt"))
# print(wordInLineInVerseInSong(1,22,3,"luther_lyrics.txt"))
# print(wordInLineInVerseInSong(18,2,3,"luther_lyrics.txt"))
# print(wordInLineInVerseInSong(1,5,2,"luther_lyrics.txt"))

# MATCH WORD
# res = findWordMatches('SeE')
# for found in res:
#     print(f'{found.SongID}\t{found.VerseID}\t{found.LineID}\t - {found.word.Text}')

# MATCH WORD
matches, contexts = findWordMatches('if')
for i in range(len(matches)):
    print(f'{matches[i].word.Text} -\ts-{matches[i].SongID}\tv-{matches[i].verse.VerseOrder}\tl-{matches[i].line.LineNumberInVerse}')
    for line in contexts[i]:
        print(line)



