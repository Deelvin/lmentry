# Table of contents
1. [LMentry](#lmentry)
2. [Environment adjustment](#environment-adjustment)
3. [Prediction](#prediction)
4. [Scoring](#scoring)
5. [Evaluation](#evaluation)
6. [Two models comparison](#two-models-comparison)
7. [README from the original github repo](#readme-from-the-original-github-repo)

# LMentry

This repository is a fork from the original one which contains the LMentry benchmark from [LMentry: A Language Model Benchmark of Elementary Language Tasks](https://arxiv.org/pdf/2211.02069.pdf), as well as the code to evaluate it.
There was refactoring of the code to support manipulation with external models (like one from HuggingFace or [mlc-llm](https://github.com/mlc-ai/mlc-llm) side). The original benchmark consists of three parts: 1. **prediction** or collection of statistics during inference of specified model on the benchmark task datasets and save it in json-files; 2. **scoring** or processing of obtained statistics and save local scores for each request to the json-files; 3. **evaluation** or processing of obtained scores and calculation final result (accuracy, robustness and LMentry score).

# Environment adjustment
All calculations occurs in conda environment. Unfortunately the original environment becomes old enough and it is needed to update some packeges:
```bash
conda env create -f environment.yml
conda activate lmentry
python3 -m pip install transformers scipy accelerate tokenizers==0.13.3
```

and additionally for support mlc-llm dependencies (do it under lmentry env):
```bash
conda install -c conda-forge libstdcxx-ng=12
python3 -m pip install decorator attrs pytest cloudpickle
```

# Prediction
Special prediction script was implemented. It supports models from HF and mlc-llm. If we want to benchmark model processed in [mlc-llm](https://github.com/mlc-ai/mlc-llm) the path to root directory with model shared library (so-file) and dependencies is simply needed:
```bash
python3 predict_model.py -m <path_to_mlc-llm>/dist/vicuna-7b-v1.3-q0f16
```
See details about other script features using help arg:
```bash
python3 predict_model.py --help
```
**Note:** additionaly to the script the mechanism of skipping prediction calculation which was done before was implemented. Usually it requires enough time but needs once. If it is needed to redo some tasks for specified model simply remove corresponding json-files in `predictions` directory.

# Scoring
Scoring process was initially hidden in evaluation one. But sometimes it is convenient to execute it separately during development. For example, if some fixes were done in annotator or some doubts appears for specified task it needs to rescore it. But evaluation or comparison scripts (see below) do it for all processed tasks which requires more time. The mechanism for skipping earlier scored tasks were added. To rescore such tasks by force use special key `--forced_scoring` (or `-f`):
```bash
python3 scoring.py -m <path_to_mlc-llm>/dist/vicuna-7b-v1.3-q0f16 -t first_letter -f -n 8
```
See details about the script features using help arg:
```bash
python3 scoring.py --help
```

# Evaluation
The original evaluation script processes statistics collected during the prediction stage and output values of accuracy, robustness and LMentry score averaged and for each task formed in csv-files. Based on number of processed task (total number is 41) and number of models it can require much time for evaluation. Due to this fact it is recommended to set as many <num-procs> as possible to accelerate the process.
```bash
python3 lmentry/evaluate.py --num-procs <num-procs>
```
**Note:** it assumes that predictions were done for all tasks. It parses `predictions` directory and finds all tasks and models processed. If not all task were proccesed for at least one model the original script fails.</br>
To do the evaluation stage more flexible (use not all tasks or models predicted earlier) a new script was implemented. The script allows to specified model(s) and task(s) for evaluation, but it calculates the accuracy only (due to robustness requires certain set of tasks for evaluation):
```bash
python3 evaluate_model.py -m <model_name_1> <model_name_2> <model_name_3> .. -t <task_name_1> <task_name_2> <task_name_3> .. -n <num-procs>
```

# Two models comparison
Sometimes the task of comparison of the original and optimized model appears. To solve it based on LMentry benchmarking a new script was implemented. The script compares two models (reference and probe ones) using five selected tasks (bigger_number, first_alphabetically, first_letter, most_associated_word, smaller_number) or other customized ones and calculating their accuracy and additional hand-made statistics (full match, correct match, wrong match, correct non-match, correct, reduction). The latter statistics gives deeper information even when models accuracy is slightly different.</br>
***Full match*** is percent of the same answers from both models from all task requests.</br>
***Correct match*** is percent of the same answers from both models from all task requests on which reference (first) model gave correct answer.</br>
***Wrong match*** is percent of the same answers from both models from all task requests on which reference (first) model gave wrong answer.</br>
***Correct non-match*** is percent of the different but correct answers from both models from all task requests on which reference (first) model gave correct answer.</br>
***Correct*** (sum of correct match and correct non-match) is percent of the correct answers from probe (second) model from all task requests on which reference (first) model gave correct answer.</br>
***Reduction*** (not the best statistics name) is part (in percent) of which is the accuracy of the probe model compared to the accuracy of the reference model. Correct is not the same as reduction due to probe model sometimes correctly answers on questions which the reference model fails.</br>
The script works from the box and does not require any other model processing (prediction, scoring, evaluation stages) due to do it subsequently by it-self. It skips prediction or/and scoring stages if it was done earlier (nevertheless scoring can be done by force). As a result a csv-file with statistics is saved in `results/comparison` directory.
```bash
python3 compare_models.py -r <reference_model_name_or_path> -p <probe_model_name_or_path> -n <num-procs>
```
See details about other script features using help arg:
```bash
python3 compare_models.py --help
```
