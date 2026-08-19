from ml.src.preprocessing.text_cleaning import (
    clean_legal_text,
    count_words,
)


def test_whitespace_normalization():

    text = (
        "This   Agreement\n\n"
        "shall\tterminate."
    )

    result = clean_legal_text(
        text
    )

    assert result == (
        "This Agreement shall terminate."
    )


def test_html_decoding():

    text = (
        "Company A &amp; Company B"
    )

    result = clean_legal_text(
        text
    )

    assert result == (
        "Company A & Company B"
    )


def test_empty_text():

    assert clean_legal_text("") == ""


def test_word_count():

    text = (
        "This Agreement terminates today."
    )

    assert count_words(text) == 4


def test_legal_symbols_preserved():

    text = (
        "Payment shall not exceed $5,000,000."
    )

    result = clean_legal_text(
        text
    )

    assert "$5,000,000" in result