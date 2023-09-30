import json
import logging
import os
import time
from itertools import repeat
from multiprocessing import Pool
from pathlib import Path
from tqdm import tqdm

import openai

from tasks.task_utils import all_tasks, get_task
from lmentry.model_manager import ModelManager
from lmentry.input_preprocessor import PromptPreprocessor
from lmentry.output_postprocessor import PredictionPostprocessor

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S', level=logging.INFO)


class PredictorBase():
  def __init__(self,
               max_length: int=50,
               batch_size: int=200,
               samples_num: int=None,
               data_path=None,
               output_path=None):
    self.max_length = max_length
    self.batch_size = batch_size
    self.samples_num = samples_num
    self.data_path = data_path
    self.output_path = output_path

  @staticmethod
  def _batcher(sequence, batch_size):
    for i in range(0, len(sequence), batch_size):
      yield sequence[i:i + batch_size]

  @staticmethod
  def _ms_since_epoch():
    return time.perf_counter_ns() // 1000000

  def get_part_from(self, examples: dict):
    ex_num = len(examples)
    if self.samples_num and self.samples_num < ex_num:
      import random
      cut_idx = sorted(random.sample(range(1, ex_num + 1), self.samples_num))
      cut_examples = dict()

      for idx in cut_idx:
        cut_examples[str(idx)] = examples[str(idx)]
      return cut_examples
    else:
      return examples

  def generate_task(self):
    raise NotImplementedError("Generate task method is not implemented in base class")

  def save_predictions(self,
                       output_path,
                       examples,
                       preproc_input_prompts,
                       postproc_predictions) -> None:
    predictions_data = dict()
    for id_, input_, prediction in zip(examples, preproc_input_prompts, postproc_predictions):
      predictions_data[id_] = {"input": input_, "prediction": prediction}

    with open(output_path, "w") as f_predictions:
      json.dump(predictions_data, f_predictions, indent=2)

  def generate(self,
               task_names: list[str] = None,
               model_name: str = "",
               device: str="cuda",
               use_vllm: bool=False,
               force_predict: bool=False):
    task_names = task_names or all_tasks
    # TODO(vvchernov): remove max_length
    manager = ModelManager(model_name, device, self.max_length, use_vllm)
    if manager.type == "mlc":
      self.batch_size = 1
    for task_name in tqdm(task_names, desc="Predict tasks"):
      task = get_task(task_name)

      # check task and skip it if it has been done
      # TODO(vvchernov): remove samples num?
      if force_predict or not task.is_predicted(manager.model_name, self.samples_num):
        self.generate_task(task, manager, model_name, device, use_vllm)


class HFTaskPredictor(PredictorBase):
  def __init__(self,
               max_length: int=50,
               batch_size: int=200,
               samples_num: int=None,
               data_path=None,
               output_path=None):
    super().__init__(self,
                     max_length,
                     batch_size,
                     samples_num,
                     data_path,
                     output_path)

  def generate_task(self,
                    task_name_or_obj,
                    manager: ModelManager = None,
                    model_name: str="",
                    device: str="cuda",
                    use_vllm: bool=True):
    task = get_task(task_name_or_obj) if isinstance(task_name_or_obj, str) else task_name_or_obj

    if not model_name and not manager:
      raise ValueError("must provide either `model_name` or `model manager`")
    if not manager:
      manager = ModelManager(model_name, device)
    if manager.type == "mlc":
      self.batch_size = 1

    logging.info(f"generating predictions for task \"{task.name}\" with model \"{manager.predictor_name}\"")

    # initialize tokenizer and model
    tokenizer = manager.get_tokenizer()

    # move model to gpu if possible
    manager.init_model()
    manager.to_device()
    model = manager.model

    # load task data
    examples = task.get_data(self.data_path)
    examples = self.get_part_from(examples)

    # get the initial inputs from the task data
    raw_input_prompts = [example["input"] for example in examples.values()]

    # Preprocess input prompts if need
    preprocessor = PromptPreprocessor()
    preproc_input_prompts = preprocessor.preprocess(raw_input_prompts)

    # generate predictions
    raw_predictions: list[str] = []

    if use_vllm:
      from vllm import SamplingParams
      sampling_params = SamplingParams(
          n=1,
          temperature=0.8,
          top_p=0.95,
          use_beam_search=False,
          ignore_eos=False,
          max_tokens=100,
      )

      for batch_of_strings in tqdm(self._batcher(preproc_input_prompts, batch_size), desc="Predict batch of requests"):
        outputs = model.generate(batch_of_strings, sampling_params)
        raw_predictions.extend(outputs)
    else:
      for batch_of_strings in tqdm(self._batcher(preproc_input_prompts, batch_size), desc="Predict batch of requests"):
        batched_encoding = tokenizer(batch_of_strings, padding="longest", return_tensors="pt")
        batched_encoding = batched_encoding.to(manager.device)
        tensor_inputs = batched_encoding["input_ids"]
        prompt_len = tensor_inputs.shape[1]
        tensor_outputs = model.generate(tensor_inputs, max_length=self.max_length + prompt_len)
        outputs = tokenizer.batch_decode(tensor_outputs, skip_special_tokens=True)
        raw_predictions.extend(outputs)

    # Postprocess output predictions if need
    postprocessor = PredictionPostprocessor()
    postproc_predictions = postprocessor.postprocess(raw_predictions)

    # save the predictions
    # TODO(vvchernov): clean path defenition
    if '/' in manager.model_name:
      manager.model_name = manager.short_name
    output_path = output_path or task.predictions_dir.joinpath(manager.model_name).with_suffix("_vllm.json" if use_vllm else ".json")
    self.save_predictions(output_path, examples, preproc_input_prompts, postproc_predictions)


class OpenAIPredictor(PredictorBase):
  def __init__(self,
               max_length: int=-1,
               batch_size: int=200,
               samples_num: int=None,
               data_path=None,
               output_path=None):
    super().__init__(self,
                     max_length,
                     batch_size,
                     samples_num,
                     data_path,
                     output_path)

  # todo make the saving of the metadata optional (with a default yes as we do it ourselves)
  # TODO(vvchernov): upstream args
  def generate_task(
      self,
      task_name_or_obj,
      model_name: str = "",
      overwrite_existing_predictions=False,
      min_ms_between_api_calls: int = 20,
      log_progress_every_n_examples: int = 100,
      save_every_n_examples: int = 300,
      org_name: str = ""
  ):
    task = get_task(task_name_or_obj) if isinstance(task_name_or_obj, str) else task_name_or_obj

    # load task data
    examples = task.get_data(self.data_path)
    examples = self.get_part_from(examples)

    if save_every_n_examples > len(examples):
      save_every_n_examples = len(examples)

    output_path = self.output_path or task.predictions_dir.joinpath(model_name).with_suffix(".json")
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
      "max_tokens": self.max_length,
      "top_p": 0,  # greedy
      "temperature": 1,
      "logprobs": 5,  # maximal value accorrding to https://beta.openai.com/docs/api-reference/completions/create#completions/create-logprobs, used to be 10...
      "model": model_name
    }
    time_of_last_api_call = self._ms_since_epoch()

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
      if (cur_time := self._ms_since_epoch()) <= time_of_last_api_call + min_ms_between_api_calls:
        ms_to_sleep = min_ms_between_api_calls - (cur_time - time_of_last_api_call)
        time.sleep(ms_to_sleep / 1000)
      time_of_last_api_call = self._ms_since_epoch()

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


  # TODO(vvchernov): upstream with base class method
  def generate(
      self,
      task_names: list[str] = None,
      model_name: str = "",
      num_processes: int = 1,
      data_path=None,
      output_path: Path = None,
      overwrite_existing_predictions=False,
      log_progress_every_n_examples: int = 100,
      save_every_n_examples: int = 300,
      org_name: str = ""
  ):
    if task_names is None:
      task_names = all_tasks

    min_ms_between_api_calls = num_processes * 20  # OpenAI limits us to 3000 calls per minute.

    # create arguments for generate_task:
    starargs = zip(task_names, repeat(model_name), repeat(data_path), repeat(output_path),
                   repeat(overwrite_existing_predictions), repeat(min_ms_between_api_calls),
                   repeat(log_progress_every_n_examples), repeat(save_every_n_examples), repeat(org_name))
    with Pool(processes=num_processes) as pool:
        pool.starmap(self.generate_task, starargs)


class OctoAIPredictor(PredictorBase):
  def __init__(self,
               max_length: int=256,
               batch_size: int=200,
               samples_num: int=None,
               data_path=None,
               output_path=None):
    super().__init__(self,
                     max_length,
                     batch_size,
                     samples_num,
                     data_path,
                     output_path)

  def call_octoai_inference(self, user_input, model_name):
    import requests
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

    # TODO(vvchernov): model name hard code
    model_name = "llama-2-70b-chat"
    data = {
        "model": model_name,
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

  def generate_task_parallel(self, id_, examples, model_name, predictions):
    id_ = str(id_)
    prompt = examples[id_]["input"]
    response = self.call_octoai_inference(prompt, model_name)

    predictions[id_] = dict()
    predictions[id_]["input"] = prompt

    response = json.loads(response.text)

    predictions[id_]["prediction"] = response['choices'][0]['message']['content']
    print(predictions[id_])

  # TODO(vvchernov): upstream args
  def generate_task(self,
                    task_name_or_obj,
                    manager: ModelManager = None,
                    model_name: str="",
                    device: str="cuda",
                    use_vllm: bool=True,
                    overwrite_existing_predictions=False,
                    log_progress_every_n_examples: int = 10,
                    save_every_n_examples: int = 300):

    import concurrent.futures
    # TODO(vvchernov): looks like OpenAI pipeline
    task = get_task(task_name_or_obj) if isinstance(task_name_or_obj, str) else task_name_or_obj

    # load task data
    examples = task.get_data(self.data_path)
    examples = self.get_part_from(examples)

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
        futures.append(executor.submit(self.generate_task_parallel, id_, examples, model_name, predictions))

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

class PredictorFactory():
  predictors_map = {
    "hf": HFTaskPredictor,
    "openai": OpenAIPredictor,
    "octoai": OctoAIPredictor,
  }

  def __init__(self) -> None:
    pass

  @staticmethod
  def get_predictor(name: str, **kwargs):
    if name in PredictorFactory.predictors_map.keys():
      return PredictorFactory.predictors_map[name](**kwargs)
    else:
      raise NotImplementedError(f"Predictor with name {name} is not supported!")
