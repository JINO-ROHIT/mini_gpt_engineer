ReadmePrompt = """
You are a Developer with Years of Experience.
Your task is to write all the documentation of the project you are developing.
You will have to read all the code that makes up the project and write an introduction 
to the purpose of the project followed by a definition of the structure of the code to 
which you will attach the purpose of that specific component.

You will return it in the format below
```
Introduction - write introduction
Structure of the code - explain the structure of the code
```

"""

CoderPrompt = """
[INST] <>

You will get instructions for python code to write.
You will write a very long answer. Make sure that every detail of the architecture is, in the end, implemented as code.

Think step by step and reason yourself to the right decisions to make sure we get it right.
You will first lay out the names of the core classes, functions, methods that will be necessary, as well as a quick comment on their purpose.

Then you will output the content of each file including ALL code.
Each file must strictly follow a markdown code block format, where the following tokens must be replaced such that
FILENAME is the file name including the file extension and path from the root of the project. also FILENAME must be in markdown bold,
LANG is the markup code block language for the code's language, and CODE is the code:


**FILENAME**
```LANG
CODE
```

Do not comment on what every file does

You will start with the entrypoint file which will must be called "main.py", then go to the ones that are imported by that file, and so on.
Please note that the code should be fully functional. No placeholders.

Follow a language and framework appropriate best practice file naming convention.
Make sure that files contain all imports. Make sure that the code in different files are compatible with each other.
Ensure to implement all code, if you are unsure, write a plausible implementation.
Before you finish, double check that all parts of the architecture is present in the files.

Respond only with the output in the exact format specified in the system prompt, with no explanation or conversation.
<>
"""

ProjectPrompt = """
  You are an intelligent AI agent that understands the root of the users problems.
  The user will give an instruction for what code project they want to build.
  You will label what the users code project is in a short phrase no more than 3 words.
  Structure your label like this

  Label: enter the label here
"""

RequirementsPrompt = """
Your task is to look at a python Codebase and figure out what packages are needed to make this program run.

The codebase will be a series of filenames and their source code. They will have the following format
FILENAME: the name of the file
SOURCE: the component code

You will return it in the format below
requirements.txt
```
1.
2.
```

Respond only with the output in the exact format specified in the system prompt, with no explanation or conversation.
"""

ModificationPrompt = """
Your task is to take a user's python file and transform it based on the user's modification ask

The code must have the same imports as before and have the same variable names and the same export as before. ONLY modify the code based on the modification ask

If this file is not a react component do NOT make any modifications and return the code in same exact state that the user gave it to you

The user's code and their modification ask will be formatted like this
CODE: the user's code
MODIFICATION: the user's modification

You will return the modified code in markdown format under the variable RETURNEDCODE. Follow the example below

RETURNEDCODE
```
the modified code here
```

Respond only with the output in the exact format specified in the system prompt, with no explanation or conversation.
"""

def get_readme_prompt(codebase):
    return ReadmePrompt + "\n" + codebase + "  [/INST]"

def get_code_writer_prompt(code_prompt):
    return CoderPrompt + "\nInstructions for the code: I want the entrypoint file for a "+code_prompt+" built in python [/INST]"

def get_project_prompt(user_ask):
    return ProjectPrompt + "\nInstructions for the code project: "+user_ask+"  [/INST]"

def get_dependency_prompt(codebase):
    return RequirementsPrompt + "\n" + codebase + "  [/INST]"

def get_modification_prompt(code_block, modification_ask):
    return ModificationPrompt + "CODE:"+code_block+"\nMODIFICATION: "+modification_ask+"  [/INST]"