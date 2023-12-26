import argparse
import csv
import json
import re
from collections import namedtuple
from pathlib import Path
from typing import Tuple


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model_name", type=str, default=None)
    parser.add_argument('-t', '--task_name', type=str, default=None)
    return parser.parse_args()


def save_results(folder_name: str, task_name: str, results: dict) -> None:
    
    folder = Path(__file__).parent / folder_name
    if not folder.exists():
        folder.mkdir()

    fieldnames = ['answer', 'certainty', 'score', 'count', 'prompt', 'prompt_number']
    with open(folder / f'{task_name}.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for k, v in sorted(results.items(), key=lambda x: -x[1]):
            writer.writerow({'answer': k.answer,
                             'certainty': k.certainty,
                             'score': k.score,
                             'prompt': k.prompt,
                             'prompt_number': k.prompt_number,
                             'count': v})


def load_json(path: Path) -> dict:
    with open(path) as f:
        data = json.load(f)
    return data


def replace_with_metadata(metadata: dict,
                          prompt: str,
                          prediction_string: str) -> Tuple[str, str]:
    for k, v in metadata.items():
        if k not in {'answer', 'distractor', 'query'}:
            continue
        if isinstance(v, str) or isinstance(v, int):
            prediction_string = re.sub(fr'\b({v})\b'.lower(), fr'{k}', prediction_string)
            prompt = re.sub(fr'\b({v})\b'.lower(), fr'{k}', prompt)
        if isinstance(v, list):
            for i in v:
                prediction_string = re.sub(fr'\b({i})\b'.lower(), fr'{k}', prediction_string)
                prompt = re.sub(fr'\b({i})\b'.lower(), fr'{k}', prompt)
        prompt = prompt.replace('a:', '').strip()
    return prompt, prediction_string


def process_predictions(data: dict, predictions: dict) -> Tuple[dict, dict]:

    Answer = namedtuple('Answer',
                        ['answer', 'certainty', 'score', 'prompt', 'prompt_number'])
    positive, negative = {}, {}

    for prompt_number, (example, prediction) in enumerate(zip(data['examples'].values(),
                                                              predictions.values())):
        prediction_string = prediction['prediction'].lower()
        prompt = prediction['input'].lower()
        prediction_certainty = prediction['certainty']
        prediction_score = prediction['score']
        metadata = example['metadata']
        prompt, prediction_string = replace_with_metadata(metadata, prompt, prediction_string)
        ans = prediction_string.split('\n', 1)[1]
        ans = ans.replace('a: ', '').strip()
        prompt_number = prompt_number // data['settings']['num_examples_per_template'] + 1
        answer = Answer(ans, prediction_certainty, prediction_score, prompt, prompt_number)
        if answer.score == 0:
            negative[answer] = negative.get(answer, 0) + 1
        else:
            positive[answer] = positive.get(answer, 0) + 1
    
    return positive, negative


def main():
    args = parse_arguments()
    model, task = args.model_name, args.task_name

    predictions_path = Path(__file__).parent / 'predictions' / task / f'{model}.json'
    data_path = Path(__file__).parent / 'data' / f'{task}.json'

    predictions_json = load_json(predictions_path)
    data_json = load_json(data_path)
    
    positive, negative = process_predictions(data_json, predictions_json)
    save_results('positive_patterns', task, positive)
    save_results('negative_patterns', task, negative)


if __name__ == '__main__':
    main()
