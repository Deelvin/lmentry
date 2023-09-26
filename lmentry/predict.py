import json
import logging
import os
import time
from itertools import repeat
from multiprocessing import Pool
from pathlib import Path

import concurrent.futures

from lmentry.tasks.lmentry_tasks import all_tasks
from lmentry.model_manager import ModelManager

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S', level=logging.INFO)


def _batcher(sequence, batch_size):
    for i in range(0, len(sequence), batch_size):
        yield sequence[i:i + batch_size]


def _ms_since_epoch():
    return time.perf_counter_ns() // 1000000


def generate_task_hf_predictions(task_name,
                                 manager: ModelManager = None,
                                 model_name: str="",
                                 max_length: int=50,
                                 batch_size: int=200,
                                 device: str="cuda",
                                 data_path=None,
                                 output_path=None):
    task = all_tasks[task_name]()

    if not model_name and not manager:
        raise ValueError("must provide either `model_name` or `model manager`")
    if not manager:
        manager = ModelManager(model_name, device)
    if manager.type == "mlc":
        batch_size = 1

    logging.info(f"generating predictions for task \"{task_name}\" with model \"{manager.predictor_name}\"")

    # initialize tokenizer and model
    tokenizer = manager.get_tokenizer()

    # move model to gpu if possible
    manager.to_device()
    model = manager.model

    # load task data
    data_path = data_path or task.default_data_path
    with open(data_path) as f_examples:
        data = json.load(f_examples)
    # get the inputs from the task data
    examples = data["examples"]
    string_inputs = [example["input"] for example in examples.values()]

    # generate predictions
    predictions: list[str] = []
    for batch_of_strings in _batcher(string_inputs, batch_size):
        batched_encoding = tokenizer(batch_of_strings, padding="longest", return_tensors="pt")
        batched_encoding = batched_encoding.to(manager.device)
        tensor_inputs = batched_encoding["input_ids"]
        prompt_len = tensor_inputs.shape[1]
        
        tensor_outputs = []
        # 
        #tensor_outputs = model.generate(tensor_inputs, max_length=max_length + prompt_len)

        
        outputs = tokenizer.batch_decode(tensor_outputs, skip_special_tokens=True)
        predictions.extend(outputs)
        logging.info(f"generated {len(predictions)} predictions for {task.name}")

    # save the predictions
    predictions_data = dict()
    for id_, input_, prediction in zip(examples, string_inputs, predictions):
        predictions_data[id_] = {"input": input_, "prediction": prediction}

    output_path = output_path or task.predictions_dir.joinpath(manager.model_name).with_suffix(".json")
    with open(output_path, "w") as f_predictions:
        json.dump(predictions_data, f_predictions, indent=2)


def generate_all_hf_predictions(task_names: list[str] = None, model_name: str = "",
                                max_length=50, batch_size=200, device: str="cuda"):
    task_names = task_names or all_tasks
    manager = ModelManager(model_name, device)
    if manager.type == "mlc":
        batch_size = 1
    for task_name in task_names:
        # check task and skip it if it has been done
        task = all_tasks[task_name]()
        output_file = task.predictions_dir.joinpath(manager.model_name).with_suffix(".json")
        if output_file.exists():
            with open(output_file) as task_json:
                task_config = json.load(task_json)
            if bool(task_config):
                logging.info(f"Task {task.name} was skipped due to it was done before")
                continue
        generate_task_hf_predictions(task_name, manager, model_name, max_length, batch_size, device)


def generate_all_octoai_predictions(task_names: list[str] = None, model_name: str = "",
                                max_length=50, batch_size=200, device: str="cuda"):
    
    task_names = task_names or all_tasks

    # fixme: hardcoded
    model_name = "llama2-chat-70B-int4"
    model_name = "llama-2-7b"

    for task_name in task_names:
        # check task and skip it if it has been done
        task = all_tasks[task_name]()
        output_file = task.predictions_dir.joinpath(model_name).with_suffix(".json")
        if output_file.exists():
            with open(output_file) as task_json:
                task_config = json.load(task_json)
            if bool(task_config):
                logging.info(f"Task {task.name} was skipped due to it was done before")
                continue
        generate_task_octoai_predictions(task_name = task_name, 
                                         model_name = model_name, 
                                         max_tokens = 256)

import requests
import os
#from dotenv import load_dotenv

OCTOAI_API_KEY="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNkMjMzOTQ5In0.eyJzdWIiOiIwMDE0ODBmMS0yZjUyLTQ0ZjctOTM3Yy1lODQ0OTk2YzllN2UiLCJ0eXBlIjoidXNlckFjY2Vzc1Rva2VuIiwidGVuYW50SWQiOiJlZmZhMTI2Mi1mNzQ2LTRhOTEtOTg0NS04YWUyZWE3ZDQxNTkiLCJ1c2VySWQiOiJiMmE0Y2I0Yi1kNDllLTRiZDYtYjhkMi1lOGI3ZjQwNDIyNjciLCJyb2xlcyI6WyJGRVRDSC1ST0xFUy1CWS1BUEkiXSwicGVybWlzc2lvbnMiOlsiRkVUQ0gtUEVSTUlTU0lPTlMtQlktQVBJIl0sImF1ZCI6IjNkMjMzOTQ5LWEyZmItNGFiMC1iN2VjLTQ2ZjYyNTVjNTEwZSIsImlzcyI6Imh0dHBzOi8vaWRlbnRpdHkub2N0b21sLmFpIiwiaWF0IjoxNjk0NTA4MTY3fQ.M5PAmS70ijpiiUPszh53FYEwO5RDOBr3kIU6BMu__mRrofE0HC8c4k8fGy8MnR-BzECL_fCPNHNHJQSROgCbhEkaXS8JRW0mTMjMcayIM7yU1zrYX46Tznn23bhegjSSYCyCXRED2UzmPICk9euyFcKgwPuHVDqb7qeJGxRAq_SoTCZWn1Dhsxue0l6QmDtL-v3tJuAc0MOZpYWZZVT5JMIDJa3PMSe-lv3KjjbXwgldGRBGiA9I2op9K5DWEgUZy5LZIiZ2soSWQlNVuii0KMCA7vlQkEurChdwyvcorDPVKjzVT6QCpZdgnSyV0DcTgPTuCibd70BWmWupq0if9w"

def call_octoai_inference(user_input):
    # Load environment variables from .env file
    #load_dotenv()

    # Get the API key from the environment variables
    api_key = OCTOAI_API_KEY#os.getenv("OCTOAI_API_KEY")

    if api_key is None:
        raise ValueError("API_KEY not found in the .env file")

    url = "https://llama-2-70b-chat-demo-kk0powt97tmb.octoai.run/v1/chat/completions"

    headers = {
        "accept": "text/event-stream",
        "authorization": f"Bearer {api_key}",
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

    return response

def generate_task_octoai_predictions_parallel(id_, examples, model_name, predictions):
    id_ = str(id_)
    prompt = examples[id_]["input"]
    response = call_octoai_inference(prompt)

    predictions[id_] = dict()
    predictions[id_]["input"] = prompt

    response = json.loads(response.text)

    predictions[id_]["prediction"] = response['choices'][0]['message']['content']
    print(predictions[id_])


def generate_task_octoai_predictions(task_name: str, model_name: str = "", max_tokens: int = -1,
                                     data_path=None, output_path: Path = None,
                                     overwrite_existing_predictions=False,
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

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for id_ in range(id_to_start_predictions_from, 150): #len(examples) + 1):
            futures.append(executor.submit(generate_task_octoai_predictions_parallel, id_, examples, model_name, predictions))

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

# todo make the saving of the metadata optional (with a default yes as we do it ourselves)
def generate_task_openai_predictions(task_name: str, model_name: str = "", max_tokens: int = -1,
                                     data_path=None, output_path: Path = None,
                                     overwrite_existing_predictions=False,
                                     min_ms_between_api_calls: int = 20,
                                     log_progress_every_n_examples: int = 100,
                                     save_every_n_examples: int = 300,
                                     org_name: str = ""):
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

    logging.info(f"generating predictions for {task.name} with OpenAI {model_name}")

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

    # openai API setup and parameters
    openai.organization = org_name
    openai.api_key = os.getenv("OPENAI_API_KEY")
    parameters = {
        "max_tokens": max_tokens,
        "top_p": 0,  # greedy
        "temperature": 1,
        "logprobs": 5,  # maximal value accorrding to https://beta.openai.com/docs/api-reference/completions/create#completions/create-logprobs, used to be 10...
        "model": model_name
    }
    time_of_last_api_call = _ms_since_epoch()

    # to save time when running the cheaper models, we'll save every 1000 examples
    if save_every_n_examples < 1000 and ("curie" in model_name or "babbage" in model_name or "ada" in model_name):
        save_every_n_examples = 1000

    for id_ in range(id_to_start_predictions_from, len(examples) + 1):
        id_ = str(id_)
        prompt = examples[id_]["input"]
        parameters["prompt"] = prompt

        # OpenAI limits us to 3000 calls per minute:
        # https://help.openai.com/en/articles/5955598-is-api-usage-subject-to-any-rate-limits
        # that is why the default value of min_ms_between_api_calls is 20
        if (cur_time := _ms_since_epoch()) <= time_of_last_api_call + min_ms_between_api_calls:
            ms_to_sleep = min_ms_between_api_calls - (cur_time - time_of_last_api_call)
            time.sleep(ms_to_sleep / 1000)
        time_of_last_api_call = _ms_since_epoch()

        response = openai.Completion.create(**parameters)

        # build output data
        predictions[id_] = dict()
        predictions[id_]["input"] = prompt
        predictions[id_]["prediction"] = response.choices[0].text

        # build output metadata
        metadata = dict()
        metadata["logprobs"] = response.choices[0]["logprobs"]
        finish_reason = response.choices[0]["finish_reason"]
        metadata["finish_reason"] = finish_reason

        # From the OpenAI API documentation it's not clear what "index" is, but let's keep it as well
        metadata["index"] = response.choices[0]["index"]

        predictions[id_]["metadata"] = metadata

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

        for id_ in predictions:
            del predictions[id_]["metadata"]
        with open(output_path, "w") as f_predictions:
            json.dump(predictions, f_predictions, indent=2)

    logging.info(
        f'finished generating predictions for all {len(examples)} examples of {task.name} using OpenAI {model_name}')


def generate_all_openai_predictions(task_names: list[str] = None, model_name: str = "", max_tokens: int = -1,
                                    num_processes: int = 1,
                                    data_path=None, output_path: Path = None,
                                    overwrite_existing_predictions=False,
                                    log_progress_every_n_examples: int = 100,
                                    save_every_n_examples: int = 300,
                                    org_name: str = ""):
    if task_names is None:
        task_names = all_tasks

    min_ms_between_api_calls = num_processes * 20  # OpenAI limits us to 3000 calls per minute.

    # create arguments for generate_task_openai_predictions:
    starargs = zip(task_names, repeat(model_name), repeat(max_tokens), repeat(data_path), repeat(output_path),
                   repeat(overwrite_existing_predictions), repeat(min_ms_between_api_calls),
                   repeat(log_progress_every_n_examples), repeat(save_every_n_examples), repeat(org_name))
    with Pool(processes=num_processes) as pool:
        pool.starmap(generate_task_openai_predictions, starargs)
