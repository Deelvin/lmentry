import re

from lmentry.scorers.scorer import LMentryScorer, the_word_regex


class EndsWithWordScorerRu(LMentryScorer):
    def __init__(self):
        super().__init__()

        a_ = r"(-|–)"
        sentence_ = r"(предложение|ответ)"
        last_ = r"(конечное|последнее|финальное)"
        possible_ = r"(возможное|возможный|такое|такой|это|этот)"
        ends_ = r"(заканчивается|оканчивается)"

        # we don't want an empty prefix here

        self.prefixes = [
            rf"{possible_} предложение {a_}",
            rf"предложение, которое {ends_} на слово [word] {a_}",
            rf"предложение, {last_} слово которого [word] {a_}",
            rf"предложение, заканчивающееся на слово [word] {a_}",
            rf"предложение, оканчивающееся на слово [word]",
            rf"предложение, в котором [word] {a_} {last_} слово",
            rf"предложение, в котором {last_} слово [word]",
            rf"{possible_} {sentence_} {a_}",
        ]

        self.suffixes = [
            r"$",
            rf"{ends_} на слово [word]",
            rf"{ends_} словом [word]",
            rf"{a_} предложение, которое {ends_} на слово [word]",
            rf"{a_} предложение, которое {ends_} словом [word]",
            rf"{a_} предложение, заканчивающееся {ends_} на слово [word]",
            rf"{a_} предложение, оканчивающееся {ends_} на слово [word]",
            rf"{a_} предложение, в котором [word] {a_} {last_} слово",
            rf"{a_} предложение, в котором {last_} слово [word]",
            rf"{a_} {possible_} {sentence_}",
        ]

        def _replace_arguments(xfixes: list[str]):
            for i in range(len(xfixes)):
                xfixes[i] = xfixes[i].format(
                                             a_=a_,
                                             last_=last_,
                                             word="[word]")  # `word` will be replaced later
        _replace_arguments(self.prefixes)
        _replace_arguments(self.suffixes)

    def get_base_patterns(self, word):

        # we want a word to contain at least two letters, with the exception of "a" and "i"
        valid_word = r"(\w\w+)"
        # we use `[^a-zA-Z0-9_]` instead of `\W` as we always lowercase the pattern in
        # `_certainty_scorer`.
        # we can't tell if the sentence words are actual English words, but as a sanity we demand at
        # least one additional "word" before the ending word
        allowed_sentence = rf".*{valid_word}[^а-яА-ЯёЁ0-9_]+{word}[^а-яА-ЯёЁ0-9_]*"

        base_patterns = [
            allowed_sentence
        ]
        return base_patterns + self.get_shared_patterns(target=allowed_sentence)
    
    def negative_scorer(self, prediction, word):
        score, certainty = None, None

        if not re.search(rf"\b[word]\b", prediction):
            score = 0
            certainty = 1

        return score, certainty

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        prediction = self.normalize_prediction(prediction, truncate_prediction)

        word = example["metadata"]["word"].lower()
        score, certainty = self.negative_scorer(prediction, word)
        if score is not None:
            return score, certainty

        word = the_word_regex(word)

        base_patterns = self.get_base_patterns(word)

        # note that the second case of `_simple_scorer` is not relevant
        score, certainty = self._simple_scorer(prediction, base_patterns[0])
        if score:
            return score, certainty

        self.prefix_kwargs = {"word": word}
        self.suffix_kwargs = {"word": word}

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty
