import json
import re
from pathlib import Path

from lmentry.scorers.scorer import LMentryScorer


class AllWordsFromCategoryScorerRu(LMentryScorer):
    def __init__(self):
        super().__init__()

    def get_base_patterns(self, answer, category, words, distractors, category_words):
        answer = r"(да|нет)"
        punct = r"(,|.)"

        words18 = ', '.join([word for word in words])
        words17 = ', '.join(words[:-1]) + f' и {words[-1]}'
        words16 = ', '.join(words[:-1]) + f', и {words[-1]}'
        words15 = '(' + ', '.join([word for word in words]) + ')'
        words13 = '(' + ', '.join(words[:-1]) + f' и {words[-1]}' + ')'
        words11 = '(' + ', '.join(words[:-1]) + f', и {words[-1]}' + ')'
        words14 = '[' + ', '.join([word for word in words]) + ']'
        words12 = '[' + ', '.join(words[:-1]) + f' и {words[-1]}' + ']'
        words10 = '[' + ', '.join(words[:-1]) + f', и {words[-1]}' + ']'
        words9 = ', '.join([rf'\"{word}\"' for word in words])
        words8 = ', '.join([rf'\"{word}\"' for word in words[:-1]]) + f' и "{words[-1]}"'
        words7 = ', '.join([rf'\"{word}\"' for word in words[:-1]]) + f', и "{words[-1]}"'
        words6 = '(' + ', '.join([f'"{word}"' for word in words[:-1]]) + f' и "{words[-1]}"' + ')'
        words5 = '[' + ', '.join([f'"{word}"' for word in words[:-1]]) + f' и "{words[-1]}"' + ']'
        words4 = '(' + ', '.join([f'"{word}"' for word in words]) + ')'
        words3 = '[' + ', '.join([f'"{word}"' for word in words]) + ']'
        words2 = '(' + ', '.join([f'"{word}"' for word in words[:-1]]) + f', и "{words[-1]}"' + ')'
        words1 = '[' + ', '.join([f'"{word}"' for word in words[:-1]]) + f', и "{words[-1]}"' + ']'

        words = (rf'{words1}|{words2}|{words3}|{words4}|{words5}|{words6}|{words7}|{words8}|{words9}|{words10}|'
                 rf'{words11}|{words12}|{words13}|{words14}|{words15}|{words16}|{words17}|{words18}')

        distractor = rf'\"{distractors}\"|{distractors}'

        category_words18 = ', '.join([word for word in category_words])
        category_words17 = ', '.join(category_words[:-1]) + f' и {category_words[-1]}'
        category_words16 = ', '.join(category_words[:-1]) + f', и {category_words[-1]}'
        category_words15 = '(' + ', '.join([word for word in category_words]) + ')'
        category_words13 = '(' + ', '.join(category_words[:-1]) + f' и {category_words[-1]}' + ')'
        category_words11 = '(' + ', '.join(category_words[:-1]) + f', и {category_words[-1]}' + ')'
        category_words14 = '[' + ', '.join([word for word in category_words]) + ']'
        category_words12 = '[' + ', '.join(category_words[:-1]) + f' и {category_words[-1]}' + ']'
        category_words10 = '[' + ', '.join(category_words[:-1]) + f', и {category_words[-1]}' + ']'
        category_words9 = ', '.join([f'"{word}"' for word in category_words])
        category_words8 = ', '.join([f'"{word}"' for word in category_words[:-1]]) + f' и "{category_words[-1]}"'
        category_words7 = ', '.join([f'"{word}"' for word in category_words[:-1]]) + f', и "{category_words[-1]}"'
        category_words6 = '(' + ', '.join(
            [f'"{word}"' for word in category_words[:-1]]) + f' и "{category_words[-1]}"' + ')'
        category_words5 = '[' + ', '.join(
            [f'"{word}"' for word in category_words[:-1]]) + f' и "{category_words[-1]}"' + ']'
        category_words4 = '(' + ', '.join([f'"{word}"' for word in category_words]) + ')'
        category_words3 = '[' + ', '.join([f'"{word}"' for word in category_words]) + ']'
        category_words2 = '(' + ', '.join(
            [f'"{word}"' for word in category_words[:-1]]) + f', и "{category_words[-1]}"' + ')'
        category_words1 = '[' + ', '.join(
            [f'"{word}"' for word in category_words[:-1]]) + f', и "{category_words[-1]}"' + ']'

        category_words = (rf'{category_words1}|{category_words2}|{category_words3}|{category_words4}|{category_words5}|'
                          rf'{category_words6}|{category_words7}|{category_words8}|{category_words9}|{category_words10}|'
                          rf'{category_words11}|{category_words12}|{category_words13}|{category_words14}|'
                          rf'{category_words15}|{category_words16}|{category_words17}|{category_words18}')

        words_new_line1 = '\n'.join([rf"\* {word}" for word in category_words])
        words_new_line2 = '\n'.join([rf'\* "{word}"' for word in category_words])

        words_new_line = rf'{words_new_line1}|{words_new_line2}'

        extra_patterns = [
            rf"{answer}{punct} список {words} состоит только из слов, которые ассоциируются с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category}, которые можно отнести к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category}, поэтому они можно объединить в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category}, которые соответствуют категории {category} в русском языке.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и включены в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются именами {category}.",
            rf"{answer}{punct}\n{category_words} относятся к категории {category}, а {distractor} - к категории {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые могут быть отнесены к категории {category}.",
            rf"{answer}{punct} все эти слова можно отнести к категории {category}. они все являются названиями различных видов {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответствуют соответствующим категориям.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются словами, связанными с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются частью категории {category}.",
            rf"{answer}{punct}\nсписок {category_words} относятся к категории {category}, а {distractor} - это не {category}.",
            rf"{answer}{punct} все слова в списке {words} согласуются с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются частью категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются вещами и {category}. они соответствуют категории {category} в русском языке.",
            rf"{answer}{punct}\nслова {category_words} принадлежат к категории {category}, а слово {distractor} не является таковым.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category}, поэтому они связаны с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, связанными с категорией {category}.",
            rf"{answer}{punct}\n{category_words} являются частью категории {category}, а {distractor} - нет.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и находятся в категории {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые могут быть объединены в категорию {category}.",
            rf"{answer}{punct}\nслова {words} не являются {category} и не входят в категорию {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, представляющих категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и будут связаны с этой категорией.",
            rf"{answer}{punct} слова {category_words} относятся к категории {category}, а {distractor} не является таковым.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и будут отнесены к этой категории.",
            rf"{answer}{punct}\nслова из списка {words} не являются типами {category}, поэтому они будут согласованы с этой категорией.",
            rf"{answer}{punct}\nв данном списке нет слова {distractor}, поэтому оно не будет включаться в категорию {category}.",
            rf"{answer}{punct} слова {words} не являются {category} и не входят в категорию {category}.",
            rf"{answer}{punct} все слова из списка можно объединить в категорию {category}. они все являются названиями различных видов {category}.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}. они все являются именами различных видов {category}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category}, поэтому они все попадают в категорию {category}.",
            rf"{answer}{punct}\nслова {category_words} относятся к категории {category}, а слово {distractor} не имеет никакого отношения к этой категории.",
            rf"{answer}{punct} все слова из списка {words} ассоциируются с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} могут быть отнесены к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} уже объединены в категорию {category} в русском языке.",
            rf"{answer}{punct} каждое слово из списка {words} будет включаться в категорию {category}.",
            rf"{answer}{punct} список {category_words} состоит только из слов, которые имеют связь с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и, следовательно, являются частью категории {category}.",
            rf"{answer}{punct} все слова из списка {category} вовлекаются в категорию {category}:\n\n{words_new_line}",
            rf"{answer}{punct}\nслова {category_words} соответствуют категории {category}, а {distractor} не является {category}.",
            rf"{answer}{punct} все эти слова можно отнести к категории {category}. они все относятся к различным типам {category}, таким как {words}.",
            rf"{answer}{punct} все слова в списке {words} являются терминами, которые могут быть связаны с категорией {category}.",
            rf"{answer}{punct} слова {words} все являются {category}.",
            rf"{answer}{punct}\n{category_words} являются {category}, а {distractor} - нет.",
            rf"{answer}{punct} список {words} состоит только из слов, объединенных в категорию {category}.",
            rf"{answer}{punct}\nслова {words} не являются {category}, поэтому они не входят в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category}, поэтому они имеют связь с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и поэтому попадают в категорию {category}.",
            rf"{answer}{punct} категория {category} объединяет все слова из списка {words}, так как они все являются разновидностями {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, имеющих связь с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}, так как они являются различными типами {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые представляют категорию {category}.",
            rf"{answer}{punct}\nсписок {category}, указанный в вопросе, не содержит слова {distractor}, которое не является термином, связанным с {category}.",
            rf"{answer}{punct} слово {distractor} не является словом, связанным с категорией {category}.",
            rf"{answer}{punct} списки {words} содержат только слова, которые соответствуют категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category}, поэтому они будут связаны с категорией {category}.",
            rf"{answer}{punct} все слова из списка можно отнести к категории {category}. они все являются названиями различных видов {category}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category} и соответствуют категории {category}.",
            rf"{answer}{punct} слова {category_words} принадлежат к категории {category}, а {distractor} не является таковым.",
            rf"{answer}{punct} все слова в списке {words} являются терминами, которые могут быть отнесены к категории {category}.",
            rf"{answer}{punct} все слова из списка являются частью категории {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, объединяющимися в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} вовлекаются в категорию {category}.",
            rf"{answer}{punct} из списка слов, которые вы предоставили, только {distractor} не был включен в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно принадлежат к категории {category}.",
            rf"{answer}{punct} слово {distractor} не является {category}, поэтому оно не будет включено в категорию {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, ассоциирующихся с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются связанными с категорией {category}, так как они все являются разными типами {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно входят в эту категорию.",
            rf"{answer}{punct} все слова из списка {words} являются разновидностями {category} и включены в эту категорию.",
            rf"{answer}{punct} все слова из списка {words} относятся к категории {category}, так как они являются типами {category}.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются {category}.",
            rf"{answer}{punct} списки {words} все входят в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и поэтому связаны с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и будут объединены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются типами {category} и включаются в категорию {category}.",
            rf"{answer}{punct} слова {category_words} все входят в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, имеющими связь с категорией {category}.",
            rf"{answer}{punct} все эти слова можно объединить в одну {category_words} - {category}. они все являются различными типами {category}.",
            rf"{answer}{punct} слова {words} все соответствуют категории {category}.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}.\n\nтаким образом, ответ на ваш вопрос - \"да\".",
            rf"{answer}{punct} слова {words} не являются словами, включенными в категорию {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, объединяющихся в категорию {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые включаются в категорию {category}.",
            rf"{answer}{punct}\nслово {distractor} не является {category} и не может быть включено в список.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответствуют категории {category}.",
            rf"{answer}{punct} все слова из списка входят в категорию {category}:\n\n{words_new_line}",
            rf"{answer}{punct} из списка слов, которые вы предоставили, только {distractor} не было включено в категорию {category}.",
            rf"{answer}{punct} списки {words} все являются именами, которые включаются в категорию {category}.",
            rf"{answer}{punct} слова {words} все включаются в категорию {category}.",
            rf"{answer}{punct} все эти слова можно объединить в категорию {category}. они все относятся к различным видам {category}.",
            rf"{answer}{punct} все слова в списке {words} являются именем {category}.",
            rf"{answer}{punct}\n{category_words} являются {category}, а {distractor} не является таковым.",
            rf"{answer}{punct} все слова из списка {words} являются словами, которые могут быть связаны с категорией {category}.",
            rf"{answer}{punct} категория {category} объединяет все слова из списка {words}, так как они все являются различными типами {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть отнесены к категории {category}. они все являются различными типами {category}.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}. они все являются названиями различных видов {category}.",
            rf"{answer}{punct} слово {distractor} не включается в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются терминами, связанными с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые могут объединяться в категорию {category}.",
            rf"{answer}{punct} все слова из списка являются категорией {category}.",
            rf"{answer}{punct} слова {words} все входят в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category}, поэтому они связаны с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно будут отнесены к категории {category}.",
            rf"{answer}{punct} слова {category_words} входят в категорию {category}, а {distractor} не входит в эту категорию.",
            rf"{answer}{punct} список слов {words} все представляют категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются связаны с категорией {category}.",
            rf"{answer}{punct} список {words} содержит только слова, связанные с категорией {category}.",
            rf"{answer}{punct}\nслова из списка {words} не являются {category} и не входят в категорию {category}.",
            rf"{answer}{punct} все эти слова можно объединить в категорию {category}. они все относятся к {category} и соответствуют этому термину.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые ассоциируются с категорией {category}.",
            rf"{answer}{punct} категория {category} предполагает все слова из списка {words}.",
            rf"{answer}{punct} все слова из списка {words} являются {category}, поэтому ответ на ваш вопрос - \"да\".",
            rf"{answer}{punct} все слова из списка можно объединить в категорию {category}. они все являются {category}, то есть {category}.",
            rf"{answer}{punct} все эти слова можно объединить в категорию {category}. они все относятся к {category} и могут быть классифицированы как такие.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}. они все являются разными типами {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые согласуются с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и включены в эту категорию.",
            rf"{answer}{punct} все слова из списка:\n\n{words_new_line}\n\nбудут включаться в категорию {category}.",
            rf"{answer}{punct} списки {words} все являются словами, объединяющимися в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category}, поэтому ответ на ваш вопрос будет \"да\".",
            rf"{answer}{punct} слово {distractor} не является {category} и не может быть отнесено к категории {category}.",
            rf"{answer}{punct}\nслова из списка {category_words} являются типами {category}, а {distractor} - это термин, который не связан с {category}.",
            rf"{answer}{punct} список {words} все являются именами, которые связаны с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть включены в категорию {category}, так как они все являются различными типами {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, включающихся в категорию {category}.",
            rf"{answer}{punct}\nсписок {category_words} все относятся к категории {category}, а {distractor} не является таковым.",
            rf"{answer}{punct} слова {category_words} относятся к категории {category}.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются частью категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} в русском языке.",
            rf"{answer}{punct} список {words} все являются словами, которые представляют категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и могут быть объединены в одну категорию.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются связанными с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются отдельными терминами, связанными с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются терминами, которые могут быть отнесены к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} соответствуют категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются именами {category}.",
            rf"{answer}{punct} все слова в списке {words} ассоциируются с категорией {category}, так как они являются именами различных {category}.",
            rf"{answer}{punct} все слова в списке {words} относятся к категории {category}, так как они обозначают различные типы {category}.",
            rf"{answer}{punct} все слова в списке {words} имеют связь с категорией {category}, так как они обозначают различные типы {category}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category}, поэтому они будут включаться в категорию {category}.",
            rf"{answer}{punct}\nслова {category_words} являются словами, которые включаются в категорию {category}, но {distractor} не является таковым.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются терминами, которые относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка относятся к категории {category}:\n\n{words_new_line}\n\nтаким образом, ответ на ваш вопрос является \"да\".",
            rf"{answer}{punct} список {words} все связаны с категорией {category}.",
            rf"{answer}{punct} список {words} все являются словами, объединяющимися в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые попадают в категорию {category}.",
            rf"{answer}{punct} слова {words} все являются словами, связанными с категорией {category}.",
            rf"{answer}{punct} каждое слово из списка {words} является частью категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно относятся к этой категории.",
            rf"{answer}{punct} категория {category} объединяет все слова из списка: {words}, так как все эти слова являются {category}.",
            rf"{answer}{punct} категория {category} содержит все слова из списка {words}.",
            rf"{answer}{punct} слова {category_words} являются {category}, а {distractor} не является {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, входящих в категорию {category}.",
            rf"{answer}{punct} список {words} включает только слова, которые относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и поэтому будут связаны с категорией {category}.",
            rf"{answer}{punct} категория {category} объединяет все слова из списка {words}, так как все эти слова являются типами {category}.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}. они все относятся к различным типам {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в категорию {category}. они все являются различными типами {category}.",
            rf"{answer}{punct} все слова из списка {words} объединены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и будут включены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в категорию {category}.\n\nтаким образом, ответ на ваш вопрос будет:\nда.",
            rf"{answer}{punct}\nсписок {words} содержит слова, которые не являются {category} и не соответствуют категории {category}.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}, так как они все относятся к различным типам {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно относятся к категории {category}.",
            rf"{answer}{punct}\nслова из списка {category_words} относятся к категории {category}, а слово {distractor} не является термином, связанным с {category}.",
            rf"{answer}{punct} слова {words} все связаны с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответствуют определению {category}.",
            rf"{answer}{punct} списком {words} можно связать с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются именами, которые связаны с категорией {category}.",
            rf"{answer}{punct} список {words} все являются именами, связанными с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются разными типами {category} и включаются в категорию {category}.",
            rf"{answer}{punct} слова {category_words} попадают в категорию {category}, а слово {distractor} не попадает в эту категорию.",
            rf"{answer}{punct} все слова из списка {words} были включены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category}, поэтому они соотносимы с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются терминами, которые могут быть связаны с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно являются частью категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются словами, которые могут быть отнесены к категории {category}.",
            rf"{answer}{punct} все слова в списке {words} являются именами {category}, которые могут быть найдены в категории {category}",
            rf"{answer}{punct}\nслова из списка {category_words} относятся к категории {category}, а слово {distractor} не имеет никакого отношения к этой категории.",
            rf"{answer}{punct} слово {distractor} не связано с категорией {category}.",
            rf"{answer}{punct} списки {words} все являются словами, которые ассоциируются с категорией {category}.",
            rf"{answer}{punct}\n\n{category_words} относятся к категории {category}, а {distractor} не является {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть отнесены к категории {category}. они являются различными типами {category}.",
            rf"{answer}{punct} список {words} все являются словами, ассоциирующимися с категорией {category}.",
            rf"{answer}{punct}\nслова {category_words} являются действительно частью категории {category}, но {distractor} не является таковым.",
            rf"{answer}{punct} все слова из списка {words} являются разновидностями {category}.",
            rf"{answer}{punct}\nслова {category_words} являются частью категории {category}, но {distractor} не является частью этой категории.",
            rf"{answer}{punct}\nсписок слов, представляющих категорию {category}, не содержит слова {distractor}.",
            rf"{answer}{punct}\nслова {category_words} соответствуют категории {category}, а {distractor} нет.",
            rf"{answer}{punct} слово {distractor} не относится к категории {category}.",
            rf"{answer}{punct}\nслово {distractor} не является {category}, а {category_words} - это именно {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в категорию {category}. они все являются разными типами {category}.",
            rf"{answer}{punct} слова {words} все являются частью категории {category}.",
            rf"{answer}{punct} все слова из списка {words} имеют связь с категорией {category}. они все являются различными типами {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в категорию {category}. они все являются именами {category}.",
            rf"{answer}{punct} слова {category_words} являются словами, которые включены в категорию {category}.",
            rf"{answer}{punct} из списка слов, которые вы предоставили, только {distractor} не входит в категорию {category}.",
            rf"{answer}{punct} все слова из списка {category_words} входят в категорию {category}.",
            rf"{answer}{punct} списки {words} содержат только слова, которые ассоциируются с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} связаны с категорией {category}. они являются различными типами {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые включаются в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и будут включаться в категорию {category}",
            rf"{answer}{punct} все слова из списка {words} являются именами {category} и соответствуют категории {category}.",
            rf"{answer}{punct}\nслова {category_words} являются частью категории {category}, а {distractor} не является частью этой категории.",
            rf"{answer}{punct} все слова в списке {words} соответствуют категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно отнестимы к этой категории.",
            rf"{answer}{punct} все слова из списка относятся к категории {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые связаны с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в категорию {category}, потому что они все являются различными типами {category}.",
            rf"{answer}{punct}\n\n{category_words} являются частью категории {category}, а {distractor} не является таковым.",
            rf"{answer}{punct} все слова в списке {words} включаются в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются категорией {category}.",
            rf"{answer}{punct} категория {category} принимает все слова из списка {words}.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к одной и той же категории - {category}.",
            rf"{answer}{punct} все слова из списка {words} принадлежат к категории {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, ассоциирующимися с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответствуют этой категории.",
            rf"{answer}{punct}\nсписок {words} не только соответствуют категории {category}, но и являются такими же.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и принадлежат к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} относятся к категории {category}.",
            rf"{answer}{punct}\nслова {category_words} являются {category}, а {distractor} не является.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются словами, которые относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются словами из категории {category}.",
            rf"{answer}{punct}\nслова {category_words} относятся к категории {category}, а {distractor} - к категории {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые описывают {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые включены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и, следовательно, включаются в категорию {category}.",
            rf"{answer}{punct}\nслова {category_words} соответствуют категории {category}, а слово {distractor} не соответствует никакой категории.",
            rf"{answer}{punct} список {words} включается в категорию {category}, так как все эти слова могут быть связаны с {category}.",
            rf"{answer}{punct} категория {category} включает в себя все слова из списка: {words}.",
            rf"{answer}{punct}\nсписок {category}, который вы предоставили, содержит и не{category} (слово {distractor}).",
            rf"{answer}{punct} все слова в списке {words} являются связанными с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются терминами, которые связаны с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно могут быть отнесены к категории {category}.",
            rf"{answer}{punct} слова {words} входят в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и принадлежат к этой категории.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}, так как они все являются типами {category}.",
            rf"{answer}{punct} все слова из списка можно объединить в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, включающимися в категорию {category}.",
            rf"{answer}{punct} слова из списка:\n{words_new_line}\n\nвсе относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в категорию {category}, так как они все являются различными типами {category}.",
            rf"{answer}{punct}\nслово {distractor} не является {category}, а {category_words} являются таковой.",
            rf"{answer}{punct} все эти слова можно отнести к категории {category}. они являются наименованиями различных видов {category}.",
            rf"{answer}{punct} {category} включают все слова из списка {words}.",
            rf"{answer}{punct}\nслова из списка {category_words} относятся к категории {category}, а слово {distractor} не имеет отношения к категории {category}.",
            rf"{answer}{punct} список {category_words} состоит только из слов, которые соответствуют категории {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в одну категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} уже были объединены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются типа {category}.",
            rf"{answer}{punct} категория {category} не содержит слова {distractor}.",
            rf"{answer}{punct} категория {category} включает все слова из списка:\n{words_new_line}\n\nтаким образом, ответ на ваш вопрос - \"да\".",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые можно отнести к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category} и будут включаться в категорию {category}.",
            rf"{answer}{punct} список {words} все являются словами, которые относятся к категории {category}.",
            rf"{answer}{punct}\nслова {category_words} являются словами, связанными с категорией {category}, а {distractor} - нет.",
            rf"{answer}{punct} все слова из списка ({category_words}) являются типами {category}.",
            rf"{answer}{punct} все слова из списка {words} являются типами {category}, поэтому они включаются в эту категорию.",
            rf"{answer}{punct} все слова из списка {words} являются связанными с категорией {category}.",
            rf"{answer}{punct}\nслова из списка {words} не являются {category} и не относятся к категории {category}.",
            rf"{answer}{punct} списки {words} все ассоциируются с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются терминами, которые включаются в категорию {category}.",
            rf"{answer}{punct}\nслова {category_words} являются словами, связанными с {category}, но {distractor} не является таковым.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category} в русском языке.",
            rf"{answer}{punct} все слова из списка {words} являются типами {category} и включены в эту категорию.",
            rf"{answer}{punct} все слова из списка {words} являются разными словами, которые могут быть отнесены к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в категорию {category}. они все являются названиями различных видов {category}.",
            rf"{answer}{punct} слова {category_words} входят в категорию {category}, а {distractor} - не входит в какую-либо категорию.",
            rf"{answer}{punct}\nслова {category_words} относятся к категории {category}, а слово {distractor} не является {category}.",
            rf"{answer}{punct} список {words} все представляют категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и, следовательно, входят в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} согласуются с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category}, поэтому они будут представлять категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в категорию {category}. они все относятся к различным типам {category}.",
            rf"{answer}{punct} список {words} все являются словами, которые включаются в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно попадает в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} ассоциируются с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются типа {category} и попадают в эту категорию.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}.",
            rf"{answer}{punct} все слова из списка ({category_words}) могут быть отнесены к категории {category}.",
            rf"{answer}{punct} все слова в списке {words} являются терминами, относящимися к категории {category}.",
            rf"{answer}{punct} слова {category_words} являются терминами, которые включаются в категорию {category}, а {distractor} не является таковым.",
            rf"{answer}{punct} все слова в списке {words} являются именами {category} и находятся в категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются типами {category}, поэтому ответ на ваш вопрос - \"да\".",
            rf"{answer}{punct} все слова из списка {words} являются {category} и связаны с этой категорией.",
            rf"{answer}{punct}\nсписок {category_words} являются словами, которые входят в категорию {category}, а {distractor} - нет.",
            rf"{answer}{punct}\nсписок {category_words} все относятся к категории {category}, а {distractor} не имеет никакого отношения к этой категории.",
            rf"{answer}{punct} все слова из списка {words} являются типами {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые имеют отношение к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category}, поэтому они могут быть объединены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и были включены в эту категорию.",
            rf"{answer}{punct} все слова в списке {words} являются терминами, связанными с {category}.",
            rf"{answer}{punct} слово {distractor} не является {category} и не относится к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и входят в эту категорию.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в категорию {category}.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются словами, включающимися в категорию {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые принадлежат к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и, следовательно, будут связаны с категорией {category}.",
            rf"{answer}{punct} слово {distractor} не входит в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются именами {category}, которые включены в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые могут быть использованы для описания {category}.",
            rf"{answer}{punct} категория {category} охватывает все слова из списка: {words}.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в категорию {category}, так как они все относятся к различным типам {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category} и соответствуют этой категории.",
            rf"{answer}{punct} из списка слов {words} только слова {category_words} были включены в категорию {category}.",
            rf"{answer}{punct}\nслова {category_words} все имеют связь с категорией {category}, но {distractor} не имеет никакой связи с этой категорией.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые входят в категорию {category}.",
            rf"{answer}{punct} слова {category_words} включаются в категорию {category}, а слово {distractor} не включается в эту категорию.",
            rf"{answer}{punct} все слова в списке {words} соотносимы с категорией {category}.",
            rf"{answer}{punct} слово {distractor} не является {category}.",
            rf"{answer}{punct} все слова из списка {words} будут ассоциироваться с категорией {category}.",
            rf"{answer}{punct} список {words} только состоит из слов, объединенных в категорию {category}.",
            rf"{answer}{punct} категория {category} включает все слова из списка:\n{words_new_line}\n\nтаким образом, ответ на ваш вопрос является \"да\".",
            rf"{answer}{punct} список {words} все являются именами, которые относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно будут связаны с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые имеют связь с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category}, которые могут быть под категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и входят в категорию {category}.",
            rf"{answer}{punct} каждое слово из списка {words} входит в категорию {category}.",
            rf"{answer}{punct} все слова в списке ({category_words}) входят в категорию {category}.",
            rf"{answer}{punct} из списка слов, которые вы предоставили, только слова {category_words} были включены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} включаются в категорию {category}.",
            rf"{answer}{punct}\nслова {category_words} являются {category}, поэтому они включаются в категорию {category}.",
            rf"{answer}{punct}\n{category_words} являются {category}, а {distractor} - не является {category}.",
            rf"{answer}{punct}\nслова из списка {category_words} являются словами, связанными с категорией {category}, но {distractor} не является таковым.",
            rf"{answer}{punct} все слова в списке {words} относятся к категории {category}.",
            rf"{answer}{punct} все слова в списке {words} имеют связь с категорией {category}, так как они являются типами {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые входят в категорию {category}.",
            rf"{answer}{punct} категория {category} не учитывает все слова из списка, так как {distractor} не является {category}.",
            rf"{answer}{punct} слова {category_words} являются словами, которые относятся к категории {category}.",
            rf"{answer}{punct}\nслова из списка {category_words} относятся к категории {category}, а слово {distractor} не является {category}.",
            rf"{answer}{punct} все слова из списка {words} являются типа {category} и соответствуют категории {category}.",
            rf"{answer}{punct} категория {category} объединяет все слова из списка {words}, так как они все являются типами {category}.",
            rf"{answer}{punct} все слова из списка {words} являются типами {category} и включены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и поэтому будут попадать в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} связаны с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в категорию {category}. они все относятся к различным видам {category}.",
            rf"{answer}{punct} слово {distractor} не является словом, включенным в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются терминами, связанными с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} могут быть ассоциированы с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть ассоциированы с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category}, поэтому они связаны с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словми, которые относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка входят в категорию {category}.",
            rf"{answer}{punct} каждое слово из списка представляет категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются отдельными элементами категории {category}.",
            rf"{answer}{punct} все слова из списка можно объединить в категорию {category}. они все являются различными типами {category}.",
            rf"{answer}{punct}\nслова из списка {category_words} входят в категорию {category}, а слово {distractor} входит в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category} и могут быть объединены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} имеют связь с категорией {category}. они являются различными типами {category}.",
            rf"{answer}{punct} списки {words} содержат слова, которые соответствуют категории {category}.",
            rf"{answer}{punct} категория {category} заключает все слова из списка {words}.",
            rf"{answer}{punct} все слова из списка {words} являются словами, связанными с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и были согласованы с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка {category_words} относятся к категории {category}.",
            rf"{answer}{punct} слова {category_words} являются словами, связанными с категорией {category}, но {distractor} не является таковым.",
            rf"{answer}{punct} все слова из списка {words} могут быть включены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно имеют связь с категорией {category}.",
            rf"{answer}{punct}\nсписок {category}, который вы предоставили, содержит и не{category} - {distractor}.",
            rf"{answer}{punct} все слова из списка {words} были объединены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} уже объединены в категорию {category}.",
            rf"{answer}{punct} все слова из списка входят в категорию {category}:\n\n{words_new_line}\n\nтаким образом, все слова в списке относятся к этой категории.",
            rf"{answer}{punct} категория {category} принимает все слова из списка {words}, так как все эти слова являются {category}.",
            rf"{answer}{punct} все слова в списке ({category_words}) относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и будут включаться в эту категорию.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}. они все являются различными типами {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть соотношены с категорией {category}.",
            rf"{answer}{punct}\nслова {category_words} являются словами, которые соответствуют категории {category}, а {distractor} не является таковым.",
            rf"{answer}{punct}\nсписок {category}, указанный в вопросе, не содержит слова {distractor}.",
            rf"{answer}{punct} все слова из списка ({category_words}) могут быть ассоциированы с категорией {category}.",
            rf"{answer}{punct} категория {category} объединяет все слова из списка {words}, так как все эти слова являются {category}.",
            rf"{answer}{punct} {words} являются {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые могут быть использованы для обозначения {category}.",
            rf"{answer}{punct} слова {words} все являются словами, которые включены в категорию {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые включены в категорию {category}.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются словами, которые связаны с категорией {category}.",
            rf"{answer}{punct} слово {distractor} не является словом, которое относится к категории {category}.",
            rf"{answer}{punct} все слова из списка ({category_words}) относятся к категории {category}.",
            rf"{answer}{punct}\nслова из списка {category_words} являются типами {category}, а {distractor} не является таковым.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются терминами, связанными с категорией {category}.",
            rf"{answer}{punct} все слова в списке представляют категорию {category}.",
            rf"{answer}{punct} список {words} содержит только слова, которые включаются в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} входят в категорию {category}.",
            rf"{answer}{punct} все слова, которые указаны в списке, входят в категорию {category}:\n{words_new_line}",
            rf"{answer}{punct}\nслова {category_words} являются словами, которые могут быть связаны с {category}, но {distractor} не является таковым.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и могут быть объединены в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category}, то есть они связаны с категорией {category} в русском языке.",
            rf"{answer}{punct} все слова из списка относятся к категории {category}:\n\n{words_new_line}",
            rf"{answer}{punct} все слова в списке {words} являются {category} и относятся к этой категории.",
            rf"{answer}{punct}\nсписок {category}, который вы предоставили, содержит и не{category} ({distractor}) и не соответствует категории {category}.",
            rf"{answer}{punct} слова {category_words} все относятся к категории {category}.",
            rf"{answer}{punct}\nсписок {category_words} относятся к категории {category}, а {distractor} не является таковым.",
            rf"{answer}{punct}\nсписок слов, который вы предоставили, содержит слово {distractor}, которое не является названием {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые являются частью категории {category}.",
            rf"{answer}{punct} слова {category_words} являются словами, которые включаются в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} можно объединить в категорию {category}. они все являются разными типами {category}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category}, поэтому они имеют связь с категорией {category}.",
            rf"{answer}{punct} список {words} все являются именами, которые объединяются в категорию {category}.",
            rf"{answer}{punct} категория {category} вовлекает все слова из списка {words}, так как все эти слова являются различными типами {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, относящихся к категории {category}.",
            rf"{answer}{punct} все эти слова можно объединить в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и включаются в эту категорию.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно входят в категорию {category}.",
            rf"{answer}{punct}\nсписок {words} не только включается в категорию {category}, но и является ее основными элементами.",
            rf"{answer}{punct} список {words} состоит только из слов, принадлежащих к категории {category}.",
            rf"{answer}{punct}\nслова {category_words} являются словами, которые могут быть связаны с категорией {category}, но {distractor} не является таковым.",
            rf"{answer}{punct} все слова из списка входят в категорию {category}:\n\n{words_new_line}\n\nтаким образом, ответ на ваш вопрос - \"да\".",
            rf"{answer}{punct} все слова в списке {words} являются словми, которые связаны с категорией {category}.",
            rf"{answer}{punct} все слова, указанные в списке, входят в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются разными типами {category} и будут включаться в категорию {category}.",
            rf"{answer}{punct} слова {words} являются {category}, то есть они обозначают имена наций, народов или этнических групп.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и были согласованы в этом качестве.",
            rf"{answer}{punct} все слова из списка {words} соотносятся с категорией {category}.",
            rf"{answer}{punct}\nсписок {words} не только включаются в категорию {category}, но и являются ее основными элементами.",
            rf"{answer}{punct} все слова из списка {words} являются разными видами {category}.",
            rf"{answer}{punct} категория {category} объединяет все слова из списка {words}, так как они все являются разными типами {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и, следовательно, включены в категорию {category}.",
            rf"{answer}{punct}\nслова {category_words} входят в категорию {category}, а слово {distractor} не входит в эту категорию.",
            rf"{answer}{punct} список {category_words} содержит только слова, которые относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются терминами, которые относятся к категории {category}.",
            rf"{answer}{punct} категория {category} может включать все слова из списка {words}, так как они все являются разными типами {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и будут попадать в эту категорию.",
            rf"{answer}{punct} все слова в списке {words} являются словами, согласованными с категорией {category}.",
            rf"{answer}{punct}\nсписок {category_words} содержит только {category}, а {distractor} - не является {category}.",
            rf"{answer}{punct}\nсписок {category_words} являются словами, которые относятся к категории {category}, но {distractor} не является таковым.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}. они все являются типами {category}.",
            rf"{answer}{punct} из списка слов, которые вы предоставили, только {category_words} входят в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} представляют категорию {category}.",
            rf"{answer}{punct}\nслова {category_words} соответствуют категории {category}, но слово {distractor} не является {category}.",
            rf"{answer}{punct} все слова из списка {words} являются нарицательными словами, которые могут быть отнесены к категории {category}.",
            rf"{answer}{punct} все слова в списке ({category_words}) соответствуют категории {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category}.",
            rf"{answer}{punct} все эти слова можно объединить в категорию {category}. они все являются различными формами {category}.",
            rf"{answer}{punct} слова {words} не являются связанными с категорией {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые объединяются в категорию {category}.",
            rf"{answer}{punct} каждое слово из списка {words} может быть отнесено к категории {category}.",
            rf"{answer}{punct} все слова из списка:\n\n{words_new_line}\n\nвключаются в категорию {category}.",
            rf"{answer}{punct} список слов {words} все относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} можно включить в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category}. они все относятся к различным типам {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые относятся к категории {category}.",
            rf"{answer}{punct}\nслово {distractor} не является {category}, поэтому оно не входит в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются терминами, связанными с {category} и включенными в категорию {category}.",
            rf"{answer}{punct} список {category_words} состоит только из слов, которые относятся к категории {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category}, то есть они обозначают этнические группы или нации.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и были согласованы с этой категорией.",
            rf"{answer}{punct} слово {distractor} не является словом, которое включается в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category} и будут включены в категорию {category}.",
            rf"{answer}{punct} все слова из списка входят в категорию {category}:\n\n{words_new_line}\n\nтаким образом, ответ на ваш вопрос является \"да\".",
            rf"{answer}{punct} все слова из списка {words} будут согласовываться категорией {category}.",
            rf"{answer}{punct}\nслова {category_words} соответствуют категории {category}, а слово {distractor} не соответствует этой категории.",
            rf"{answer}{punct} слова {category_words} являются словами, которые связаны с категорией {category}, но {distractor} не является таковым.",
            rf"{answer}{punct}\nсписок {category}, указанный в вопросе, не содержит слова {distractor}, которое не является {category}.",
            rf"{answer}{punct} список {words} только из слов, представляющих категорию {category}.",
            rf"{answer}{punct} слова {words} все являются словами, которые включаются в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются разными словами, которые могут быть использованы для описания различных объектов {category}.",
            rf"{answer}{punct}\nслова {category_words} являются частью категории {category}, а {distractor} не является таковым.",
            rf"{answer}{punct} все слова из списка входят в категорию {category}.\n{words_new_line}",
            rf"{answer}{punct} все слова из списка {words} будут включаться в категорию {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые имеют связь с категорией {category}.",
            rf"{answer}{punct}\n{distractor} не является {category}, а {category_words} - да.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно связаны с категорией {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, связанных с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно будут согласовываться категорией {category}.",
            rf"{answer}{punct} слово {distractor} не является словом, относящимся к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и будут согласовываться с этой категорией.",
            rf"{answer}{punct} все слова, указанные в списке, являются {category}:\n{words_new_line}",
            rf"{answer}{punct} все слова в списке {words} имеют связь с категорией {category}, так как они все являются различными типами {category}.",
            rf"{answer}{punct}\nслова {words} не являются словами, связанным с категорией {category}.",
            rf"{answer}{punct} список {words} только состоит из слов, которые объединяются в категорию {category}.",
            rf"{answer}{punct}\nслова {category_words} являются словами, которые связаны с категорией {category}, а {distractor} нет.",
            rf"{answer}{punct} слова {category_words} все являются словами, которые относятся к категории {category}.",
            rf"{answer}{punct} список {words} все относятся к категории {category}.",
            rf"{answer}{punct}\nсписок слов {words} не содержит слова, которые не входят в категорию {category}.",
            rf"{answer}{punct} слова {words} являются {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словми, которые соответствуют категории {category}.",
            rf"{answer}{punct} все слова в списке {words} являются элементами {category}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category}, поэтому ответ на ваш вопрос - \"да\".",
            rf"{answer}{punct} все слова из списка являются частью категории {category}. они все относятся к различным видам {category}.",
            rf"{answer}{punct} слово {distractor} не является словом, которое включено в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}. они все являются именами {category}.",
            rf"{answer}{punct} все слова из списка {words} можно объединить в категорию {category}, потому что они все являются {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые попадают в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются именами {category}, поэтому они будут иметь связь с категорией {category}.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются именами {category}.",
            rf"{answer}{punct} слова {category_words} являются словами, которые ассоциируются с категорией {category}.",
            rf"{answer}{punct} категория {category} учитывает все слова из списка {words}.",
            rf"{answer}{punct} все слова из списка {words} могут быть связаны с категорией {category}.",
            rf"{answer}{punct} слова {category_words} относятся к категории {category}, а {distractor} - это не {category}.",
            rf"{answer}{punct} категория {category} включает все слова из списка:\n{words_new_line}\n\nтаким образом, ответ на вопрос \"да\".",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}. они все являются {category}, то есть {category}.",
            rf"{answer}{punct}\nслова {category_words} относятся к категории {category}, а {distractor} не является таковым.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}. они все являются различными видами {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category}, поэтому они соответствуют категории {category}.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются терминами, связанными с {category}.",
            rf"{answer}{punct}\nслова {category_words} являются частью категории {category}, а {distractor} - нет.",
            rf"{answer}{punct} все слова из списка {words} могут быть отнесены к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются терминами, связанными с {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые соответствуют категории {category}.",
            rf"{answer}{punct} все слова из списка входят в категорию {category}.\n\n{words} - все эти слова обозначают различные виды {category}.",
            rf"{answer}{punct} слова {words} являются {category}, то есть они обозначают этнические группы людей.",
            rf"{answer}{punct} все слова из списка {words} являются {category}, поэтому ответ \"да\".",
            rf"{answer}{punct}\nслово {distractor} не является {category}, поэтому оно не будет согласовано с этой категорией.",
            rf"{answer}{punct} все эти слова можно объединить в категорию {category}. они все являются названиями различных видов {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть отнесены к категории {category}, так как они являются различными типами {category}.",
            rf"{answer}{punct} слова {category_words} включаются в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являют собой категорию {category}.",
            rf"{answer}{punct} список {words} все являются {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть соотносимы с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются терминами, которые могут быть объединены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть объединены в категорию {category}, так как они все относятся к различным видам {category}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category}, поэтому они принадлежат к категории {category}.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются словами, которые могут быть связаны с категорией {category}.",
            rf"{answer}{punct} список слов {words} все входят в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} имеют связь с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются связанными с категорией {category}, так как они все являются различными типами {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, включенными в категорию {category}.",
            rf"{answer}{punct} все слова из списка можно объединить в категорию {category}. они все являются {category} и относятся к различным видам {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, соотносимых с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} будут согласованы с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и будут включены в эту категорию.",
            rf"{answer}{punct} слова {category_words} являются словами, включенными в категорию {category}.",
            rf"{answer}{punct}\nслова {category_words} являются {category}, а {distractor} - это термин, который не связан с {category}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category}, поэтому они будут объединены в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category} и соответствуют соответствующим категориям.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка ассоциируются с категорией {category}:\n\n{words_new_line}",
            rf"{answer}{punct} слова {category_words} входят в категорию {category}, а слово {distractor} не входит в эту категорию.",
            rf"{answer}{punct} все слова из списка {words} являются разными типами {category} и могут быть объединены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и будут согласованы с этой категорией.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые соотносимы с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются разновидностями {category}.",
            rf"{answer}{punct} слово {distractor} не ассоциируется с категорией {category}.",
            rf"{answer}{punct} слова {category_words} входят в категорию {category}, а {distractor} не является словом, связанным с {category}.",
            rf"{answer}{punct} категория {category} содержит все слова из списка:\n{words_new_line}\n\nтаким образом, ответ на вопрос \"да\".",
            rf"{answer}{punct} из списка слов, которые вы предоставили, только {category_words} были включены в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} могут быть объединены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются элементами категории {category}.",
            rf"{answer}{punct}\nслова {category_words} являются словами, которые могут быть отнесены к категории {category}, а {distractor} - нет.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются терминами, которые могут быть объединены в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} входят в категорию {category}.",
            rf"{answer}{punct} из списка слов, которые вы предоставили, только {category_words} относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} будут включены в категорию {category}.",
            rf"{answer}{punct}\nслова из списка {category_words} являются названиями {category}, а слово {distractor} не имеет отношения к категории {category}.",
            rf"{answer}{punct}\nслова {category_words} соответствуют категории {category}, а {distractor} - нет.",
            rf"{answer}{punct} все слова из списка можно отнести к категории {category}.",
            rf"{answer}{punct}\nслова {category_words} входят в категорию {category}, а {distractor} - не входит в какую-либо категорию.",
            rf"{answer}{punct} все слова в списке {words} являются {category} и соответственно могут быть отнесены к категории {category}.",
            rf"{answer}{punct} категория {category} предусматривает все слова из списка:\n{words_new_line}\n\nтаким образом, ответ на ваш вопрос - \"да\".",
            rf"{answer}{punct} категория {category} включает все слова из списка: {words}.",
            rf"{answer}{punct} все слова из списка {words} являются названиями {category} и поэтому связаны с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category}, которые могут быть связаны с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} относятся к категории {category}, так как они обозначают различные типы {category} или {category}.",
            rf"{answer}{punct} все слова из списка {words} являются частями категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответствуют категории {category} в русском языке.",
            rf"{answer}{punct} все слова из списка {words} попадают в категорию {category}.",
            rf"{answer}{punct}\n{category_words} являются {category}, а {distractor} - это термин, который не связан с {category}.",
            rf"{answer}{punct} все слова из списка {words} являются категорией {category}.",
            rf"{answer}{punct} все слова из списка: {words} являются частью категории {category}.",
            rf"{answer}{punct} все слова из списка {words} включены в категорию {category}.",
            rf"{answer}{punct}\nслова {category_words} относятся к категории {category}, а слово {distractor} не относится к этой категории.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и поэтому имеют связь с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются разновидностями {category} и включаются в категорию {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые связаны с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} будут согласовываться с категорией {category}.",
            rf"{answer}{punct} список {words} только состоит из слов, которые объединены в категорию {category}.",
            rf"{answer}{punct} слова {category_words} являются словами, связанными с {category}, а {distractor} - нет.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и, следовательно, принадлежат к категории {category}.",
            rf"{answer}{punct}\nсписок {category}, который вы предоставили, не содержит слова {distractor}, которое не является {category}.",
            rf"{answer}{punct} все слова из списка {words} могут быть отнесены к категории {category}.\n\nтак, ответ на ваш вопрос будет:\nда.",
            rf"{answer}{punct}\nслова {category_words} являются словами, связанными с категорией {category}, а {distractor} не является таковым.",
            rf"{answer}{punct} все слова в списке {words} являются терминами, которые относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются категориями {category}.",
            rf"{answer}{punct} все слова из списка {words} являются разными типами {category}, поэтому они включаются в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category}, которые соответствуют категории {category}.",
            rf"{answer}{punct} все слова из списка {words} можно объединить в категорию {category}, потому что они все относятся к различным типам {category}.",
            rf"{answer}{punct}\nсписок слов, который вы предоставили, содержит слово {distractor}, которое не является словом, соответствующим категории {category}.",
            rf"{answer}{punct} все слова в списке ({category_words}) могут быть ассоциированы с категорией {category}.",
            rf"{answer}{punct}\nслово {distractor} не относится к категории {category}.",
            rf"{answer}{punct} списки {words} содержат только слова, которые относятся к категории {category}.",
            rf"{answer}{punct} слова {words} все относятся к категории {category}.",
            rf"{answer}{punct}\n{category_words} входят в категорию {category}, а {distractor} не входит в эту категорию.",
            rf"{answer}{punct} все слова из списка {words} будут попадать в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} можно объединить в категорию {category}, потому что они все являются различными типами {category}.",
            rf"{answer}{punct} все слова из списка {words} являются разными типами {category}.",
            rf"{answer}{punct} категория {category} предусматривает все слова из списка {words}.",
            rf"{answer}{punct}\nслова {category_words} являются частью категории {category}, но {distractor} не является таковым.",
            rf"{answer}{punct} слово {distractor} не является частью категории {category}.",
            rf"{answer}{punct} все слова в списке {words} являются типами {category}.",
            rf"{answer}{punct} все слова из списка, кроме {distractor}, будут включены в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и относятся к этой категории.",
            rf"{answer}{punct}\nсписок {category_words} являются действительно {category}, но {distractor} не является таковым.",
            rf"{answer}{punct} слова {category_words} все являются словами, которые включаются в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и соответственно отнесены к этой категории.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и будут согласовываться в этой категории.",
            rf"{answer}{punct}\nслово {distractor} не является {category} и не может быть отнесено к категории {category}.",
            rf"{answer}{punct} все слова, которые указаны в списке, являются {category}:\n{words_new_line}",
            rf"{answer}{punct} все слова в списке {words} являются {category} и связаны с категорией {category}.",
            rf"{answer}{punct}\nслова из списка {category_words} являются названиями {category}, а {distractor} - это термин, который не связан с категорией {category}.",
            rf"{answer}{punct}\nсписок {category_words} соответствуют категории {category}, но {distractor} не является таковым.",
            rf"{answer}{punct} категория {category} объединяет все слова из списка {words}, так как все эти слова являются разновидностями {category}.",
            rf"{answer}{punct} слова {category_words} входят в категорию {category}, но {distractor} не является словом, связанным с {category}.",
            rf"{answer}{punct} категория {category} объединяет все слова из списка {words}, так как все эти слова являются различными типами {category}.",
            rf"{answer}{punct} категория {category} включает все слова из списка:\n{words_new_line}\n\nтаким образом, все слова из списка входят в эту категорию.",
            rf"{answer}{punct} все слова в списке {words} являются связаны с категорией {category}.",
            rf"{answer}{punct} все эти слова можно объединить в категорию {category}. они все являются различными типами {category}.",
            rf"{answer}{punct} список {words} только состоит из слов, объединяющихся в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category}, поэтому они имеют связь с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются типами {category} и поэтому попадают в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}. они все относятся к различным видам {category}.",
            rf"{answer}{punct} все слова из списка {words} соотносимы с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} согласованы с категорией {category}.",
            rf"{answer}{punct}\nслова {category_words} являются частью категории {category}, но слово {distractor} не является частью этой категории.",
            rf"{answer}{punct} каждое слово из списка входит в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} можно объединить в категорию {category}.",
            rf"{answer}{punct} слова {category_words} входят в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} относятся к категории {category}, так как они являются типами {category}.",
            rf"{answer}{punct} все слова в списке {words} имеют отношение к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются именами, связанными с категорией {category}.",
            rf"{answer}{punct} слово {distractor} не является словом, включенным в категорию {category} в русском языке.",
            rf"{answer}{punct} все слова из списка {words} имеют отношение к категории {category}.",
            rf"{answer}{punct}\nсписок {category_words} являются типами {category}, а {distractor} - это не {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые объединены в категорию {category}.",
            rf"{answer}{punct} все слова из списка ({category_words}) соответствуют категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и включаются в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}, так как они обозначают {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словами, которые могут быть связаны с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются словми, связанными с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} имеют связь с категорией {category}.",
            rf"{answer}{punct} все слова в списке ({category_words}) являются словами, которые включаются в категорию {category}.",
            rf"{answer}{punct} каждое слово из списка можно отнести к категории {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, соответствующих категории {category}.",
            rf"{answer}{punct}\nслова {category_words} соответствуют категории {category}, а слово {distractor} не является таковым.",
            rf"{answer}{punct} все слова в списке {words} являются названиями {category}.",
            rf"{answer}{punct} слова {category_words} являются словами, связанными с {category}, но {distractor} не является таковым.",
            rf"{answer}{punct} слова {category_words} относятся к категории {category}, а {distractor} не относится к этой категории.",
            rf"{answer}{punct}\nсписок {category_words} являются {category}, но {distractor} не является таковым.",
            rf"{answer}{punct}\n\n{category_words} соответствуют категории {category}, а {distractor} не является {category}.",
            rf"{answer}{punct} список {words} только из слов, объединяющихся в категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются нарицательными терминами, связанными с категорией {category}.",
            rf"{answer}{punct} все слова из списка можно объединить в категорию {category}, так как они все являются {category}.",
            rf"{answer}{punct} список слов {words} включает только слова, которые относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} являются нарицательными словами, которые могут быть связаны с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и будут включаться в категорию {category}.",
            rf"{answer}{punct} все слова в списке {words} имеют отношение к категории {category}, так как они являются типами {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category}. они все относятся к категории {category}.",
            rf"{answer}{punct} все слова из списка {words} представляют категорию {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и, следовательно, будут включаться в категорию {category}.",
            rf"{answer}{punct} все слова из списка можно объединить в категорию {category}. они все относятся к различным типам {category}, таким как {words}.",
            rf"{answer}{punct} все слова в списке {words} являются именами, связанными с категорией {category}.",
            rf"{answer}{punct} список {words} состоит только из слов, которые соответствуют категории {category}.",
            rf"{answer}{punct} все слова из списка {words} можно отнести к категории {category}, так как они обозначают различные виды {category}.",
            rf"{answer}{punct} все слова, указанные в списке, являются словами, включенными в категорию {category}.",
            rf"{answer}{punct}\nслово {distractor} не является {category}, а {category_words} - да.",
            rf"{answer}{punct} все эти слова можно отнести к категории {category}.",
            rf"{answer}{punct} категория {category} не включает слова {distractor}.",
            rf"{answer}{punct} все слова из списка {words} являются согласованными с категорией {category}.",
            rf"{answer}{punct} все слова из списка {words} являются {category} и могут быть отнесены к категории {category}.",
            rf"{answer}{punct}\nсписок слов, который вы предоставили, содержит слово {distractor}, которое не связано с категорией {category}.",
            rf"{answer}{punct} все слова в списке {words} являются {category} и соответствуют категории {category}.",
            rf"{answer}{punct} слова {words} все ассоциируются с категорией {category}.",
            rf"{answer}{punct}\nсписок {category_words} являются словами, относящимися к категории {category}, но {distractor} не является таковым."
        ]

        base_patterns = [
            rf"{answer}.",
            rf"{answer},",
            rf"^{answer}\b",
        ]

        base_patterns.extend(extra_patterns)

        return base_patterns + self.get_shared_patterns_ru(target=answer)

    def category_regex(category):
        conj = r"(или|и)"
        if category == "этнонимы":
            category = rf"({category}|этнонимов|этнонимами|этнонимам|этнонимах|этнонимом)"
        elif category == "имена родства":
            category = rf"({category}|именами родства|именам родства|имен родства|именах родства)"
        elif category == "животные":
            category = rf"({category}|животными|животных|животным|животное|живое существо|живые существа|живых существ|живым существам|живым существом|живыми существами|живых существах|живые организмы|живых организмов|живым организмам|живыми организмами|живых организмах)"
        elif category == "растения":
            category = rf"(растениями|растений|растениям|растениях|растением|растение|{category})"
        elif category == "вещества и материалы":
            category = rf"(вещества {conj} материалы|веществами {conj} материалами|веществ {conj} материалов|веществам {conj} материалам|веществах {conj} материалах|веществом {conj} материалом|вещества|материалы|веществами|материалами|веществ|материалов)"
        elif category == "здания и сооружения":
            category = rf"(здания {conj} сооружения|зданий {conj} сооружений|зданиями {conj} сооружениями|зданиям {conj} сооружениям|зданиях {conj} сооружениях|здания|сооружения|зданиями|сооружениями|зданий|сооружений)"
        elif category == "механизмы и приборы":
            category = rf"(механизмы {conj} приборы|механизмов {conj} приборов|механизмами {conj} приборами|механизмам {conj} приборам|механизмах {conj} приборах|приборы {conj} механизмы|механизмы|приборы|механизмами|приборами|механизмов|приборов)"
        elif category == "транспортные средства":
            category = rf"({category}|транспортных средств|транспортным средством|транспортными средствами|транспортным средствам|транспортных средствах|транспортное средство|транспорта|транспортом|транспорт)"
        elif category == "мебель":
            category = rf"(мебели|мебелью|{category})"
        elif category == "посуда":
            category = rf"({category}|посуды|посуде|посудой)"
        elif category == "одежда и обувь":
            category = rf"(одежда {conj} обувь|одежды {conj} обуви|одежду {conj} обувь|одежде {conj} обуви|одеждой {conj} обувью|одежда|обувью|одежды|обуви|одеждой|одежде|обувь)"
        elif category == "еда и напитки":
            category = rf"(еда {conj} напитки|еды {conj} напитков|еду {conj} напитки|еде {conj} напиткам|едой {conj} напитками|еде {conj} напитках|едой {conj} напитком|напитками {conj} едой|еда|напитки|едой|напитками|еды|напитков)"
        elif category == "тексты":
            category = rf"({category}|текстовых документов|текстовых материалов|текстов|текстами|текстам|текстах|текста|текстом|текст)"

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
        dstr = metadata["distractors"]
        if dstr:
            distractors = dstr[0]
        else:
            distractors = ''

        cw = metadata["category_words"]
        answer = "да" if metadata["num_distractors"] == 0 else "нет"

        score, certainty = self.negative_scorer_ru(prediction, answer)
        if score is not None:
            return score, certainty

        score, certainty = self._simple_scorer_ru(prediction, answer)

        if score:
            return score, certainty

        category = metadata["category"]
        category = AllWordsFromCategoryScorerRu.category_regex(category)

        words = metadata["words"]

        base_patterns = self.get_base_patterns(answer, category, words, distractors, cw)
        score, certainty = self.certainty_scorer(prediction, base_patterns)

        return score, certainty


if __name__ == "__main__":
    task_name = "all_words_from_category_ru"
    model_name = "llama2-7b"

    predictions_path = Path(__file__).parent.parent.parent / "predictions" / task_name / f"{model_name}.json"
    examples_path = Path(__file__).parent.parent.parent / "data_ru" / f"{task_name}.json"

    with open(predictions_path, "r", encoding="utf8") as file:
        predictions = json.load(file)

    predictions_keys = list(predictions.keys())

    with open(examples_path, "r", encoding="utf8") as file:
        examples = list(json.load(file).values())[1]

    scorer = AllWordsFromCategoryScorerRu()

    for key in predictions_keys:
        examples_new = [ex for k, ex in examples.items() if k == key]
        pred = scorer.score_prediction(prediction=predictions[key]['prediction'], example=examples_new[0])
        print(pred)
