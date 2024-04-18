import re

from lmentry.scorers.scorer import LMentryScorer


class AllWordsFromCategoryScorerRu(LMentryScorer):
    def __init__(self):
        super().__init__()

    def get_base_patterns(self, answer, category):
        pass

    @staticmethod
    def category_regex(category):
        pass

    @staticmethod
    def negative_scorer(prediction, answer):
        pass

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        pass
