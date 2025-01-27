import os
from typing import Callable, List

import torch
import numpy as np

import tvm
from tvm import relax


def load_params(artifact_path: str, device) -> List[tvm.nd.NDArray]:
  from tvm.contrib import tvmjs  # pylint: disable=import-outside-toplevel

  params, meta = tvmjs.load_ndarray_cache(f"{artifact_path}/params", device)
  plist = []
  size = meta["ParamSize"]
  for i in range(size):
      plist.append(params[f"param_{i}"])
  return plist


class TVMModel:
  def __init__(self, config: dict) -> None:
    self.device = tvm.device(config["device"])
    self.const_params = load_params(config["artifact_path"], self.device)
    ex = tvm.runtime.load_module(
      os.path.join(
        config["artifact_path"],
        f"{config['mlc_model_name']}-{config['device']}.so",
      )
    )
    self.vm = relax.VirtualMachine(ex, self.device)

    self.tot_seq_len = 0
    self.kv_cache = self.vm["create_kv_cache"]()
    self.kv_cache_clear = tvm.get_global_func("vm.builtin.attention_kv_cache_array_clear")

    try:
      self.prefill_func = self.vm["prefill"]
    except AttributeError:
      self.prefill_func = None

  def reset(self):
    self.kv_cache_clear(self.kv_cache)
    self.tot_seq_len = 0

  def torch_to_tvm(self, torch_t):
    return tvm.nd.from_dlpack(torch.utils.dlpack.to_dlpack(torch_t))
  
  def torch_from_tvm(self, tvm_t):
    return(torch.utils.dlpack.from_dlpack(tvm_t.to_dlpack()))

  def forward(self, inputs: torch.Tensor, seq_len: int=1, reset: bool=False) -> torch.Tensor:
    if reset:
      self.reset()
    self.tot_seq_len += seq_len
    seq_len_shape = tvm.runtime.ShapeTuple([self.tot_seq_len])
    if seq_len > 1 and self.prefill_func:
      inputs = tvm.nd.from_dlpack(inputs)
      logits, kv_cache = self.prefill_func(
          inputs, seq_len_shape, self.kv_cache, self.const_params
      )
    else:
      for i in range(seq_len):
        input_slice = tvm.nd.from_dlpack(inputs[:, i : i + 1])
        logits, kv_cache = self.vm["decode"](
            input_slice, seq_len_shape, self.kv_cache, self.const_params
        )
    self.kv_cache = kv_cache

    return torch.from_dlpack(logits)


def get_tvm_model(config):
    model = TVMModel(config)
    return model.forward


def sample_top_p(probs, p):
  probs_sort, probs_idx = torch.sort(probs, dim=-1, descending=True)
  probs_sum = torch.cumsum(probs_sort, dim=-1)
  mask = probs_sum - probs_sort > p
  probs_sort[mask] = 0.0
  probs_sort.div_(probs_sort.sum(dim=-1, keepdim=True))
  next_token = torch.multinomial(probs_sort, num_samples=1)
  next_token = torch.gather(probs_idx, -1, next_token)
  return next_token


class RelaxModelWrapper:
  def __init__(self,
               model: Callable,
               stop_tokens: List[int],
               config: dict,
  ):
    self.device = tvm.device(config["device"])
    self.model = model
    self.stop_tokens = stop_tokens

    self.temperature = config["temperature"]
    self.top_p = config["top_p"]

  def generate(
    self,
    in_tokens: torch.Tensor,
    max_length: int,
  ):
    prompt_len = in_tokens.shape[1]
    tvm_tokens = tvm.nd.array(np.zeros((1, max_length), dtype="int32"), device=self.device)
    tokens = torch.from_dlpack(tvm_tokens)
    tokens[0, : prompt_len] = in_tokens
    start_pos = prompt_len
    for cur_pos in range(start_pos, max_length):
      if cur_pos == start_pos:
        logits = self.model(tokens[:, :cur_pos], cur_pos, reset=True)
      else:
        tvm_to_model = tvm.nd.array(np.zeros((1, 1), dtype="int32"), device=self.device)
        to_model = torch.from_dlpack(tvm_to_model)
        to_model[0, 0] = tokens[:, cur_pos - 1 : cur_pos]
        logits = self.model(to_model)
      logits = logits[:, -1, :].to(torch.float32)
      # if self.temperature > 0:
      #   probs = torch.softmax(logits / self.temperature, dim=-1)
      #   next_token = sample_top_p(probs, self.top_p)
      # else:
      next_token = torch.argmax(logits, dim=-1)
      next_token = next_token.reshape(-1)
      tokens[:, cur_pos] = next_token

      if next_token[0] in self.stop_tokens:
        break

    return tokens[:, :cur_pos + 1]


def get_relax_model(config, eos_token_id):
  return RelaxModelWrapper(get_tvm_model(config), [eos_token_id], config)
