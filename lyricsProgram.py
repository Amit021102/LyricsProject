import os
import re
from models import Base, Song, Verse, Line, WordOccurrence
from utils import get_or_create_word



def process_song(file_path, session):
    file_name = os.path.basename(file_path)

    # Check for duplicate
    existing_song = session.query(Song).filter_by(FileName=file_name).first()
    if existing_song:
        print(f"⚠️ Song '{file_name}' already processed. Skipping.")
        return

    try: 
        # Create song entry
        song = Song(FileName=file_name)
        session.add(song)
        session.flush()  # gets SongID

        line_number_in_song = 1
        word_index = 1
        verse_order = 1

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

                    # this gets or creates the word entity
                    # it does the same for lemma behind the scenes
                    word = get_or_create_word(session, word_text)
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

                line_number_in_song += 1
                line_number_in_verse += 1

            verse.WordCounter = verse_word_count
            verse.VerseOrder = verse_order
            verse_order += 1

        song.NumberOfLines = line_number_in_song - 1

        session.flush()
        print(f"✅ Song '{song.FileName}' processed and ready to be saved to PostgreSQL.")
    
    except Exception as e:
        session.rollback()
        print(f"❌ Error processing '{file_name}': {e}")
