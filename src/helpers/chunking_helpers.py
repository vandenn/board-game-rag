# Based on:
# https://weaviate.io/developers/academy/py/standalone/chunking/example_chunking

from typing import List

from src.settings import CHUNK_OVERLAP, CHUNK_SIZE


def word_splitter(source_text: str) -> List[str]:
    import re

    source_text = re.sub(r"\s+", " ", source_text)  # Replace multiple whitespces
    return re.split(r"\s", source_text)  # Split by single whitespace


def get_chunks_fixed_size_with_overlap(
    text: str, chunk_size: int, overlap_fraction: float
) -> List[str]:
    text_words = word_splitter(text)
    overlap_int = int(chunk_size * overlap_fraction)
    chunks = []
    for i in range(0, len(text_words), chunk_size):
        chunk = " ".join(text_words[max(i - overlap_int, 0) : i + chunk_size])
        chunks.append(chunk)
    return chunks


def chunk_rules(rules):
    rules_chunks = []
    for i, chunk in enumerate(
        get_chunks_fixed_size_with_overlap(rules["content"], CHUNK_SIZE, CHUNK_OVERLAP)
    ):
        # We also store the chunk index to determine order if we were to use it for reconstructing a rules page
        # in a downstream task.
        rules_chunks.append({**rules, "content": chunk, "chunk_index": i})
    return rules_chunks
