import json
import re
from pathlib import Path

from lmentry.scorers.scorer import LMentryScorer


class AnyWordsFromCategoryScorerRu(LMentryScorer):
    def __init__(self):
        super().__init__()

    def get_base_patterns(self, answer, category, category_word, distractors, words):

        base_patterns = [
            rf"^{answer}\b",
        ]

        punct = r"(,|.)"
        category_word = rf'\"{category_word}\"|{category_word}'

        words = self.get_punctuation(words)
        distractors = self.get_punctuation(distractors)

        extra_patterns = [
            rf"из выбранных слов, {category_word} является {category}.",
            rf"из выбранных слов, {category_word} является именем родства.",
            rf"из выбранных слов, только {category_word} является {category}.",
            rf"из выбранных слов, {category_word} входит в категорию {category}.",
            rf"из выбранных слов, {category_word} связан с категорией {category}.",
            rf"из выбранных слов, {category_word} попадает в категорию {category}.",
            rf"из выбранных слов, {category_word} связана с категорией {category}.",
            rf"из выбранных слов, {category} относится к категории {category_word}.",
            rf"из выбранных слов, {category_word} относится к категории {category}.",
            rf"из выбранных слов, {category_word} представляет категорию {category}.",
            rf"из выбранных слов, {category_word} соответствует категории {category}.",
            rf"из выбранных слов, {category_word} принадлежит к категории {category}.",
            rf"из выбранных слов, {category_word} и {category} входят в категорию {category}.",
            rf"из выбранных слов, {category_word} согласуется с категорией {category}.",
            rf"из выбранных слов, {category_word} и {category} относятся к категории {category}.",
            rf"из выбранных слов, только {category_word} входит в категорию {category}.",
            rf"из выбранных слов, {category_word} является частью категории {category}.",
            rf"из выбранных слов, только {category_word} связан с категорией {category}.",
            rf"из выбранных слов, {category_word} ассоциируется с категорией {category}.",
            rf"из выбранных слов, {category_word} и {category} относятся к категории {category}.",
            rf"из выбранных слов, только {category_word} попадает в категорию {category}.",
            rf"из выбранных слов, только {category_word} связано с категорией {category}.",
            rf"из выбранных слов, только {category_word} связана с категорией {category}.",
            rf"из выбранных слов, {category_word} является объектом категории {category}.",
            rf"из выбранных слов, {category_word} и {category} соответствуют категории {category}.",
            rf"из выбранных слов, {category_word} и {category} представляют категорию {category}.",
            rf"из выбранных слов, только {category_word} относится к категории {category}.",
            rf"из выбранных слов, {category_word} и {category} соответствуют категории {category}.",
            rf"из выбранных слов, только {category_word} соответствует категории {category}.",
            rf"из выбранных слов, только {category_word} принадлежит к категории {category}.",
            rf"из выбранных слов, только {category_word} согласуется с категорией {category}.",
            rf"из выбранных слов, {category_word} является связанным с категорией {category}.",
            rf"из выбранных слов, только {category_word} является частью категории {category}.",
            rf"из выбранных слов, {category_word} и {category} связаны с категорией {category}.",
            rf"из выбранных слов, только {category_word} ассоциируется с категорией {category}.",
            rf"из выбранных слов, только {category_word} имеет отношение к категории {category}.",
            rf"из выбранных слов, {category_word} является согласованным с категорией {category}.",
            rf"из выбранных слов, {category_word} и {category} могут быть объединены в категорию {category}.",
            rf"из выбранных слов, только {category_word} согласуется с категорией {category}.",
            rf"из выбранных слов, {category_word} является {category}, так как {category_word} - это {category}.",
            rf"из выбранных слов, {category_word} и {category} могут быть объединены в категорию {category}.",
            rf"из выбранных слов, {category_word} является тем, который связан с категорией {category}.",
            rf"из выбранных слов, только {category_word} является согласованным с категорией {category}.",
            rf"из выбранных слов, {category_word} является {category} и принадлежит к категории {category}.",
            rf"из выбранных слов, {category_word} является тем, который можно отнести к категории {category}.",
            rf"из выбранных слов, {category_word} является объектом, который относится к категории {category}.",
            rf"из выбранных слов, {category_word} является {category}, так как оно означает {category_word}.",
            rf"из выбранных слов, {category_word} является {category}, поэтому оно входит в категорию {category}.",
            rf"из выбранных слов, {category_word} является {category}, поэтому оно представляет категорию {category}.",
            rf"из выбранных слов, {category_word} является объектом, который может быть отнесен к категории {category}.",
            rf"из выбранных слов, {category_word} является {category}, поэтому оно соответствует категории {category}.",
            rf"из выбранных слов, {category_word} является {category}, поэтому вы можете выбрать ее из категории {category}.",
            rf"из выбранных слов, {category_word} ассоциируется с категорией {category}.",
            rf"из выбранных слов, только {category_word} имеет отношение к категории {category}.",
            rf"из выбранных слов, {category_word} является {category}.",
            rf"из выбранных слов, {category_word} является частью категории {category}, так как {category_word} - это {category}.",
            rf"из выбранных слов, {category_word} является {category}, поэтому вы можете выбрать его из категории {category}.",
            rf"из выбранных слов, {category_word} является {category}, так как это название принадлежит к категории {category}.",
            rf"из выбранных слов, только {category_word} имеет отношение к категории {category}.",
            rf"из выбранных слов, {category_word} является {category}, поэтому оно может быть объединено в категорию {category}.",
            rf"из выбранных слов, {category_word} связано с категорией {category}.",
            rf"из выбранных слов, {category_word} связана с категорией {category}.",
            rf"из выбранных слов, {category_word} является частью категории {category}.",
            rf"из выбранных слов, {category_word} является {category}, поэтому вы можете выбрать ее из списка.\nтаким образом, выберите {category_word}.",
            rf"из предложенных слов, {category_word} является {category}.",
            rf"из предложенных слов, {category_word} является {category}.",
            rf"из предложенных слов, {category_word} является {category}.",
            rf"из предложенных слов, только {category_word} является {category}.",
            rf"из предложенных слов, {category_word} входит в категорию {category}.",
            rf"из предложенных слов, {category_word} и {category} входят в категорию {category}.",
            rf"из предложенных слов, {category_word} соответствует категории {category}.",
            rf"из предложенных слов, только {category_word} являются частью категории {category}.",
            rf"из предложенных слов, {category_word} является частью категории {category}.",
            rf"из предложенных слов, {category_word} и {category} относятся к категории {category}.",
            rf"из предложенных слов, {category_word} может быть отнесена к категории {category}.",
            rf"из предложенных слов, только {category_word} входит в категорию {category}.",
            rf"из предложенных слов, только {category_word} связан с категорией {category}.",
            rf"из предложенных слов, {category_word} и {category} представляют категорию {category}.",
            rf"из предложенных слов, {category_word} ассоциируется с категорией {category}.",
            rf"из предложенных слов, только {category_word} попадает в категорию {category}.",
            rf"из предложенных слов, только {category_word} связана с категорией {category}.",
            rf"из предложенных слов, только {category_word} связано с категорией {category}.",
            rf"из предложенных слов, только {category_word} относится к категории {category}.",
            rf"из предложенных слов, только {category_word} может быть отнесено к категории {category}.",
            rf"из предложенных слов, только {category_word} может быть отнесено к категории {category}.",
            rf"из предложенных слов, только {category_word} может быть отнесено к категории {category}.",
            rf"из предложенных слов, {category_word} и {category} являются частью категории {category}.",
            rf"из предложенных слов, только {category_word} представляет категорию {category}.",
            rf"из предложенных слов, только {category_word} может быть отнесено к категории {category}.",
            rf"из предложенных слов, только {category_word} соответствует категории {category}.",
            rf"из предложенных слов, только {category_word} принадлежит к категории {category}.",
            rf"из предложенных слов, только {category_word} согласуется с категорией {category}.",
            rf"из предложенных слов, только {category_word} может быть отнесена к категории {category}.",
            rf"из предложенных слов, только {category_word} может быть отнесено к категории {category}.",
            rf"из предложенных слов, только {category_word} может быть отнесена к категории {category}.",
            rf"из предложенных слов, только {category_word} является частью категории {category}.",
            rf"из предложенных слов, только {category_word} может быть отнесено к категории {category}.",
            rf"из предложенных слов, только {category_word} ассоциируется с категорией {category}.",
            rf"из предложенных слов, только {category_word} может быть отнесено к категории {category}.",
            rf"из предложенных слов, только {category_word} имеет отношение к категории {category}.",
            rf"из предложенных слов, {category_word} и {category} могут быть объединены в категорию {category}.",
            rf"из предложенных слов, только {category_word} может быть связан с категорией {category}.",
            rf"из предложенных слов, только {category_word} может быть связана с категорией {category}.",
            rf"из предложенных слов, только {category_word} может быть связано с категорией {category}.",
            rf"из предложенных слов, только {category_word} соответствует категории {category}, так как {distractors} не являются {category}.",
            rf"из предложенных слов, только {category_word} согласуется с категорией {category}, так как {distractors} не являются {category}.",
            rf"да{punct} все слова в списке {words} не являются {category}.",
            rf"да{punct} все слова из списка {words} не являются {category}.",
            rf"да{punct} все слова из списка {words} не относятся к категории {category}.",
            rf"да{punct} все слова из списка {words} не являются {category} и соответственно не согласованы с категорией {category}.",
            rf"да{punct} из списка выбрано слово {category_word}.",
            rf"да{punct} из списка слов {words} есть {category}.",
            rf"да{punct} из списка слов {words} есть {category} - {category_word}.",
            rf"да{punct} из списка слов {category} входит слово {category_word}.",
            rf"да{punct} из списка слов {words} существует слово {category_word}.",
            rf"да{punct} из списка слов {words} есть один {category} - {category_word}.",
            rf"да{punct} из списка слов {words} существует {category} - {category_word}.",
            rf"да{punct} из списка предлагаемых слов можно выбрать {category_word}.",
            rf"да{punct} из списка слов {words} можно выбрать слово {category_word}.",
            rf"да{punct} из списка слов {words} можно выделить {category} {category_word}.",
            rf"да{punct} из списка слов {words} есть один {category} {category_word}.",
            rf"да{punct} из списка слов {words} существует {category} - {category_word}.",
            rf"да{punct} из списка слов {words} можно выделить {category} - {category_word}.",
            rf"да{punct} из списка слов {category} связано слово {category_word}.",
            rf"да{punct} из списка слов {words} можно выделить {category} - {category_word}.",
            rf"да{punct} из списка слов {words} существует {category} - {category_word}.",
            rf"да{punct} из списка слов {words} можно выбрать {category} - {category_word}.",
            rf"да{punct} из списка слов {words} можно выбрать категорию {category}.",
            rf"да{punct} из списка слов {words} принадлежит к категории {category}.",
            rf"да{punct} из списка слов {words} можно выбрать {category} - {category_word}.",
            rf"да{punct} из списка слов {words} существует {category} - {category_word}.",
            rf"да{punct} из списка слов {words} можно выделить {category} - {category_word}.",
            rf"да{punct} из списка слов {words} можно выделить {category} - {category_word}.",
            rf"да{punct} из списка слов {words} можно отнести к категории {category}.",
            rf"да{punct} из списка слов {words} можно выбрать {category} - {category_word}.",
            rf"да{punct} из списка слов {category} входит слово {category_word}.",
            rf"да{punct} из списка слов {words} можно выбрать {category} - {category_word}.",
            rf"да{punct} из списка слов {words} можно выделить {category} - {category_word}.",
            rf"да{punct} из списка слов {words} ассоциируется с категорией {category}.",
            rf"да{punct} из списка слов {category} входит слово {category_word}.",
            rf"да{punct} из списка выделенных слов, {category_word} является {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, есть слово {category}.",
            rf"да{punct} из списка предлагаемых слов, {category_word} является {category}.",
            rf"да{punct} из списка слов {words} можно согласовать с категорией {category}.",
            rf"да{punct} из списка предложенных слов следует выделить {category_word} как {category}.",
            rf"да{punct} из списка слов, вы можете отнести {category_word} к категории {category}.",
            rf"да{punct} из списка слов {words} только {category_word} является {category}.",
            rf"да{punct} из списка слов {words} можно найти {category}.\n{category}: {category_word}"
            rf"да{punct} из списка слов, вы можете соотносить {category_word} с категорией {category}.",
            rf"да{punct} из списка слов {words} только {category_word} относятся к категории {category}.",
            rf"да{punct} из списка слов, вы можете ассоциировать {category_word} с категорией {category}.",
            rf"да{punct} из списка слов {words} только слово {category_word} является {category}.",
            rf"да{punct} из списка слов, указанных в вопросе, {category_word} является {category}.",
            rf"да{punct} из списка выделенных слов, {category} соответствует слову {category_word}.",
            rf"да{punct} из списка выделенных слов, {category_word} связан с категорией {category}.",
            rf"да{punct} из списка слов, выделенных в запросе, {category_word} является {category}.",
            rf"да{punct} из списка выделенных слов, {category_word} относится к категории {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, {category_word} является {category}.",
            rf"да{punct} из списка слов {words} связано с категорией {category} слово {category_word}.",
            rf"да{punct} из списка предложенных слов, {category_word} относится к категории {category}.",
            rf"да{punct} из списка предлагаемых слов, {category_word} является {category}.",
            rf"да{punct} из списка слов {words} отношение к категории {category} есть только для {category_word}.",
            rf"да{punct} из списка слов {words} только {category_word} относится к категории {category}.",
            rf"да{punct} из списка слов {words} можно выбрать слово {category_word}, потому что это {category}.",
            rf"да{punct} из списка слов {words} есть слово {category_word}, которое является {category}.",
            rf"да{punct} из списка выделенных слов, {category_word} является частью категории {category}.",
            rf"да{punct} из списка слов {words} только слово {category_word} имеет связь с категорией {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, {category_word} является {category}.",
            rf"да{punct} из списка слов {words} только {category_word} может быть отнесена к категории {category}.",
            rf"да{punct} из списка слов {words} только {category_word} может быть отнесено к категории {category}.",
            rf"да{punct} из списка выделенных слов, слово {category_word} будет согласоваться с категорией {category}.",
            rf"да{punct} из списка слов, выделенных в вопросе, только {category_word} относятся к категории {category}.",
            rf"да{punct} из списка слов {words} только {category_word} может быть отнесено к категории {category}.",
            rf"да{punct} из списка слов {words} только слово {category_word} связано с категорией {category}.",
            rf"да{punct} из списка предлагаемых слов, {category} может быть связано с словом {category_word}.",
            rf"да{punct} из списка слов {words} есть связь с категорией {category}.\n\n{category_word} - это {category}.",
            rf"да{punct} из списка слов {words} есть связь с категорией {category}.\n\n* {category_word} - это {category}.",
            rf"да{punct} из списка слов {words} только слово {category_word} относится к категории {category}.",
            rf"да{punct} из списка выбрано слово {category_word}, которое соотносится с категорией {category}.",
            rf"да{punct} из списка слов {words} есть слово, связанное с категорией {category}: {category_word}.",
            rf"да{punct} из списка слов {words} только слово {category_word} может быть отнесено к категории {category}.",
            rf"да{punct} из списка выделены следующие слова, которые относятся к категории {category}:\n\n* {category_word},"
            rf"да{punct} из списка слов, которые вы предоставили, {category_word} связан с категорией {category}.",
            rf"да{punct} из списка слов {words} только слово {category_word} соотносится с категорией {category}.",
            rf"да{punct} из списка слов есть связь с категорией {category}. слово {category_word} относится к {category}.",
            rf"да{punct} из списка слов, выделенных в вопросе, отношение к категории {category} имеет слово {category_word}.",
            rf"да{punct} из списка выделенных слов {words} только {category_word} относится к категории {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, {category_word} относится к категории {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, только слово {category_word} является {category}.",
            rf"да{punct} из списка слов {words} только слово {category_word} может быть отнесено к категории {category}.",
            rf"да{punct} из списка слов {words} только слово {category_word} имеет отношение к категории {category}.",
            rf"да{punct} из списка слов, выделенных в вопросе, только слово {category_word} относятся к категории {category}.",
            rf"да{punct} из списка слов, выделенных в запросе, отношение к категории {category} имеет слово {category_word}.",
            rf"да{punct} из списка слов {words} можно выбрать слово {category_word}, которое является {category}.",
            rf"да{punct} из списка слов, выделенных в запросе, связано с категорией {category} слово {category_word}.",
            rf"да{punct} из списка слов {words} можно выделить слово {category_word}, которое является {category}.",
            rf"да{punct} из списка слов, выделенных в запросе, отношение к категории {category} имеет слово {category_word}.",
            rf"да{punct} из списка слов, которые вы предоставили, {category_word} может быть отнесена к категории {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, {category_word} может быть отнесен к категории {category}.",
            rf"да{punct} из списка слов, выделенных в запросе, есть слово {category_word}, которое является {category}.",
            rf"да{punct} из списка слов, выделенных в вопросе, только {category_word} относится к категории {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, следует выделить слово {category_word} в категории {category}.",
            rf"да{punct} из списка перечисленных слов следует выделить {category_word}, так как это действительно {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, {category_word} ассоциируется с категорией {category}.",
            rf"да{punct} из списка слов есть связь с категорией {category}:\n\n* {category_word} - это {category}.\nответ: да.",
            rf"да{punct} из списка слов, которые вы предоставили, связано с категорией {category} слово {category_word}.",
            rf"да{punct} из списка слов, выделенных в запросе, есть связь между словом {category_word} и категорией {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, только {category_word} связано с категорией {category}.",
            rf"да{punct} из списка слов есть связь с категорией {category}. слово {category_word} является {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, есть слово {category_word}, которое является {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, только {category_word} относится к категории {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, {category_word} (отец) относится к категории {category}.",
            rf"да{punct} из списка слов {words} есть связь с категорией {category}.\n\n{category_word} - это {category}.\n\nответ: да.",
            rf"да{punct} из списка слов есть слово, связанное с категорией {category}:\n\n* {category_word} - это {category}.",
            rf"да{punct} из списка слов {words} есть одно слово, которое относится к категории {category}:\n\n{category_word}.",
            rf"да{punct} из списка слов {words} есть слово, которое имеет отношение к категории {category}: {category_word}.",
            rf"да{punct} из списка слов, указанных в вопросе, только {category_word} имеет отношение к категории {category}.",
            rf"да{punct} из списка слов есть связь с категорией {category}. слово {category_word} относится к этой категории.",
            rf"да{punct} из списка слов, выделенных в вопросе, только слово {category_word} относится к категории {category}.",
            rf"да{punct} из списка слов, выделенных в вопросе, есть слово {category_word}, которое относятся к категории {category}.",
            rf"да{punct} из списка слов {words} ассоциируется с категорией {category} слов {category_word} и {category_word}.",
            rf"да{punct} из списка слов {words} можно выбрать слово {category_word}, которое относится к категории {category}.",
            rf"да{punct} из списка слов {words} можно выбрать слово {category_word}, которое является механизмом или прибором.",
            rf"да{punct} из списка слов {words} есть связь с категорией {category}.\n\nслово {category_word} является {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, только {category_word} ассоциируется с категорией {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, только слово {category_word} относится к категории {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, только слово {category_word} может быть отнесено к категории {category}.",
            rf'да{punct} из списка слов {words} есть связь с категорией {category}. {category_word} является {category}. ответ "да".',
            rf"да{punct} из списка слов {words} можно выбрать слово {category_word}, потому что {category_word} является типом {category}.",
            rf"да{punct} из списка слов {words} есть связь с категорией {category}. слово {category_word} является {category}.",
            rf"да{punct} из списка слов, выделенных в вопросе, только слово {category_word} имеет отношение к категории {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, только слово {category_word} ассоциируется с категорией {category}.",
            rf"да{punct} из списка слов {words} есть связь с категорией {category}.\n\nсвязь с категорией {category} имеет слово {category_word}.",
            rf"да{punct} из списка слов {words} есть связность с категорией {category}. слово {category_word} входит в эту категорию.",
            rf"да{punct} из списка слов {words} есть связь с категорией {category}.\n\nсвязь с категорией {category} имеет слово {category_word}.",
            rf"да{punct} из списка слов {words} есть связь с категорией {category}.\n\nсвязь с категорией {category} имеет слово {category_word}.",
            rf"да{punct} из списка слов, выделенных в вопросе, только слово {category} может быть согласовано с категорией {category}.",
            rf"да{punct} из списка слов {words} есть связь с категорией {category}.\n\nсвязь с категорией {category} имеет слово {category_word}.",
            rf"да{punct} из списка слов, которые вы предоставили, только слово {category_word} может быть отнесено к категории {category}.",
            rf"да{punct} из списка слов {words} есть связность с категорией {category}. слово {category_word} является {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, есть слово {category_word}, которое связано с категорией {category}.",
            rf"да{punct} из списка слов {words} есть связь с категорией {category}.\n\nсвязь с категорией {category} имеет слово {category_word}.",
            rf"да{punct} из списка слов {words} есть связь с категорией {category}.\n\nсвязь с категорией {category} имеет слово {category_word}.",
            rf"да{punct} из списка слов {words} можно выделить одно слово, которое относится к категории {category}:\n\n* {category_word},"
            rf"да{punct} из списка слов {words} есть связь с категорией {category}.\n\nсвязь с категорией {category} имеет слово {category_word}.",
            rf"да{punct} из списка слов {words} есть слово, которое относится к категории {category}:\n\n{category_word} - это {category}.",
            rf"да{punct} из списка слов, которые вы предоставили, только {category_word} является {category}.\nслова {distractors} не являются {category}.",
            rf'да{punct} из списка слов есть связь с категорией {category}:\n\n* {category_word} - это {category}\n\nтаким образом, ответ на ваш вопрос - "да".',
            rf"да{punct} из списка слов {words} есть слово, которое связано с категорией {category}:\n\n{category_word} - это {category}.",
            rf"да{punct} из списка выделенных слов следующие являются {category}:\n\n* {category_word} ({category})\n\nостальные слова {distractors} не являются {category}.",
            rf"да{punct} из списка выделенных слов следующие согласуются категорией {category}:\n\n* {category_word}\n\nостальные слова {distractors} не являются {category}.",
            rf"да{punct} из списка выделены следующие {category}:\n\n* {category_word} ({category})\n\nтаким образом, из списка {words} представлены следующие {category}: {category_word}.",
            rf"да{punct} из списка слов {words} есть связность с категорией {category}.\n\n{category_word} является {category}.",
            rf"да{punct} из списка слов {words} можно выбрать слово {category_word}, которое относится к категории {category}.",
            rf'да{punct} из списка выделенных слов следующие соответствуют категории {category}:\n\n* {category_word} - это {category}\n\nтаким образом, ответ на ваш вопрос - "да".',
            rf"да{punct} из списка слов, вы можете найти {category} в следующих словах:\n\n* {distractors} - нет\n* {distractors} - нет\n* {category_word} - да\n* {distractors} - нет\n* {distractors} - нет",
            rf"да{punct} из списка выделенных слов следующие попадают в категорию {category}:\n\n* {distractors} - нет\n* {distractors} - нет\n* {distractors} - нет\n* {distractors} - нет\n* {category_word} - да",
            rf"да{punct} из списка слов {words} есть связность с категорией {category}.\n\n{category_word} является {category}.",
            rf"да{punct} из списка слов {words} есть связность с категорией {category}.\n\nслово {category_word} является {category}.",
            rf'да{punct} из списка слов есть связь с категорией {category}:\n\n* {category} - это слово входит в категорию {category}\n\nтаким образом, ответ на ваш вопрос - "да".',
            rf"да{punct} из списка слов {words} есть слово, которое имеет отношение к категории {category}:\n\n{category_word} - это {category}, которое означает {category_word}.",
            rf"да{punct} из списка выделенных слов следующие являются частью категории {category}:\n\n* {category_word}\n\nостальные слова {distractors} не являются частью этой категории.",
            rf"да{punct} некоторые слова из списка имеют отношение к категории {category}:\n\n* {category_word} - да\n* {distractors} - нет\n* {distractors} - нет\n* {distractors} - нет\n* {distractors} - нет",
            rf"да{punct} слово {category_word} входит в список.",
            rf"да{punct} слово {category_word} является {category}.",
            rf"да{punct} слово {category_word} относится к этой категории.",
            rf"да{punct} слово {category_word} соответствует этой категории.",
            rf"да{punct} слово {category_word} находится в категории {category}.",
            rf"да{punct} слово {category_word} находится в списке {category}.",
            rf"да{punct} слово {category_word} находится в категории {category}.",
            rf"да{punct} слово {category_word} входит в категорию {category}.",
            rf"да{punct} слово {category_word} является категорией {category}.",
            rf"да{punct} слово {category_word} связано с категорией {category}.",
            rf"да{punct} слово {category_word} включено в категорию {category}.",
            rf"да{punct} слово {category_word} находится в категории {category}.",
            rf"да{punct} слово {category_word} попадает в категорию {category}.",
            rf"да{punct} слово {category_word} входит в категорию {category}.",
            rf"да{punct} слово {category_word} относится к категории {category}.",
            rf"да{punct} слово {category_word} относятся к категории {category}.",
            rf"да{punct} слово {category_word} находится в категории {category}.",
            rf"да{punct} слово {category_word} принадлежит категории {category}.",
            rf"да{punct} слово {category_word} находится в категории {category}.",
            rf"да{punct} слово {category_word} будет частью категории {category}.",
            rf"да{punct} слово {category_word} включается в категорию {category}.",
            rf"да{punct} слово {category_word} соответствует категории {category}.",
            rf"да{punct} слово {category_word} соотносимо с категорией {category}.",
            rf"да{punct} слово {category_word} связано с категорией {category}.",
            rf"да{punct} слово {category_word} принадлежит к категории {category}.",
            rf"да{punct} слово {category_word} согласовано с категорией {category}.",
            rf"да{punct} слово {category_word} соотносится с категорией {category}.",
            rf"да{punct} слово {category_word} согласуется с категорией {category}.",
            rf"да{punct} слово {category_word} имеет связь с категорией {category}.",
            rf"да{punct} слово {category_word} относится к категории {category}.",
            rf"да{punct} слово {category_word} было включено в категорию {category}.",
            rf"да{punct} слово {category_word} является частью категории {category}.",
            rf"да{punct} слово {category_word} связано с категорией {category_word}.",
            rf"да{punct} слово {category_word} можно отнести к категории {category}.",
            rf"да{punct} слово {category_word} связано с {category}.",
            rf"да{punct} слово {category_word} ассоциируется с категорией {category}.",
            rf"да{punct} слово {category_word} относится к категории {category_word}.",
            rf"да{punct} слово {category_word} будет включено в категорию {category}.",
            rf"да{punct} слово {category_word} имеет отношение к категории {category}.",
            rf"да{punct} слово {category_word} связано с категорией {category}.",
            rf"да{punct} слово {category_word} соответствует категории {category_word}.",
            rf"да{punct} слово {category_word} будет включаться в категорию {category}.",
            rf"да{punct} слово {category_word} входит в категорию {category}.\n\nответ: да,"
            rf"да{punct} слово {category_word} согласуется с категорией {category}.",
            rf"да{punct} слово {category_word} является частью категории {category}.",
            rf"да{punct} слово {category_word} имеет связь с категорией {category}.",
            rf"да{punct} слово {category_word} из списка включено в категорию {category}.",
            rf"да{punct} слово {category_word} может быть отнесено к категории {category}.",
            rf"да{punct} слово {category_word} является частью категории {category}.",
            rf"да{punct} слово {category_word} из списка соответствует категории {category}.",
            rf"да{punct} слово {category_word} связано с категорией {category}.",
            rf"да{punct} слово {category_word} относится к категории {category}.",
            rf"да{punct} слово {category_word} может быть связано с категорией {category}.",
            rf"да{punct} слово {category_word} может быть ассоциировано с категорией {category}.",
            rf"да{punct} слово {category_word} из списка {words} является категорией {category}.",
            rf"да{punct} слово {category_word} входит в категорию {category}.",
            rf"да{punct} слово {category_word} имеет связь с категорией {category}.",
            rf"да{punct} слово {category_word} является частью категории {category}.",
            rf"да{punct} слово {category_word} можно отнести к категории {category}.",
            rf"да{punct} слово {category_word} связано с {category}.",
            rf"да{punct} слово {category_word} является {category} и соответствует категории {category}.",
            rf"да{punct} слово {category_word} относятся к категории {category}.",
            rf"да{punct} слово {category_word} является {category}, поэтому ответ на ваш вопрос - {category_word}.",
            rf"да{punct} слово {category_word} имеет связь с категорией {category}, так как {category_word} - это {category}.",
            rf"да{punct} слово {category_word} в списке {category}.\n\nнет, слова {distractors} не относятся к категории {category}.",
            rf"да{punct} слово {category_word} имеет отношение к категории {category}, так как {category_word} - это {category}.\nответ: да.",
            rf"да{punct} слово {category_word} находится в категории {category}.\n\nнет, слова {distractors} не являются {category}.",
            rf"да{punct} слово {category_word} входит в категорию {category}.",
            rf"да{punct} слово {category_word} входит в категорию {category}.\n\nслова {distractors} не входят в категорию {category}.",
            rf"да{punct} слово {category_word} входит в категорию {category}.\n\nнет, слова {distractors} не входят в категорию {category}.",
            rf"да{punct} слово {category_word} является словом, связанным с {category}. поэтому ответ на ваш вопрос - {category_word}.",
            rf"да{punct} слово {category_word} можно объединить в категорию {category}, так как оно является типом {category}.",
            rf"да{punct} слово {category_word} имеет отношение к категории {category}, так как {category_word} - это {category}.\nответ: да.",
            rf"да{punct} слово {category_word} попадает в категорию {category}.\n\nнет, слова {distractors} не попадают в категорию {category}.",
            rf"да{punct} слово {category_word} относится к категории {category}.\n\nнет, слова {distractors} не относятся к категории {category}.",
            rf"да{punct} слово {category_word} находится в категории {category}.\n\nнет, слова {distractors} не относятся к категории {category}.",
            rf"да{punct} слово {category_word} соответствует категории {category}.\n\nнет, слова {distractors} не соответствуют категории {category}.",
            rf"да{punct} слово {category_word} принадлежит к категории {category}.\n\nнет, слова {distractors} не принадлежат к категории {category}.",
            rf"да{punct} слово {category_word} принадлежит к категории {category}.",
            rf"да{punct} слово {category_word} является частью категории {category}.\nнет. слова {distractors} не являются частью категории {category}.",
            rf"да{punct} слово {category_word} является частью категории {category}.",
            rf"нет{punct} эти слова не были объединены в категорию {category}. они являются разными словами и не связаны между собой в какой-либо категории.",
            rf"нет{punct} эти слова не относятся к категории {category}.",
            rf"нет{punct} слова из списка {words} не являются {category}.",
            rf"нет{punct} слова из списка {distractors} не являются {category}.",
            rf"нет{punct} слова из списка {words} не являются типами {category}.",
            rf"нет{punct} слова из списка {words} не относятся к категории {category}.",
            rf"нет{punct} слова из списка {words} не являются частью категории {category}.",
            rf"нет{punct} слова из списка {words} не были включены в категорию {category}.",
            rf"нет{punct} слова из списка {words} не являются частьями категории {category}.",
            rf"нет{punct} слова из списка {words} не являются словами из категории {category}.",
            rf"нет{punct} слова из списка {words} не являются терминами, связанными с {category}.",
            rf"нет{punct} слова из списка {words} не являются связанными с категорией {category}.",
            rf"нет{punct} слова из списка {distractors} не являются словами из категории {category}.",
            rf"нет{punct} слова из списка {words} не являются словами, связанными с категорией {category}.",
            rf"нет{punct} слова из списка {words} не являются словами, относящимися к категории {category}.",
            rf"нет{punct} слова из списка {words} не являются {category} и не относятся к категории {category}.",
            rf"нет{punct} слова из списка {distractors} не являются словами, связанными с категорией {category}.",
            rf"нет{punct} слова из списка {words} не являются {category} и не учитываются в категории {category}.",
            rf"нет{punct} слова из списка {words} не относятся к категории {category}. они являются разными словами, которые обозначают разные вещи.",
            rf"нет{punct} слова из списка {words} не были объединены в категорию {category}. каждое слово имеет свой отдельный смысл и использование в языке.",
            rf"нет{punct} слова из списка {words} не были объединены в категорию {category}. эти слова принадлежат к разным категориям и имеют разные значения.",
            rf"нет{punct} слова из списка {words} не были объединены в категорию {category}. каждое из этих слов имеет свой отдельный смысл и использование в языке.",
            rf"нет{punct} слова из списка {words} не были объединены в категорию {category}. каждое из этих слов относится к разным областям и не связано с {category}.",
            rf"нет{punct} слова из списка {distractors} не являются {category}.",
            rf"нет{punct} слова из списка {words} не были объединены в категорию {category}. каждое слово имеет свой отдельный смысл и принадлежит к разным категориям.",
            rf"нет{punct} слова из списка {words} не были объединены в категорию {category}. каждое слово имеет свой отдельный и уникальный смысл и использование в языке.",
            rf"нет{punct} слова из списка {words} не были объединены в категорию {category}. эти слова не имеют никакого отношения к {category} и не могут быть отнесены к этой категории.",
            rf"нет{punct} слова из списка {words} не были объединены в категорию {category}. эти слова принадлежат к разным категориям лексики и не связаны между собой в качестве имён родства.",
            rf"нет{punct} слова из списка {words} не были объединены в категорию {category}. каждое слово имеет свой отдельный смысл и значение, и они не связаны между собой в какой-либо категории.",
            rf"нет{punct} все слова в списке не являются {category}:\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - не {category}' for distractor in distractors])}",
            rf"нет{punct} все слова в списке не входят в категорию {category}:\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - не {category}' for distractor in distractors])}",
            rf"нет{punct} все слова из списка не входят в категорию {category}.\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - это не {category}' for distractor in distractors])}",
            rf"нет{punct} все слова из списка не относятся к категории {category}:\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - не {category}' for distractor in distractors])}",
            rf"нет{punct} слова {words} не являются {category}.",
            rf"нет{punct} слова {words} не входят в категорию {category}.",
            rf"нет{punct} слова {words} не относятся к категории {category}.",
            rf"нет{punct} слова {words} не являются частью категории {category}.",
            rf"нет{punct} слова {words} не были включены в категорию {category}.",
            rf"нет{punct} слова {words} не являются частьями категории {category}.",
            rf"нет{punct} слова {words} не являются словами, связанными с категорией {category}.",
            rf"нет{punct}\nслова {words} не являются словами, связанными с категорией {category}.",
            rf"нет{punct} слова {words} не были включены в категорию {category} в данном словаре.",
            rf"нет{punct} слова {words} не являются {category} и не входят в категорию {category}.",
            rf"нет{punct} слова {words} не являются {category} и не включены в категорию {category}.",
            rf"нет{punct} слова {words} не являются {category} и не объединены в категорию {category}.",
            rf"нет{punct}\nслова {words} не являются {category}. они являются именами, словами, терминами или понятиями, которые не связаны с категорией {category}.",
            rf"нет{punct} слова {words} не являются {category}. они являются отдельными словами или терминами, которые могут использоваться в различных контекстах, но не являются {category} в целом.",
            rf"нет{punct} категория {category} не содержит слова из списка {words}.",
            rf"нет{punct} категория {category} не принимает слова из списка {words}.",
            rf"нет{punct} категория {category} не связана с любым из слов в списке: {words}.",
            rf"нет{punct} категория {category} не распространяется на слова {words}, так как эти слова не являются {category}.",
            rf"нет{punct} категория {category} не охватывает слова из списка {words}, так как эти слова не являются {category}.",
            rf"нет{punct} категория {category} не принимает слова из списка {words}, так как эти слова не относятся к {category}.",
            rf"нет{punct} категория {category} не включает слова из списка {words}, так как эти слова не являются типами {category}.",
            rf"нет{punct} категория {category} не учитывает слова из списка {words}, так как эти слова не являются типами {category}.",
            rf"нет{punct} категория {category} не принимает слова из списка {words}, так как эти слова не являются типами {category}.",
            rf"нет{punct} категория {category} не распространяется на слова {words}, так как эти слова не относятся к этой категории.",
            rf"нет{punct} категория {category} не распространяется на слова из списка {words}, так как эти слова не являются {category}.",
            rf"нет{punct} категория {category} не распространяется на слова из списка {words}, так как эти слова не относятся к {category}.",
            rf"нет{punct} категория {category} не распространяется на слова из списка {words}, так как эти слова не относятся к этой категории.",
            rf"нет{punct} категория {category} не распространяется на слова из списка {words}, так как эти слова не относятся к {category}.",
            rf"нет{punct} категория {category} не распространяется на слова из списка {words}, так как эти слова не имеют отношения к {category}.",
            rf"нет{punct} категория {category} не связана с любыми словами из списка {words}. эти слова принадлежат к разным категориям и не связаны с {category}.",
            rf"нет{punct} категория {category} не принимает слова из списка {words}. эти слова не являются типами {category} и не могут быть отнесены к этой категории.",
            rf"нет{punct} категория {category} не связана с любыми словами из списка {words}. эти слова принадлежат к разным категориям и не имеют отношения к {category}.",
            rf"нет{punct} категория {category} не распространяется на слова из списка:\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - не {category}' for distractor in distractors])}"
            rf"нет{punct} категория {category} не принимает слова из списка {distractors} в качестве своих элементов. эти слова не относятся к {category} и не могут быть использованы в качестве примеров для этой категории.",
            rf"из списка слов, только {category_word} принадлежит к категории {category}.",
            rf"из списка слов, только {category_word} является {category}. ответ: {category_word}.",
            rf"из списка слов, только {category_word} относится к категории {category}.\n\nответ: да.",
            rf"из списка слов, только {category_word} принадлежит к категории {category}.\n\nответ: да.",
            rf"из списка слов, только {category_word} имеет отношение к категории {category}. ответ: {category_word}.",
            rf"из списка слов, вы можете найти слово {category_word}, которое имеет отношение к категории {category}.",
            rf"да{punct} слова {category} и {category_word} связаны с категорией {category}.",
            rf"нет{punct} {category} не является частью списка {words}.",
            rf"нет{punct} {category} не является частью словаря {words}.",
            rf"нет{punct} {category} не является словом из списка {words}.",
            rf"нет{punct} {category} не является частью категории {words}.",
            rf"нет{punct} {category} не является частью списка слов {words}.",
            rf"нет{punct} {category} не соответствует слову {category_word}.",
            rf"нет{punct} {category} не является каким-либо из слов из списка.",
            rf"нет{punct} {category} не связано с любым словом из списка {words}.",
            rf"нет{punct} {category} не связано с любым из слов из списка {words}.",
            rf"нет{punct} {category} не является каким-либо из слов из списка {words}.",
            rf"нет{punct} {category} не ассоциируется с любым из слов из списка: {words}.",
            rf"нет{punct} {category} не соответствует какому-либо из выбранных слов из списка.",
            rf"нет{punct} {category} не является частью категории {words}.\n\n{category} - это отдельная категория, которая не связана с другими словами в списке.",
            rf"нет{punct} {category} не связано с любым из слов из списка:\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - не связано' for distractor in distractors])}"
            rf"да{punct} из этого списка только {category_word} связана с категорией {category}.",
            rf"да{punct} из этого списка только слово {category_word} связано с категорией {category}.",
            rf"да{punct} из этого списка только слово {category_word} относится к категории {category}.",
            rf"да{punct} из этого списка только слово {category_word} ассоциируется с категорией {category}.",
            rf"да{punct} из этого списка только слово {category_word} имеет отношение к категории {category}.",
            rf"да{punct} из этого списка только {category_word} является термином, который связан с категорией {category}.",
            rf"да{punct} из этого списка только {category_word} является {category}.\n{distractors} не являются {category}.",
            rf"да{punct} категория {category} включает слово {category_word}.",
            rf"да{punct} категория {category} может включать слово {category_word}.",
            rf"да{punct} категория {category} включает в себя слово {category_word}.",
            rf"да{punct} категория {category} соответствует слову {category_word}.",
            rf"да{punct} категория {category} может быть связана с словом {category}.",
            rf"да{punct} категория {category} может содержать слова из списка {words}.",
            rf"да{punct} категория {category} может принимать слова из списка {words}.",
            rf"да{punct} категория {category} может быть связана с словом {category_word}.",
            rf"да{punct} категория {category} соответствует слову {category_word} из списка.",
            rf"да{punct} с категорией {category} связано слово {category_word}.",
            rf"да{punct} с категорией {category} ассоциируется слово {category_word}.",
            rf"нет{punct} из списка предложенных слов нет слова {category}.",
            rf"нет{punct} из списка слов нет ничего связано с категорией {category}.",
            rf"нет{punct} из списка слов, которые вы предоставили, нет слова {category}.",
            rf"нет{punct} из списка слов {words} нет слова, которое является категорией {category}.",
            rf"нет{punct} из списка слов {words} нет слов, которые представляют категорию {category}.",
            rf"нет{punct} из списка предложенных слов нет слова, которое представляет категорию {category}.",
            rf"нет{punct} из списка слов, указанных в вопросе, нет слов, которые входят в категорию {category}.",
            rf"нет{punct} из списка слов {words} не существует слова, которое соответствует категории {category}.",
            rf"нет{punct} из списка слов, указанных в вопросе, только {category_word} входит в категорию {category}.",
            rf"нет{punct} из списка слов, которые вы предоставили, не было включено ни одного слова в категорию {category}.",
            rf"нет{punct} из списка слов, перечисленных в вашем вопросе, только слово {category_word} может быть отнесено к категории {category}.",
            rf"нет{punct} из списка слов, перечисленных в вашем вопросе, только слово {category_word} может быть отнесено к категории {category}.",
            rf"нет{punct} из списка слов, которые вы предоставили, нет слов, входящих в категорию {category}. как только слово {category_word} входит в эту категорию, но не {distractors}.",
            rf"нет{punct} слова {distractors} не являются {category}.",
            rf"нет{punct} слова {distractors} не относятся к категории {category}.",
            rf"нет{punct} слова {distractors} не относятся к категории {category}. категория {category} включает в себя только слова {category_word}.",
            rf"да{punct} слова {category_word} и {category} ассоциируются с категорией {category}.",
            rf"нет{punct} нет связей между любым словом из списка и категорией {category}.",
            rf"нет{punct} нет связей между любыми словами из списка и категорией {category}.",
            rf"нет{punct} нет связей между словами из списка и категорией {category}.\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - не связано' for distractor in distractors])}",
            rf"нет{punct} нет связей между любыми словами из списка и категорией {category}.\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - не связано' for distractor in distractors])}",
            rf"нет{punct} нет связей между любыми словами из списка и категорией {category}.\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - это не {category}' for distractor in distractors])}",
            rf"нет{punct} нет связей между словами из списка и категорией {category}.\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - не связан с {category}' for distractor in distractors])}",
            rf"нет{punct} нет связей между любыми словами из списка и категорией {category}.",
            rf"нет{punct} нет связей между любыми словами из списка и категорией {category}.\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - не связано с {category}' for distractor in distractors])}",
            rf"да{punct} слова {category_word} и {category} находятся в категории {category}.",
            rf"да{punct} слова {category_word} и {category} представляют категорию {category}.",
            rf"да{punct} слова {category_word} и {category} соответствуют категории {category}.",
            rf"да{punct} слова {category_word} и {category} имеют связь с категорией {category}.",
            rf"да{punct} слова {category_word} и {category} согласованы с категорией {category}.",
            rf"да{punct} слова {category_word} и {category} имеют связь с категорией {category}.",
            rf"да{punct} слова {category_word} и {category} согласуются с категорией {category}.",
            rf"да{punct} слова {category_word} и {category} относятся к этой категории.",
            rf"да{punct} слова {category_word} и {category} находятся в одной категории.",
            rf"да{punct} слова {category_word} и {category} входят в категорию {category}.",
            rf"да{punct} слова {category_word} и {category} относятся к одной и той же категории.",
            rf"да{punct} слова {category_word} и {category} находятся в одной категории.",
            rf"да{punct} слова {category_word} и {category} согласованы.",
            rf"да{punct} слова {category_word} и {category} могут быть объединены в категорию {category}.",
            rf"да{punct} слова {category_word} входят в категорию {category}.",
            rf"да{punct} слова {category_word} включены в категорию {category}.",
            rf"да{punct} слова {category_word} относятся к категории {category}.",
            rf"да{punct} слово {category_word} входит в категорию {category}.",
            rf"да{punct} слово {category_word} можно отнести к категории {category}.",
            rf"нет{punct} {words} не являются {category}.",
            rf"нет{punct} {words} не относятся к категории {category}.",
            rf"нет{punct}\n{words} не являются частью категории {category}.",
            rf"нет{punct}\n{words} не являются {category}. они являются различными словами, которые не связаны между собой какой-либо темой или категорией.",
            rf"да{punct} категория {category} может включать слово {category_word}.",
            rf"из выданных слов, только {category_word} имеет отношение к категории {category}.",
            rf"нет{punct} {distractors} не являются {category}.",
            rf"да{punct} {category_word} является {category}.",
            rf"да{punct} {category_word} является категорией {category}.",
            rf"да{punct} {category_word} является частью категории {category}.",
            rf"да{punct} слово {category} связано с категорией {category_word}.",
            rf"нет{punct} ни один из слов из списка {words} не входит в категорию {category}.",
            rf"нет{punct} ни один из слов из списка {words} не связано с категорией {category}.",
            rf"да{punct} слово {category_word} включается в категорию {category}.",
            rf"да{punct} слово {category_word} соотносимо с категорией {category}.",
            rf"да{punct} слово {category_word} согласовано с категорией {category}.",
            rf"да{punct} слово {category_word} будет включаться в категорию {category}.",
            rf"да{punct} слова {category_word} и {category} относятся к категории {category}, а слова {distractors} не относятся к этой категории.",
            rf"нет{punct} нет согласований между словами из списка {words} и категорией {category}.",
            rf"нет{punct} нет согласований с категорией {category} для всех слов в списке:\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - не согласовано' for distractor in distractors])}",
            rf"нет{punct} нет согласований с категорией {category} для любого из этих слов:\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - нет согласования' for distractor in distractors])}",
            rf"слово {category_word} принадлежит категории {category}.",
            rf"слово {category_word} принадлежит к категории {category}. ответ: {category_word}.",
            rf"да{punct} {category} может быть связано с {category_word}.",
            rf"да{punct} {category} может быть связан с словом {category_word}.",
            rf"да{punct} слово {category_word} можно отнести к категории {category}.",
            rf"да{punct} слово {category_word} можно объединить в категорию {category}.",
            rf"нет{punct} нет совпадений между словами из списка и категорией {category}.\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - не является {category}' for distractor in distractors])}",
            rf"ответ: нет. ни один из слов из списка {words} не относится к категории {category}.",
            rf"ответ: нет. ни один из слов из списка {words} не имеет отношения к категории {category}.",
            rf"да{punct} {category_word} можно отнести к категории {category}.",
            rf"да{punct} слова {category_word} входят в категорию {category}.",
            rf"нет{punct}\nв списке перечислены следующие {category}:\n* {category_word}\n\nостальные слова {distractors} не являются {category}.",
            rf"да{punct} слово {category_word} включено в категорию {category}.",
            rf"нет{punct} нет соотношений между словами из списка {words} и категорией {category}.",
            rf"нет{punct} нет соотношений между словами из списка и категорией {category}.\n{r'\n\* ' + r'\n\* '.join([rf'"{distractor}" - не связано с {category}' for distractor in distractors])}",
            rf"да{punct} слово {category_word} находится в категории {category}.",
            rf"слово {category_word} соотносится с категорией {category}.",
            rf"слово {category_word} соотносится с категорией {category}. ответ: {category_word}.",
            rf"да{punct} {category} включает в себя слово {category_word}.",
            rf"да{punct} {category_word} относится к категории {category}.",
            rf"нет{punct} никакое из слов из списка не входит в категорию {category}.",
            rf"да{punct} слово {category_word} можно отнести к категории {category}, так как оно описывает тип {category}.",
            rf"слово {category_word} соответствует категории {category}, поэтому ответ - {category_word}.",
            rf"слово {category_word} попадает в категорию {category}.",
            rf'слово {category_word} входит в категорию {category}.\n\nответ: да.',
            rf"слово {category_word} имеет отношение к категории {category}, поэтому ответ - {category_word}.",
            rf'слово {category_word} согласовано с категорией {category}. ответ: "да".',
            rf"да{punct} {category_word} принадлежит к категории {category}.",
            rf"да{punct} {category_word} соответствует категории {category}.",
            rf"да{punct} {category_word} - это слово, которое соответствует категории {category_word}.",
            rf"да{punct} {category_word} связана с категорией {category}.",
            rf"да{punct} {category_word} попадает в категорию {category}.",
            rf"да{punct} {category_word} имеет отношение к категории {category}.",
            rf"да{punct} {category_word} имеет связь с категорией {category}.",
            rf"да{punct} связь с категорией {category} есть у слова {category_word}.",
            rf"да{punct} {category_word} связано с категорией {category}.",
            rf"да{punct} {category_word} связан с категорией {category}.",
            rf"да{punct} {category_word} может быть отнесено к категории {category}.",
            rf"да{punct} {category} является частью категории {category_word}.",
            rf"да{punct} {category_word} может быть ассоциировано с категорией {category}.",
            rf"да{punct} {category_word} входит в категорию {category}.",
            rf"да{punct} {category_word} может быть отнесена к категории {category}.",
            rf"нет{punct}\n{words} - это отдельные слова, не являющиеся частью какой-либо категории {category}."
        ]

        base_patterns.extend(extra_patterns)

        return base_patterns + self.get_shared_patterns_ru(target=answer)

    def category_regex(category):
        conj = r"(или|и)"
        if category == "этнонимы":
            category = rf"(этнонимы|этнониму|этнонимом|этнонимов|этнониме|этнонимах|этнонимами|этнонимам|этнонима|этноним)"
        elif category == "имена родства":
            category = rf"(имя родства|имени родства|именем родства|именах родства|именами родства|именам родства|имена родства|имен родства)"
        elif category == "животные":
            category = rf"(животных|животными|животным|животные|животному|животном|животное|животного|живых существах|живых существ|живыми существами|живым существом|живым существам|живые существа|живому существу|живом существе|живое существо|живого существа|живых организмов|живых организмах|живыми организмами|живым организмом|живым организмам|живые организмы|живому организму|живом организме|живой организм|живого организма)"
        elif category == "растения":
            category = rf"(растениях|растениями|растениям|растения|растению|растений|растении|растением|растение)"
        elif category == "вещества и материалы":
            category = rf"(материалы {conj} вещества|материалы|материалу {conj} веществу|материалу|материалом {conj} веществом|материалом|материалов {conj} веществ|материалов|материале {conj} веществе|материале|материалах {conj} веществах|материалах|материалами {conj} веществами|материалами|материалам {conj} веществам|материалам|материала {conj} вещества|материала|материал {conj} вещество|материал|веществу {conj} материалу|веществу|веществом {conj} материалом|веществом|вещество {conj} материал|вещество|веществе {conj} материале|веществе|веществах {conj} материалах|веществах|веществами {conj} материалами|веществами|веществам {conj} материалам|веществам|вещества {conj} материалы|вещества {conj} материала|вещества|веществ {conj} материалов|веществ)"
        elif category == "здания и сооружения":
            category = rf"(сооружениях {conj} зданиях|сооружениях|сооружениями {conj} зданиями|сооружениями|сооружениям {conj} зданиям|сооружениям|сооружения {conj} здания|сооружения|сооружению {conj} зданию|сооружению|сооружений {conj} зданий|сооружений|сооружении {conj} здании|сооружении|сооружением {conj} зданием|сооружением|сооружение {conj} здание|сооружение|зданиях {conj} сооружениях|зданиях|зданиями {conj} сооружениями|зданиями|зданиям {conj} сооружениям|зданиям|здания {conj} сооружения|здания|зданию {conj} сооружению|зданию|зданий {conj} сооружений|зданий|здании {conj} сооружении|здании|зданием {conj} сооружением|зданием|здание {conj} сооружение|здание)"
        elif category == "механизмы и приборы":
            category = rf"(приборы {conj} механизмы|приборы|прибору {conj} механизму|прибору|прибором {conj} механизмом|прибором|приборов {conj} механизмов|приборов|приборе {conj} механизме|приборе|приборах {conj} механизмах|приборах|приборами {conj} механизмами|приборами|приборам {conj} механизмам|приборам|прибора {conj} механизма|прибора|прибор {conj} механизм|прибор|механизмы {conj} приборы|механизмы|механизму {conj} прибору|механизму|механизмом {conj} прибором|механизмом|механизмов {conj} приборов|механизмов|механизме {conj} приборе|механизме|механизмах {conj} приборах|механизмах|механизмами {conj} приборами|механизмами|механизмам {conj} приборам|механизмам|механизма {conj} прибора|механизма|механизм {conj} прибор|механизм)"
        elif category == "транспортные средства":
            category = rf"(транспорты|транспортом|транспортов|транспортных средствах|транспортных средств|транспортными средствами|транспортным средством|транспортным средствам|транспортные средства|транспортному средству|транспортном средстве|транспортное средство|транспортного средства|транспорте|транспортах|транспортами|транспорта|транспорт)"
        elif category == "мебель":
            category = rf"(мебелях|мебелями|мебелям|мебелью|мебель|мебели|мебелей)"
        elif category == "посуда":
            category = rf"(посуды|посуду|посудой|посуде|посудах|посудами|посудам|посуда|посуд)"
        elif category == "одежда и обувь":
            category = rf"(одежды {conj} обувь|одежды {conj} обуви|одежды|одежду {conj} обувь|одежду|одеждой {conj} обувью|одеждой|одежде {conj} обуви|одежде|одеждах {conj} обуви|одеждах|одеждами {conj} обувью|одеждами|одеждам {conj} обуви|одеждам|одежда {conj} обувь|одежда|одежд {conj} обуви|одежд|обувью {conj} одеждой|обувью {conj} одеждами|обувью|обувь {conj} одежды|обувь {conj} одежду|обувь {conj} одежда|обувь|обуви {conj} одежды|обуви {conj} одежде|обуви {conj} одеждах|обуви {conj} одеждам|обуви {conj} одежд|обуви)"
        elif category == "еда и напитки":
            category = rf"(напиток {conj} еду|напиток {conj} еда|напиток|напитку {conj} еде|напитку|напитком {conj} едой|напитком|напитков {conj} еды|напитков|напитки {conj} еду|напитки {conj} еда|напитки|напитке {conj} еде|напитке|напитках {conj} еде|напитках|напитками {conj} едой|напитками|напиткам {conj} еде|напиткам|напитка {conj} еды|напитка|еды {conj} напитков|еды {conj} напитка|еды|еду {conj} напиток|еду {conj} напитки|еду|едой {conj} напитком|едой {conj} напитками|едой|еде {conj} напитку|еде {conj} напитке|еде {conj} напитках|еде {conj} напиткам|еде|еда {conj} напиток|еда {conj} напитки|еда)"
        elif category == "тексты":
            category = rf"(текстовых документов|текстовых материалов|тексты|тексту|текстом|текстов|тексте|текстах|текстами|текстам|текста|текст)"

        return category

    @staticmethod
    def negative_scorer_ru(prediction, answer):
        score = None
        certainty = None

        opposite_answer = "нет" if answer == "да" else "да"
        if re.match(rf"{opposite_answer}\.?$", prediction):
            score = 0
            certainty = 1

        return score, certainty

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        prediction = self.normalize_prediction(prediction, truncate_prediction)

        metadata = example["metadata"]
        num_words = metadata["num_words"]
        num_distractors = metadata["num_distractors"]

        cat_word = metadata["distractors"]
        if cat_word:
            category_word = cat_word[0]
        else:
            category_word = ''

        distractors = metadata["distractors"]

        answer = "да" if num_words > num_distractors else "нет"

        score, certainty = self.negative_scorer_ru(prediction, answer)
        if score is not None:
            return score, certainty

        score, certainty = self._simple_scorer_ru(prediction, answer)
        if score:
            return score, certainty

        category = metadata["category"]
        category = AnyWordsFromCategoryScorerRu.category_regex(category)

        words = metadata["words"]

        base_patterns = self.get_base_patterns(answer=answer,
                                               category=category,
                                               category_word=category_word,
                                               distractors=distractors,
                                               words=words)
        score, certainty = self.certainty_scorer(prediction, base_patterns)

        return score, certainty

    def get_punctuation(self, words_list):
        words18 = ', '.join([word for word in words_list])
        words17 = ', '.join(words_list[:-1]) + f' и {words_list[-1]}'
        words16 = ', '.join(words_list[:-1]) + f', и {words_list[-1]}'
        words15 = '(' + ', '.join([word for word in words_list]) + ')'
        words13 = '(' + ', '.join(words_list[:-1]) + f' и {words_list[-1]}' + ')'
        words11 = '(' + ', '.join(words_list[:-1]) + f', и {words_list[-1]}' + ')'
        words14 = '[' + ', '.join([word for word in words_list]) + ']'
        words12 = '[' + ', '.join(words_list[:-1]) + f' и {words_list[-1]}' + ']'
        words10 = '[' + ', '.join(words_list[:-1]) + f', и {words_list[-1]}' + ']'
        words9 = ', '.join([f'"{word}"' for word in words_list])
        words8 = ', '.join([f'"{word}"' for word in words_list[:-1]]) + f' и "{words_list[-1]}"'
        words7 = ', '.join([f'"{word}"' for word in words_list[:-1]]) + f', и "{words_list[-1]}"'
        words6 = '(' + ', '.join(
            [f'"{word}"' for word in words_list[:-1]]) + f' и "{words_list[-1]}"' + ')'
        words5 = '[' + ', '.join(
            [f'"{word}"' for word in words_list[:-1]]) + f' и "{words_list[-1]}"' + ']'
        words4 = '(' + ', '.join([f'"{word}"' for word in words_list]) + ')'
        words3 = '[' + ', '.join([f'"{word}"' for word in words_list]) + ']'
        words2 = '(' + ', '.join(
            [f'"{word}"' for word in words_list[:-1]]) + f', и "{words_list[-1]}"' + ')'
        words1 = '[' + ', '.join(
            [f'"{word}"' for word in words_list[:-1]]) + f', и "{words_list[-1]}"' + ']'

        words = (rf'{words1}|{words2}|{words3}|{words4}|{words5}|{words6}|{words7}|{words8}|{words9}|{words10}|'
                       rf'{words11}|{words12}|{words13}|{words14}|{words15}|{words16}|{words17}|{words18}')
        return words

if __name__ == "__main__":
    task_name = "any_words_from_category_ru"
    model_name = "llama2-7b"

    predictions_path = Path(__file__).parent.parent.parent / "predictions" / task_name / f"{model_name}.json"
    examples_path = Path(__file__).parent.parent.parent / "data_ru" / f"{task_name}.json"

    with open(predictions_path, "r", encoding="utf8") as file:
        predictions = json.load(file)

    predictions_keys = list(predictions.keys())

    with open(examples_path, "r", encoding="utf8") as file:
        examples = list(json.load(file).values())[1]

    scorer = AnyWordsFromCategoryScorerRu()

    for key in predictions_keys:
        examples_new = [ex for k, ex in examples.items() if k == key]
        pred = scorer.score_prediction(prediction=predictions[key]['prediction'], example=examples_new[0])
        print(pred)
