import spacy
from models import Song, Verse, Line, Word, Lemma, WordOccurrence
nlp = spacy.load("en_core_web_sm")

# number of lines shown before and after a match - default 0
CONTEXT = 1

def lemmatize(word):
    doc = nlp(word)
    return doc[0].lemma_


def limitContext(occurrence: WordOccurrence):
    mid = occurrence.line.LineNumberInSong
    last_line = occurrence.song.NumberOfLines

    begin = max(1, mid - CONTEXT)
    end = min(last_line, mid + CONTEXT)

    return (begin, end)

