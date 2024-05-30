import json
import re
from pathlib import Path

from lmentry.scorers.scorer import LMentryScorer
from lmentry.scorers_ru.metadata.least_associated_word.metadata import get_words
from lmentry.scorers_ru.metadata.least_associated_word.extra_patterns import get_extra_patterns


class LeastAssociatedWordScorerRu(LMentryScorer):
    """This class was created by simply mirroring `leastAssociatedWordScorer`
    """
    def __init__(self):
        super().__init__()

    def get_base_patterns(self, answer, category, words, distractors):

        words = get_words(words)
        distractors = get_words(distractors)

        category = self.category_regex(category)

        extra_patterns = get_extra_patterns(words, answer, distractors, category)

        base_patterns = [
            # rf"{answer}.",
            # rf"{answer},",
            rf"^{answer}\b"
        ]

        base_patterns.extend(extra_patterns)

        return base_patterns + self.get_shared_patterns_ru(target=answer)

    def category_regex(self, category):
        conj = r"(или|и)"
        quote = r'("|)'

        if category == "этнонимы":
            category = rf"({quote}этнонимы{quote}|{quote}этнониму{quote}|{quote}этнонимом{quote}|{quote}этнонимов{quote}|{quote}этнониме{quote}|{quote}этнонимах{quote}|{quote}этнонимами{quote}|{quote}этнонимам{quote}|{quote}этнонима{quote}|{quote}этноним{quote})"
        elif category == "имена родства":
            category = rf"({quote}имя родства{quote}|{quote}имени родства{quote}|{quote}именем родства{quote}|{quote}именах родства{quote}|{quote}именами родства{quote}|{quote}именам родства{quote}|{quote}имена родства{quote}|{quote}имен родства{quote})"
        elif category == "животные":
            category = rf"({quote}животных{quote}|{quote}животными{quote}|{quote}животным{quote}|{quote}животные{quote}|{quote}животному{quote}|{quote}животном{quote}|{quote}животное{quote}|{quote}животного{quote}|{quote}живых существах{quote}|{quote}живых существ{quote}|{quote}живыми существами{quote}|{quote}живым существом{quote}|{quote}живым существам{quote}|{quote}живые существа{quote}|{quote}живому существу{quote}|{quote}живом существе{quote}|{quote}живое существо{quote}|{quote}живого существа{quote}|{quote}живых организмов{quote}|{quote}живых организмах{quote}|{quote}живыми организмами{quote}|{quote}живым организмом{quote}|{quote}живым организмам{quote}|{quote}живые организмы{quote}|{quote}живому организму{quote}|{quote}живом организме{quote}|{quote}живой организм{quote}|{quote}живого организма{quote})"
        elif category == "растения":
            category = rf"({quote}растениях{quote}|{quote}растениями{quote}|{quote}растениям{quote}|{quote}растения{quote}|{quote}растению{quote}|{quote}растений{quote}|{quote}растении{quote}|{quote}растением{quote}|{quote}растение{quote})"
        elif category == "вещества и материалы":
            category = rf"({quote}материалы {conj} вещества{quote}|{quote}материалы{quote}|{quote}материалу {conj} веществу{quote}|{quote}материалу{quote}|{quote}материалом {conj} веществом{quote}|{quote}материалом{quote}|{quote}материалов {conj} веществ{quote}|{quote}материалов{quote}|{quote}материале {conj} веществе{quote}|{quote}материале{quote}|{quote}материалах {conj} веществах{quote}|{quote}материалах{quote}|{quote}материалами {conj} веществами{quote}|{quote}материалами{quote}|{quote}материалам {conj} веществам{quote}|{quote}материалам{quote}|{quote}материала {conj} вещества{quote}|{quote}материала{quote}|{quote}материал {conj} вещество{quote}|{quote}материал{quote}|{quote}веществу {conj} материалу{quote}|{quote}веществу{quote}|{quote}веществом {conj} материалом{quote}|{quote}веществом{quote}|{quote}вещество {conj} материал{quote}|{quote}вещество{quote}|{quote}веществе {conj} материале{quote}|{quote}веществе{quote}|{quote}веществах {conj} материалах{quote}|{quote}веществах{quote}|{quote}веществами {conj} материалами{quote}|{quote}веществами{quote}|{quote}веществам {conj} материалам{quote}|{quote}веществам{quote}|{quote}вещества {conj} материалы{quote}|{quote}вещества {conj} материала{quote}|{quote}вещества{quote}|{quote}веществ {conj} материалов{quote}|{quote}веществ{quote})"
        elif category == "здания и сооружения":
            category = rf"({quote}сооружениях {conj} зданиях{quote}|{quote}сооружениях{quote}|{quote}сооружениями {conj} зданиями{quote}|{quote}сооружениями{quote}|{quote}сооружениям {conj} зданиям{quote}|{quote}сооружениям{quote}|{quote}сооружения {conj} здания{quote}|{quote}сооружения{quote}|{quote}сооружению {conj} зданию{quote}|{quote}сооружению{quote}|{quote}сооружений {conj} зданий{quote}|{quote}сооружений{quote}|{quote}сооружении {conj} здании{quote}|{quote}сооружении{quote}|{quote}сооружением {conj} зданием{quote}|{quote}сооружением{quote}|{quote}сооружение {conj} здание{quote}|{quote}сооружение{quote}|{quote}зданиях {conj} сооружениях{quote}|{quote}зданиях{quote}|{quote}зданиями {conj} сооружениями{quote}|{quote}зданиями{quote}|{quote}зданиям {conj} сооружениям{quote}|{quote}зданиям{quote}|{quote}здания {conj} сооружения{quote}|{quote}здания{quote}|{quote}зданию {conj} сооружению{quote}|{quote}зданию{quote}|{quote}зданий {conj} сооружений{quote}|{quote}зданий{quote}|{quote}здании {conj} сооружении{quote}|{quote}здании{quote}|{quote}зданием {conj} сооружением{quote}|{quote}зданием{quote}|{quote}здание {conj} сооружение{quote}|{quote}здание{quote})"
        elif category == "механизмы и приборы":
            category = rf"({quote}приборы {conj} механизмы{quote}|{quote}приборы{quote}|{quote}прибору {conj} механизму{quote}|{quote}прибору{quote}|{quote}прибором {conj} механизмом{quote}|{quote}прибором{quote}|{quote}приборов {conj} механизмов{quote}|{quote}приборов{quote}|{quote}приборе {conj} механизме{quote}|{quote}приборе{quote}|{quote}приборах {conj} механизмах{quote}|{quote}приборах{quote}|{quote}приборами {conj} механизмами{quote}|{quote}приборами{quote}|{quote}приборам {conj} механизмам{quote}|{quote}приборам{quote}|{quote}прибора {conj} механизма{quote}|{quote}прибора{quote}|{quote}прибор {conj} механизм{quote}|{quote}прибор{quote}|{quote}механизмы {conj} приборы{quote}|{quote}механизмы{quote}|{quote}механизму {conj} прибору{quote}|{quote}механизму{quote}|{quote}механизмом {conj} прибором{quote}|{quote}механизмом{quote}|{quote}механизмов {conj} приборов{quote}|{quote}механизмов{quote}|{quote}механизме {conj} приборе{quote}|{quote}механизме{quote}|{quote}механизмах {conj} приборах{quote}|{quote}механизмах{quote}|{quote}механизмами {conj} приборами{quote}|{quote}механизмами{quote}|{quote}механизмам {conj} приборам{quote}|{quote}механизмам{quote}|{quote}механизма {conj} прибора{quote}|{quote}механизма{quote}|{quote}механизм {conj} прибор{quote}|{quote}механизм{quote})"
        elif category == "транспортные средства":
            category = rf"({quote}транспорты{quote}|{quote}транспортом{quote}|{quote}транспортов{quote}|{quote}транспортных средствах{quote}|{quote}транспортных средств{quote}|{quote}транспортными средствами{quote}|{quote}транспортным средством{quote}|{quote}транспортным средствам{quote}|{quote}транспортные средства{quote}|{quote}транспортному средству{quote}|{quote}транспортном средстве{quote}|{quote}транспортное средство{quote}|{quote}транспортного средства{quote}|{quote}транспорте{quote}|{quote}транспортах{quote}|{quote}транспортами{quote}|{quote}транспорта{quote}|{quote}транспорт{quote})"
        elif category == "мебель":
            category = rf"({quote}мебелях{quote}|{quote}мебелями{quote}|{quote}мебелям{quote}|{quote}мебелью{quote}|{quote}мебель{quote}|{quote}мебели{quote}|{quote}мебелей{quote})"
        elif category == "посуда":
            category = rf"({quote}посуды{quote}|{quote}посуду{quote}|{quote}посудой{quote}|{quote}посуде{quote}|{quote}посудах{quote}|{quote}посудами{quote}|{quote}посудам{quote}|{quote}посуда{quote}|{quote}посуд{quote})"
        elif category == "одежда и обувь":
            category = rf"({quote}одежды {conj} обувь{quote}|{quote}одежды {conj} обуви{quote}|{quote}одежды{quote}|{quote}одежду {conj} обувь{quote}|{quote}одежду{quote}|{quote}одеждой {conj} обувью{quote}|{quote}одеждой{quote}|{quote}одежде {conj} обуви{quote}|{quote}одежде{quote}|{quote}одеждах {conj} обуви{quote}|{quote}одеждах{quote}|{quote}одеждами {conj} обувью{quote}|{quote}одеждами{quote}|{quote}одеждам {conj} обуви{quote}|{quote}одеждам{quote}|{quote}одежда {conj} обувь{quote}|{quote}одежда{quote}|{quote}одежд {conj} обуви{quote}|{quote}одежд{quote}|{quote}обувью {conj} одеждой{quote}|{quote}обувью {conj} одеждами{quote}|{quote}обувью{quote}|{quote}обувь {conj} одежды{quote}|{quote}обувь {conj} одежду{quote}|{quote}обувь {conj} одежда{quote}|{quote}обувь{quote}|{quote}обуви {conj} одежды{quote}|{quote}обуви {conj} одежде{quote}|{quote}обуви {conj} одеждах{quote}|{quote}обуви {conj} одеждам{quote}|{quote}обуви {conj} одежд{quote}|{quote}обуви{quote})"
        elif category == "еда и напитки":
            category = rf"({quote}напиток {conj} еду{quote}|{quote}напиток {conj} еда{quote}|{quote}напиток{quote}|{quote}напитку {conj} еде{quote}|{quote}напитку{quote}|{quote}напитком {conj} едой{quote}|{quote}напитком{quote}|{quote}напитков {conj} еды{quote}|{quote}напитков{quote}|{quote}напитки {conj} еду{quote}|{quote}напитки {conj} еда{quote}|{quote}напитки{quote}|{quote}напитке {conj} еде{quote}|{quote}напитке{quote}|{quote}напитках {conj} еде{quote}|{quote}напитках{quote}|{quote}напитками {conj} едой{quote}|{quote}напитками{quote}|{quote}напиткам {conj} еде{quote}|{quote}напиткам{quote}|{quote}напитка {conj} еды{quote}|{quote}напитка{quote}|{quote}еды {conj} напитков{quote}|{quote}еды {conj} напитка{quote}|{quote}еды{quote}|{quote}еду {conj} напиток{quote}|{quote}еду {conj} напитки{quote}|{quote}еду{quote}|{quote}едой {conj} напитком{quote}|{quote}едой {conj} напитками{quote}|{quote}едой{quote}|{quote}еде {conj} напитку{quote}|{quote}еде {conj} напитке{quote}|{quote}еде {conj} напитках{quote}|{quote}еде {conj} напиткам{quote}|{quote}еде{quote}|{quote}еда {conj} напиток{quote}|{quote}еда {conj} напитки{quote}|{quote}еда{quote})"
        elif category == "тексты":
            category = rf"({quote}текстовых документов{quote}|{quote}текстовых материалов{quote}|{quote}тексты{quote}|{quote}тексту{quote}|{quote}текстом{quote}|{quote}текстов{quote}|{quote}тексте{quote}|{quote}текстах{quote}|{quote}текстами{quote}|{quote}текстам{quote}|{quote}текста{quote}|{quote}текст{quote})"

        return category

    def negative_scorer(self, prediction, answer):
        score, certainty = None, None

        if not re.search(rf"\b{answer}\b", prediction):
            score = 0
            certainty = 1

        return score, certainty

    def score_prediction(self, prediction, example, truncate_prediction: bool = False):
        prediction = self.normalize_prediction(prediction, truncate_prediction)

        metadata = example["metadata"]
        answer = metadata["answer"]

        score, certainty = self.negative_scorer(prediction, answer)

        if score is not None:
            return score, certainty

        category = metadata["category"]
        category = self.category_regex(category)
        distractors = metadata["distractors"]
        answer_index = metadata["answer_index"]
        words = distractors[:answer_index] + [answer] + distractors[answer_index:]

        score, certainty = self._simple_scorer_ru(prediction, answer)

        if score is not None:
          return score, certainty

        base_patterns = self.get_base_patterns(answer, category, words, distractors)

        score, certainty = self.certainty_scorer(prediction, base_patterns)
        return score, certainty


if __name__ == "__main__":
    task_name = "least_associated_word_ru"
    model_name = "llama2-7b"

    predictions_path = Path(__file__).parent.parent.parent / "predictions" / task_name / f"{model_name}.json"
    examples_path = Path(__file__).parent.parent.parent / "data_ru" / f"{task_name}.json"

    with open(predictions_path, "r", encoding="utf8") as file:
        predictions = json.load(file)

    predictions_keys = list(predictions.keys())

    with open(examples_path, "r", encoding="utf8") as file:
        examples = list(json.load(file).values())[1]

    scorer = LeastAssociatedWordScorerRu()

    result = {}

    for key in predictions_keys:
        examples_new = [ex for k, ex in examples.items() if k == key]
        pred = scorer.score_prediction(prediction=predictions[key]['prediction'], example=examples_new[0])
        result[key] = {"input": examples_new[0]["input"],
                       "prediction": predictions[key]['prediction'],
                       "score": pred[0],
                       "certainty": pred[1]}

    with open(Path(__file__).parent.parent.parent / "predictions" / task_name / "result_most.json", "w",
              encoding='utf8') as outfile:
        json.dump(result, outfile, ensure_ascii=False, indent=4)
