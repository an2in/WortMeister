from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextToken:
    text: str
    start: int
    end: int


def scan_word_tokens(text: str) -> list[TextToken]:
    tokens: list[TextToken] = []
    index = 0

    while index < len(text):
        if not _is_word_char(text[index]):
            index += 1
            continue

        start = index
        while index < len(text) and _is_word_char(text[index]):
            index += 1
        tokens.append(TextToken(text=text[start:index], start=start, end=index))

    return tokens


def contains_whole_word(text: str, target: str) -> bool:
    normalized_target = target.casefold()
    for token in scan_word_tokens(text):
        if token.text.casefold() == normalized_target:
            return True
    return False


def compact_whitespace(value: str) -> str:
    parts: list[str] = []
    current: list[str] = []

    for char in value.strip().lower():
        if char.isspace():
            if current:
                parts.append("".join(current))
                current = []
        else:
            current.append(char)

    if current:
        parts.append("".join(current))

    return " ".join(parts)


def is_safe_identifier(value: str, min_length: int = 8, max_length: int = 64) -> bool:
    if len(value) < min_length or len(value) > max_length:
        return False
    for char in value:
        if not (char.isascii() and (char.isalnum() or char in "_-")):
            return False
    return True


def _is_word_char(char: str) -> bool:
    return char.isalpha() or char == "-"
