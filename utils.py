import spacy
from models import Song, Verse, Line, Word, Lemma, WordOccurrence, Cluster, WordInCluster
nlp = spacy.load("en_core_web_sm")


# the number of lines added before and after the wanted line in match finding
CONTEXT = 2

def lemmatize(word: str):
    word = word.lower()
    doc = nlp(word)
    return doc[0].lemma_


def limitContext(occurrence: WordOccurrence):
    mid = occurrence.line.LineNumberInSong
    last_line = occurrence.song.NumberOfLines

    begin = max(1, mid - CONTEXT)
    end = min(last_line, mid + CONTEXT)

    return (begin, end)


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
        session.commit()
        print(f"Added '{word_text}' to cluster '{cluster_name}'")

