from lmentry.scorers.scorer import LMentryScorer, the_word_regex, the_letter_regex


class WordContainingScorerRu(LMentryScorer):
    def __init__(self):
        super().__init__()

    def get_base_patterns(self, letter, word):

        word_ = r"(слово|ответ)"
        possible = r"(возможное|возможный|такое|такой|это|этот)"
        a = r"(-|–)"
        has = r"(есть|присутствует|имеется)"
        
        base_patterns = [
            rf"{word} {a} слово, которое содержит букву {letter}",
            rf"{word} {a} слово, содержащее букву {letter}",
            rf"{word} {a} слово, в котором {has} буква {letter}",
            rf"{word} {a} слово с буквой {letter}",
            rf"{word} {a} {possible} {word_}",
            rf"слово, которое содержит букву {letter} {a} {word}",
            rf"слово, содержащее букву {letter} {a} {word}",
            rf"слово, в котором {has} буква {letter} {a} {word}",
            rf"слово с буквой {letter} {a} {word}",
        ]

        return base_patterns + self.get_shared_patterns(target=word)

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        prediction = self.normalize_prediction(prediction, truncate_prediction)

        letter = example["metadata"]["letter"]

        word = (rf"\w*{letter}\w*"
                if letter in {"a", "i"}
                else rf"((\w+{letter}\w*)|(\w*{letter}\w+)|({letter}-\w+))"
                # the third option under `else` is for cases like "e-mail" and "x-ray"
                )
        word = the_word_regex(word)

        score, certainty = self._simple_scorer(prediction, word)
        if score:
            return score, certainty

        letter = the_letter_regex(letter)
        base_patterns = self.get_base_patterns(letter, word)

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty
