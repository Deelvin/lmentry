import re

from lmentry.scorers.scorer import LMentryScorer, the_word_regex, the_words_regex, swap_substrings


class LeastAssociatedWordScorerRu(LMentryScorer):
    """This class was created by simply mirroring `leastAssociatedWordScorer`
    """
    def __init__(self):
        super().__init__()

        # we use `[^a-zA-Z0-9_]` instead of `\W` as we always lowercase the pattern in
        # `certainty_scorer`. See the to-do suggestion in normalize_string

        self.prefixes.extend([
            r"{words}[^а-яА-ЯёЁ0-9_]*"
        ])

        self.suffixes.extend([
            r"[^а-яА-ЯёЁ0-9_]*{words}"
        ])

    def get_base_patterns(self, answer, category, words):

        least = r"(наименее|менее всего|меньше всего|меньше|реже|реже всего)"
        associated = r"(связано|ассоциируется)"
        least_associated = r"(наименее|менее всего|меньше всего|меньше|реже|реже всего)? (связано|ассоциируется)"
        a = r"(-|–)"

        base_patterns = [
            rf"Слово, которое {least_associated} со словом {category} {a} {answer}",
            rf"Слово, которое {associated} со словом {category} {least} {a} {answer}",
            rf"Слово {category} {least_associated} со словом {answer}",
        ]
        
        # swap answer and category
        more_base_patterns = [
            swap_substrings(s, subs1=answer, subs2=category) for s in base_patterns
        ]
        base_patterns.extend(more_base_patterns)

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

        score, certainty = self.negative_scorer(prediction, answer)
        if score is not None:
            return score, certainty

        category = metadata["category"]
        distractors = metadata["distractors"]
        answer_index = metadata["answer_index"]
        words = distractors[:answer_index] + [answer] + distractors[answer_index:]

        answer = the_word_regex(answer)
        category = the_word_regex(category)
        words = the_words_regex(words)

        of = r"(среди|из)"
        options_pl = r"(слов|вариантов)"
        options_sg = r"(набора слов|списка слов)"
        given_pl = r"(приведённых|приведенных|перечисленных|следующих)"
        given_sg = r"(приведённого|приведенного|перечисленного|следующего)"
        words = rf"{of} ({words}|{given_pl} {options_pl}|{given_sg} {options_sg})"

        score, certainty = self._simple_scorer(prediction, answer)
        if score:
            return score, certainty

        base_patterns = self.get_base_patterns(answer, category, words)

        self.prefix_kwargs = {"words": words}
        self.suffix_kwargs = {"words": words}

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty
