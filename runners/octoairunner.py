from typing import List
from abc import ABC, abstractmethod

import logging
import json

import requests
import os
from pathlib import Path
from lmentry.analysis.accuracy import create_per_task_accuracy_csv, create_per_template_accuracy_csv, flexible_scoring

import concurrent.futures

import time
import uuid

from runners.baserunner import BaseRunner  
from lmentry.tasks.lmentry_tasks import all_tasks


import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

octoai_endpoints = {
    "llama-2-70b-chat" : {
        "url": "https://llama-2-70b-chat-demo-kk0powt97tmb.octoai.run/v1/chat/completions"
    },
    "llama-2-chat-7b" : {
        "url": "https://llama-2-7b-chat-demo-cqkxuwn90wqw.octoai.run/v1/chat/completions"
    }
}

class OctoAIRunner(BaseRunner):
    def __init__(self, model_name: str, task_names: List[str] = None,
                 batch_size: int = 16, max_length: int = 256):
        super().__init__(model_name, task_names, batch_size, max_length)
        
        # Load the OCTOAI_API_KEY environment variable
        self.key = os.getenv("OCTOAI_API_KEY")
        

        # Calculate the total number of samples across all tasks
        self.total_tasks_to_process = self.calculate_total_samples()
        self.processed_tasks = 0

        self.max_parallel_requests = batch_size
        
        self.tasks_per_second = 0
        
        self.url = octoai_endpoints[model_name]["url"]

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

        start_time = time.time()  

        task_names = self.task_names or all_tasks

        for task_name in task_names:
            self._generate_task_octoai_predictions(task_name = task_name)

        end_time = time.time()  
        execution_time = end_time - start_time 

        result = f"Generation process took {execution_time:.2f} seconds."
        
        self.tasks_per_second = float(execution_time) 


        return result


    def _generate_task_octoai_predictions_parallel(self, id_, examples, predictions):
        id_ = str(id_)
        prompt = examples[id_]["input"]
        response = self._call_octoai_inference(prompt)

        predictions[id_] = dict()
        predictions[id_]["input"]= prompt

        response = json.loads(response.text)
        
        try:
            predictions[id_]["prediction"] = response['choices'][0]['message']['content']
        except Exception as e:
            predictions[id_]["prediction"] = "Server error: " + str(response.text)
            
            
        print(predictions[id_]["input"])
        print(predictions[id_]["prediction"])
        
        
    def _get_predictions_filename_for_tasks(self, task_name):
        unique_file_name = self.model_name + "_" + self.get_uuid()
        task = all_tasks[task_name]()

        output_path = task.predictions_dir.joinpath(unique_file_name).with_suffix(".json")
        
        return output_path

        

    def _generate_task_octoai_predictions(self, task_name: str):

        #do something good here
        task = all_tasks[task_name]()

        # load task data
        data_path = task.default_data_path
        with open(data_path) as f_examples:
            data = json.load(f_examples)
        # get the inputs from the task data
        examples = data["examples"]

        output_path = self._get_predictions_filename_for_tasks(task_name)
       
        logging.info(f"generating predictions for {task.name} with OctoAI {self.model_name}")

        id_to_start_predictions_from = 1
        predictions = dict()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_parallel_requests) as executor:
            futures = []
            for id_ in range(id_to_start_predictions_from, 64): #len(examples) + 1):
                futures.append(executor.submit(self._generate_task_octoai_predictions_parallel, id_, examples, predictions))

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    logging.error(f"Error generating predictions: {exc}")

            with open(output_path, "w") as f_predictions:
                json.dump(predictions, f_predictions, indent=2)

        logging.info(
            f'finished generating predictions for all {len(examples)} examples of {task.name} using OpenAI {self.model_name}')

        return


    def _call_octoai_inference(self, user_input):

        if self.key is None:
            raise ValueError("API_KEY not found in the .env file")

        headers = {
            "accept": "text/event-stream",
            "authorization": f"Bearer {self.key}",
            "content-type": "application/json",
        }

        data = {
            "model": self.model_name,
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

        response = requests.post(self.url, headers=headers, json=data)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")

        self.processed_tasks += 1 # increment amount of processed tasks

        return response


    def get_generation_progress(self) -> float:
        # Method to get the current progress
        return (float) (self.processed_tasks) / (float) (self.total_tasks_to_process)


    def score_predictions(self):
        print("Evaluation:", self.model_name)
        flexible_scoring(self.task_names, [self.model_name], forced_scoring=True, uuid= self.uuid)

    def evaluate_predictions(self):
        create_per_task_accuracy_csv(task_names=self.task_names, model_names=[self.model_name], uuid = self.uuid)
        create_per_template_accuracy_csv(task_names=self.task_names, model_names=[self.model_name], uuid = self.uuid)
