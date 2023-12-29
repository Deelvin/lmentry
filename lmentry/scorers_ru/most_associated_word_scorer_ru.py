from lmentry.scorers.scorer import LMentryScorer, the_word_regex, the_words_regex, swap_substrings


class MostAssociatedWordScorerRu(LMentryScorer):
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

    def get_base_patterns(self, answer, category):

        most = r"(наиболее|более всего|больше всего|больше|чаще|чаще всего)"
        associated = r"(связано|ассоциируется)"
        most_associated = r"(наиболее|более всего|больше всего|больше|чаще|чаще всего)? (связано|ассоциируется)"
        a = r"(-|–)"

        base_patterns = [
            rf"Слово, которое {most_associated} со словом {category} {a} {answer}",
            rf"Слово, которое {associated} со словом {category} {most} {a} {answer}",
            rf"Слово {category} {most_associated} со словом {answer}",
        ]
        
        # swap answer and category
        more_base_patterns = [
            swap_substrings(s, subs1=answer, subs2=category) for s in base_patterns
        ]
        base_patterns.extend(more_base_patterns)

        return base_patterns + self.get_shared_patterns(target=answer)

    def get_exact_patterns(self, answer, category):
        return [
            rf"{answer}",
            rf"{category} - {answer}"
        ]

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

        exact_patterns = self.get_exact_patterns(answer, category)
        for exact_pattern in exact_patterns:
            score, certainty = self._simple_scorer(prediction, answer=exact_pattern)
            if score:
                return score, certainty

        words = the_words_regex(words)
        of = r"(среди|из)"
        options_pl = r"(слов|вариантов)"
        options_sg = r"(набора слов|списка слов)"
        given_pl = r"(приведённых|приведенных|перечисленных|следующих)"
        given_sg = r"(приведённого|приведенного|перечисленного|следующего)"
        words = rf"{of} ({words}|{given_pl} {options_pl}|{given_sg} {options_sg})"

        base_patterns = self.get_base_patterns(answer, category)

        self.prefix_kwargs = {"words": words}
        self.suffix_kwargs = {"words": words}

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty
