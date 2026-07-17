"""
Pure-function tests for local_detection.py. No mocking needed — every function
here is deterministic given fixed input text.

Primary coverage is on perplexity, coherence_score, and named_entity_density,
since those are the three bot.py actually imports and uses (as LLM-judge
context and fallback-scorer inputs). Everything else gets one smoke test —
they're not on the live detection path, so deep coverage isn't worth the
investment.
"""
import local_detection as ld


# --- perplexity ---

def test_perplexity_empty_string_is_zero():
    assert ld.perplexity("") == 0.0


def test_perplexity_below_ngram_threshold_is_zero():
    # n=2 by default; a single token can't form a bigram
    assert ld.perplexity("word") == 0.0


def test_perplexity_repeated_bigrams_lower_than_varied_text():
    repeated = "the cat the cat the cat the cat the cat"
    varied = "the cat sat on a warm windowsill watching birds fly past quietly"
    assert ld.perplexity(repeated) < ld.perplexity(varied)


# --- coherence_score ---

def test_coherence_single_sentence_is_one():
    assert ld.coherence_score("Just one sentence here.") == 1.0


def test_coherence_empty_string_is_one():
    # re.split on an empty string yields no non-empty sentences -> short-circuit
    assert ld.coherence_score("") == 1.0


def test_coherence_identical_sentences_is_one():
    text = "The dog ran fast. The dog ran fast."
    assert ld.coherence_score(text) == 1.0


def test_coherence_disjoint_sentences_is_zero():
    text = "Quantum physics equations. Bake the cake slowly."
    assert ld.coherence_score(text) == 0.0


# --- named_entity_density ---

def test_named_entity_density_empty_string_is_zero():
    assert ld.named_entity_density("") == 0.0


def test_named_entity_density_no_entities_is_zero():
    assert ld.named_entity_density("i like to eat food and walk around") == 0.0


def test_named_entity_density_with_entities_is_positive():
    assert ld.named_entity_density("Barack Obama visited Paris last year.") > 0.0


# --- smoke tests for everything else ---

def test_burstiness_smoke():
    assert ld.burstiness("Short one. This one is a fair bit longer than the first.") >= 0.0
    assert ld.burstiness("") == 0.0


def test_vocabulary_richness_smoke():
    assert ld.vocabulary_richness("") == 0.0
    assert 0.0 < ld.vocabulary_richness("the cat sat on the mat") <= 1.0


def test_count_weird_spaces_smoke():
    assert ld.count_weird_spaces("no weird spaces here") == 0
    assert ld.count_weird_spaces("has​a zero-width space") == 2


def test_count_em_dashes_and_ellipses_smoke():
    assert ld.count_em_dashes("a — b — c") == 2
    assert ld.count_ellipses("wait… what…") == 2


def test_count_fancy_quotes_smoke():
    assert ld.count_fancy_quotes('plain "quotes" only') == 0
    assert ld.count_fancy_quotes("“fancy” and ‘these’") == 4


def test_detect_safe_phrases_smoke():
    assert ld.detect_safe_phrases("nothing special here") == []
    assert "in conclusion" in ld.detect_safe_phrases("In conclusion, this is done.")


def test_detect_repeated_sentence_starters_smoke():
    assert ld.detect_repeated_sentence_starters("Unique start. Another beginning.") == []
    result = ld.detect_repeated_sentence_starters("I went home. I ate food. I slept.")
    assert "i" in result


def test_detect_slang_or_emoji_smoke():
    result = ld.detect_slang_or_emoji("lol that's great 😀")
    assert "lol" in result["slang"]
    assert len(result["emojis"]) == 1


def test_check_no_contractions_smoke():
    assert ld.check_no_contractions("I do not think so") is True
    assert ld.check_no_contractions("I don't think so") is False


def test_check_long_word_overuse_smoke():
    assert ld.check_long_word_overuse("short simple words") is False


def test_avg_sentence_length_and_word_length_smoke():
    assert ld.avg_sentence_length("") == 0.0
    assert ld.avg_word_length("") == 0.0
    assert ld.avg_sentence_length("one two three.") == 3.0


def test_flesch_reading_ease_and_grade_level_zero_on_empty():
    assert ld.flesch_reading_ease("") == 0.0
    assert ld.flesch_kincaid_grade_level("") == 0.0


def test_count_syllables_smoke():
    assert ld.count_syllables("cat") >= 1
    assert ld.count_syllables("beautiful") >= 1


def test_detect_special_unicode_characters_smoke():
    assert ld.detect_special_unicode_characters("plain ascii text") == 0
    assert ld.detect_special_unicode_characters("emoji 😀 here") == 1


def test_count_overused_words_smoke():
    assert ld.count_overused_words("") == 0


def test_noun_to_verb_ratio_smoke():
    assert ld.noun_to_verb_ratio("") == 0.0
    assert ld.noun_to_verb_ratio("The dog runs and jumps over the fence") >= 0.0


def test_personal_pronoun_ratio_smoke():
    assert ld.personal_pronoun_ratio("") == 0.0
    assert ld.personal_pronoun_ratio("I think my dog likes me") > 0.0


def test_pos_tag_distribution_smoke():
    result = ld.pos_tag_distribution("")
    assert result == {"noun_ratio": 0.0, "verb_ratio": 0.0, "adj_ratio": 0.0}


def test_repeated_ngrams_smoke():
    assert ld.repeated_ngrams("too short") == 0
    text = "the quick fox the quick fox the quick fox"
    assert ld.repeated_ngrams(text, n=3, min_repeats=2) > 0
