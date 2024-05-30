import re

from lmentry.scorers.scorer import LMentryScorer, the_word_regex, the_letter_regex


class LastLetterScorerRu(LMentryScorer):
    """This class was created by simply mirroring `FirstLetterScorer`
    """
    def __init__(self):
        super().__init__()

    def get_base_patterns(self, answer, word):

        of = "(в)"
        a = r"(-|–)"
        ends = "(заканчивается|оканчивается)"
        last = r"(конечная|последняя|финальная)"
        
        base_patterns = [
            rf"{last} буква {a} {answer}",
            rf"{last} буква {of} {word} {a} {answer}",
            rf"{answer} {a} {last} буква {of} слове {word}",
            rf"{answer} {a} {last} буква слова {word}",
            rf"{word} {ends} буквой {answer}",
            rf"{word} {ends} на букву {answer}",
            rf"буква, которой {ends} {word} {a} {answer}",
            rf"буква, на которую {ends} {word} {a} {answer}",
            rf"{answer} {a} {last} буква {of} слове {word}",
            rf"{answer} {a} {last} буква слова {word}",
            rf"буква {answer} стоит в конце слова {word}",
            rf"буква {answer} завершает слово {word}",
            rf"{word}: {answer}",
            rf"{last} буква: {answer}",
        ]

        return base_patterns + self.get_shared_patterns(target=answer)

    def negative_scorer(self, prediction, answer):
        score, certainty = None, None

        if not re.search(rf"\b{answer}\b", prediction):
            score = 0
            certainty = 1

        return score, certainty

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        prediction = self.normalize_prediction(prediction, truncate_prediction)

        metadata = example["metadata"]
        answer = metadata["answer"]
        word = metadata["word"]

        score, certainty = self.negative_scorer(prediction, answer)
        if score is not None:
            return score, certainty

        answer = the_letter_regex(answer)

        score, certainty = self._simple_scorer(prediction, answer)
        if score:
            return score, certainty

        word = the_word_regex(word)
        base_patterns = self.get_base_patterns(answer, word)

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty
