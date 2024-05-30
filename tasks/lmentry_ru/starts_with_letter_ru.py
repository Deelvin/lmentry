from lmentry.scorers_ru.starts_with_letter_scorer_ru import StartsWithLetterScorerRu
from tasks.task import LMentryTaskRu


class StartsWithLetterRu(LMentryTaskRu):

    scorer_cls = StartsWithLetterScorerRu

    def __init__(self, name="starts_with_letter_ru"):
        super().__init__(name)

        self.canonical_template = 'Напишите слово, которое начинается с буквы "{letter}":\n'
        self.second_template = 'Напишите слово, первая буква которого "{letter}":\n'
        self.third_template = 'Напишите слово, начинающееся с буквы "{letter}":\n'
        self.fourth_template = 'Напишите слово, в котором "{letter} – начальная буква":\n'
        self.fifth_template = 'Напишите слово, в котором "{letter} – первая буква":\n'
        self.sixth_template = 'Напишите слово, в котором начальная буква – "{letter}":\n'
        self.seventh_template = 'Напишите слово, в котором первая буква – "{letter}":\n'
        self.all_templates = [self.canonical_template, self.second_template, self.third_template, self.fourth_template,
                              self.fifth_template, self.sixth_template, self.seventh_template]
        self.parameter_names = ["letter"]

    def _create_input(self, template, letter):
        input_ = template.format(letter=letter)
        return input_

    def create_data(self, task_data_path=None):

        # create examples
        examples = {}
        allowed_letters = "йцукенгшщзхфвапролджэячсмитбюё" # all letters except 'ъ', 'ы', 'ь'

        for template_id, template in enumerate(self.all_templates):
            for letter in allowed_letters:
                # create the input
                input_ = self._create_input(template, letter)

                # create the metadata
                metadata = dict()
                metadata["letter"] = letter
                metadata["template_id"] = template_id

                # create the example
                example = dict()
                example["input"] = input_
                example["metadata"] = metadata
                examples[str(len(examples) + 1)] = example

        # create the shared settings
        settings = dict()
        settings["canary"] = self.canary_string
        settings["name"] = self.name
        settings["num_examples_per_template"] = len(allowed_letters)
        settings["input_templates"] = self.all_templates

        # build the task_data
        task_data = dict()
        task_data["settings"] = settings
        task_data["examples"] = examples

        # save the data
        self.save_task_data(task_data, task_data_path)


if __name__ == '__main__':
    task = StartsWithLetterRu()
    # task.create_data()
