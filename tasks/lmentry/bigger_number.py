import random

from lmentry.scorers.bigger_number_scorer import BiggerNumberScorer
from tasks.task import LMentryTask


class BiggerNumber(LMentryTask):

    scorer_cls = BiggerNumberScorer

    def __init__(self, name="bigger_number"):
        super().__init__(name)
        self.canonical_template = "Q: Which number is bigger, {n1} or {n2}?\nA:"
        self.second_template = "Q: Of the numbers {n1} and {n2}, which is bigger?\nA:"
        self.third_template = "From the numbers {n1} and {n2}, write the bigger number:\n"

        self.fourth_template = "Q: Which number is larger, {n1} or {n2}?\nA:"
        self.fifth_template = "Q: Of the numbers {n1} and {n2}, which is larger?\nA:"
        self.sixth_template = "From the numbers {n1} and {n2}, write the larger number:\n"
        
        self.all_templates = [self.canonical_template, self.second_template, self.third_template, 
                              self.fourth_template, self.fifth_template, self.sixth_template]

        self.new_templates = [
            "Is {n1} or {n2} the larger number?",
            "Which of the two numbers, {n1} or {n2}, is greater?",
            "{n1} or {n2} - which number is larger?",
            "Which number has a greater value, {n1} or {n2}?",
            "Among {n1} and {n2}, which one is the bigger number?",
            "{n1} and {n2} - which number is the larger one?",
            "Compare {n1} and {n2} and tell me which one is bigger.",
            "I need to know if {n1} or {n2} is the larger number.",
            "Could you determine which number is larger between {n1} and {n2}?",
            "Which is the bigger number - {n1} or {n2}?",
            "I'm curious to know which of the two numbers, {n1} or {n2}, is greater.",
            "Is {n1} greater than {n2}, or is it the other way around?",
            "Of {n1} and {n2}, which one has a higher numerical value?",
            "Please identify the larger number between {n1} and {n2}.",
            "Which number prevails in terms of magnitude, {n1} or {n2}?",
            "Could you ascertain if {n1} or {n2} is the greater number?",
            "Is the magnitude of {n1} greater than that of {n2}?",
            "Determine whether {n1} or {n2} is the bigger number.",
            "Which one is the bigger numeral, {n1} or {n2}?",
            "Compare {n1} and {n2} to find out which number is larger.",
            "I'm interested to know if {n1} or {n2} is the larger numeral.",
            "Please indicate the bigger of the two numbers, {n1} or {n2}.",
            "Would you be able to discern the greater number between {n1} and {n2}?",
            "Which numeral possesses a greater value, {n1} or {n2}?",
            "I'd like to know if {n1} or {n2} is the larger numerical value.",
            "Could you determine the greater of the two numbers, {n1} or {n2}?",
            "Which number stands higher in magnitude, {n1} or {n2}?",
            "Is {n1} or {n2} the larger numeral in this scenario?",
            "I'm wondering if {n1} is greater than {n2}, or vice versa.",
            "Of the two numbers, {n1} and {n2}, which one is the greater?",
            "Please compare {n1} and {n2} and tell me which number is bigger.",
            "I need to establish if {n1} or {n2} is the larger of the two numbers.",
            "Which of {n1} and {n2} has a higher numerical value?",
            "Determine the larger number between {n1} and {n2}.",
            "Between {n1} and {n2}, which number has a greater magnitude?",
            "Which number possesses a greater value, {n1} or {n2}?",
            "Among {n1} and {n2}, which one has a higher numerical magnitude?",
            "Compare {n1} and {n2} to determine which number is larger.",
            "I'm interested in knowing if {n1} or {n2} is the larger number.",
            "Please indicate which of the two numbers, {n1} or {n2}, is greater.",
            "Would you be able to ascertain if {n1} or {n2} is the greater number?",
            "Which numeral holds a greater value, {n1} or {n2}?",
            "I'd like to know if {n1} or {n2} is the larger numerical quantity.",
            "Could you determine the greater number between {n1} and {n2}?",
            "Which number has a higher magnitude, {n1} or {n2}?",
            "Is {n1} or {n2} the larger numeral in terms of value?",
            "I'm wondering if {n1} is greater than {n2}, or if it's the other way around.",
            "Of the two numbers, {n1} and {n2}, which one has a greater value?",
            "Please compare {n1} and {n2} and indicate which number is bigger.",
            "I need to know if {n1} or {n2} is the larger numerical value.",
            "Which is the larger number between {n1} and {n2}?",
            "I'm curious to know which number, {n1} or {n2}, is bigger.",
            "Is {n1} greater than {n2}, or is it the opposite?",
            "Which one of {n1} and {n2} has a higher numerical value?",
            "Please identify the bigger number among {n1} and {n2}.",
            "Which number has a greater magnitude, {n1} or {n2}?",
            "Determine whether {n1} or {n2} is the greater numeral.",
            "Which numeral is larger, {n1} or {n2}?",
            "Compare {n1} and {n2} to determine which number is greater.",
            "Please indicate the bigger number between {n1} and {n2}.",
            "Would you be able to discern the greater number among {n1} and {n2}?",
            "Is {n1} or {n2} the larger numeral in this context?",
            "Of the two numbers, {n1} and {n2}, which one is greater?",
            "Please compare {n1} and {n2} and tell me which number is larger."
            ]

        self.all_templates.extend(self.new_templates)
        self.parameter_names = ["answer", "distractor"]

    def _create_input(self, template, n1, n2):
        input_ = template.format(n1=str(n1), n2=str(n2))
        return input_

    def create_data(self, num_examples=1000, seed=None, task_data_path=None):

        examples = {}
        numbers_range = range(10, 1000)

        for template_id, template in enumerate(self.all_templates):
            # set random seed
            seed = seed or self.default_seed
            random.seed(seed)
            num_examples_created = 0
            already_sampled = []

            # create examples
            while num_examples_created < num_examples:
                # create the input
                # samples two different numbers
                numbers = random.sample(numbers_range, 2)
                if numbers in already_sampled:
                    continue
                already_sampled.append(numbers)
                num_examples_created += 1

                input_ = self._create_input(template, n1=numbers[0], n2=numbers[1])
                max_val = max(numbers[0], numbers[1])

                # create the metadata
                metadata = dict()
                metadata["num_digits"] = [len(str(numbers[0])), len(str(numbers[1]))]
                metadata["n1"] = numbers[0]
                metadata["n2"] = numbers[1]
                metadata["answer"] = max_val
                metadata["answer_index"] = numbers.index(max_val)
                metadata["distractor"] = metadata["n2"] if metadata["answer_index"] == 0 else metadata["n1"]
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
        settings["num_examples_per_template"] = num_examples
        settings["seed"] = seed
        settings["input_templates"] = self.all_templates

        # build the task_data
        task_data = dict()
        task_data["settings"] = settings
        task_data["examples"] = examples

        # save the data
        self.save_task_data(task_data, task_data_path)


if __name__ == '__main__':
    task = BiggerNumber()
    task.create_data()
