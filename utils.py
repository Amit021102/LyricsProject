import spacy
from models import Song, Verse, Line, Word, Lemma, WordOccurrence, Cluster, WordInCluster, Phrase, WordInPhrase
nlp = spacy.load("en_core_web_sm")


# the number of lines added before and after the wanted line in match finding
CONTEXT = 2

def lemmatize(word: str):
    word = word.lower()
    doc = nlp(word)
    return doc[0].lemma_

def limit_context(occurrence: WordOccurrence):
    mid = occurrence.line.LineNumberInSong
    last_line = occurrence.song.NumberOfLines

    begin = max(1, mid - CONTEXT)
    end = min(last_line, mid + CONTEXT)

    return (begin, end)

def get_context(session, matches: list[WordOccurrence]):
    
    if not matches:
        return []
    
    contexts = []
    for instance in matches:
        context = []
        begin, end = limit_context(instance)
        for i in range(begin, end+1):
            line_text = session.query(Line).filter_by(SongID=instance.SongID, LineNumberInSong=i).first().Text
            context.append(line_text)
        contexts.append(context)

    return contexts


def get_or_create_word(session, word_text: str):
    # ensuriong lower-cased and non-blanks word
    normalized = word_text.lower().strip()
    word = session.query(Word).filter_by(Text=normalized).first()
    if word:
        word.lemma.TotalOccurrences += 1
        return word

    lemma = get_or_create_lemma(session, normalized)
    lemma.TotalOccurrences += 1
    word = Word(Text=normalized, LemmaID=lemma.LemmaID, WordLength=len(normalized), TotalOccurrences=0)
    session.add(word)
    session.flush()  # So it gets a WordID before commit
    return word

def get_or_create_lemma(session, word_text: str):
    lemma_text = lemmatize(word_text)
    lemma = session.query(Lemma).filter_by(Text=lemma_text).first()
    if lemma:
        return lemma

    lemma = Lemma(Text=lemma_text, TotalOccurrences=0)
    session.add(lemma)
    session.flush()
    return lemma


# THE 2 METHODS DO NOT SUPPORT ADDING THE DESCRIPTION JUST YET!
# ADD THAT IN THE FUTURE

def add_to_cluster(session, word_text: str, cluster_name: str):

    # LATER - check that word_text is valid
    normalized = word_text.lower().strip()
    word = get_or_create_word(session, normalized)
    cluster = session.query(Cluster).filter_by(Name=cluster_name).first()
    
    if not cluster:
        cluster = Cluster(Name=cluster_name)
        session.add(cluster)
        session.flush()

    exists = session.query(WordInCluster).filter_by(WordID=word.WordID, ClusterID=cluster.ClusterID).first()
    if exists:
        print(f"'{word_text}' is already in cluster '{cluster_name}'")
    else:
        session.add(WordInCluster(WordID=word.WordID, ClusterID=cluster.ClusterID))
        session.flush()
        print(f"Added '{word_text}' to cluster '{cluster_name}'")

def get_or_create_phrase(session, phrase_words: str):
    import re

    valid_phrase = re.sub(r"[^\w\s]", ' ', phrase_words).strip()

    phrase = session.query(Phrase).filter_by(Name=valid_phrase).first()
    # if the phrase already exists
    if phrase:
        return phrase
    # if not, we create it:
    phrase = Phrase(Name=valid_phrase)
    session.add(phrase)
    session.flush()

    indexInPhrase = 1
    parts = valid_phrase.split()
    for part in parts:
        part = part.lower()
        word = get_or_create_word(session, part)
        phraseWord = WordInPhrase(PhraseID=phrase.PhraseID, WordIndexInPhrase=indexInPhrase, WordID=word.WordID)
        session.add(phraseWord)
        indexInPhrase += 1

    session.commit()
    return phrase

