import re

from lmentry.scorers.scorer import LMentryScorer, the_word_regex, the_letter_regex


class EndsWithLetterScorerRu(LMentryScorer):
    """This class was created by simply mirroring `StartsWithLetterScorer`
    """
    def __init__(self):
        super().__init__()

    def get_base_patterns(self, letter, word):

        word_ = r"(слово|ответ)"
        possible = r"(возможное|возможный|такое|такой|это|этот)"
        ends = r"(заканчивается|оканчивается)"
        ending = r"(конечная|последняя|финальная)"
        a = r"(-|–)"

        base_patterns = [
            rf"{possible} {word_} {a} {word}",
            rf"{word} {a} слово, которое {ends} на букву {letter}",
            rf"{word} {a} слово, последняя буква которого {letter}",
            rf"{word} {a} слово, заканчивающееся на букву {letter}",
            rf"{word} {a} слово, оканчивающееся на букву {letter}",
            rf"{word} {a} слово, в котором {letter} {a} {ending} буква",
            rf"{word} {a} слово, в котором {ending} буква {letter}",
            rf"{word} {ends} на букву {letter}",
            rf"{word} {a} {possible} {word_}",
        ]
        return base_patterns + self.get_shared_patterns(target=word)

    def negative_scorer(self, prediction, letter):
        score, certainty = None, None

        prediction_words = re.findall(r"\b[а-яё]+\b", prediction)

        if all([word[-1] != letter for word in prediction_words]):
            score = 0
            certainty = 1

        return score, certainty

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        prediction = self.normalize_prediction(prediction, truncate_prediction)

        letter = example["metadata"]["letter"]

        score, certainty = self.negative_scorer(prediction, letter)
        if score is not None:
            return score, certainty

        before_the_letter = r"\w+"

        word = rf"{before_the_letter}{letter}"
        word = the_word_regex(word)

        score, certainty = self._simple_scorer(prediction, word)
        if score:
            return score, certainty

        letter = the_letter_regex(letter)

        base_patterns = self.get_base_patterns(letter, word)

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty
