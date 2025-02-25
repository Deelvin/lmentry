import argparse
from tqdm import tqdm

from lmentry.predict import PredictorFactory
from tasks.task_utils import get_tasks_names, task_groups, all_tasks
from lmentry.constants import DEFAULT_MAX_LENGTH


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("-m", "--model_names", nargs="+", type=str, default=["vicuna-7b-v1-3"],
                      help="Model names or paths to the root directory of mlc-llm models for predictions.")
  parser.add_argument("-t", "--task_names", nargs="+", type=str, default=all_tasks,
                      help="If need to evaluate specified set of tasks set their names or name(s) of specified task set(s). "
                           f"Task set names should be from the list: {task_groups.keys()}. "
                           f"Task names should be from the list: {all_tasks}. "
                           "It tries to analyze all tasks by default")
  parser.add_argument("-pr", "--predictor_type", type=str, default="hf",
                      help=f"Type of predictor, can be chosen from the list: {PredictorFactory.predictors_map.keys()}")
  parser.add_argument("-d", "--device", type=str, default="cuda",
                      help="Device name. It is needed and used by mlc model only")
  parser.add_argument("-b", "--batch_size", type=int, default=100,
                      help="For calculation on A10G batch size 100 is recommended. For mlc-llm models batch size is reduced to 1")
  parser.add_argument("-s", "--samples_num", type=int, default=None,
                      help="Number of samples to choose randomly from task dataset. "
                           "If set 'None' or the value is bigger than all samples number - all samples will be chosen.")
  parser.add_argument("-ml", "--max_length", type=int, default=DEFAULT_MAX_LENGTH,
                      help="Output max length")
  parser.add_argument("-uv", "--use_vllm", action="store_true", default=False,
                      help="Whether to use vLLM inference.")
  parser.add_argument("-fp", "--force_predict", action="store_true", default=False,
                      help="Whether to force regenerate predictions.")
  parser.add_argument("-ip", "--ip", type=str, default="0.0.0.0",
                      help="IP address of mlc-llm server (need for 'mlc-serve' predictor)")
  parser.add_argument("-p", "--port", type=int, default=9000,
                      help="port of mlc-llm server (need for 'mlc-serve' predictor)")

  args = parser.parse_args()
  return args


def main():
  args = parse_args()
  # TODO: Check skip mechanism: 1. (NO FORCE) samples_num <= len(task_config) -> Should skip [V][Task bigger_number was skipped due to it was done before. (200 generated vs. 100 requested)]
  # TODO: Check skip mechanism: 2. (NO FORCE) len(task_config) < samples_num < max_samples  -> Should generate s_n predictions [V]
  # TODO: Check skip mechanism: 3. (NO FORCE) samples_num=None and samples_num > len(task_config) -> Should set s_n to m_s and generate s_n predictions [V]
  # TODO: Check skip mechanism: 4. (NO FORCE) samples_num=None and samples_num <= len(task_config) -> Should skip [V]
  # TODO: Check skip mechanism: 5. (FORCE) samples_num <= max_samples (3000) -> Should generate s_n predictions [V]
  # TODO: Check skip mechanism: 6. (FORCE) samples_num > max_samples (3000) -> Should set s_n to m_s and generate m_s predictions [V]
  # TODO: Check --use_vllm and --samples_num (-sn) to work correctly [V]
  # TODO: Check that all other TODOs are done or marked [V]
  task_names = get_tasks_names(args.task_names)

  # Init predictor
  predictor = PredictorFactory.get_predictor(
      name=args.predictor_type,
      max_length=args.max_length,
      batch_size=args.batch_size,
      samples_num=args.samples_num,
      ip = args.ip,
      port = args.port,
      parallel = True,
  )

  for model_name in tqdm(args.model_names, desc="Predict specified models"):
    print(f"Prediction of tasks for {model_name} model starts")
    predictor.generate(
      task_names=task_names,
      model_name=model_name,
      device=args.device,
      use_vllm=args.use_vllm,
      force_predict=args.force_predict,
    )
    print(f"Prediction of tasks for {model_name} model finished")


if __name__ == "__main__":
  main()
