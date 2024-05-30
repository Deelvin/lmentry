import json
import random

from lmentry.constants import LMENTRY_WORDS_RU_PATH
from lmentry.scorers_ru.sentence_not_containing_scorer_ru import SentenceNotContainingScorerRu
from tasks.task import LMentryTaskRu


class SentenceNotContainingRu(LMentryTaskRu):

    scorer_cls = SentenceNotContainingScorerRu

    def __init__(self, name="sentence_not_containing_ru"):
        super().__init__(name)
        self.canonical_template = 'Напишите предложение, которое не содержит слово "{word}":\n'
        self.second_template = 'Напишите предложение, не используя слово "{word}":\n'
        self.third_template = 'Напишите предложение, не содержащее слово "{word}":\n'
        self.fourth_template = 'Напишите предложение, в котором отсутствует слово "{word}":\n'
        self.fifth_template = 'Напишите предложение без слова "{word}":\n'
        self.sixth_template = 'Напишите предложение, исключая слово "{word}":\n'
        self.all_templates = [self.canonical_template, self.second_template, self.third_template,
                              self.fourth_template, self.fifth_template, self.sixth_template]

    @staticmethod
    def get_task_words():
        with open(LMENTRY_WORDS_RU_PATH) as f:
            task_words = json.load(f)

        for word in list(task_words):
            word_levels = set(task_words[word]["levels"])
            if not {"A1", "A2"} & word_levels:
                del task_words[word]

        return task_words

    def _create_input(self, template, word):
        input_ = template.format(word=word)
        return input_

    def create_data(self, num_examples=1000, seed=None, task_data_path=None):

        # sample num_examples words from the data
        task_words = self.get_task_words()
        seed = seed or self.default_seed
        random.seed(seed)
        sampled_words = random.sample(list(task_words), num_examples)
        task_words = {word: task_words[word] for word in sampled_words}

        # create examples
        examples = {}

        for template_id, template in enumerate(self.all_templates):
            for word, word_info in task_words.items():
                # create the input
                input_ = self._create_input(template, word)

                # create the metadata
                metadata = dict()
                metadata["word"] = word
                metadata["word_pos_tags"] = word_info["pos"]
                metadata["word_levels"] = word_info["levels"]
                metadata["template_id"] = template_id

                # create the example
                example = dict()
                example["input"] = input_
                example["metadata"] = metadata
                examples[f"{len(examples) + 1}"] = example

        # create the shared settings
        settings = dict()
        settings["canary"] = self.canary_string
        settings["name"] = self.name
        settings["num_examples_per_template"] = len(task_words)
        settings["input_templates"] = self.all_templates

        # build the task_data
        task_data = dict()
        task_data["settings"] = settings
        task_data["examples"] = examples

        # save the data
        self.save_task_data(task_data, task_data_path)


if __name__ == '__main__':
    task = SentenceNotContainingRu()
    # task.create_data()
