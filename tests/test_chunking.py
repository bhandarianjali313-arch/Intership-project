import pytest

from ml.src.preprocessing.chunking import (
    create_word_chunks,
)


def test_short_text_single_chunk():

    text = (
        "one two three four five"
    )

    chunks = create_word_chunks(
        text,
        chunk_size=10,
        overlap=2,
    )

    assert len(chunks) == 1

    assert (
        chunks[0]["word_count"]
        == 5
    )


def test_multiple_chunks():

    text = " ".join(
        str(i)
        for i in range(20)
    )

    chunks = create_word_chunks(
        text,
        chunk_size=10,
        overlap=2,
    )

    assert len(chunks) > 1


def test_chunk_size_limit():

    text = " ".join(
        str(i)
        for i in range(100)
    )

    chunks = create_word_chunks(
        text,
        chunk_size=20,
        overlap=5,
    )

    for chunk in chunks:

        assert (
            chunk["word_count"]
            <= 20
        )


def test_overlap():

    text = (
        "one two three four "
        "five six seven"
    )

    chunks = create_word_chunks(
        text,
        chunk_size=4,
        overlap=1,
    )

    first_words = (
        chunks[0][
            "chunk_text"
        ].split()
    )

    second_words = (
        chunks[1][
            "chunk_text"
        ].split()
    )

    assert (
        first_words[-1]
        == second_words[0]
    )


def test_invalid_overlap():

    with pytest.raises(
        ValueError
    ):

        create_word_chunks(
            "test text",
            chunk_size=10,
            overlap=10,
        )


def test_empty_text():

    chunks = create_word_chunks(
        "",
        chunk_size=10,
        overlap=2,
    )

    assert chunks == []