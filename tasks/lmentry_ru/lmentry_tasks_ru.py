import json
import logging
from pathlib import Path

from lmentry.constants import TASKS_DATA_DIR
# from tasks.lmentry_ru.all_words_from_category import AllWordsFromCategory
# from tasks.lmentry_ru.all_words_from_category_0_distractors import AllWordsFromCategory0Distractors
# from tasks.lmentry_ru.all_words_from_category_1_distractors import AllWordsFromCategory1Distractors
# from tasks.lmentry_ru.all_words_from_category_2_distractors import AllWordsFromCategory2Distractors
# from tasks.lmentry_ru.any_words_from_category import AnyWordsFromCategory
# from tasks.lmentry_ru.any_words_from_category_3_distractors import AnyWordsFromCategory3Distractors
# from tasks.lmentry_ru.any_words_from_category_4_distractors import AnyWordsFromCategory4Distractors
# from tasks.lmentry_ru.any_words_from_category_5_distractors import AnyWordsFromCategory5Distractors
from tasks.lmentry_ru.bigger_number_ru import BiggerNumberRu
from tasks.lmentry_ru.ends_with_letter_ru import EndsWithLetterRu
from tasks.lmentry_ru.ends_with_word_ru import EndsWithWordRu
from tasks.lmentry_ru.first_alphabetically_ru import FirstAlphabeticallyRu
# from tasks.lmentry_ru.first_alphabetically_consecutive_first_letter import FirstAlphabeticallyConsecutiveFirstLetter
# from tasks.lmentry_ru.first_alphabetically_different_first_letter import FirstAlphabeticallyDifferentFirstLetter
# from tasks.lmentry_ru.first_alphabetically_far_first_letter import FirstAlphabeticallyFarFirstLetter
# from tasks.lmentry_ru.first_alphabetically_same_first_letter import FirstAlphabeticallySameFirstLetter
from tasks.lmentry_ru.first_letter_ru import FirstLetterRu
from tasks.lmentry_ru.first_word_ru import FirstWordRu
# from tasks.lmentry_ru.homophones import Homophones
from tasks.lmentry_ru.last_letter_ru import LastLetterRu
from tasks.lmentry_ru.last_word_ru import LastWordRu
from tasks.lmentry_ru.least_associated_word_ru import LeastAssociatedWordRu
from tasks.lmentry_ru.less_letters_ru import LessLettersRu
# from tasks.lmentry_ru.less_letters_length_diff_3plus import LessLettersLengthDiff3plus
# from tasks.lmentry_ru.less_letters_length_diff_1 import LessLettersLengthDiff1
from tasks.lmentry_ru.more_letters_ru import MoreLettersRu
# from tasks.lmentry_ru.more_letters_length_diff_3plus import MoreLettersLengthDiff3plus
# from tasks.lmentry_ru.more_letters_length_diff_1 import MoreLettersLengthDiff1
from tasks.lmentry_ru.most_associated_word_ru import MostAssociatedWordRu
# from tasks.lmentry_ru.rhyming_word import RhymingWord
# from tasks.lmentry_ru.rhyming_word_orthographically_different import RhymingWordOrthographicallyDifferent
# from tasks.lmentry_ru.rhyming_word_orthographically_similar import RhymingWordOrthographicallySimilar
from tasks.lmentry_ru.sentence_containing_ru import SentenceContainingRu
from tasks.lmentry_ru.sentence_not_containing_ru import SentenceNotContainingRu
from tasks.lmentry_ru.smaller_number_ru import SmallerNumberRu
from tasks.lmentry_ru.starts_with_letter_ru import StartsWithLetterRu
from tasks.lmentry_ru.starts_with_word_ru import StartsWithWordRu
from tasks.task import LMentryTask
from tasks.lmentry_ru.word_after_ru import WordAfterRu
from tasks.lmentry_ru.word_before_ru import WordBeforeRu
from tasks.lmentry_ru.word_containing_ru import WordContainingRu
from tasks.lmentry_ru.word_not_containing_ru import WordNotContainingRu

core_tasks_ru = {
    "sentence_containing": SentenceContainingRu,
    "sentence_not_containing": SentenceNotContainingRu,
    "word_containing": WordContainingRu,
    "word_not_containing": WordNotContainingRu,
    "most_associated_word": MostAssociatedWordRu,
    "least_associated_word": LeastAssociatedWordRu,
    # "any_words_from_category": AnyWordsFromCategory,
    # "all_words_from_category": AllWordsFromCategory,
    "first_alphabetically": FirstAlphabeticallyRu,
    "more_letters": MoreLettersRu,
    "less_letters": LessLettersRu,
    "bigger_number": BiggerNumberRu,
    "smaller_number": SmallerNumberRu,
    # "rhyming_word": RhymingWord,
    # "homophones": Homophones,
    "word_after": WordAfterRu,
    "word_before": WordBeforeRu,
    "starts_with_word": StartsWithWordRu,
    "ends_with_word": EndsWithWordRu,
    "starts_with_letter": StartsWithLetterRu,
    "ends_with_letter": EndsWithLetterRu,
    "first_word": FirstWordRu,
    "last_word": LastWordRu,
    "first_letter": FirstLetterRu,
    "last_letter": LastLetterRu,
}

analysis_tasks_ru = {
    # "first_alphabetically_far_first_letter": FirstAlphabeticallyFarFirstLetter,
    # "first_alphabetically_different_first_letter": FirstAlphabeticallyDifferentFirstLetter,
    # "first_alphabetically_consecutive_first_letter": FirstAlphabeticallyConsecutiveFirstLetter,
    # "first_alphabetically_same_first_letter": FirstAlphabeticallySameFirstLetter,
    # "any_words_from_category_5_distractors": AnyWordsFromCategory5Distractors,
    # "any_words_from_category_4_distractors": AnyWordsFromCategory4Distractors,
    # "any_words_from_category_3_distractors": AnyWordsFromCategory3Distractors,
    # "all_words_from_category_0_distractors": AllWordsFromCategory0Distractors,
    # "all_words_from_category_1_distractors": AllWordsFromCategory1Distractors,
    # "all_words_from_category_2_distractors": AllWordsFromCategory2Distractors,
    # "rhyming_word_orthographically_similar": RhymingWordOrthographicallySimilar,
    # "rhyming_word_orthographically_different": RhymingWordOrthographicallyDifferent,
    # "more_letters_length_diff_3plus": MoreLettersLengthDiff3plus,
    # "more_letters_length_diff_1": MoreLettersLengthDiff1,
    # "less_letters_length_diff_3plus": LessLettersLengthDiff3plus,
    # "less_letters_length_diff_1": LessLettersLengthDiff1,
}

all_tasks_ru = core_tasks_ru | analysis_tasks_ru

# It is part from core tasks
sensetive_7b_model_tasks_ru = {
    "bigger_number": BiggerNumberRu,
    "smaller_number": SmallerNumberRu,
    "first_alphabetically": FirstAlphabeticallyRu,
    "first_letter": FirstLetterRu,
    "most_associated_word": MostAssociatedWordRu,
}


def create_task_data_ru(task_name: str):
  task: LMentryTask = all_tasks_ru[task_name]()
  logging.info(f"creating data for task \"{task_name}\"")
  task.create_data()


def create_all_task_data_ru():
  for task_name in all_tasks_ru:
    create_task_data_ru(task_name)


def count_examples_ru(tasks_to_count: list[str] = None, tasks_data_dir: Path = None):
  tasks_data_dir = tasks_data_dir or TASKS_DATA_DIR

  if tasks_to_count is None:
    tasks_to_count = all_tasks_ru

  n_examples = 0
  for task_name in tasks_to_count:
    task_data_path = tasks_data_dir.joinpath(f"{task_name}.json")
    with open(task_data_path) as f:
      task_data = json.load(f)
      n_examples += len(task_data["examples"])

  print(f"#examples in all tasks combined: {n_examples}")
  return n_examples
