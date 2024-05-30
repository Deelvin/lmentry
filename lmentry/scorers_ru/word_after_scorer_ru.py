import re

from lmentry.scorers.scorer import LMentryScorer, the_sentence_regex, the_word_regex, swap_substrings


class WordAfterScorerRu(LMentryScorer):
    def __init__(self):
        super().__init__()

        self.prefixes.extend([
            "В предложении {sentence} ",
        ])

        self.suffixes.extend([
            " (в) {sentence}",
        ])

    def get_base_patterns(self, answer, query, sentence):

        a = r"(-|–)"
        after = r"(прямо |непосредственно )?после"
        follows = r"(прямо |непосредственно )?следует за"
        comes = r"(идёт|стоит|располагается)"

        base_patterns = [
            rf"{answer} {comes} {after} {query}",
            rf"{answer} {a} слово, которое {comes} {after} {query}",
            rf"{answer} {follows} {query}",
            rf"Слово, которое {comes} {after} {query} {a} {answer}",
            rf"Слово, которое {comes} {after} {query} в предложении {sentence} {a} {answer}",
            rf"Слово, которое {follows} {query} {a} {answer}",
        ]

        # replace after with before and swap answer and query
        before = r"(прямо |непосредственно )?перед"
        more_base_patterns1 = [
            swap_substrings(s, subs1=answer, subs2=query).replace(after, before)
            for s in base_patterns
            if after in s
        ]
        base_patterns.extend(more_base_patterns1)

        return base_patterns + self.get_shared_patterns(target=answer)

    def negative_scorer(self, prediction, answer, sentence):
        score, certainty = None, None

        if not re.search(rf"\b{answer}\b", prediction):
            score = 0
            certainty = 1

        if re.sub(r'[^\w ]+', '', prediction) == sentence:
            score = 0
            certainty = 1

        return score, certainty

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        prediction = self.normalize_prediction(prediction, truncate_prediction)

        metadata = example["metadata"]
        answer = metadata["answer"]
        query = metadata["query"]
        sentence = metadata["sentence"]

        # in the word after/before tasks, the sentence, the answer, and the query are saved in their
        # original case as many sentence words are named entities. in scoring, we choose to ignore
        # the case.
        answer = answer.lower()
        query = query.lower()
        sentence = sentence.lower()

        score, certainty = self.negative_scorer(prediction, answer, sentence)
        if score is not None:
            return score, certainty

        answer = the_word_regex(answer)
        query = the_word_regex(query)
        sentence = the_sentence_regex(sentence)

        score, certainty = self._simple_scorer(prediction, answer)
        if score:
            return score, certainty

        base_patterns = self.get_base_patterns(answer, query, sentence)
        self.prefix_kwargs = {"sentence": sentence}
        self.suffix_kwargs = {"sentence": sentence}

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty
