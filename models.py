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
    clusters = relationship("WordInCluster", back_populates="word", cascade="all, delete-orphan")
    phrases = relationship("WordInPhrase", back_populates="word", cascade="all, delete-orphan")

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

class Cluster(Base):
    __tablename__ = "clusters"

    ClusterID = Column(Integer, primary_key=True)
    Name = Column(String, unique=True, nullable=False)
    Description = Column(String)
    
    words = relationship("WordInCluster", back_populates="cluster", cascade="all, delete-orphan")

class WordInCluster(Base):
    __tablename__ = "word_in_cluster"

    ClusterID = Column(Integer, ForeignKey("clusters.ClusterID"), primary_key=True)
    WordID = Column(Integer, ForeignKey("words.WordID"), primary_key=True)

    cluster = relationship("Cluster", back_populates="words")
    word = relationship("Word", back_populates="clusters")

class Phrase(Base):
    __tablename__ = "phrases"

    PhraseID = Column(Integer, primary_key=True)
    Name = Column(String, unique=True, nullable=False)
    Description = Column(String)
    
    words = relationship("WordInPhrase", back_populates="phrase", cascade="all, delete-orphan")

class WordInPhrase(Base):
    __tablename__ = "word_in_phrase"
  
    PhraseID = Column(Integer, ForeignKey("phrases.PhraseID"), primary_key=True)
    WordIndexInPhrase = Column(Integer, primary_key=True)
    WordID = Column(Integer, ForeignKey("words.WordID"), ForeignKey("words.WordID"))
    
    phrase = relationship("Phrase", back_populates="words")
    word = relationship("Word", back_populates="phrases")

