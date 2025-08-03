from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from models import Base, Song, Verse, Line, Word, Lemma, WordOccurrence
from utils import lemmatize, limitContext



CONTEXT = 1

engine = create_engine("postgresql+pg8000://postgres:rya33rya@localhost:5432/lyrics_db")
Session = sessionmaker(bind=engine)
session = Session()

def wordInSong(index, song_name):

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

def wordInLineInSong(word_index, line_index, song_name):

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
   
def wordInVerseInSong(word_index, verse_index, song_name):

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
   
def wordInLineInVerseInSong(word_index, line_index, verse_index, song_name):

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



def findWordMatches(text: str):
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


def findLemmaMatches(text: str):
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
    return matches