import typer, os, json, anthropic
from typing_extensions import Annotated
from utility import (
	load_json,
	modify_json_file,
	submit_to_AI,
	split_paragraph,
	replace_string_in_files,
	sanitize_folder_name,
	append_and_clean
)
from __init__ import initialize_directories,initialize_files
import os
from openai import OpenAI

from bs4 import BeautifulSoup
from scrape import create_selenium_driver, find_divs_with_text,scrape_webpage
from extract import extract_chinese, sorting, name_translation_aid




rootDir = os.path.expanduser("~/cli-tool/")
api_data = load_json( os.path.join(rootDir, "APIKEY.json") )
app = typer.Typer(help="This is a CLI tool that scrapes, translates and improves the translation of Chinese fanfictions and novels.")

@app.command(help="Setup")
def setup():
	print("Making Directories")
	initialize_directories()
	print("Making Config files.")
	initialize_files()


@app.command(help="Add story")
def addstory():
	"""
	Add story. 
	Suppose you copy a folder in. This is since we may use lncrawl
	We need to then add the folder and file to the system.
	"""
	initialize_directories()
	initialize_files()

	story_name= str(input("Actual story name: "))
	output_folder = sanitize_folder_name(story_name)
	
	 
	isChineseChoice = str(input("Is the story Chinese? (y/n): ")).lower()
	if isChineseChoice == "y": isChinese = True
	else: isChinese = False

	if isChinese:
		full_dir = os.path.join(rootDir, "input", "chinese", output_folder)
		story_list_file = os.path.join(rootDir, "ch_storylist.txt")
	else:
		full_dir = os.path.join(rootDir, "input", "english", output_folder)
		story_list_file = os.path.join(rootDir, "en_storylist.txt")
	os.makedirs(full_dir, exist_ok=True)
	

	
	append_and_clean(story_list_file, story_name)


	modify_json_file(
		file_path= os.path.join(rootDir,"next-translation.json"),
		appendJson={
			story_name : 1
		}
	)



@app.command(help="Translate Chinese stories to English or refine English grammar")
def process_story():
	initialize_directories()
	initialize_files()

	def return_story_name(mode):
		print("Choose the story name using the number")
		storylist_file = open(f"{rootDir}\\{'ch' if mode == 'translate' else 'en'}_storylist.txt", "r")
		storylist = storylist_file.read().split("\n")

		for i, story in enumerate(storylist, 1):
			print(f"{i}: {story}")
		return storylist[int(input(":"))-1]

	mode = input("Choose mode (translate/refine): ").lower()
	if mode not in ['translate', 'refine']:
		raise ValueError("Invalid mode. Choose 'translate' or 'refine'.")

	STORYNAME = return_story_name(mode)
	storyfolder = sanitize_folder_name(STORYNAME)
	print("In Folder: " + storyfolder)

	if mode == 'translate':
		context = input("Context of the story: ")
		names = ""
		while True:
			name_temp = input("Key Names? (empty = break): ")
			if not name_temp:
				break
			names += (name_temp + "\n")

	chapters = int(input("How many chapters to process: "))
	useGPT = input("Use GPT? (y/n): ").lower() == 'y'

	if useGPT:
		client = OpenAI(api_key=api_data['openAI'])
		translation_model = "gpt-4-turbo"
		grammar_model = "gpt-4o"
	else:
		client = anthropic.Anthropic(api_key=api_data['Anthropic'])
		translation_model = grammar_model = "claude-3-5-sonnet-20240620"

	next_chapter_to_process = load_json(os.path.join(rootDir, "next-translation.json"))[STORYNAME]
	input_folder = os.path.join(rootDir, "input", "chinese" if mode == 'translate' else "english", storyfolder)
	output_folder = os.path.join(rootDir, "output-text", "chinese" if mode == 'translate' else "english", storyfolder)

	if not os.path.isdir(output_folder):
		os.makedirs(output_folder)

	try:
		for _ in range(chapters):
			print(f"Processing chapter: {next_chapter_to_process}")
			
			current_chapter_str = str(next_chapter_to_process)
			potential_names = [f"{current_chapter_str.zfill(i)}.txt" for i in range(6)]

			chapter_file_dir = None
			for file_name in potential_names:
				file_path = os.path.join(input_folder, file_name)
				if os.path.isfile(file_path):
					chapter_file_dir = file_path
					break
					
			outputchapter = sorted(
								os.listdir(output_folder), 
							   	key=lambda name: int(name.split('.')[0])
							   )[-1]
			outputchapter = f"{int(outputchapter.split('.')[0]) + 1}.txt"

			print(chapter_file_dir)
			if chapter_file_dir is None:
				raise FileNotFoundError("Chapter file not found")

			with open(chapter_file_dir, "r", encoding="utf-8") as content_file:
				content = content_file.read().replace("\n\n", "\n")

			if mode == 'translate':
				translation_message = f"""
### Mission
You are a highly skilled translator with expertise in Chinese. 
You are to accurately translate from Chinese to English following the context given. 
The USER will give you a text input and the name list. 

### Context
The context is of: {context}

### Instructions
- Only output the edited and translated version
- Preserve all dialogues.
- Minimal edits to the story.
"""
				grammar_message = """
Correct any English grammar and sentence structure error. 

### Rules
Only output the corrected version. No other comments needed
Do not edit the names, locations or key details of the story. 
Do not summarise the story.
""".strip()

			else:  # refine mode
				grammar_message = """
Correct any English grammar and sentence structure error. Sentences should make logical sense. 
Then reformat the sentences so they are connected. Sentences may be disconnected due to newlines

### Rules
Only output the corrected version. No other comments needed
Do not edit the names, locations or key details of the story. 
Do not summarise the story.""".strip()

			final_text = None
			try:
				first_chunk, second_chunk = split_paragraph(content)

				

				if mode == 'translate':
					first_chunk = f"""
### Common Names (not limited to this list)
{names}

### Story
{first_chunk}
""".strip()


					second_chunk = f"""
### Common Names (not limited to this list)
{names}

### Story
{second_chunk}
""".strip()


					temp = submit_to_AI(client, useGPT, translation_model, translation_message, first_chunk, "Translating")
					final_text = submit_to_AI(client, useGPT, grammar_model, grammar_message, temp, "Improving Grammar")
					final_text += "\n\n"
					temp = submit_to_AI(client, useGPT, translation_model, translation_message, second_chunk, "Translating")
					final_text += submit_to_AI(client, useGPT, grammar_model, grammar_message, temp, "Improving Grammar")
				else:
					final_text = submit_to_AI(client, useGPT, grammar_model, grammar_message, first_chunk, "Improving Grammar")
					final_text += "\n\n"
					final_text += submit_to_AI(client, useGPT, grammar_model, grammar_message, second_chunk, "Improving Grammar")

			except Exception as e:
				print("ERROR OCCURRED\n", e)

			if final_text is not None:
				with open(os.path.join(output_folder, outputchapter), "w", encoding="utf-8") as append_to_file:
					append_to_file.write(str(final_text))
				next_chapter_to_process += 1
			else:
				raise Exception("Error in processing!!!!")
	except Exception as e:
		print(e)
	finally:
		updated_json = {STORYNAME: next_chapter_to_process}
		modify_json_file(os.path.join(rootDir, "next-translation.json"), updated_json)

@app.command(help="List all English and Chinese stories")
def list():
	"""
	List all stories. English and Chinese. 
	"""
	# initialize_directories()
	# initialize_files()

	story_list_file = os.path.join(rootDir, "ch_storylist.txt")
	with open(story_list_file, "r", encoding="utf-8") as file:
		print("Chinese stories:")
		print(file.read())
		

	print("=======================")

	story_list_file = os.path.join(rootDir, "en_storylist.txt")
	with open(story_list_file, "r", encoding="utf-8") as file:
		print("English stories:")
		print(file.read())  


@app.command(help="Scrape chapters from the provided URL, by either using 'next' button. Use a chapter page in the story, not the story directory.")
def scrape():
	initialize_directories()
	initialize_files()

	current_chapter_number = int(input("Current chapter number: "))
	story_name= str(input("Story name: "))

	output_folder = sanitize_folder_name(story_name)
	url_to_scrape= str(input("URL of the chapter: "))
	content= str(input("A part of the content of the chapter (copy a small part of the content): "))
	link_text= str(input("The text on the button leading to the next chapter (multiple = separated by space):"))
	isChineseChoice = str(input("Is the story Chinese? (y/n): ")).lower()
	if isChineseChoice == "y": isChinese = True
	else: isChinese = False

	if isChinese:
		full_dir = os.path.join(rootDir, "input", "chinese", output_folder)
		story_list_file = os.path.join(rootDir, "ch_storylist.txt")
	else:
		full_dir = os.path.join(rootDir, "input", "english", output_folder)
		story_list_file = os.path.join(rootDir, "en_storylist.txt")
	os.makedirs(full_dir, exist_ok=True)
	

	append_and_clean(story_list_file, story_name)


	modify_json_file(
		file_path= os.path.join(rootDir,"next-translation.json"),
		appendJson={
			story_name : 1
		}
	)

	def access_website_with_selenium():
		driver = create_selenium_driver()
		try:
			driver.get(url_to_scrape)
			soup = BeautifulSoup(driver.page_source, "html.parser")
			content_class, content_id = find_divs_with_text(soup, content)
			scrape_webpage(driver, 
				  url_to_scrape, 
				  link_text, 
				  content_class, 
				  content_id, 
				  full_dir, 
				  current_chapter_number)
		finally:
			driver.quit()

	access_website_with_selenium()


@app.command(help="Replace Chinese names with English names to maintain name coherence.")
def replaceNames():
	"""
	Replace Chinese names with English names to maintain name coherence
	"""
	initialize_directories()
	initialize_files()

	chineseInputFolder = os.path.join(rootDir, "input", "chinese")    

	def return_folder():
		print("Choose the folder using the number")
		listFolder = os.listdir(chineseInputFolder)

		for i, story in enumerate(listFolder, 1):
			print(f"{i}: {story}")
		return listFolder[int(input(":"))-1]

	folderChoice = return_folder()
	print("Selected:", folderChoice)
	fromChapter = int(input("From Chapter: "))
	toChapter = int(input("To Chapter: "))

	useGPT = str(input("Use GPT? (y/n): ")).lower()
	if useGPT == "y": 
		isGPT = True 
		client = OpenAI(api_key= api_data['openAI'])
		model = "gpt-4o"
	else: 
		isGPT = False
		client = anthropic.Anthropic(api_key=api_data['Anthropic'])
		model = "claude-3-5-sonnet-20240620"

	finalNameList = []


	extraction_prompt = """
# Mission
Extract all names of organisations and characters from the text and list them.

# Expected Input
A text containing a story.

# Expected Output
Only output the names, separated by a newline.""".strip()
	try:
		
		
		
		for chapter in range(fromChapter, toChapter + 1):
			currentChapterStr = str(chapter)

			potentialNames = [f"{currentChapterStr.zfill(i)}.txt" for i in range(0, 6)]
			chapterFileDir = None
			for file_name in potentialNames:
				file_path = os.path.join(rootDir, "input", "chinese", file_name)
				if os.path.isfile(file_path):
					chapterFileDir = file_path
					break

			
			with open(chapterFileDir, "r", encoding="utf-8") as content_file:
				content = content_file.read()
				content = content.replace("\n\n", "\n")
				content = content.replace("\n\n", "\n")

			namelist = submit_to_AI(
				client,
				isGPT,
				model,
				extraction_prompt,
				content,
				"Extracting..."
			).split("\n")

			for line in namelist:
				chinese_extracted = extract_chinese(line)
				finalNameList.extend([name for name in chinese_extracted if len(name) >= 2])

	except Exception as e:
		print("Error!")
		print(e)
	finally:
		finalNameList = sorting(list(set(finalNameList)))

		print("Completed list processing. Eliminating unnecessary names. Please wait")
		
		context = str(input("Context:"))
		gpt_namelist_dict, pip_namelist_dict = name_translation_aid(client, isGPT, finalNameList, context)

		print(f"Be prepared for: {len(pip_namelist_dict)} names (BRUH)")


		replace_name_list = []
		try:
			for counter, name in enumerate(pip_namelist_dict, 1):
				gpt_name = gpt_namelist_dict.get(name, "GPT Translation encountered an error/missing this name")
				english_name = input(f"""
==============================================
{counter}. 
Replace {name} with? (empty = no replace)
Suggestions:
ChatGPT Direct Translate: {gpt_name}
Translate directly: {pip_namelist_dict[name]}
==============================================
				""".strip())
				if english_name:
					replace_name_list.append([name, english_name])
					
		except Exception as e:
			print(e)
		finally:
			for [name, english_name] in replace_name_list:
				replace_string_in_files(
					directory= os.path.join(rootDir, "input", "chinese"),
					old_string= name,
					new_string= english_name
				)

@app.command(help="Setup the directories and files. Nothing else")
def setup():
	initialize_directories()
	initialize_files()

if __name__ == "__main__":
	app()
