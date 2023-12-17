from colorama import init, Fore, Style
init(autoreset=True)

from src.utils import *
from init_prompts import *


if __name__ == "__main__":
    user_input = input("What would you like to build?")
    print(Fore.GREEN + f"You want to build: {user_input}" + Style.RESET_ALL)
    initial_sum_prompt = get_project_prompt(user_input)
    project_label_generation = generate(initial_sum_prompt, max_tokens = 150)
    
    project_label = parse_for_title(project_label_generation)
    print(Fore.YELLOW + f"Parsed project title : {project_label}" + Style.RESET_ALL)
    
    code_prompt = get_code_writer_prompt(project_label)
    code_generated = generate(code_prompt, max_tokens = 5000)
    
    code_files = parse_code_result(code_generated)
    
    final = develop_files(code_files, user_input)