import re
import math
from collections import Counter
from typing import List, Dict, Optional
import numpy as np
import spacy

# Load spaCy English model (will be used for POS and NER features)
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    import os
    os.system('python -m spacy download en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

# Berechnet die Burstiness (Satzlängen-StdAbw / Mittelwert)
def burstiness(text: str) -> float:
    sentences = re.split(r'[.!?]', text)
    lengths = [len(s.split()) for s in sentences if s.strip()]
    if not lengths or len(lengths) < 2:
        return 0.0
    mean = sum(lengths) / len(lengths)
    variance = sum((l - mean) ** 2 for l in lengths) / (len(lengths) - 1)
    stddev = math.sqrt(variance)
    return stddev / mean if mean else 0.0

# Berechnet die Perplexität mit einfachem n-Gramm-Modell (hier: 2-Gramm)
def perplexity(text: str, n: int = 2) -> float:
    tokens = text.lower().split()
    if len(tokens) < n:
        return 0.0
    ngrams = [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
    counts = Counter(ngrams)
    total = sum(counts.values())
    probs = [count/total for count in counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    return 2 ** entropy

# Berechnet die Vokabularvielfalt (Type-Token-Ratio)
def vocabulary_richness(text: str) -> float:
    tokens = [w for w in re.findall(r'\w+', text.lower())]
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)

# Zählt seltsame Leerzeichen (Unicode)
def count_weird_spaces(text: str) -> int:
    weird_spaces = ['\u200b', '\u00A0', '\u202F']
    return sum(text.count(ws) for ws in weird_spaces)

# Zählt Em-Dashes (—)
def count_em_dashes(text: str) -> int:
    return text.count('—')

# Zählt Auslassungspunkte (…)
def count_ellipses(text: str) -> int:
    return text.count('…')

# Zählt „fancy quotes“
def count_fancy_quotes(text: str) -> int:
    return sum(text.count(q) for q in ['“', '”', '‘', '’'])

# Erkennt typische "Safe Phrases"
def detect_safe_phrases(text: str) -> List[str]:
    phrases = [
        'it is important to note',
        'in conclusion',
        'as previously mentioned',
        'the purpose of this',
        'in summary',
        'this essay will',
        'in this paper',
        'to conclude',
        'in other words',
        'in addition',
    ]
    found = [p for p in phrases if p in text.lower()]
    return found

# Erkennt wiederholte Satzanfänge
def detect_repeated_sentence_starters(text: str) -> List[str]:
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    starters = [s.split()[0].lower() for s in sentences if s]
    counter = Counter(starters)
    return [word for word, count in counter.items() if count > 1]

# Erkennt Slang oder Emojis
def detect_slang_or_emoji(text: str) -> Dict[str, List[str]]:
    slang = ['lol', 'omg', 'brb', 'idk', 'btw', 'lmao', 'rofl', 'smh', 'tbh']
    emojis = re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text)
    found_slang = [w for w in slang if w in text.lower()]
    return {'slang': found_slang, 'emojis': emojis}

# Prüft, ob keine Kontraktionen verwendet werden
def check_no_contractions(text: str) -> bool:
    contractions = ["'s", "n't", "'re", "'ve", "'ll", "'d", "'m"]
    return not any(c in text for c in contractions)

# Erkennt übermäßigen Gebrauch von langen/fancy Wörtern
def check_long_word_overuse(text: str, threshold: int = 10, min_length: int = 10) -> bool:
    words = re.findall(r'\w+', text)
    long_words = [w for w in words if len(w) >= min_length]
    return len(long_words) > threshold

# Syntaktische Komplexität: Durchschnittliche Satzlänge (Wörter)
def avg_sentence_length(text: str) -> float:
    sentences = re.split(r'[.!?]', text)
    lengths = [len(s.split()) for s in sentences if s.strip()]
    return float(np.mean(lengths)) if lengths else 0.0

# Syntaktische Komplexität: Durchschnittliche Wortlänge (Zeichen)
def avg_word_length(text: str) -> float:
    words = re.findall(r'\w+', text)
    lengths = [len(w) for w in words]
    return float(np.mean(lengths)) if lengths else 0.0

# Lesbarkeit: Flesch Reading Ease (Englisch)
def flesch_reading_ease(text: str) -> float:
    words = re.findall(r'\w+', text)
    sentences = re.split(r'[.!?]', text)
    syllables = sum(count_syllables(w) for w in words)
    num_words = len(words)
    num_sentences = len([s for s in sentences if s.strip()])
    if num_words == 0 or num_sentences == 0:
        return 0.0
    return 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (syllables / num_words)

# Hilfsfunktion: Zählt Silben in einem Wort (grob)
def count_syllables(word: str) -> int:
    word = word.lower()
    return max(1, len(re.findall(r'[aeiouy]+', word)))

# Kohärenz: Kosinus-Ähnlichkeit zwischen Satz-Embeddings (Bag-of-Words, einfach)
def coherence_score(text: str) -> float:
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    if len(sentences) < 2:
        return 1.0
    # Bag-of-words Vektor für jeden Satz
    vocab = list(set(w for s in sentences for w in s.lower().split()))
    vecs = []
    for s in sentences:
        vec = np.array([s.lower().split().count(w) for w in vocab])
        vecs.append(vec)
    # Kosinus-Ähnlichkeit zwischen benachbarten Sätzen
    sims = []
    for i in range(len(vecs) - 1):
        v1, v2 = vecs[i], vecs[i+1]
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            sims.append(0.0)
        else:
            sims.append(float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))))
    return float(np.mean(sims)) if sims else 0.0

def detect_special_unicode_characters(text: str) -> int:
    """
    Counts the number of special (non-ASCII, non-standard) Unicode characters in the text.
    Excludes common punctuation and whitespace.
    """
    return sum(1 for c in text if ord(c) > 127 and c not in ['—', '…', '“', '”', '‘', '’'])

def count_overused_words(text: str, threshold: int = 10, per_words: int = 1000) -> int:
    """
    Counts the number of words that appear more than 'threshold' times per 'per_words' words.
    """
    words = re.findall(r'\w+', text.lower())
    if not words:
        return 0
    word_count = Counter(words)
    scale = max(1, len(words) / per_words)
    return sum(1 for w, c in word_count.items() if c / scale > threshold)

def flesch_kincaid_grade_level(text: str) -> float:
    """
    Computes the Flesch-Kincaid Grade Level for English text.
    """
    words = re.findall(r'\w+', text)
    sentences = re.split(r'[.!?]', text)
    syllables = sum(count_syllables(w) for w in words)
    num_words = len(words)
    num_sentences = len([s for s in sentences if s.strip()])
    if num_words == 0 or num_sentences == 0:
        return 0.0
    return 0.39 * (num_words / num_sentences) + 11.8 * (syllables / num_words) - 15.59

# Try to use spaCy for POS tagging, fallback to NLTK or regex
try:
    import spacy
    nlp = spacy.load('en_core_web_sm')
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False
    try:
        import nltk
        from nltk import pos_tag, word_tokenize
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        NLTK_AVAILABLE = True
    except Exception:
        NLTK_AVAILABLE = False

def noun_to_verb_ratio(text: str) -> float:
    """
    Computes the ratio of nouns to verbs in the text.
    """
    words = re.findall(r'\w+', text)
    if not words:
        return 0.0
    if SPACY_AVAILABLE:
        doc = nlp(text)
        nouns = sum(1 for token in doc if token.pos_ == 'NOUN')
        verbs = sum(1 for token in doc if token.pos_ == 'VERB')
    elif 'NLTK_AVAILABLE' in globals() and NLTK_AVAILABLE:
        tags = pos_tag(word_tokenize(text))
        nouns = sum(1 for word, tag in tags if tag.startswith('NN'))
        verbs = sum(1 for word, tag in tags if tag.startswith('VB'))
    else:
        # Fallback: crude regex for verbs/nouns
        nouns = sum(1 for w in words if w.endswith('ion') or w.endswith('ment') or w.endswith('ness'))
        verbs = sum(1 for w in words if w.endswith('ing') or w.endswith('ed'))
    return (nouns / verbs) if verbs else 0.0

def personal_pronoun_ratio(text: str) -> float:
    """
    Computes the ratio of first-person personal pronouns to total words.
    """
    pronouns = {'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours'}
    words = re.findall(r'\w+', text.lower())
    if not words:
        return 0.0
    pronoun_count = sum(1 for w in words if w in pronouns)
    return pronoun_count / len(words)

def pos_tag_distribution(text: str) -> dict:
    """
    Returns the ratio of nouns, verbs, and adjectives to total tokens using spaCy POS tagging.
    """
    doc = nlp(text)
    total = len([token for token in doc if token.is_alpha])
    if total == 0:
        return {'noun_ratio': 0.0, 'verb_ratio': 0.0, 'adj_ratio': 0.0}
    noun_count = sum(1 for token in doc if token.pos_ == 'NOUN')
    verb_count = sum(1 for token in doc if token.pos_ == 'VERB')
    adj_count = sum(1 for token in doc if token.pos_ == 'ADJ')
    return {
        'noun_ratio': noun_count / total,
        'verb_ratio': verb_count / total,
        'adj_ratio': adj_count / total
    }

def named_entity_density(text: str) -> float:
    """
    Returns the number of named entities per 100 words using spaCy NER.
    """
    doc = nlp(text)
    num_words = len([token for token in doc if token.is_alpha])
    if num_words == 0:
        return 0.0
    num_entities = len([ent for ent in doc.ents])
    return (num_entities / num_words) * 100

def repeated_ngrams(text: str, n: int = 3, min_repeats: int = 2) -> int:
    """
    Returns the number of unique n-grams (of length n) that are repeated at least min_repeats times in the text.
    """
    tokens = [w for w in re.findall(r'\w+', text.lower())]
    if len(tokens) < n:
        return 0
    ngrams = [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
    counts = Counter(ngrams)
    repeated = [ng for ng, c in counts.items() if c >= min_repeats]
    return len(repeated) 