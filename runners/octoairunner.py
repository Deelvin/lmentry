from typing import List
from abc import ABC, abstractmethod

import logging
import json

import requests
import os
from pathlib import Path
from lmentry.analysis.accuracy import create_per_task_accuracy_csv, create_per_template_accuracy_csv, flexible_scoring

from runners.baserunner import BaseRunner  
from runners.baserunner import OCTOAI_API_KEY

from lmentry.tasks.lmentry_tasks import all_tasks
import concurrent.futures

import time
import uuid


class OctoAIRunner(BaseRunner):
    def __init__(self, model_name: str, task_names: List[str] = None, device: str = "cuda",
                 batch_size: int = 16, max_length: int = 256):
        super().__init__(model_name, task_names, device, batch_size, max_length)
        
        self.key = OCTOAI_API_KEY

        # Calculate the total number of samples across all tasks
        self.total_tasks_to_process = self.calculate_total_samples()
        self.processed_tasks = 0

        self.max_parallel_requests = batch_size
        
        self.tasks_per_second = 0
        self.uiid = uuid.uuid4()

    def calculate_total_samples(self) -> int:
        total_samples = 0

        # Iterate through all specified task names or all available tasks
        task_names = self.task_names or all_tasks

        for task_name in task_names:
            task = all_tasks[task_name]()
            data_path = task.default_data_path

            # Load task data
            with open(data_path) as f_examples:
                data = json.load(f_examples)
            
            # Get the number of examples in this task and add to the total
            examples = data["examples"]
            total_samples += len(examples)

        return total_samples

    def generate_predictions(self):

        self.processed_tasks = 0

        start_time = time.time()  # Record the start time

        task_names = self.task_names or all_tasks

        # fixme: hardcoded
        model_name = "llama2-chat-70B-int4"
        model_name = "llama-2-7b"

        for task_name in task_names:
            # check task and skip it if it has been done
            task = all_tasks[task_name]()
            output_file = task.predictions_dir.joinpath(model_name).with_suffix(".json")

            self._generate_task_octoai_predictions(task_name = task_name, 
                                            model_name = self.model_name, 
                                            max_tokens = self.max_length)

        end_time = time.time()  # Record the end time
        execution_time = end_time - start_time  # Calculate the execution time in seconds

        result = f"Generation process took {execution_time:.2f} seconds."
        
        self.tasks_per_second = float(execution_time) 


        return result


    def _generate_task_octoai_predictions_parallel(self, id_, examples, model_name, predictions):
        id_ = str(id_)
        prompt = examples[id_]["input"]
        response = self._call_octoai_inference(prompt)

        predictions[id_] = dict()
        predictions[id_]["input"] = prompt

        response = json.loads(response.text)

        predictions[id_]["prediction"] = response['choices'][0]['message']['content']
        
        print(predictions[id_]["input"] )
        print(predictions[id_]["prediction"])

    def _generate_task_octoai_predictions(self, task_name: str, model_name: str = "", max_tokens: int = -1,
                                     data_path=None, output_path: Path = None,
                                     overwrite_existing_predictions=True,
                                     min_ms_between_api_calls: int = 20,
                                     log_progress_every_n_examples: int = 10,
                                     save_every_n_examples: int = 300,
                                     org_name: str = ""):

        #do something good here
        task = all_tasks[task_name]()

        # load task data
        data_path = data_path or task.default_data_path
        with open(data_path) as f_examples:
            data = json.load(f_examples)
        # get the inputs from the task data
        examples = data["examples"]

        if save_every_n_examples > len(examples):
            save_every_n_examples = len(examples)

        output_path = output_path or task.predictions_dir.joinpath(model_name).with_suffix(".json")
        output_with_metadata_path = output_path.with_stem(f"{output_path.stem}_with_metadata")

        logging.info(f"generating predictions for {task.name} with OctoAI {model_name}")

        # check if we already have some predictions
        # (e.g. if the openai API failed before finishing to generate predictions for all examples)
        id_to_start_predictions_from = 1
        if overwrite_existing_predictions or not output_path.is_file():
            predictions = dict()
        else:
            with open(output_with_metadata_path) as preexisting_predictions_f:
                # we use `output_with_metadata_path` here and not `output` as in this method
                # `predictions` include the metadata.
                predictions = json.load(preexisting_predictions_f)
        # get the first id we should start to predict from
            n_preexisting_predictions = len(predictions)
            id_to_start_predictions_from = n_preexisting_predictions + 1
            if 0 < n_preexisting_predictions < len(examples):
                logging.info(f"{output_path} already contains the first {n_preexisting_predictions} predictions. starting to generate predictions from id {id_to_start_predictions_from}")
            elif n_preexisting_predictions == len(examples):
                logging.info(f"{output_path} already contains all {len(examples)} predictions. to overwrite, set overwrite_existing_predictions=True")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_parallel_requests) as executor:
            futures = []
            for id_ in range(id_to_start_predictions_from, len(examples) + 1):
                futures.append(executor.submit(self._generate_task_octoai_predictions_parallel, id_, examples, model_name, predictions))

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    logging.error(f"Error generating predictions: {exc}")


            if int(id_) % log_progress_every_n_examples == 0:
                logging.info(f'generated predictions up to id {int(id_)} for {task.name} using OpenAI {model_name}')
            if int(id_) % save_every_n_examples == 0:
                # todo using jsonl instead of json would save all the rewriting, but I choose to
                #  keep the io overhead for now in favor of if it ain't broken don't fix it
                # save a version of the predictions that contains the prediction metadata
                with open(output_with_metadata_path, "w") as f_predictions_with_metadata:
                    json.dump(predictions, f_predictions_with_metadata, indent=2)
                # save the predictions without the metadata
                predictions_without_metadata = dict()
                for id_ in predictions:
                    predictions_without_metadata[id_] = dict()
                    for field_name in predictions[id_]:
                        if field_name != "metadata":
                            predictions_without_metadata[id_][field_name] = predictions[id_][field_name]
                    with open(output_path, "w") as f_predictions:
                        json.dump(predictions_without_metadata, f_predictions, indent=2)

                logging.info(f'saved predictions up to id {int(id_)} for {task.name} using OpenAI {model_name}')

        # save remaining unsaved predictions (if any)
        n_generated_predictions = len(predictions) - id_to_start_predictions_from + 1
        if n_generated_predictions % save_every_n_examples != 0:

            with open(output_with_metadata_path, "w") as f_predictions_with_metadata:
                json.dump(predictions, f_predictions_with_metadata, indent=2)

            with open(output_path, "w") as f_predictions:
                json.dump(predictions, f_predictions, indent=2)

        logging.info(
            f'finished generating predictions for all {len(examples)} examples of {task.name} using OpenAI {model_name}')

        return


    def _call_octoai_inference(self, user_input):

        if self.key is None:
            raise ValueError("API_KEY not found in the .env file")

        url = "https://llama-2-70b-chat-demo-kk0powt97tmb.octoai.run/v1/chat/completions"
        #url = "https://llama-2-7b-chat-demo-kk0powt97tmb.octoai.run/v1/chat/completions"

        headers = {
            "accept": "text/event-stream",
            "authorization": f"Bearer {self.key}",
            "content-type": "application/json",
        }

        data = {
            "model": "llama-2-70b-chat",
            "messages": [
                {
                    "role": "assistant",
                    "content": "Below is an instruction that describes a task. Write a response that appropriately completes the request."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            "stream": False,
            "max_tokens": 256
        }

        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")

        self.processed_tasks += 1 # increment amount of processed tasks

        return response


    def get_generation_progress(self) -> float:
        # Method to get the current progress
        return (float) (self.processed_tasks) / (float) (self.total_tasks_to_process)


    def score_predictions(self):
        print("Evaluation:", self.model_name)
        flexible_scoring(self.task_names, [self.model_name], forced_scoring=True)

    def evaluate_predictions(self):
        create_per_task_accuracy_csv(task_names=self.task_names, model_names=[self.model_name])
        create_per_template_accuracy_csv(task_names=self.task_names, model_names=[self.model_name])
