from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Song(Base):
    __tablename__ = 'songs'
    SongID = Column(Integer, primary_key=True)
    FileName = Column(String, unique=True)
    NumberOfLines = Column(Integer)
    
    verses = relationship("Verse", back_populates="song")
    lines = relationship("Line", back_populates="song")
    word_occurrences = relationship("WordOccurrence", back_populates="song")

class Verse(Base):
    __tablename__ = 'verses'
    VerseID = Column(Integer, primary_key=True)
    SongID = Column(Integer, ForeignKey('songs.SongID'))
    VerseOrder = Column(Integer)
    WordCounter = Column(Integer)

    song = relationship("Song", back_populates="verses")
    lines = relationship("Line", back_populates="verse")
    word_occurrences = relationship("WordOccurrence", back_populates="verse")

class Line(Base):
    __tablename__ = 'lines'
    LineID = Column(Integer, primary_key=True)
    SongID = Column(Integer, ForeignKey('songs.SongID'))
    VerseID = Column(Integer, ForeignKey('verses.VerseID'))
    Text = Column(String)
    LineNumberInSong = Column(Integer)
    LineNumberInVerse = Column(Integer)

    song = relationship("Song", back_populates="lines")
    verse = relationship("Verse", back_populates="lines")
    word_occurrences = relationship("WordOccurrence", back_populates="line")

class Lemma(Base):
    __tablename__ = 'lemmas'
    LemmaID = Column(Integer, primary_key=True)
    Text = Column(String, unique=True)
    TotalOccurrences = Column(Integer)

    words = relationship("Word", back_populates="lemma")

class Word(Base):
    __tablename__ = 'words'
    WordID = Column(Integer, primary_key=True)
    LemmaID = Column(Integer, ForeignKey('lemmas.LemmaID'))
    Text = Column(String, unique=True)
    WordLength = Column(Integer)
    TotalOccurrences = Column(Integer)

    lemma = relationship("Lemma", back_populates="words")
    word_occurrences = relationship("WordOccurrence", back_populates="word")

class WordOccurrence(Base):
    __tablename__ = 'word_occurrences'
    OccurrenceID = Column(Integer, primary_key=True)
    SongID = Column(Integer, ForeignKey('songs.SongID'))
    VerseID = Column(Integer, ForeignKey('verses.VerseID'))
    LineID = Column(Integer, ForeignKey('lines.LineID'))
    WordID = Column(Integer, ForeignKey('words.WordID'))
    WordIndex = Column(Integer)
    WordInLine = Column(Integer)

    song = relationship("Song", back_populates="word_occurrences")
    verse = relationship("Verse", back_populates="word_occurrences")
    line = relationship("Line", back_populates="word_occurrences")
    word = relationship("Word", back_populates="word_occurrences")
