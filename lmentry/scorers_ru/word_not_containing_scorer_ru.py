import re
import string

from lmentry.scorers.scorer import LMentryScorer, the_word_regex, the_letter_regex


class WordNotContainingScorerRu(LMentryScorer):
    def __init__(self):
        super().__init__()

    def get_base_patterns(self, letter, word):

        word_ = r"(слово|ответ)"
        possible = r"(возможное|возможный|такое|такой|это|этот)"
        a = r"(-|–)"
        
        base_patterns = [
            rf"{word} {a} слово, которое не содержит букву {letter}",
            rf"{word} {a} слово, не содержащее букву {letter}",
            rf"{word} {a} слово, в котором отсутствует буква {letter}",
            rf"{word} {a} слово без буквы {letter}",
            rf"{word} {a} {possible} {word_}",
            rf"слово, которое не содержит букву {letter} {a} {word}",
            rf"слово, не содержащее букву {letter} {a} {word}",
            rf"слово, в котором отсутствует буква {letter} {a} {word}",
            rf"слово без буквы {letter} {a} {word}",
        ]

        return base_patterns

    def negative_scorer(self, prediction, input_, letter):
        score, certainty = None, None

        # the prediction just repeats the input (maybe asking for a different letter now)
        input_ = self.normalize_string(input_)
        input_ = input_.replace(f"\"{letter}\"", r'"\w"')

        if re.match(input_ + "$", prediction):
            score = 0
            certainty = 1

        # the prediction is a single word that contains the letter
        if not re.search(r"\W", prediction) and letter in prediction:
            score = 0
            certainty = 1

        return score, certainty

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        prediction = self.normalize_prediction(prediction, truncate_prediction)

        letter = example["metadata"]["letter"]

        input_ = example["input"]
        score, certainty = self.negative_scorer(prediction, input_, letter)
        if score is not None:
            return score, certainty

        allowed_letters = string.ascii_lowercase.replace(letter, "")
        allowed_word = rf"(\b[{allowed_letters}]{{2,}}\b)"
        
        allowed_word = the_word_regex(allowed_word)

        # allowing the answer pattern to repeat is too lax for this task
        # e.g. "A giraffe is bending down to eat some grass." shouldn't be considered accurate for
        # the input "Write a word that doesn't contain the letter "c":"
        score, certainty = self._simple_scorer(prediction, allowed_word,
                                               allow_answer_pattern_repetitions=False)
        if score:
            return score, certainty

        letter = the_letter_regex(letter)

        base_patterns = self.get_base_patterns(letter, allowed_word)

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty
