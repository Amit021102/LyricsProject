import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from setup_db import Session  # or however you get a session
from queries import wordInSong, wordInLineInSong, wordInVerseInSong, wordInLineInVerseInSong
from lyricsProgram import process_song


@pytest.fixture
def session():
    session = Session()
    yield session
    session.rollback()  # so we don't keep test data


def test_word_in_song(session):

    process_song("lyrics/test_lyrics.txt", session)

    assert wordInSong(2, "not_test_lyrics.txt", session) is None
    assert wordInSong(56, "test_lyrics.txt", session) is None
    assert wordInSong(12, "test_lyrics.txt", session) == "h"



