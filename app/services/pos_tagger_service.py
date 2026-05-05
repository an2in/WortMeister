from __future__ import annotations


class POSTaggerService:
    """Assign a lightweight POS tag using German-oriented heuristics."""

    _NOUN_ARTICLES = {"der", "die", "das"}
    _VERB_SUFFIXES = ("en", "eln", "ern")
    _ADJECTIVE_SUFFIXES = ("ig", "lich", "isch", "los", "bar", "sam", "haft")
    _ADVERB_SUFFIXES = ("erweise",)

    def detect(self, word: str, article: str = "") -> str:
        normalized_word = word.strip()
        normalized_article = article.strip().lower()
        lower_word = normalized_word.lower()

        if normalized_article in self._NOUN_ARTICLES:
            return "noun"
        if normalized_word[:1].isupper():
            return "noun"
        if lower_word.endswith(self._VERB_SUFFIXES):
            return "verb"
        if lower_word.endswith(self._ADJECTIVE_SUFFIXES):
            return "adjective"
        if lower_word.endswith(self._ADVERB_SUFFIXES):
            return "adverb"
        return "other"
