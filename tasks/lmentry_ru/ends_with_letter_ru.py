from lmentry.scorers_ru.ends_with_letter_scorer_ru import EndsWithLetterScorerRu
from tasks.task import LMentryTask


class EndsWithLetterRu(LMentryTask):

    scorer_cls = EndsWithLetterScorerRu

    def __init__(self, name="ends_with_letter_ru"):
        super().__init__(name)

        self.canonical_template = 'Напишите слово, которое заканчивается на букву "{letter}":\n'
        self.second_template = 'Напишите слово, последняя буква которого "{letter}":\n'
        self.third_template = 'Напишите слово, заканчивающееся на букву "{letter}":\n'
        self.fourth_template = 'Напишите слово, в котором "{letter} – конечная буква":\n'
        self.fifth_template = 'Напишите слово, в котором "{letter} – последняя буква":\n'
        self.sixth_template = 'Напишите слово, в котором конечная буква – "{letter}":\n'
        self.seventh_template = 'Напишите слово, в котором последняя буква – "{letter}":\n'
        self.all_templates = [self.canonical_template, self.second_template, self.third_template, self.fourth_template,
                              self.fifth_template, self.sixth_template, self.seventh_template]
        self.parameter_names = ["letter"]

    def _create_input(self, template, letter):
        input_ = template.format(letter=letter)
        return input_

    def create_data(self, task_data_path=None):

        # create examples
        examples = {}
        allowed_letters = "йцукенгшщзхъфывапролджэячсмитьбюё"

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
        settings["num_examples_per_template"] = int(len(examples) / len(self.all_templates))
        settings["input_templates"] = self.all_templates

        # build the task_data
        task_data = dict()
        task_data["settings"] = settings
        task_data["examples"] = examples

        # save the data
        self.save_task_data(task_data, task_data_path)


if __name__ == '__main__':
    task = EndsWithLetterRu()
    # task.create_data()
