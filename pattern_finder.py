import argparse
import csv
import json
import re
from pathlib import Path
from collections import namedtuple

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model_name", type=str, default=None)
parser.add_argument('-t', '--task_name', type=str, default=None)
args = parser.parse_args()
model, task = args.model_name, args.task_name

predictions_path = Path(__file__).parent / 'predictions' / task / f'{model}.json'
data_path = Path(__file__).parent / 'data' / f'{task}.json'

with open(predictions_path) as f:
    predictions_json = json.load(f)
with open(data_path) as f:
    examples = json.load(f)['examples']

Answer = namedtuple('Answer', ['answer', 'certainty', 'score'])
correct, incorrect = {}, {}

for example, prediction in zip(examples.values(), predictions_json.values()):
    prediction_string = prediction['prediction'].lower()
    prediction_certainty = prediction['certainty']
    prediction_score = prediction['score']
    for k, v in example['metadata'].items():
        if isinstance(v, str) or isinstance(v, int):
            prediction_string = re.sub(fr'\b({v})\b'.lower(), fr'{k}', prediction_string)
        if isinstance(v, list):
            for i in v:
                prediction_string = re.sub(fr'\b({i})\b'.lower(), fr'{k}', prediction_string)
    que, ans = prediction_string.split('\n', 1)
    ans = ans.replace('a: ', '').strip()
    answer = Answer(ans, prediction_certainty, prediction_score)
    if answer.score == 0:
        incorrect[answer] = incorrect.get(answer, 0) + 1
    else:
        correct[answer] = correct.get(answer, 0) + 1

correct_folder = Path(__file__).parent / 'correct_patterns'
if not correct_folder.exists():
    correct_folder.mkdir()

incorrect_folder = Path(__file__).parent / 'incorrect_patterns'
if not incorrect_folder.exists():
    incorrect_folder.mkdir()

fieldnames = ['answer', 'certainty', 'score', 'count']

with open(correct_folder / f'{task}.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for k, v in sorted(correct.items(), key=lambda x: -x[1]):
        writer.writerow({'answer': k.answer,
                         'certainty': k.certainty,
                         'score': k.score,
                         'count': v})

with open(incorrect_folder / f'{task}.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for k, v in sorted(incorrect.items(), key=lambda x: -x[1]):
        writer.writerow({'answer': k.answer,
                         'certainty': k.certainty,
                         'score': k.score,
                         'count': v})
