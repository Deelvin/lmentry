import re

from lmentry.scorers.scorer import LMentryScorer, the_word_regex, the_letter_regex


class StartsWithLetterScorerRu(LMentryScorer):
    def __init__(self):
        super().__init__()

    def get_base_patterns(self, letter, word):

        word_ = r"(слово|ответ)"
        possible = r"(возможное|возможный|такое|такой|это|этот)"
        starting = r"(начальная|первая)"
        a = r"(-|–)"

        base_patterns = [
            rf"{possible} {word_} {a} {word}",
            rf"{word} {a} слово, которое начинается на букву {letter}",
            rf"{word} {a} слово, {starting} буква которого {letter}",
            rf"{word} {a} слово, начинающееся на букву {letter}",
            rf"{word} {a} слово, в котором {letter} {a} {starting} буква",
            rf"{word} {a} слово, в котором {starting} буква {a} {letter}",
            rf"{word} начинается на букву {letter}",
            rf"{word} {a} {possible} {word_}",
        ]
        return base_patterns + self.get_shared_patterns(target=word)

    def negative_scorer(self, prediction, letter):
        score, certainty = None, None

        prediction_words = re.findall(r"\b[а-яё]+\b", prediction)

        if all([word[0] != letter for word in prediction_words]):
            score = 0
            certainty = 1

        return score, certainty

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        prediction = self.normalize_prediction(prediction, truncate_prediction)

        letter = example["metadata"]["letter"]

        score, certainty = self.negative_scorer(prediction, letter)
        if score is not None:
            return score, certainty

        after_the_letter = r"\w+"

        word = rf"{letter}-?{after_the_letter}"  # the "-" is for cases like e-mail and x-ray
        word = the_word_regex(word)

        score, certainty = self._simple_scorer(prediction, word)
        if score:
            return score, certainty

        letter = the_letter_regex(letter)

        base_patterns = self.get_base_patterns(letter, word)

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty
