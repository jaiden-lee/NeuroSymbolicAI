# Overview
1. Running tasks
2. Creating new tasks

# 1. Running Tasks/Evaluating on Existing Tasks
To see a list of all available tasks, you can run:
`lm_eval --tasks list`

Also, if you have lm-eval-harness repo installed, then you can go from root > lm_eval > tasks

To evaluate a model a gguf model, run:

`lm_eval --model gguf --model_args base_url=[URL, most likely localhost:8000] --tasks [TASKNAME] --limit [how many you want to evaluate] --batch_size [number (i.e., 8), or auto (chooses most your device can handle)] --device [cuda, cpu]`

There are more commands, but these are pretty much all the basic ones you need to get started

Evaluating a gguf model requires that gguf model to be running on some inference server, so you can boot up your own local one with:
`python -m llama_cpp.server --model "PATH TO GGUF FILE HERE"`

# 2. Creating new Tasks
To create new tasks, you go to root > lm_eval > tasks

Inside this directory, you can see the available tasks, which are in their own folder. A task has:
1. YAML Config file
2. Python files (for preprocessing of the data)

Most importantly, in the YAML config file, there is a `dataset_path`, which is the dataset name on HuggingFace.

A keyword in this YAML file is `!function [file_name.function_name]`

This lets you specify a function to be run. This is often used for preprocessing of data.

Most likely, just take an existing one of these tasks, and slightly modify to work on new task.