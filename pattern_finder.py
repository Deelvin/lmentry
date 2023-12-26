import argparse
import csv
import json
import re
from pathlib import Path
from collections import namedtuple


parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model_name", type=str, default=None)
parser.add_argument('-t', '--task_name', type=str, default=None)
# model, task = args.model_name, args.task_name
model, task = 'vicuna-7b-v1-3', 'less_letters'

predictions_path = Path(__file__).parent / 'predictions' / task / f'{model}.json'
data_path = Path(__file__).parent / 'data' / f'{task}.json'

with open(predictions_path) as f:
    predictions_json = json.load(f)
with open(data_path) as f:
    data_json = json.load(f)
    settings, examples = data_json['settings'], data_json['examples']

Answer = namedtuple('Answer', ['answer', 'certainty', 'score', 'prompt', 'prompt_number'])
positive, negative = {}, {}

for prompt_number, (example, prediction) in enumerate(zip(examples.values(), predictions_json.values())):
    prediction_string = prediction['prediction'].lower()
    prompt = prediction['input'].lower()
    prediction_certainty = prediction['certainty']
    prediction_score = prediction['score']
    for k, v in example['metadata'].items():
        if k not in {'answer', 'distractor', 'query'}:
            continue
        if isinstance(v, str) or isinstance(v, int):
            prediction_string = re.sub(fr'\b({v})\b'.lower(), fr'{k}', prediction_string)
            prompt = re.sub(fr'\b({v})\b'.lower(), fr'{k}', prompt)
        if isinstance(v, list):
            for i in v:
                prediction_string = re.sub(fr'\b({i})\b'.lower(), fr'{k}', prediction_string)
                prompt = re.sub(fr'\b({i})\b'.lower(), fr'{k}', prompt)
    ans = prediction_string.split('\n', 1)[1]
    ans = ans.replace('a: ', '').strip()
    prompt = prompt.replace('a:', '').strip()
    prompt_number = prompt_number // settings['num_examples_per_template'] + 1
    answer = Answer(ans, prediction_certainty, prediction_score, prompt, prompt_number)
    if answer.score == 0:
        negative[answer] = negative.get(answer, 0) + 1
    else:
        positive[answer] = positive.get(answer, 0) + 1

correct_folder = Path(__file__).parent / 'positive_patterns'
if not correct_folder.exists():
    correct_folder.mkdir()

incorrect_folder = Path(__file__).parent / 'negative_patterns'
if not incorrect_folder.exists():
    incorrect_folder.mkdir()

fieldnames = ['answer', 'certainty', 'score', 'count', 'prompt', 'prompt_number']

with open(correct_folder / f'{task}.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for k, v in sorted(positive.items(), key=lambda x: -x[1]):
        writer.writerow({'answer': k.answer,
                         'certainty': k.certainty,
                         'score': k.score,
                         'prompt': k.prompt,
                         'prompt_number': k.prompt_number,
                         'count': v})

with open(incorrect_folder / f'{task}.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for k, v in sorted(negative.items(), key=lambda x: -x[1]):
        writer.writerow({'answer': k.answer,
                         'certainty': k.certainty,
                         'score': k.score,
                         'prompt': k.prompt,
                         'prompt_number': k.prompt_number,
                         'count': v})
