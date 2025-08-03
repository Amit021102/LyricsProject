import os
from lyricsProgram import process_song
from queries import wordInSong, wordInLineInSong, wordInVerseInSong, wordInLineInVerseInSong, findWordMatches, findLemmaMatches, findClusterMatches
from models import Cluster, Word, WordInCluster
from setup_db import Session

session = Session()


# readty_to_add = [
#     "dodger blue.txt",
#     "gloria.txt",
#     "gnx.txt",
#     "heart pt. 6.txt",
#     "hey now.txt",
#     "luther.txt",
#     "man at the garden.txt",
#     "peekaboo.txt",
#     "reincarnated.txt",
#     "squabble up.txt",
#     "tv off.txt",
#     "wacced out murals.txt"
# ]


readty_to_add = [
    "friday night lights.txt",
    "too deep for the intro.txt",
    "before im gone.txt",
    "back to the topic.txt",
    "you got it.txt",
    "villematic.txt",
    "enchanted.txt",
    "blow up.txt",
    "higher.txt",
    "in the morning.txt"
]


# adding a song
for song in readty_to_add:
    file_path = os.path.join("lyrics", song)
    print(f'working on {file_path}')
    process_song(file_path)

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
# matches, contexts = findWordMatches('if')
# for i in range(len(matches)):
#     print(f'{matches[i].word.Text} -\ts-{matches[i].SongID}\tv-{matches[i].verse.VerseOrder}\tl-{matches[i].line.LineNumberInVerse}')
#     for line in contexts[i]:
#         print(line)

# MATCH CLUSTER
# matches, contexts = findClusterMatches('numbers')
# for i in range(len(matches)):
#     print(f'{matches[i].word.Text} -\ts-{matches[i].SongID}\tv-{matches[i].verse.VerseOrder}\tl-{matches[i].line.LineNumberInVerse}')
#     for line in contexts[i]:
#         print(line)


# MANUALLY CREATING A CLUSTER
# new_cluster = Cluster(name="numbers", description="words with numerical characters")
# session.add(new_cluster)
# session.commit()

cluster_id = 1

# words = [
#     "2", "6", "7", "8", "10", "405", "1947", "2014", "2025", "one"
# ]


# ADDING NUMERICAL WORDS TO THE ABOVE CLUSTER
# for word_text in words:
        
#     # Get the WordID from the Words table
#     word = session.query(Word).filter_by(Text=word_text).first()

#     if word:
#         word_id = word.WordID

#         # Create new WordInCluster entry
#         entry = WordInCluster(ClusterID=cluster_id, WordID=word_id)
#         session.add(entry)
#         session.commit()
#         print(f"Added word '{word_text}' to cluster {cluster_id}")
#     else:
#         print(f"Word '{word_text}' not found in Words table.")

session.close()



