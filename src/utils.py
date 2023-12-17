from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
import transformers
import torch
import re
import os
from init_prompts import *

from colorama import init, Fore, Back, Style
init(autoreset=True)

def parse_for_title(output):
    label_token = 'Label:'
    output_lines = output.split("\n")
    for i in reversed(range(0, len(output_lines))):
        if label_token in output_lines[i]:
            return output_lines[i][output_lines[i].index(label_token) + 6:].strip()

def parse_code_result(output):
    output = output[output.index("[/INST]"):]
    code_blocks = re.findall(r"```(.*?)```", output, re.DOTALL)
    file_names = re.findall(r"\*\*(.*?)\*\*", output, re.DOTALL)

    code_files = []
    print(Fore.GREEN + f"Total files: {len(file_names)}" + Style.RESET_ALL)

    for i in range(0, len(file_names)):
        if i < len(code_blocks):
            code_files.append({
                "file_name": file_names[i],
                "code_block": code_blocks[i]
            })

    return code_files

def initiate_code_modification(code_files, modification_ask):
    new_code_files = []
    for file_code_pair in code_files:
        mod_prompt = get_modification_prompt("\n".join(file_code_pair["code_block"].split("\n")[1:]), modification_ask)
        modification_result = generate(mod_prompt, max_tokens = 1024)
        print("MOD_RESULT:", modification_result)
        if "RETURNEDCODE" in modification_result:
            modification_result = modification_result[modification_result.index("[/INST]"):]
            code_block_raw_string = modification_result[modification_result.index("RETURNEDCODE") + len("RETURNEDCODE"):]
            file_code_pair["code_block"] = re.findall(r"```(.*?)```", code_block_raw_string, re.DOTALL)[0]
        new_code_files.append(file_code_pair)
    return new_code_files

def create_readme(code_files):
    print(Fore.BLUE + "Generating the README..." + Style.RESET_ALL)

    readme_prompt = get_readme_prompt(str(code_files))
    readme_result = generate(readme_prompt, max_tokens = 2000)
    return readme_result[readme_result.find('[/INST]') + 7: - 7]

def load_model(model_flag = "llama2_hf"):
    ''' Recommended - Add a flag that will indicate the user choice of using model, can be implemented by keeping a setup or config file
        Below is a sample implementation of users if they dont want to use LLAMA2 and rather want to opt for more open-source models.
        Once the Flag is offset, we can extend this with a model_str param in the config file

        **********************************************************************************************************************************************
        Current Implementation : Using model_flag variable inside the function to determine the model to be chosen for generation of content
        **********************************************************************************************************************************************
        model_flag (str) : determines the model to be used by the function. Default Value - llama2_hf
                                                                            Other Values - mistral_8x7b_instruct
    '''

    if model_flag == "llama2_hf":
        model_name = "meta-llama/Llama-2-7b-chat-hf"

        tokenizer = AutoTokenizer.from_pretrained(model_name,
                                                use_fast = True,
                                                token = 'enter your hf token here')

        streamer = TextStreamer(tokenizer, skip_special_tokens=True)
        model = AutoModelForCausalLM.from_pretrained(model_name,  
                                                    load_in_8bit=True,
                                                    device_map="auto",
                                                    token = 'enter your hf token here')

        pipeline = transformers.pipeline(
            "text-generation",
            model=model,
            tokenizer = tokenizer,
            torch_dtype=torch.float16,
            streamer = streamer
        )
        print(Fore.GREEN + "Model is loaded" + Style.RESET_ALL)

        return model, tokenizer, pipeline
    
    elif model_flag == "mistral_8x7b_instruct":
        model_name = "mistralai/Mixtral-8x7B-Instruct-v0.1"

        tokenizer = AutoTokenizer.from_pretrained(model_name,
                                                use_fast = True)

        streamer = TextStreamer(tokenizer, skip_special_tokens=True)
        model = AutoModelForCausalLM.from_pretrained(model_name,  
                                                    load_in_8bit=True, #load_in_4bit = True can be used if load_in_8bit fails
                                                    device_map="auto")

        pipeline = transformers.pipeline(
            "text-generation",
            model=model,
            tokenizer = tokenizer,
            torch_dtype=torch.float16,
            streamer = streamer
        )
        print(Fore.GREEN + "Model is loaded" + Style.RESET_ALL)

        return model, tokenizer, pipeline

model, tokenizer, pipeline = load_model(model_flag="llama2_hf") #available options for model_flag = [llama2_hf, mistral_8x7b_instruct]

def generate(prompt, max_tokens):
    sequences = pipeline(
      prompt,
      do_sample=True,
      top_k=10,
      num_return_sequences=1,
      eos_token_id=tokenizer.eos_token_id,
      max_length=max_tokens,
    )
    return sequences[0]['generated_text']

def develop_files(code_files, user_ask, modification_ask=None):
    if modification_ask:
        code_files = initiate_code_modification(code_files, modification_ask)

    readme_generate = create_readme(code_files)

    for file_code_pair in code_files:
        filepath = "code-output/"+file_code_pair["file_name"]
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w+") as f:
            code_block = file_code_pair["code_block"].split("\n")[1:]
            f.write("\n".join(code_block).encode('ascii', 'ignore').decode('ascii'))

    
    filepath = "code-output/"+'README.md'
    with open(filepath, "w+") as f:
        f.write("\n".join(readme_generate).encode('ascii', 'ignore').decode('ascii'))
    
    
    print(Fore.GREEN + "Done! Check out your codebase in the folder python-output/" + Style.RESET_ALL)
    user_input = input("Do you wish to make modifications? [y/n]")
    if user_input == "y":
        modification_ask = input("What modifications do you want to make?")
        develop_files(code_files, user_ask, modification_ask=modification_ask)
    else:
        print(Fore.GREEN + "Project successfully built" + Style.RESET_ALL)