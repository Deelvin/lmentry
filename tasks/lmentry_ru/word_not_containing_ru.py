from lmentry.scorers_ru.word_not_containing_scorer_ru import WordNotContainingScorerRu
from tasks.task import LMentryTaskRu


class WordNotContainingRu(LMentryTaskRu):

    scorer_cls = WordNotContainingScorerRu

    def __init__(self, name="word_not_containing_ru"):
        super().__init__(name)
        self.canonical_template = 'Напишите слово, которое не содержит букву "{letter}":\n'
        self.second_template = 'Напишите слово, не используя букву "{letter}":\n'
        self.third_template = 'Напишите слово, не содержащее букву "{letter}":\n'
        self.fourth_template = 'Напишите слово, в котором отсутствует буква "{letter}":\n'
        self.fifth_template = 'Напишите слово без буквы "{letter}":\n'
        self.sixth_template = 'Напишите слово, исключая букву "{letter}":\n'
        self.all_templates = [self.canonical_template, self.second_template, self.third_template,
                              self.fourth_template, self.fifth_template, self.sixth_template]
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
        settings["num_examples_per_template"] = len(allowed_letters)
        settings["input_templates"] = self.all_templates

        # build the task_data
        task_data = dict()
        task_data["settings"] = settings
        task_data["examples"] = examples

        # save the data
        self.save_task_data(task_data, task_data_path)


if __name__ == '__main__':
    task = WordNotContainingRu()
    # task.create_data()
