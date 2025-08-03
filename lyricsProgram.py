import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Song, Verse, Line, Word, Lemma, WordOccurrence
from nltk.stem import WordNetLemmatizer
from nltk import download

# Ensure required NLTK data is available
download('wordnet')
download('omw-1.4')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Connect to PostgreSQL
engine = create_engine("postgresql+pg8000://postgres:rya33rya@localhost:5432/lyrics_db")
Session = sessionmaker(bind=engine)
session = Session()

# === Main Function ===
def process_song(file_path):
    file_name = os.path.basename(file_path)

    # Check for duplicate
    existing_song = session.query(Song).filter_by(FileName=file_name).first()
    if existing_song:
        print(f"⚠️ Song '{file_name}' already processed. Skipping.")
        return

    # Create song entry
    song = Song(FileName=file_name)
    session.add(song)
    session.flush()  # gets SongID

    line_number_in_song = 1
    word_index = 1
    verse_id = 1
    line_id = 1
    word_dict = {w.Text: w for w in session.query(Word).all()}
    lemma_dict = {l.Text: l for l in session.query(Lemma).all()}

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    raw_verses = content.strip().split('\n\n')
    for raw_verse in raw_verses:
        verse_word_count = 0
        line_number_in_verse = 1

        verse = Verse(SongID=song.SongID)
        session.add(verse)
        session.flush()

        raw_lines = raw_verse.strip().split('\n')
        for raw_line in raw_lines:
            words_in_line = re.findall(r"\b\w[\w']*\b", raw_line.lower())
            word_in_line = 1

            line = Line(
                SongID=song.SongID,
                VerseID=verse.VerseID,
                Text=raw_line,
                LineNumberInSong=line_number_in_song,
                LineNumberInVerse=line_number_in_verse
            )
            session.add(line)
            session.flush()

            for word_text in words_in_line:
                lemma_text = lemmatizer.lemmatize(word_text)

                # Lemma
                if lemma_text not in lemma_dict:
                    lemma = Lemma(Text=lemma_text, TotalOccurrences=1)
                    session.add(lemma)
                    session.flush()
                    lemma_dict[lemma_text] = lemma
                else:
                    lemma = lemma_dict[lemma_text]
                    lemma.TotalOccurrences += 1

                # Word
                if word_text not in word_dict:
                    word = Word(
                        LemmaID=lemma.LemmaID,
                        Text=word_text,
                        WordLength=len(word_text),
                        TotalOccurrences=1
                    )
                    session.add(word)
                    session.flush()
                    word_dict[word_text] = word
                else:
                    word = word_dict[word_text]
                    word.TotalOccurrences += 1

                # WordOccurrence
                occurrence = WordOccurrence(
                    SongID=song.SongID,
                    VerseID=verse.VerseID,
                    LineID=line.LineID,
                    WordID=word.WordID,
                    WordIndex=word_index,
                    WordInLine=word_in_line
                )
                session.add(occurrence)

                word_index += 1
                word_in_line += 1
                verse_word_count += 1

            line_id += 1
            line_number_in_song += 1
            line_number_in_verse += 1

        verse.WordCounter = verse_word_count
        verse.VerseOrder = verse_id
        verse_id += 1

    song.NumberOfLines = line_number_in_song - 1

    session.commit()
    print(f"✅ Song '{file_name}' processed and saved to PostgreSQL.")
