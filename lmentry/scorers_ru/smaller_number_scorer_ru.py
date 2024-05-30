import re

from lmentry.scorers.scorer import LMentryScorer, swap_substrings, the_number_regex


class SmallerNumberScorerRu(LMentryScorer):
    """This class was created by simply mirroring `BiggerNumberScorerRu`
    """

    def __init__(self):
        super().__init__()

        self.prefixes.extend([
            "Из чисел {n1} и {n2} ",
            "Среди чисел {n1} и {n2} ",
            "Между числами {n1} и {n2} ",
        ])

    def get_base_patterns(self, answer, distractor):

        smaller = r"(меньше|меньшее)"

        base_patterns = [
            rf"{answer} {smaller}",
            rf"{answer} {smaller}, чем {distractor}",
            rf"{answer} – {smaller} число",
            rf"{smaller} число – {answer}",
            rf"{smaller} – {answer}",
            rf"{distractor}(\s|)>(\s|){answer}",
            rf"{answer}(\s|)<(\s|){distractor}",
            rf"Число, которое {smaller}, чем {distractor} – {answer}.",
            rf"Число, {smaller}, чем {distractor} – {answer}.",
        ]

        # replace smaller with bigger and swap answer and distractor
        bigger = r"(больше|большее)"

        more_base_patterns = [
            swap_substrings(s, subs1=answer, subs2=distractor).replace(smaller, bigger)
            for s in base_patterns
        ]
        base_patterns.extend(more_base_patterns)

        return base_patterns + self.get_shared_patterns(target=answer)

    def negative_scorer(self, prediction, answer):
        score, certainty = None, None

        alphanumeric_pattern = r"\b[а-я\d]+\b"
        all_alphanumeric_words = re.findall(alphanumeric_pattern, prediction)

        if len(set(all_alphanumeric_words)) == 1:
            answer = str(answer)
            if all_alphanumeric_words[0] != answer:
                score = 0
                certainty = 1

        return score, certainty

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        prediction = self.normalize_prediction(prediction, truncate_prediction)

        metadata = example["metadata"]
        n1 = metadata["n1"]
        n2 = metadata["n2"]
        answer = metadata["answer"]

        score, certainty = self.negative_scorer(prediction, answer)
        if score is not None:
            return score, certainty

        distractor = metadata["distractor"]

        answer = the_number_regex(answer)
        distractor = the_number_regex(distractor)

        score, certainty = self._simple_scorer(prediction, answer)
        if score:
            return score, certainty

        base_patterns = self.get_base_patterns(answer, distractor)
        self.prefix_kwargs = {"n1": n1, "n2": n2}

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty
