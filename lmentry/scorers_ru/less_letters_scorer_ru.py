import re

from lmentry.scorers.scorer import (
    LMentryScorer, swap_substrings, the_word_regex, standardized_number_regex
)


class LessLettersScorerRu(LMentryScorer):
    """This class was created by simply mirroring `MoreLettersScorer`
    """
    def __init__(self):
        super().__init__()

        self.prefixes.extend([
            "Из слов {word1} и {word2} ",
            "Среди слов {word1} и {word2} ",
        ])

    def get_base_patterns(self, answer, distractor, diff):

        a = r"(-|–)"
        less = r"(меньше)"
        
        base_patterns = [
            rf"В слове {answer} {less} букв",
            rf"В слове {answer} {less} букв, чем в слове {distractor}",
            rf"Слово {answer} содержит {less} букв, чем слово {distractor}",
            rf"Количество букв в слове {answer} {less}, чем в слове {distractor}",
            rf"Слово {answer} короче, чем слово {distractor}",
            rf"Слово {answer} имеет меньшую длину, чем слово {distractor}",
            rf"Длина слова {answer} {less}, чем длина слова {distractor}",
            rf"Слово, в котором {less} букв, {a} {answer}",
            rf"{answer} {a} слово, в котором {less} букв",
            rf"{answer} короче",
            rf"{answer} короче, чем {distractor}",
            rf"Самое короткое слово {a} {answer}",
            rf"Слово, которое короче, {a} {answer}",
            rf"{answer} {a} это слово короче",
            rf"В слове {answer} на {diff} букв {less}",
            rf"В слове {answer} на {diff} букв {less}, чем в слове {distractor}",
            rf"Слово {answer} короче на {diff} букву(ы)",
            rf"Слово {answer} короче, чем {distractor} на {diff} букву(ы)",
            rf"В слове {answer} {less} букв, чем в слове {distractor} на {diff} букву(ы)",
        ]
        
        # replace less with more and swap answer and distractor
        less = r"(меньше)"
        more_base_patterns1 = [
            swap_substrings(s, subs1=answer, subs2=distractor).replace(less, "больше")
            for s in base_patterns
            if less in s
        ]
        base_patterns.extend(more_base_patterns1)

        # replace shorter with longer and swap answer and distractor
        more_base_patterns2 = [
            swap_substrings(s, subs1=answer, subs2=distractor).replace("короче", "длиннее")
            for s in base_patterns
            if "короче" in s
        ]
        base_patterns.extend(more_base_patterns2)

        return base_patterns + self.get_shared_patterns(target=answer)
    
    def negative_scorer(self, prediction, answer, distractor, diff):
        score, certainty = None, None

        a = r"(-|–)"
        less = r"(меньше)"
              
        negative_patterns = [
            rf"В слове {distractor} {less} букв",
            rf"В слове {distractor} {less} букв, чем в слове {answer}",
            rf"Слово {distractor} содержит {less} букв, чем слово {answer}",
            rf"Количество букв в слове {distractor} {less}, чем в слове {answer}",
            rf"Слово {distractor} короче, чем слово {answer}",
            rf"Слово {distractor} имеет меньшую длину, чем слово {answer}",
            rf"Длина слова {distractor} {less}, чем длина слова {answer}",
            rf"Слово, в котором {less} букв, {a} {distractor}",
            rf"{distractor} {a} слово, в котором {less} букв",
            rf"{distractor} короче",
            rf"{distractor} короче, чем {answer}",
            rf"Самое короткое слово {a} {distractor}",
            rf"Слово, которое короче, {a} {distractor}",
            rf"{distractor} {a} это слово короче",
            rf"В слове {distractor} на {diff} букв {less}",
            rf"В слове {distractor} на {diff} букв {less}, чем в слове {answer}",
            rf"Слово {distractor} короче на {diff} букву(ы)",
            rf"Слово {distractor} короче, чем {answer} на {diff} букву(ы)",
            rf"В слове {distractor} {less} букв, чем в слове {answer} на {diff} букву(ы)",
        ]
     
        for negative_pattern in negative_patterns:
            negative_pattern = self.normalize_string(negative_pattern)
            if re.match(rf"{negative_pattern}\.?$", prediction):
                score = 0
                certainty = 1
                break

        # the model correctly picks the shorter word, but wrongly states the difference in letters:
        number_regex = r"(?P<number>\d+|одну|две|три|четыре|пять|шесть|семь|восемь|девять|десять|ноль)"
        wrong_diff_patterns = [
            rf"В слове {answer} на {number_regex} букв {less}",
            rf"В слове {answer} на {number_regex} букв {less}, чем в слове {distractor}",
            rf"Слово {answer} короче на {number_regex} букву(ы)",
            rf"Слово {answer} короче, чем {distractor} на {number_regex} букву(ы)",
            rf"В слове {answer} {less} букв, чем в слове {distractor} на {number_regex} букву(ы)",
        ]
        
        for wrong_diff_pattern in wrong_diff_patterns:
            if res := re.match(wrong_diff_pattern, prediction):
                predicted_diff = res.group("number")
                if not re.match(diff, predicted_diff):
                    score = 0
                    certainty = 1
                    break

        return score, certainty

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        prediction = self.normalize_prediction(prediction, truncate_prediction)

        metadata = example["metadata"]
        answer = metadata["answer"]

        distractor = metadata["distractor"]
        diff = len(distractor) - len(answer)
        word1 = metadata["word1"]
        word2 = metadata["word2"]

        answer = the_word_regex(answer)
        distractor = the_word_regex(distractor)
        diff = standardized_number_regex(diff)
        word1 = the_word_regex(word1)
        word2 = the_word_regex(word2)
        
        score, certainty = self.negative_scorer(prediction, answer, distractor, diff)
        if score is not None:
            return score, certainty

        score, certainty = self._simple_scorer(prediction, answer)
        if score:
            return score, certainty

        base_patterns = self.get_base_patterns(answer, distractor, diff)
        self.prefix_kwargs = {"word1": word1, "word2": word2}

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty
