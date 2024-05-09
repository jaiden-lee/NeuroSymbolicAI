# Results

Tested Mistral with first 500 datapoints (means 2000 loglikelihood requests) of hellaswag

Took 2 hours to complete

Acc: .574, std = .0221
Acc_norm: .738, std = .0197

# How to Reproduce
Since I am running Mistral 7B gguf quantized version with llama.cpp, I needed to create a local server, since lm-eval-harness passes inputs through the server. Type:

`python -m llama_cpp.server --model "PATH TO GGUF FILE HERE"`

ex: `python -m llama_cpp.server --model "C:\Users\test_user\.cache\huggingface\hub\models--TheBloke--Mistral-7B-Instruct-v0.2-GGUF\snapshots\3a6fbf4a41a1d52e415a4958cde6856d34b2db93\mistral-7b-instruct-v0.2.Q2_K.gguf"`

After, enter this command in a new terminal window:

`lm_eval --model gguf --model_args base_url=http://localhost:8000 --tasks hellaswag --batch_size auto --device cpu --limit 500`

The --limit keyword specifies how many datapoints to actually evaluate the model on, so you don't have to run through all 40,000 or so, which would probably take around a week.