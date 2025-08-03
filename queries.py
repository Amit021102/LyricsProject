from models import Song, Verse, Line, Word, Lemma, WordOccurrence, Cluster, WordInCluster
from utils import lemmatize, limitContext


# the number of lines added before and after the wanted line in match finding
CONTEXT = 0


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

def addToCluster(cluster_name, word_text, session):
    cluster_id = session.query(Cluster).filter(Cluster.name == cluster_name).first()
    word_id = session.query(Word).filter(Word.text == word_text).first()
    # word does not appear in the text
    # we must add it to the Word table and Lemma table accordingly
    if not word_id:
        pass
    if not cluster_id:
        entry = WordInCluster(ClusterID=cluster_id, WordID=word_id)
        session.add(entry)
        session.commit()
        print(f"Added word '{word_text}' to cluster {cluster_id}")

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

    res1 = []
    res2 = []
    for instance in matches:
        context = []
        begin, end = limitContext(instance)
        for i in range(begin, end+1):
            line_text = session.query(Line).filter_by(SongID=instance.SongID, LineNumberInSong=i).first().Text
            context.append(line_text)
        res1.append(instance)
        res2.append(context)
    
        # print(f'{instance.SongID}\t{instance.VerseID}\t{instance.LineID}\t - {instance.word.Text}')
        # print(f'from line {begin} to line {end}')

    return res1, res2

def findLemmaMatches(text: str, session):
    text = text.lower()
    lemma_text = lemmatize(text)
    matches = (
        session.query(WordOccurrence)
        .join(Word)
        .join(Lemma)
        .filter(Lemma.Text == lemma_text)
        .all()
    )
    if not matches:
        print(f"No matches found for lemma '{lemma_text}'")

    res1 = []
    res2 = []
    for instance in matches:
        context = []
        begin, end = limitContext(instance)
        for i in range(begin, end+1):
            line_text = session.query(Line).filter_by(SongID=instance.SongID, LineNumberInSong=i).first().Text
            context.append(line_text)
        res1.append(instance)
        res2.append(context)
        return res1, res2
    
def findClusterMatches(name: str, session):
    name = name.lower()
    cluster_id = session.query(Cluster).filter(Cluster.name == name).first().ClusterID
    words = session.query(WordInCluster).filter(Cluster.ClusterID == cluster_id).all()

    res1 = []
    res2 = []

    for word in words:
        matches = (
            session.query(WordOccurrence)
            .join(Word)
            .filter(WordOccurrence.WordID == word.WordID)
            .all()
        )
        if not matches:
            print(f"No matches found for word '{word.word.text}'")

        
        for instance in matches:
            context = []
            begin, end = limitContext(instance)
            for i in range(begin, end+1):
                line_text = session.query(Line).filter_by(SongID=instance.SongID, LineNumberInSong=i).first().Text
                context.append(line_text)
            res1.append(instance)
            res2.append(context)

    return res1, res2