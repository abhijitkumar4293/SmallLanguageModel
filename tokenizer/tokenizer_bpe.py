"""
A minimal byte-level BPE tokenizer implemented from scratch.

- No external tokenization libraries.
- Uses only Python stdlib + (optional) numpy/torch for downstream.
- Suitable for Hinglish + emojis because it tokenizes UTF-8 bytes.

This is NOT optimized for huge corpora. It's meant to be correct, readable,
and a good foundation. We'll later optimize if needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable, Optional
from collections import Counter, defaultdict
import json
import os
from pathlib import Path


# ----------------------------
# Helpers: reading data safely
# ----------------------------

def iter_text_lines(directory: str) -> Iterable[str]:
    """
    Stream lines from all .txt files in a directory.
    - We read as UTF-8 and replace invalid bytes.
    - Yields one line at a time so we don't load everything into memory.
    """
    dir_path = Path(directory)
    for filepath in sorted(dir_path.glob("*.txt")):
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip("\n")
                if line.strip() == "":
                    # Skip empty lines; you can keep them if you want as separators.
                    continue
                yield line


def text_to_bytes(text: str) -> bytes:
    """
    Convert Python string to UTF-8 bytes.
    Byte-level tokenization is robust across languages and emojis.
    """
    return text.encode("utf-8", errors="replace")


# ----------------------------
# BPE training representation
# ----------------------------

def bytes_to_initial_symbols(b: bytes) -> Tuple[int, ...]:
    """
    Represent a byte string as a tuple of integers in [0..255].
    Each integer is a base 'symbol' before BPE merges.
    """
    return tuple(b)


def get_pair_frequencies(words: Counter[Tuple[int, ...]]) -> Counter[Tuple[int, int]]:
    """
    Count frequencies of adjacent symbol pairs across the corpus.

    words:
      Counter mapping (symbol_tuple) -> count
      Example symbol_tuple: (72, 101, 108, 108, 111) for b"Hello"

    returns:
      Counter mapping (sym_i, sym_{i+1}) -> frequency
    """
    pair_freq = Counter()

    for sym_tuple, count in words.items():
        if len(sym_tuple) < 2:
            continue
        # Count adjacent pairs in this token sequence.
        for i in range(len(sym_tuple) - 1):
            pair = (sym_tuple[i], sym_tuple[i + 1])
            pair_freq[pair] += count

    return pair_freq


def merge_pair_in_word(word: Tuple[int, ...], pair: Tuple[int, int], new_symbol: int) -> Tuple[int, ...]:
    """
    Replace occurrences of a given adjacent pair in a single word with new_symbol.

    Example:
      word = (97, 98, 99, 98)   # a b c b
      pair = (98, 99)           # b c
      new_symbol = 300

      => (97, 300, 98)
    """
    a, b = pair
    out: List[int] = []
    i = 0

    while i < len(word):
        # If we see the pair at positions i and i+1, merge it.
        if i < len(word) - 1 and word[i] == a and word[i + 1] == b:
            out.append(new_symbol)
            i += 2  # skip both symbols
        else:
            out.append(word[i])
            i += 1

    return tuple(out)


def apply_merge(words: Counter[Tuple[int, ...]], pair: Tuple[int, int], new_symbol: int) -> Counter[Tuple[int, ...]]:
    """
    Apply a merge (pair -> new_symbol) across the entire corpus 'words' counter.
    Returns a new Counter with updated symbol tuples.
    """
    updated = Counter()

    for sym_tuple, count in words.items():
        new_tuple = merge_pair_in_word(sym_tuple, pair, new_symbol)
        updated[new_tuple] += count

    return updated


# ----------------------------
# Tokenizer object
# ----------------------------

@dataclass
class ByteBPE:
    """
    A minimal byte-level BPE tokenizer.

    - base_vocab: token_id -> bytes for ids [0..255] (single-byte tokens)
    - merges: list of merges in order: ((a,b), new_id)
    - token_to_bytes: token_id -> bytes (including merged tokens)
    - bytes_to_token: bytes -> token_id (reverse map for decoding)
    """
    merges: List[Tuple[Tuple[int, int], int]]
    token_to_bytes: Dict[int, bytes]
    bytes_to_token: Dict[bytes, int]

    @staticmethod
    def train(
        corpus_dir: str,
        vocab_size: int = 50000,
        max_lines: Optional[int] = None,
        verbose: bool = True,
    ) -> "ByteBPE":
        """
        Train a byte-level BPE tokenizer.

        Args:
          corpus_dir: directory containing .txt files (already cleaned pretrain corpus).
          vocab_size: desired final vocab size. Must be >= 256.
          max_lines: optional cap for training speed while debugging.
          verbose: print progress.

        Returns:
          A trained ByteBPE tokenizer.
        """
        assert vocab_size >= 256, "vocab_size must be at least 256 for byte-level tokens."

        # 1) Initialize base vocab: each byte value is its own token.
        token_to_bytes: Dict[int, bytes] = {i: bytes([i]) for i in range(256)}
        bytes_to_token: Dict[bytes, int] = {v: k for k, v in token_to_bytes.items()}

        # We'll allocate new token IDs starting from 256 upward.
        next_token_id = 256

        # 2) Build a Counter of "words" (here: each line as a sequence of bytes).
        # Using a Counter compresses duplicates: repeated lines don't reappear many times.
        words: Counter[Tuple[int, ...]] = Counter()

        line_count = 0
        for line in iter_text_lines(corpus_dir):
            b = text_to_bytes(line)
            sym_tuple = bytes_to_initial_symbols(b)
            words[sym_tuple] += 1

            line_count += 1
            if max_lines is not None and line_count >= max_lines:
                break

        if verbose:
            print(f"[train] Loaded {line_count} lines into Counter with {len(words)} unique sequences.")

        merges: List[Tuple[Tuple[int, int], int]] = []

        # 3) Iteratively merge the most frequent adjacent pair until reaching vocab_size.
        target_new_tokens = vocab_size - 256
        for step in range(target_new_tokens):
            pair_freq = get_pair_frequencies(words)
            if not pair_freq:
                if verbose:
                    print("[train] No more pairs to merge. Stopping early.")
                break

            # Most common pair in the corpus.
            best_pair, best_count = pair_freq.most_common(1)[0]

            # Create new token for this merged pair.
            new_id = next_token_id
            next_token_id += 1

            # Save merge rule (order matters!)
            merges.append((best_pair, new_id))

            # Create the bytes representation for the new token:
            # bytes(new_token) = bytes(token_a) + bytes(token_b)
            a, b = best_pair
            token_to_bytes[new_id] = token_to_bytes[a] + token_to_bytes[b]
            bytes_to_token[token_to_bytes[new_id]] = new_id

            # Apply the merge across all sequences.
            words = apply_merge(words, best_pair, new_id)

            if verbose and (step + 1) % 200 == 0:
                print(f"[train] step={step+1}/{target_new_tokens} merged={best_pair} freq={best_count} vocab={new_id+1}")

        if verbose:
            print(f"[train] Done. Final vocab size = {len(token_to_bytes)} merges = {len(merges)}")

        return ByteBPE(merges=merges, token_to_bytes=token_to_bytes, bytes_to_token=bytes_to_token)

    def encode(self, text: str) -> List[int]:
        """
        Encode text into token IDs by:
        1) converting to bytes
        2) starting from byte tokens
        3) applying merges in training order

        Note: This naive implementation applies merges by scanning each time.
        It's correct but not the fastest. Good for learning + smaller corpora.
        """
        b = text_to_bytes(text)
        # Start with a list of base byte token IDs (0..255).
        ids = list(b)

        # Apply merges in order. Each merge replaces adjacent ids (a,b) with new_id.
        for (a, b_pair), new_id in self.merges:
            # a is a tuple (sym1, sym2); name it clearly:
            sym1, sym2 = a

            out: List[int] = []
            i = 0
            while i < len(ids):
                if i < len(ids) - 1 and ids[i] == sym1 and ids[i + 1] == sym2:
                    out.append(new_id)
                    i += 2
                else:
                    out.append(ids[i])
                    i += 1
            ids = out

        return ids

    def decode(self, token_ids: List[int]) -> str:
        """
        Decode token IDs back into text by concatenating their byte strings.
        """
        out_bytes = b"".join(self.token_to_bytes[t] for t in token_ids)
        return out_bytes.decode("utf-8", errors="replace")

    def save(self, path: str) -> None:
        """
        Save merges + token bytes to disk as JSON.
        (Bytes are stored as lists of ints for portability.)
        """
        obj = {
            "merges": [([int(p[0][0]), int(p[0][1])], int(p[1])) for p in self.merges],
            "token_to_bytes": {str(k): list(v) for k, v in self.token_to_bytes.items()},
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f)

    @staticmethod
    def load(path: str) -> "ByteBPE":
        """
        Load tokenizer from JSON saved by save().
        """
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)

        merges = [((pair[0], pair[1]), new_id) for pair, new_id in obj["merges"]]
        token_to_bytes = {int(k): bytes(v) for k, v in obj["token_to_bytes"].items()}
        bytes_to_token = {v: k for k, v in token_to_bytes.items()}

        return ByteBPE(merges=merges, token_to_bytes=token_to_bytes, bytes_to_token=bytes_to_token)


def build_training_tokens(
    tokenizer: ByteBPE,
    corpus_dir: str,
    out_path: str,
    max_lines: Optional[int] = None,
) -> None:
    """
    Convert your corpus into a stream of token IDs and write them as one integer per line.

    Why "one int per line"?
    - dead simple format
    - easy to memory-map later
    - can be chunked into fixed-length sequences for training

    Output file example:
      102
      55
      301
      9
      ...
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as w:
        line_count = 0
        for line in iter_text_lines(corpus_dir):
            ids = tokenizer.encode(line)
            for t in ids:
                w.write(str(t) + "\n")

            # Add an explicit separator between lines. You can also omit this.
            # We use token 10 (newline byte) as a natural separator.
            w.write("10\n")

            line_count += 1
            if max_lines is not None and line_count >= max_lines:
                break

    print(f"[build_training_tokens] Wrote tokens to: {out_path}")


if __name__ == "__main__":
    # Example usage:
    # 1) Train tokenizer on your processed corpus directory.
    corpus_dir = "data/raw"

    tok = ByteBPE.train(corpus_dir=corpus_dir, vocab_size=50000, max_lines=None, verbose=True)
    tok.save("tokenizer/bpe_tokenizer.json")

    # 2) Convert corpus to token IDs for training.
    build_training_tokens(tok, corpus_dir, out_path="data/processed/pretrain_tokens.txt")
