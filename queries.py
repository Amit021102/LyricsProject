from models import Song, Verse, Line, Word, Lemma, WordOccurrence, Cluster, WordInCluster, Phrase, WordInPhrase
from utils import lemmatize, limit_context, CONTEXT




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

    print(f'valid phrae is \'{valid_phrase}\'')

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
