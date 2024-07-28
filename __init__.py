# cli-tool/__init__.py


__version__ = "0.1.0"


import os
import json



def initialize_directories():
    directories = [
        os.path.expanduser("~/cli-tool/output-text"),
        os.path.expanduser("~/cli-tool/input"),
        os.path.expanduser("~/cli-tool/input/english"),
        os.path.expanduser("~/cli-tool/input/chinese"),
        os.path.expanduser("~/cli-tool/output-text/english"),
        os.path.expanduser("~/cli-tool/output-text/chinese")
    ]

    for directory in directories:
        if(not os.path.isdir(directory)):
            os.makedirs(directory, exist_ok=True)

def initialize_files():
    config_path = os.path.expanduser("~/cli-tool/APIKEY.json")
    if not os.path.exists(config_path):
        openai_key = input("Please enter your OpenAI API key: ")
        anthropic_key = input("Please enter your Anthropic API key: ")
        config_data = {
            "openAI": openai_key,
            "Anthropic":anthropic_key
        }
        with open(config_path, "w") as config_file:
            json.dump(config_data, config_file, indent=4)
        print(f"Created config file: {config_path}")


    config_path = os.path.expanduser("~/cli-tool/en_storylist.txt")
    if not os.path.exists(config_path):
        with open(config_path, "w") as config_file:
            config_file.write("")

    config_path = os.path.expanduser("~/cli-tool/ch_storylist.txt")
    if not os.path.exists(config_path):
        with open(config_path, "w") as config_file:
            config_file.write("")

    config_path = os.path.expanduser("~/cli-tool/next-translation.json")
    if not os.path.exists(config_path):
        with open(config_path, "w") as config_file:
            json.dump({}, config_file, indent=4)
        

    config_path = os.path.expanduser("~/cli-tool/Story Language Identifier.json")
    if not os.path.exists(config_path):
        with open(config_path, "w") as config_file:
            json.dump({}, config_file, indent=4)
        

# Run the initialization functions when the package is imported
initialize_directories()
initialize_files()
