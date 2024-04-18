import json
import random
from itertools import chain

from lmentry.constants import RESOURCES_RU_DIR
from lmentry.scorers_ru.any_words_from_category_scorer_ru import AnyWordsFromCategoryScorerRu
from tasks.task import LMentryTaskRu


class AnyWordsFromCategoryRu(LMentryTaskRu):

    scorer_cls = AnyWordsFromCategoryScorerRu

    def __init__(self, name="any_words_from_category_ru"):
        super().__init__(name)

        with open("templates/any_words_from_category_templates_ru.json", "r", encoding="utf8") as file:
            self.all_templates = json.load(file)
        self.non_and_template_id = 2
        self.parameter_names = ["category"]

    def _create_input(self, template, words, category):

        # create the string representation of the words
        words = [f"\"{word}\"" for word in words]

        template_id = self.all_templates.index(template)

        if template_id != self.non_and_template_id:  # add "and" before the last word
            words = ", ".join(words[:-1]) + f" и {words[-1]}"
        else:
            words = ", ".join(words)

        input_ = template.format(words=words, category=category)

        return input_

    def create_data(self, num_words_options: tuple = (5,), num_distractors_options: tuple = (4, 5),
                    num_examples=1000, seed=None, task_data_path=None):

        with open(RESOURCES_RU_DIR.joinpath("nouns_by_category_ru.json")) as f:
            source_data = json.load(f)

        # create examples
        examples = {}
        category_names = list(source_data.keys())
        for template_id, template in enumerate(self.all_templates):
            # set random seed
            seed = seed or self.default_seed
            random.seed(seed)

            num_template_examples_created = 0
            already_seen_arguments = set()

            while num_template_examples_created < num_examples:

                # sample category, number of distractors, and category words
                category = random.choice(category_names)
                num_distractors = random.choice(num_distractors_options)
                num_words = random.choice(num_words_options)
                category_words = random.sample(source_data[category], k=num_words-num_distractors)

                # sample distractors
                if num_distractors > 0:
                    distractor_pool = list(chain.from_iterable([source_data[c] for c in category_names
                                                                if c != category]))
                    distractors = random.sample(distractor_pool, k=num_distractors)
                    distractor_indices = sorted(random.sample(range(num_words), k=num_distractors))
                else:
                    distractors, distractor_indices = [], []

                # resample if the arguments are already used
                if (tuple(category_words), tuple(distractors), tuple(distractor_indices)) in already_seen_arguments:
                    continue
                already_seen_arguments.add((tuple(category_words), tuple(distractors), tuple(distractor_indices)))

                # create a list of all the words
                words = category_words.copy()
                for i, distractor in enumerate(distractors):
                    distractor_index = distractor_indices[i]
                    words.insert(distractor_index, distractor)

                # create the input
                input_ = self._create_input(template, words, category,
                                            )
                # create the metadata
                metadata = dict()
                metadata["category"] = category
                metadata["num_words"] = num_words
                metadata["words"] = words
                metadata["category_words"] = category_words
                metadata["distractors"] = distractors
                metadata["num_distractors"] = num_distractors
                metadata["distractor_indices"] = distractor_indices
                metadata["template_id"] = template_id

                # create the example
                example = dict()
                example["input"] = input_
                example["metadata"] = metadata
                examples[str(len(examples) + 1)] = example

                num_template_examples_created += 1

        # create the shared settings
        settings = dict()
        settings["canary"] = self.canary_string
        settings["name"] = self.name
        settings["num_words_options"] = num_words_options
        settings["num_distractors_options"] = num_distractors_options
        settings["seed"] = seed
        settings["num_examples_per_template"] = num_examples
        settings["input_templates"] = self.all_templates

        # build the task_data
        task_data = dict()
        task_data["settings"] = settings
        task_data["examples"] = examples

        # save the data
        self.save_task_data(task_data, task_data_path)


if __name__ == '__main__':
    task = AnyWordsFromCategoryRu()
    # task.create_data()
