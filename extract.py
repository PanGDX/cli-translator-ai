import os, re
import argostranslate.package
import argostranslate.translate
from utility import submit_to_AI
rootDir = os.path.expanduser("~/cli-tool/")


translation_prompt = """
# Mission
Translate names from Chinese to English in the context of {context}. Inaccuracies are acceptable.

# Output Format
Only output the following, line by line.
(Chinese name) - (Translated English name)
No additional comments needed."""

reduction_prompt = """
# Mission
Take the names and eliminate ones that do not seem relevant to the context of {context}.
The condition for relevancy are: names of characters and names of organisations.

# Output Format
Only output the following, line by line.
(Chinese name) - (Translated English name)
No additional comments needed."""


def translate_text(string):
    from_code, to_code = "zh", "en"
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        (pkg for pkg in available_packages if pkg.from_code == from_code and pkg.to_code == to_code), None
    )
    if package_to_install:
        argostranslate.package.install_from_path(package_to_install.download())
        return argostranslate.translate.translate(string, from_code, to_code)
    return string

def extract_chinese(text):
    pattern = r'[\u4e00-\u9fff]+'
    return re.findall(pattern, text)

def sorting(lst):
    return sorted(lst, key=len)


def name_translation_aid(client, isGPT:bool, model:str, namelist:list, context:str):
    def return_segmented_namelist(namelist:list, numberOfNames:int = 20):
        """
        @param: namelist a list of strings (names)
        @param: numberOfNames the number of names in one 'long name string'
        @return: a list of long strings of names separated by \n

        This is so that the model bulk translates instead of translating one by one. 
        """
        
        long_string_list = []
        sub_namelist = ""
        for name in namelist:
            if len(sub_namelist.split("\n")) > numberOfNames:
                long_string_list.append(sub_namelist)
                sub_namelist = ""
            sub_namelist += f"{name}\n"
        long_string_list.append(sub_namelist)
        return long_string_list

    translation_prompt = translation_prompt.format(context = context)
    reduction_prompt = reduction_prompt.format(context = context)
    segmented_namelist = return_segmented_namelist(namelist, 20)
    
    translated_names = []

    for sub_namelist in segmented_namelist:
        names_translated_list = submit_to_AI(
				client,
				isGPT,
				model,
				translation_prompt,
				sub_namelist,
				"Translating..."
			).split("\n")
        
        
        translated_names.append(names_translated_list)

    translated_names = (list(set(translated_names)))
    segmented_translated_namelist = return_segmented_namelist(namelist, 50)
    
    final_namelist = []
    for segmented_translated_names in segmented_translated_namelist:
        reduced_translated_list = submit_to_AI(
                    client,
                    isGPT,
                    model,
                    reduction_prompt,
                    segmented_translated_names,
                    "Reducing..."
                ).split("\n")
        final_namelist.append(reduced_translated_list)


    gpt_translated_dict = {line.split("-")[0].strip(): line.split("-")[1].strip() for line in final_namelist if line}
    
    argos_translated = {name: translate_text(name) for name in gpt_translated_dict}
    
    return gpt_translated_dict, argos_translated



