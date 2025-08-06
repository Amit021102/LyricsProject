import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from setup_db import Session
from queries import CONTEXT ,wordInSong, wordInLineInSong, wordInVerseInSong, wordInLineInVerseInSong, findWordMatches, findLemmaMatches, findClusterMatches, findPhraseMatches
from queries import chars_in_word, chars_in_line, chars_in_verse, chars_in_song, words_in_line, words_in_verse, words_in_song, lines_in_verse, lines_in_song, verses_in_song
from utils import add_to_cluster, get_or_create_phrase
from lyricsProgram import process_song


@pytest.fixture
def session():
    session = Session()
    yield session
    session.rollback()  # so we don't keep test data


def test_word_in_song(session):

    process_song("lyrics/test_lyrics.txt", session)

    assert wordInSong(2, "not_test_lyrics.txt", session) is None
    assert wordInSong(190, "test_lyrics.txt", session) is None
    assert wordInSong(12, "test_lyrics.txt", session) == "h"

def test_word_in_line_in_song(session):

    process_song("lyrics/test_lyrics.txt", session)

    assert wordInLineInSong(2, 1, "not_test_lyrics.txt", session) is None
    assert wordInLineInSong(56, 1, "test_lyrics.txt", session) is None
    assert wordInLineInSong(2, 100, "test_lyrics.txt", session) is None
    assert wordInLineInSong(2, 5, "test_lyrics.txt", session) == "z"

def test_word_in_verse_in_song(session):

    process_song("lyrics/test_lyrics.txt", session)

    assert wordInVerseInSong(2, 1, "not_test_lyrics.txt", session) is None
    assert wordInVerseInSong(56, 1, "test_lyrics.txt", session) is None
    assert wordInVerseInSong(2, 100, "test_lyrics.txt", session) is None
    assert wordInVerseInSong(2, 3, "test_lyrics.txt", session) == "is"

def test_word_in_line_in_verse_in_song(session):

    process_song("lyrics/test_lyrics.txt", session)

    assert wordInLineInVerseInSong(2, 1, 3, "not_test_lyrics.txt", session) is None
    assert wordInLineInVerseInSong(56, 1, 3, "test_lyrics.txt", session) is None
    assert wordInLineInVerseInSong(2, 100, 3, "test_lyrics.txt", session) is None
    assert wordInLineInVerseInSong(2, 3, 41, "test_lyrics.txt", session) is None
    assert wordInLineInVerseInSong(1, 2, 3, "test_lyrics.txt", session) == "run"




def test_find_word_matches(session):

    process_song("lyrics/test_lyrics.txt", session)

    matches = findWordMatches("test_word", session)
    assert len(matches) == 4
    for match in matches:
        assert match.word.Text == "test_word"

    assert matches[0].line.LineNumberInSong == 16
    assert matches[1].line.LineNumberInSong == 16
    assert matches[2].line.LineNumberInSong == 17
    assert matches[3].line.LineNumberInSong == 19

def test_find_lemma_match(session):
    from models import Lemma

    process_song("lyrics/test_lyrics.txt", session)

    
    matches = findLemmaMatches("test", session)
    rel_matches = [match for match in matches if match.song.FileName=="test_lyrics.txt"]

    assert len(rel_matches) == 6
    assert rel_matches[0].line.LineNumberInSong == 1
    assert rel_matches[1].line.LineNumberInSong == 6
    assert rel_matches[2].line.LineNumberInSong == 10
    assert rel_matches[3].line.LineNumberInSong == 17
    assert rel_matches[4].line.LineNumberInSong == 20
    assert rel_matches[5].line.LineNumberInSong == 20

def test_find_cluster_match(session):
    from models import Cluster

    process_song("lyrics/test_lyrics.txt", session)

    test_cluster = Cluster(Name="test_digits")
    session.add(test_cluster)
    session.flush()

    for i in range(1, 10):
        add_to_cluster(session, str(i), "test_digits")

    session.flush()

    matches = findClusterMatches("test_digits", session)

    rel_matches = [match for match in matches if match.song.FileName=="test_lyrics.txt"]

    assert len(rel_matches) == 9
    assert rel_matches[0].line.LineNumberInSong == 7
    assert rel_matches[4].line.LineNumberInSong == 8
    assert rel_matches[8].line.LineNumberInSong == 9

def test_find_phrase_matches(session):

    from models import Song

    get_or_create_phrase(session, "this is a test")
    session.flush()
    process_song("lyrics/test_lyrics.txt", session)
    test_song_id = session.query(Song).filter_by(FileName="test_lyrics.txt").first().SongID
    
    matches = findPhraseMatches("This is-a test?!", session)

    rel_matches = []

    for i in range(len(matches)):
        if matches[i].SongID == test_song_id:
            rel_matches.append(matches[i])


    assert len(rel_matches) == 2

    assert rel_matches[0].line.LineNumberInSong == 1
    assert rel_matches[1].line.LineNumberInSong == 10




def test_chars_in_word(session):
    from models import Word

    process_song("lyrics/test_lyrics.txt", session)
    word_id = session.query(Word).filter_by(Text="test").first().WordID
    
    assert chars_in_word(session, word_id) == 4
    assert chars_in_word(session, -1) is None

def test_chars_in_line(session):
    from models import Song

    process_song("lyrics/test_lyrics.txt", session)
    song_id = session.query(Song).filter_by(FileName="test_lyrics.txt").first().SongID

    assert chars_in_line(session, 1, 0) == 0
    assert chars_in_line(session, 23, song_id) == 0
    assert chars_in_line(session, 2, song_id) == 8

    
    assert chars_in_line(session, 1, 0, 3) == 0
    assert chars_in_line(session, 1, song_id, 23) == 0
    assert chars_in_line(session, 11, song_id, 2) == 0
    assert chars_in_line(session, 3, song_id, 2) == 3
    
def test_chars_in_verse(session):
    from models import Song

    process_song("lyrics/test_lyrics.txt", session)
    song_id = session.query(Song).filter_by(FileName="test_lyrics.txt").first().SongID

    assert chars_in_verse(session, 1, 0) == 0
    assert chars_in_verse(session, 8, song_id) == 0
    assert chars_in_verse(session, 2, song_id) == 26
  
def test_chars_in_song(session):
    from models import Song, Verse
    from sqlalchemy import func

    process_song("lyrics/test_lyrics.txt", session)
    song_id = session.query(Song).filter_by(FileName="test_lyrics.txt").first().SongID

    verses_number = (
        session.query(func.max(Verse.VerseOrder))
        .filter(Verse.SongID == song_id)
        .scalar()
    )
    total = 0
    for i in range(1, verses_number+1):
        total += chars_in_verse(session, i, song_id)

    assert chars_in_song(session, -1) == 0
    assert chars_in_song(session, song_id) == total
  

def test_words_in_line(session):
    from models import Song

    process_song("lyrics/test_lyrics.txt", session)
    song_id = session.query(Song).filter_by(FileName="test_lyrics.txt").first().SongID

    assert words_in_line(session, 1, -1) == 0
    assert words_in_line(session, 23, song_id) == 0
    assert words_in_line(session, 6, song_id) == 4

    
    assert words_in_line(session, 1, -1, 3) == 0
    assert words_in_line(session, 1, song_id, 23) == 0
    assert words_in_line(session, 11, song_id, 2) == 0
    assert words_in_line(session, 2, song_id, 3) == 3

def test_words_in_verse(session):
    from models import Song

    process_song("lyrics/test_lyrics.txt", session)
    song_id = session.query(Song).filter_by(FileName="test_lyrics.txt").first().SongID

    total = 0
    for i in range(1,7):
        total += words_in_line(session, i, song_id, 3)


    assert words_in_verse(session, 1, -1) == 0
    assert words_in_verse(session, 23, song_id) == 0
    assert words_in_verse(session, 3, song_id) == total

def test_words_in_song(session):
    from models import Song

    process_song("lyrics/test_lyrics.txt", session)
    song_id = session.query(Song).filter_by(FileName="test_lyrics.txt").first().SongID
    total = 0
    for i in range(1,5):
        total += words_in_verse(session, i, song_id)

    assert words_in_song(session, -1) == 0
    assert words_in_song(session, song_id) == total
   

def test_lines_in_verse(session):
    from models import Song

    process_song("lyrics/test_lyrics.txt", session)
    song_id = session.query(Song).filter_by(FileName="test_lyrics.txt").first().SongID

    assert lines_in_verse(session, 1, -1) == 0
    assert lines_in_verse(session, 23, song_id) == 0
    assert lines_in_verse(session, 3, song_id) == 6   

def test_lines_in_song(session):
    from models import Song

    process_song("lyrics/test_lyrics.txt", session)
    song_id = session.query(Song).filter_by(FileName="test_lyrics.txt").first().SongID

    assert lines_in_song(session, -1) == 0
    assert lines_in_song(session, song_id) == 20   


def test_verses_in_song(session):
    from models import Song

    process_song("lyrics/test_lyrics.txt", session)
    song_id = session.query(Song).filter_by(FileName="test_lyrics.txt").first().SongID

    assert verses_in_song(session, -1) == 0
    assert verses_in_song(session, song_id) == 4
