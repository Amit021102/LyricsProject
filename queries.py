from models import Song, Verse, Line, Word, Lemma, WordOccurrence, Cluster, WordInCluster, Phrase, WordInPhrase
from utils import lemmatize



# STANDARD WORD LOCATIONS

def wordInSong(index, song_name, session):

    print('entered')

    song = session.query(Song).filter_by(FileName=song_name).first()
    if not song:
        print(f"❌ Song '{song_name}' is not in the DataBase.")
        return 
    
    word = session.query(WordOccurrence).filter_by(SongID=song.SongID, WordIndex=index).first()
    if not word:
        print(f"❌ Song '{song_name}' has less than {index} words.")
        return 
    
    text = session.query(Word).filter_by(WordID=word.WordID).first()
    return text.Text

def wordInLineInSong(word_index, line_index, song_name, session):

    song = session.query(Song).filter_by(FileName=song_name).first()
    if not song:
        print(f"❌ Song '{song_name}' is not in the DataBase.")
        return 
    
    line = session.query(Line).filter_by(SongID=song.SongID, LineNumberInSong=line_index).first()
    if not line:
        print(f"❌ Song '{song_name}' has less than {line_index} lines.")
        return 
    
    word = session.query(WordOccurrence).filter_by(LineID=line.LineID, WordInLine=word_index).first()
    if not word:
        print(f"❌ Line {line_index} of song '{song_name}' has less than {word_index} words.")
        return 
    
    text = session.query(Word).filter_by(WordID=word.WordID).first()
    return text.Text
   
def wordInVerseInSong(word_index, verse_index, song_name, session):

    song = session.query(Song).filter_by(FileName=song_name).first()
    if not song:
        print(f"❌ Song '{song_name}' is not in the DataBase.")
        return 
    
    verse = session.query(Verse).filter_by(SongID=song.SongID, VerseOrder=verse_index).first()
    if not verse:
        print(f"❌ Song '{song_name}' has less than {verse_index} verses.")
        return 
    
    word = session.query(WordOccurrence).filter_by(VerseID=verse.VerseID, WordInLine=word_index).first()
    if not word:
        print(f"❌ Verse {verse_index} in song '{song_name}' has less than {word_index} words.")
        return 
    
    text = session.query(Word).filter_by(WordID=word.WordID).first()
    return text.Text
   
def wordInLineInVerseInSong(word_index, line_index, verse_index, song_name, session):

    song = session.query(Song).filter_by(FileName=song_name).first()
    if not song:
        print(f"❌ Song '{song_name}' is not in the DataBase.")
        return 
    
    verse = session.query(Verse).filter_by(SongID=song.SongID, VerseOrder=verse_index).first()
    if not verse:
        print(f"❌ Song '{song_name}' has less than {verse_index} verses.")
        return 
    
    line = session.query(Line).filter_by(VerseID=verse.VerseID ,LineNumberInVerse=line_index).first()
    if not line:
        print(f"❌ Verse {verse_index} in song '{song_name}' has less than {line_index} lines.")
        return 
    
    word = session.query(WordOccurrence).filter_by(LineID=line.LineID, WordInLine=word_index).first()
    if not word:
        print(f"❌ Line {line_index} of verse {verse_index} in song '{song_name}' has less than {word_index} words.")
        return 
    
    text = session.query(Word).filter_by(WordID=word.WordID).first()
    return text.Text


# COMPLEX MATCH FINDING

def findWordMatches(text: str, session):
    text = text.lower()
    matches = (
        session.query(WordOccurrence)
        .join(Word)
        .filter(Word.Text == text)
        .all()
    )
    if not matches:
        print(f"No matches found for word '{text}'")

    return matches

def findLemmaMatches(text: str, session):
    text = text.lower()
    lemma_text = lemmatize(text)

    lemma = session.query(Lemma).filter_by(Text=lemma_text).first()
    if lemma is None:
        print(f"No matches found for lemma '{lemma_text}'")
        return []


    matches = (
        session.query(WordOccurrence)
        .join(Word, WordOccurrence.WordID == Word.WordID)
        .filter(Word.LemmaID == lemma.LemmaID)
        .all()
    )

    return matches
    
def findClusterMatches(name: str, session):
    name = name.lower()
    cluster_id = session.query(Cluster).filter(Cluster.Name == name).first().ClusterID
    if not cluster_id:
        print(f"No cluster named '{name}' in the DB")
        return []

    words = session.query(WordInCluster).filter(WordInCluster.ClusterID == cluster_id).all()

    matches = []

    for word in words:
        res1 = findWordMatches(word.word.Text, session)
        matches += res1

    return matches

def findPhraseMatches(name: str, session):
    import re
    from collections import defaultdict

    valid_phrase = re.sub(r"[^\w\s]", ' ', name).lower().strip()

    phrase_id = session.query(Phrase).filter(Phrase.Name == valid_phrase).first().PhraseID
    if not phrase_id:
        print(f"No phrase named '{valid_phrase}' saved in the DB")
        return []
    
    word_ids = [wid for (wid,) in session.query(WordInPhrase.WordID).filter_by(PhraseID=phrase_id).all()]
    
    occurrences = (
        session.query(WordOccurrence)
        .filter(WordOccurrence.WordID.in_(word_ids))
        .order_by(WordOccurrence.SongID, WordOccurrence.LineID, WordOccurrence.WordInLine)
        .all()
    )

    print('here')

    # Group occurrences by song+line
    grouped = defaultdict(list)
    for occ in occurrences:
        key = (occ.SongID, occ.LineID)
        grouped[key].append(occ)

    # Phrase matching using sliding window
    matches = []
    for occ_list in grouped.values():
        # sorting each line value of the dict by order of appearence
        occ_list.sort(key=lambda o: o.WordInLine)
        for i in range(len(occ_list) - len(word_ids) + 1):
            window = occ_list[i:i+len(word_ids)]
            if all(window[j].WordID == word_ids[j] and
                window[j].WordInLine == window[0].WordInLine + j
                for j in range(len(word_ids))):
                matches.append(window[0])

    return matches


# STATISTICAL DATA

# chars in - word, line, verse, song
# words in - line, verse, song
# lines in - verse, song
# verses in - song

def chars_in_word(session, word_id: int):

    word = session.query(Word).filter_by(WordID=word_id).first()

    if not word:
        print(f"word '{word_id}' not in DB")
        return
    
    return word.WordLength

def chars_in_line(session, line_number: int, song_id: int, verse_number=0):

    from sqlalchemy import func


    if session.query(Song).filter_by(SongID=song_id).first() is None:
        print(f'No song matches the ID {song_id}')
        return 0

    # verse number passed, line number is relative to verse
    if verse_number:
        verse = session.query(Verse).filter_by(VerseOrder=verse_number, SongID=song_id).first()
        if not verse:
            print(f'The song has less than {verse_number} verses')
            return 0
        line = session.query(Line).filter_by(LineNumberInVerse=line_number, VerseID=verse.VerseID).first()        
        if not line:
            print(f'Verse {verse_number} in the song has less than {line_number} lines')
            return 0
    # verse number not passed, line number is relative to song
    else:
        line = session.query(Line).filter_by(LineNumberInSong=line_number, SongID=song_id).first()
        if not line:
            print(f'The song has less than {line_number} lines')
            return 0
        
    total_chars = (
        session.query(func.sum(Word.WordLength))
        .join(WordOccurrence, Word.WordID == WordOccurrence.WordID)
        .filter(WordOccurrence.LineID == line.LineID)
        .scalar()
    )

    total_chars = total_chars or 0

    print('Success!')
    return total_chars

def chars_in_verse(session, verse_number: int, song_id: int):

    from sqlalchemy import func


    if session.query(Song).filter_by(SongID=song_id).first() is None:
        print(f'No song matches the ID {song_id}')
        return 0

    verse = session.query(Verse).filter_by(VerseOrder=verse_number, SongID=song_id).first()
    if not verse:
        print(f'The song has less than {verse_number} verses')
        return 0

    total_chars = (
        session.query(func.sum(Word.WordLength))
        .join(WordOccurrence, Word.WordID == WordOccurrence.WordID)
        .filter(WordOccurrence.VerseID == verse.VerseID)
        .scalar()
    )

    total_chars = total_chars or 0

    print('Success!')
    return total_chars

def chars_in_song(session, song_id: int):

    from sqlalchemy import func


    if session.query(Song).filter_by(SongID=song_id).first() is None:
        print(f'No song matches the ID {song_id}')
        return 0
    
    total_chars = (
        session.query(func.sum(Word.WordLength))
        .join(WordOccurrence, Word.WordID == WordOccurrence.WordID)
        .filter(WordOccurrence.SongID == song_id)
        .scalar()
    )

    total_chars = total_chars or 0

    print('Success!')
    return total_chars



def words_in_line(session, line_number: int, song_id: int, verse_number=0):

    from sqlalchemy import func


    if session.query(Song).filter_by(SongID=song_id).first() is None:
        print(f'No song matches the ID {song_id}')
        return 0

    # verse number passed, line number is relative to verse
    if verse_number:
        verse = session.query(Verse).filter_by(VerseOrder=verse_number, SongID=song_id).first()
        if not verse:
            print(f'The song has less than {verse_number} verses')
            return 0
        line = session.query(Line).filter_by(LineNumberInVerse=line_number, VerseID=verse.VerseID).first()        
        if not line:
            print(f'Verse {verse_number} in the song has less than {line_number} lines')
            return 0
    # verse number not passed, line number is relative to song
    else:
        line = session.query(Line).filter_by(LineNumberInSong=line_number, SongID=song_id).first()
        if not line:
            print(f'The song has less than {line_number} lines')
            return 0
        
    total_words = (
        session.query(func.count(WordOccurrence.WordID))
        .filter(WordOccurrence.LineID == line.LineID)
        .scalar()
    )

    total_words = total_words or 0

    print('Success!')
    return total_words

def words_in_verse(session, verse_number: int, song_id: int):

    from sqlalchemy import func


    if session.query(Song).filter_by(SongID=song_id).first() is None:
        print(f'No song matches the ID {song_id}')
        return 0

    verse = session.query(Verse).filter_by(VerseOrder=verse_number, SongID=song_id).first()
    if not verse:
        print(f'The song has less than {verse_number} verses')
        return 0

    print('Success!')
    return verse.WordCounter

def words_in_song(session, song_id: int):

    from sqlalchemy import func


    if session.query(Song).filter_by(SongID=song_id).first() is None:
        print(f'No song matches the ID {song_id}')
        return 0
 
    total_words = (
        session.query(func.count(WordOccurrence.WordID))
        .filter(WordOccurrence.SongID == song_id)
        .scalar()
    )

    total_words = total_words or 0

    print('Success!')
    return total_words



def lines_in_verse(session, verse_number: int, song_id: int):
    from sqlalchemy import func

    if session.query(Song).filter_by(SongID=song_id).first() is None:
        print(f'No song matches the ID {song_id}')
        return 0
    
    verse = session.query(Verse).filter_by(SongID=song_id, VerseOrder=verse_number).first()
    if not verse:
        print(f'The song has less than {verse_number} verses')
        return 0

    return session.query(func.count(Line.LineID)).filter_by(VerseID=verse.VerseID).scalar()

def lines_in_song(session, song_id: int):

    if session.query(Song).filter_by(SongID=song_id).first() is None:
        print(f'No song matches the ID {song_id}')
        return 0
    
    return session.query(Song).filter_by(SongID=song_id).first().NumberOfLines



def verses_in_song(session, song_id: int):

    from sqlalchemy import func

    if session.query(Song).filter_by(SongID=song_id).first() is None:
        print(f'No song matches the ID {song_id}')
        return 0
    
    return session.query(func.count(Verse.VerseID)).filter_by(SongID=song_id).scalar()


