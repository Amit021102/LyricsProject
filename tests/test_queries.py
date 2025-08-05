import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from setup_db import Session  # or however you get a session
from queries import CONTEXT ,wordInSong, wordInLineInSong, wordInVerseInSong, wordInLineInVerseInSong, findWordMatches, findLemmaMatches, findClusterMatches
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

    res1, res2 = findWordMatches("test_word", session)
    assert len(res1) == 4
    for match in res1:
        assert match.word.Text == "test_word"

    assert res1[0].line.LineNumberInSong == 16
    assert res1[1].line.LineNumberInSong == 16
    assert res1[2].line.LineNumberInSong == 17
    assert res1[3].line.LineNumberInSong == 19

    assert res2[0][CONTEXT] == "Test_word test_word"

def test_find_lemma_match(session):
    from models import Lemma

    process_song("lyrics/test_lyrics.txt", session)

    
    res1, res2 = findLemmaMatches("test", session)
    new_res1, new_res2 = [], []

    for i in range(len(res1)):
        if res1[i].song.FileName == "test_lyrics.txt":
            new_res1.append(res1[i])
            new_res2.append(res2[i])
            assert res1[i].word.lemma.Text == "test"

    assert len(new_res1) == 6
    assert new_res1[0].line.LineNumberInSong == 1
    assert new_res1[1].line.LineNumberInSong == 6
    assert new_res1[2].line.LineNumberInSong == 10
    assert new_res1[3].line.LineNumberInSong == 17
    assert new_res1[4].line.LineNumberInSong == 20
    assert new_res1[5].line.LineNumberInSong == 20

    assert new_res2[2][CONTEXT] == "this is a test again"

def test_find_cluster_match(session):
    from models import Word, Cluster, WordInCluster

    process_song("lyrics/test_lyrics.txt", session)

    test_cluster = Cluster(Name="test_digits")
    session.add(test_cluster)
    session.flush()

    for i in range(1, 10):
        digit = session.query(Word).filter_by(Text=str(i)).first()
        print(f'digit {i}\'s id is {digit.WordID}')
        digit_in_cluster = WordInCluster(ClusterID=test_cluster.ClusterID, WordID=digit.WordID)
        session.add(digit_in_cluster)

    session.flush()
    

    print('before')
    res1, res2 = findClusterMatches("test_digits", session)
    new_res1, new_res2 = [], []
    print('after')
    print(f'number of matches in res1 is {len(res1)}')
    print(f'number of matches in res2 is {len(res2)}')

    for i in range(len(res1)):

        print(f'handling with {res1[i].word.Text} of index {res1[i].WordIndex}')

        if res1[i].song.FileName == "test_lyrics.txt":
            new_res1.append(res1[i])
            new_res2.append(res2[i])
            print(f"inserted {new_res1[-1].word.Text}")
            assert res1[i].word.Text.isdigit() == True

    print('continued')

    assert len(new_res1) == 9
    assert new_res1[0].line.LineNumberInSong == 7
    assert new_res1[4].line.LineNumberInSong == 8
    assert new_res1[8].line.LineNumberInSong == 9

    assert new_res2[6][CONTEXT] == "7 8 9"

