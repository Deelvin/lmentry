import re

from lmentry.scorers.scorer import LMentryScorer, the_word_regex, the_letter_regex


class FirstLetterScorerRu(LMentryScorer):
    def __init__(self):
        super().__init__()

    def get_base_patterns(self, answer, word):

        of = "(в)"
        a = r"(-|–)"
        starts = "(начинается)"
        first = r"(первая|начальная)"
        
        base_patterns = [
            rf"{first} буква {a} {answer}",
            rf"{first} буква {of} {word} {a} {answer}",
            rf"{answer} {a} {first} буква {of} слове {word}",
            rf"{answer} {a} {first} буква слова {word}",
            rf"{word} {starts} с буквы {answer}",
            rf"буква, с которой {starts} {word} {a} {answer}",
            rf"буква, на которую {starts} {word} {a} {answer}",
            rf"{answer} {a} {first} буква {of} слове {word}",
            rf"{answer} {a} {first} буква слова {word}",
            rf"буква {answer} стоит в начале слова {word}",
            rf"буква {answer} начинает слово {word}",
            rf"{word} {starts} с буквы {answer}",
            rf"{word} {starts} буквой {answer}",
            rf"{word}: {answer}",
            rf"{first} буква: {answer}",
        ]
        
        return base_patterns + self.get_shared_patterns(target=answer)

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        prediction = self.normalize_prediction(prediction, truncate_prediction)

        metadata = example["metadata"]
        answer = metadata["answer"]
        word = metadata["word"]

        score, certainty = self.negative_scorer(prediction, answer)
        if score is not None:
            return score, certainty

        answer = the_letter_regex(answer)

        score, certainty = self._simple_scorer(prediction, answer, False)
        if score:
            return score, certainty

        word = the_word_regex(word)

        base_patterns = self.get_base_patterns(answer, word)

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty
