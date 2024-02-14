import json
from typing import List

import requests


class MLCServeModelWrapper:
  def __init__(
    self,
    model_name: str,
    ip: str = "0.0.0.0",
    port: int = 32777,
    temperature: float = 0.0,
    top_p: float = 1.0,
    parallel: bool = False,
  ):
    self.model_name = model_name
    self.ip = ip
    self.port = port
    self.temperature = temperature
    self.top_p = top_p

    self.url_suffix = "/v1/chat/completions"
    self.parallel = parallel

    self.headers = {
        "Content-Type": "application/json",
    }

  def create_chat_completion_payload(
        self,
        prompt,
        stop_tokens = [],
    ):
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
            "stop": stop_tokens,
            "top_p": self.top_p,
            "temperature": self.temperature,
        }

        return payload

  def send_request(self, payload):
      response = requests.post(
          f"http://{self.ip}:{self.port}{self.url_suffix}", json=payload, headers=self.headers
      )

      if response.status_code != 200:
          print(f"Error: {response.status_code} - {response.text}")

      return json.loads(response.text)

  def get_output(self, response):
    return response["choices"][0]["message"]["content"]

  def model_call(self, prompt, results):
    payload = self.create_chat_completion_payload(prompt)
    output_json = self.send_request(payload)

    results.append(self.get_output(output_json))

  def model_generate_parallel(self, input_batch, results):
      import concurrent.futures

      batch_size = len(input_batch)
      with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
        futures = []
        parallel_results = {}
        for id in range(batch_size):
          parallel_results[id]=[]
          futures.append(executor.submit(self.model_call, input_batch[id], parallel_results[id]))

      for future in concurrent.futures.as_completed(futures):
        try:
          future.result()
        except Exception as exc:
          print(f"Error parallel generating predictions: {exc}")

      # Collect results together
      for id in range(batch_size):
        results.extend(parallel_results[id])

  def generate(
    self,
    in_strs: List[str],
  )-> List[str]:
    if not in_strs:
      return []

    results = []
    if self.parallel:
      self.model_generate_parallel(in_strs, results)
    else:
      for prompt in in_strs:
        self.model_call(prompt, results)

    return results


def get_mlc_serve_model(model_name, ip, port, parallel=False):
  return MLCServeModelWrapper(
    model_name=model_name,
    ip=ip,
    port=port,
    parallel=parallel,
  )
