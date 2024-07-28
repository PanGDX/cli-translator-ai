import pyautogui
import time
import os
import json
import threading
import keyboard
from utility import (load_json,
					modify_json_file,  
					sanitize_folder_name,
					open_patreon,
					open_inkstone_and_choose_story,
					load_inkstone,
					loop_for_webnovel_submission,
					loop_for_patreon_submission)

rootDir = os.path.expanduser("~/cli-tool/")
language_identifier = load_json(os.path.join(rootDir,"Story Language Identifier.json"))
inkstone_procedure_json = load_json(os.path.join(rootDir,"Inkstone Story Selection.json"))
patreon_procedure_json = load_json(os.path.join(rootDir,"Patreon Story Selection.json"))
inkstone_next_chapter_json = load_json(os.path.join(rootDir,"Inkstone Next Upload.json"))
patreon_next_chapter_json = load_json(os.path.join(rootDir,"Patreon Next Upload.json"))






def get_story_folder_path(story_name):

	language = language_identifier[story_name]

	if language == "English":    
		folderDir = os.path.join(rootDir,
						"output-text",
						"english",
							sanitize_folder_name(story_name))
	else:
		folderDir = os.path.join(rootDir,
						"output-text",
						"chinese",
							sanitize_folder_name(story_name))
		
	
	print("Language: " + language)
	print("Folder DIR: " + folderDir)
	return folderDir





def submit_chapters(story_name, chapters, platform, next_chapter_json, procedure_json):
    current_chapter_in_folder = next_chapter_json[story_name]["Chapter"]
    current_chapter_online = current_chapter_in_folder + next_chapter_json[story_name]["Append"]
    story_folder = get_story_folder_path(story_name)
    counter = 0

    try:
        for i in range(chapters):
            story_file_dir = os.path.join(story_folder, f"{current_chapter_in_folder + i}.txt")
            
            with open(story_file_dir, "r", encoding="utf-8") as file:
                content = file.read().strip().replace("\n\n", "\n")
                
                title = f"Chapter {current_chapter_online + i}"
                if platform == "patreon":
                    title = f"{story_name} - " + title
                    loop_for_patreon_submission(title, content, procedure_json[story_name])
                elif platform == "inkstone":
                    
                    output_content = ("Future chapters at patreon.com/FFAddict. "
                                    "Additionally, I have many new works readers may be interested in. "
                                    "Go look! Thanks!\n\n") + content
                    loop_for_webnovel_submission(title, output_content)

            counter+=1
    except:
        print("There was an error. File not found most likely")
        print(f"Stopping and updating json to be: {current_chapter_in_folder + counter} for {story_name}")
    finally:
        updated_json = {story_name: {"Chapter": current_chapter_in_folder + counter}}
        json_file_path = os.path.join(rootDir, f"{platform.capitalize()} Next Upload.json")
        modify_json_file(json_file_path, updated_json)

def main_process():
    submission_type = int(input("Custom submit (1). All submit (2): "))

    if submission_type == 1:
        for i,name in enumerate(patreon_next_chapter_json.keys(), 1):
            print(f"{i}. {name}")
        
        story_names = list(patreon_next_chapter_json.keys())
        story_name = story_names[int(input("Choose number: ")) - 1]
        print(f"Selected: {story_name}")
    else:
        story_names = list(patreon_next_chapter_json.keys())

    chapters = int(input("How many chapters: "))
    submit_to_patreon = input("Submit to Patreon (y/n): ").lower() == 'y'
    submit_to_inkstone = input("Submit to Inkstone (y/n): ").lower() == 'y'

    print("Go To Firefox")
    time.sleep(5)

    if submit_to_patreon:
        open_patreon()
        stories_to_submit = [story_name] if submission_type == 1 else story_names
        for story in stories_to_submit:
            submit_chapters(story, chapters, "patreon", patreon_next_chapter_json, patreon_procedure_json)

    if submit_to_inkstone:
        load_inkstone()
        stories_to_submit = [story_name] if submission_type == 1 else story_names
        for story in stories_to_submit:
            open_inkstone_and_choose_story(inkstone_procedure_json[story])
            submit_chapters(story, chapters, "inkstone", inkstone_next_chapter_json, inkstone_procedure_json)



def check_for_exit():
	while True:
		if keyboard.is_pressed('ctrl+c'):  # Detect CTRL-C key press
			print("CTRL-C pressed. Exiting...")
			os._exit(1)  # Forcefully exit the program


if __name__ == "__main__":
	exit_thread = threading.Thread(target=check_for_exit, daemon=True)
	exit_thread.start()

	main_process()
