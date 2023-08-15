import argparse
import logging

from lmentry.constants import TASKS_DATA_DIR, RESULTS_DIR
from lmentry.tasks.lmentry_tasks import all_tasks, tasks_to_compare
from lmentry.predict import generate_all_hf_predictions
from lmentry.analysis.accuracy import (
  score_all_predictions,
  create_per_task_accuracy_csv,
  create_per_template_accuracy_csv,
)


def parse_arguments():
  parser = argparse.ArgumentParser(
      description="CLI for comparison of two models (reference and probe) using LMentry tasks from the default file locations and additional heuristics",
      formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument("-r", "--ref_model_name", type=str, default="vicuna-7b-v1-3-q0f16",
                      help="Name of reference model. It is assumed that the model is original, "
                           "uses high-precision data type and has better accuracy")
  parser.add_argument('-p', '--probe_model_name', type=str, default="vicuna-7b-v1-3-q4f16_0",
                      help=f"If need to evaluate specified set of tasks set their names. "
                            "Task names should be from the list: {all_tasks.keys()}. "
                            "It tries to analyze all tasks by default")
  parser.add_argument('-t', '--task_names', nargs="+", type=str, default=None,
                      help="If need to evaluate specified set of tasks set their names. "
                           f"Task names should be from the list: {all_tasks.keys()}. "
                            "It tries to analyze all tasks by default")
  parser.add_argument('-d', '--device', type=str, default="cuda",
                      help="Device name. It is needed and used by mlc model only during predictions")
  parser.add_argument('-b', '--batch_size', type=int, default=100,
                      help="For calculation on A10G batch size 100 is recommended. "
                           "For mlc-llm models batch size is reduced to 1. "
                           "It is used duirng predictions.")
  parser.add_argument('-ml', '--max_length', type=int, default=53,
                      help="Input max length. It is used duirng predictions.")
  parser.add_argument("-n", "--num-procs",
                      default=1,
                      type=int,
                      help="The number of processes to use when scoring the predictions. "
                           "Can be up to the number of models you want to evaluate * 41.")
  return parser.parse_args()


def main():
  if not TASKS_DATA_DIR.exists():
    logging.error(f"LMentry tasks data not found at {TASKS_DATA_DIR}. aborting.\n")
    return
  RESULTS_DIR.mkdir(exist_ok=True)

  args = parse_arguments()
  if args.task_names is not None:
    task_names = args.task_names
  else:
    task_names = sorted(tasks_to_compare.keys())

  # Predict specified tasks for given models
  # Reference model
  logging.info(f"Prediction for {args.ref_model_name} model starts")
  generate_all_hf_predictions(
    task_names=task_names,
    model_name=args.ref_model_name,
    max_length=args.max_length,
    batch_size=args.batch_size,
    device=args.device,
  )
  logging.info(f"Prediction for {args.ref_model_name} model finished")
  # Probe_model
  logging.info(f"Prediction for {args.probe_model_name} model starts")
  generate_all_hf_predictions(
    task_names=task_names,
    model_name=args.probe_model_name,
    max_length=args.max_length,
    batch_size=args.batch_size,
    device=args.device,
  )
  logging.info(f"Prediction for {args.probe_model_name} model finished")

  logging.info(f"scoring LMentry predictions for specified models")
  score_all_predictions(task_names=task_names,
                        model_names=args.model_names,
                        num_processes=args.num_procs
                        )
  logging.info(f"finished scoring all LMentry predictions for specified models")

  model_names = [args.ref_model_name, args.probe_model_name]
  create_per_task_accuracy_csv(task_names=task_names, model_names=model_names)
  create_per_template_accuracy_csv(task_names=task_names, model_names=model_names)


if __name__ == "__main__":
  main()