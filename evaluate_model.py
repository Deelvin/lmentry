import argparse
import logging

from lmentry.constants import PREDICTIONS_ROOT_DIR, TASKS_DATA_DIR, RESULTS_DIR
from lmentry.analysis.accuracy import (
  score_all_predictions,
  create_per_task_accuracy_csv,
  create_per_template_accuracy_csv,
)
from tasks.task_utils import get_tasks_names, task_groups, all_tasks
from lmentry.model_manager import get_short_model_names


def parse_arguments():
  parser = argparse.ArgumentParser(
      description="CLI for evaluating LMentry using the default file locations",
      formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument("-m", "--model_names", nargs="+", type=str, default=None,
                      help="Names of models which statistics were collected and should evaluate. "
                           "If it is None the predictions directory is analized and evailable model-statistics are evaluated")
  parser.add_argument('-t', '--task_names', nargs="+", type=str, default=all_tasks,
                      help="If need to evaluate specified set of tasks set their names or name(s) of specified task set(s). "
                           f"Task set names should be from the list: {task_groups.keys()}. "
                           f"Task names should be from the list: {all_tasks}. "
                           "It tries to analyze all tasks by default")
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
  if not PREDICTIONS_ROOT_DIR.exists():
    logging.error(f"Predictions not found at {PREDICTIONS_ROOT_DIR}. aborting.\n")
    return
  RESULTS_DIR.mkdir(exist_ok=True)

  args = parse_arguments()

  task_names = get_tasks_names(args.task_names)
  model_names = get_short_model_names(args.model_names)

  logging.info(f"scoring LMentry predictions for models {model_names}")
  score_all_predictions(
    task_names=task_names,
    model_names=model_names,
    num_processes=args.num_procs
  )
  logging.info(f"finished scoring all LMentry predictions for models {model_names}")

  create_per_task_accuracy_csv(task_names=task_names, model_names=model_names)
  create_per_template_accuracy_csv(task_names=task_names, model_names=model_names)


if __name__ == "__main__":
  main()
