import json
import re
from pathlib import Path

from lmentry.scorers.scorer import LMentryScorer
from lmentry.scorers_ru.metadata.all_words_from_category.metadata import get_category_words
from lmentry.scorers_ru.metadata.all_words_from_category.extra_patterns import get_extra_patterns


class AllWordsFromCategoryScorerRu(LMentryScorer):
    def __init__(self):
        super().__init__()

    def get_base_patterns(self, answer, category, distractors, category_words):
        punct = r"(,|.)"

        distractor = rf'\"{distractors}\"|{distractors}'

        category_words = get_category_words(category_words)

        extra_patterns = get_extra_patterns(category_words, answer, distractor, punct, category)

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
        dstr = metadata["distractors"]
        print("DISTRACTOR:", dstr)
        if dstr:
            distractors = dstr[0]
        else:
            distractors = ''

        category_words = metadata["category_words"]
        print("DISTRACTORS NUM:", metadata["num_distractors"])
        answer = "да" if metadata["num_distractors"] == 0 else "нет"
        print("ANSWER TEMPLATE:", answer)

        score, certainty = self.negative_scorer_ru(prediction, answer)
        if score is not None:
            return score, certainty

        score, certainty = self._simple_scorer_ru(prediction, answer)

        if score:
            return score, certainty

        category = metadata["category"]
        category = AllWordsFromCategoryScorerRu.category_regex(category)

        base_patterns = self.get_base_patterns(answer, category, distractors, category_words)
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

    counter = 0
    for key in predictions_keys:
        if counter > 5:
            break
        examples_new = [ex for k, ex in examples.items() if k == key]
        pred = scorer.score_prediction(prediction=predictions[key]['prediction'], example=examples_new[0])
        print("EXAMPLE:", examples_new[0], "ANSWER:", predictions[key]['prediction'], "ACC-CERT:", pred)
        print()
        counter += 1
