import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from setup_db import Session  # or however you get a session
from models import Word, Lemma, Song, WordOccurrence
from utils import CONTEXT, lemmatize, limit_context, get_context, get_or_create_word, get_or_create_lemma, add_to_cluster, get_or_create_phrase
from lyricsProgram import process_song

@pytest.fixture
def session():
    session = Session()
    yield session
    session.rollback()  # so we don't keep test data


def test_lemmatize_basic_words():

    lemma1 =  lemmatize("Running")
    lemma2 =  lemmatize("Dogs")
    lemma3 =  lemmatize("HELLO")

    assert lemma1 == "run"
    assert lemma2 == "dog"
    assert lemma3 == "hello"


def test_limit_context(session):
    from models import Song, Line, WordOccurrence

    # Setup
    song = Song(FileName="test_song.txt", NumberOfLines=20)
    session.add(song)
    session.flush()  # Now song.SongID is available

    # Create lines
    lines = []
    for i in range(1, 21):
        line = Line(SongID=song.SongID, LineNumberInSong=i)
        lines.append(line)
    session.add_all(lines)
    session.flush()

    # Helper to create occurrence on a line
    def create_occurrence_on_line(line_number):
        wanted_line = next(l for l in lines if l.LineNumberInSong == line_number)
        occ = WordOccurrence(SongID=song.SongID, LineID=wanted_line.LineID, line=wanted_line, song=song)
        return occ


    # ASSERTIONS SHOULD DEFER FOR DIFFERENT CONTEXT VALUES - current is 2

    # Test start of song
    occ1 = create_occurrence_on_line(1)
    first, last = limit_context(occ1)
    assert first == 1
    assert last == 3  

    # Test middle
    occ10 = create_occurrence_on_line(10)
    first, last = limit_context(occ10)
    assert first == 8
    assert last == 12

    # Test near end
    occ19 = create_occurrence_on_line(19)
    first, last = limit_context(occ19)
    assert first == 17
    assert last == 20

    # Test end
    occ20 = create_occurrence_on_line(20)
    first, last = limit_context(occ20)
    assert first == 18
    assert last == 20


def test_get_context(session):

    process_song("lyrics/test_lyrics.txt", session)
    song_id = session.query(Song).filter_by(FileName="test_lyrics.txt").first().SongID
    id_8 = get_or_create_word(session, "8").WordID
    print(id_8)
    occ_8 = session.query(WordOccurrence).filter_by(WordID=id_8, SongID=song_id).first()
    print(f'occ_8 is None? {occ_8 is None}')

    context = get_context(session, [occ_8])
    print(context)

    assert context[0][CONTEXT] == "7 8 9"
    assert len(context[0]) == 2*CONTEXT + 1



def test_get_or_create_word(session):
    word_text = "unique_test_word"
    word = get_or_create_word(session, word_text)
    
    assert isinstance(word, Word)
    assert word.Text == word_text.lower()
    assert word.TotalOccurrences == 0

    # Test re-fetching the same word doesn't create a new one
    word2 = get_or_create_word(session, word_text)
    assert word.WordID == word2.WordID
   

def test_get_or_create_lemma(session):
    lemma_text = "unique_test_lemma"
    lemma = get_or_create_lemma(session, lemma_text)

    assert isinstance(lemma, Lemma)
    assert lemma.Text == lemma_text.lower()
    assert lemma.TotalOccurrences == 0

    lemma2 = get_or_create_lemma(session, lemma_text)
    assert lemma.LemmaID == lemma2.LemmaID


def test_add_to_cluster(session):
    from models import WordInCluster, Cluster

    word = get_or_create_word(session, "clusterwordtest")
    cluster_name = "cluster_test"  # you must ensure this exists in your DB

    add_to_cluster(session, word.Text, cluster_name)
    cluster = session.query(Cluster).filter_by(Name=cluster_name).first()

    # Query WordInCluster to confirm it was added
    link = session.query(WordInCluster).filter_by(WordID=word.WordID, ClusterID=cluster.ClusterID).first()

    assert link is not None


def test_get_or_create_phrase(session):
    from models import WordInPhrase, Phrase

    test_phrase = get_or_create_phrase(session, "tHis, IS a test?!")

    # Query WordInPhrase to confirm it was added
    words_in_test_phrase = session.query(WordInPhrase).filter_by(PhraseID=test_phrase.PhraseID).all()
    assert len(words_in_test_phrase) == 4

    word_this = session.query(Word).filter_by(Text="this").first()
    word_test = session.query(Word).filter_by(Text="test").first()

    word_this_index = session.query(WordInPhrase).filter_by(PhraseID=test_phrase.PhraseID, WordID=word_this.WordID).first().WordIndexInPhrase
    word_test_index = session.query(WordInPhrase).filter_by(PhraseID=test_phrase.PhraseID, WordID=word_test.WordID).first().WordIndexInPhrase

    assert word_this_index == 1
    assert word_test_index == 4
