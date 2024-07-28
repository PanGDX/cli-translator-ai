import os,json, pyperclip, pyautogui, re, time



def load_json(file_path):
    if file_path and not file_path.endswith(".json"):
        file_path += ".json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

def split_paragraph(text):
	midpoint = len(text) // 2
	closest_newline = text.find('\n', midpoint)

	if closest_newline == -1:
		# If no newline character is found, search backwards from the midpoint.
		closest_newline = text.rfind('\n', 0, midpoint)
		if closest_newline == -1:
			# If still no newline character, split at the midpoint.
			closest_newline = midpoint

	part1 = text[:closest_newline].strip()
	part2 = text[closest_newline:].strip()

	return part1, part2


def deep_merge(source, update):
    for key, value in update.items():
        if isinstance(value, dict):
            source[key] = deep_merge(source.get(key, {}), value)
        else:
            source[key] = value
    return source

def modify_json_file(file_path, append_json):
    """
    @param file_path: full directory
    @param append_json: json to merge
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    merged_data = deep_merge(data, append_json)
    
    with open(file_path, 'w') as file:
        json.dump(merged_data, file, indent=4)


def submit_to_AI(client, isGPT: bool, model:str, system_message, user_message, log:str = ""):
    if isGPT:
        completion = client.chat.completions.create(
            model=model,
            max_tokens = 4095,
            messages=[{"role": "system", "content": system_message}, 
                      {"role": "user", "content": user_message}
                      ],
        )
        if(log!=""): print(log)

        return completion.choices[0].message.content
    else:
        message = client.messages.create(
            model=model,
            max_tokens=4095,
            system=system_message,
            messages=[
                {"role": "user", "content": user_message} 
            ]
        )
        if(log!=""): print(log)
        return message.content[0].text
    

def sanitize_folder_name(folder_name):
    """
    Takes a string and makes it a valid folder name by removing or replacing invalid characters.

    Parameters:
    folder_name (str): The input string to be sanitized.

    Returns:
    str: A sanitized string that can be used as a folder name.
    """
    # Define a list of characters that are not allowed in folder names
    invalid_characters = r'<>:"/\|?*'
    
    # Replace invalid characters with an underscore
    sanitized_name = re.sub(f'[{re.escape(invalid_characters)}]', '_', folder_name)
    
    # Remove leading and trailing whitespace and dots
    sanitized_name = sanitized_name.strip().strip('.')

    return sanitized_name


def replace_string_in_files(directory, old_string, new_string):
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_contents = file.read()

            file_contents = file_contents.replace(old_string,new_string)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(file_contents)
    print(f"Replaced: {old_string} --> {new_string}")



def append_and_clean(file_path, text):
    # Read the existing content of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Filter out any empty lines
    lines = [line for line in lines if line.strip()]

    # Append the new text
    lines.append(text + '\n')

    # Write the cleaned lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)












def count_words(string):
    words = string.split()
    print(len(words))


def copy_paste(text: str):
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')

    
def loop_for_patreon_submission(title: str, content: str, procedure: dict):
    scroll_clicks = procedure["Scroll"]
    pos_X = procedure["PositionX"]
    pos_Y = procedure["PositionY"]

    pyautogui.click(x=144, y=804)  # go to create and press it
    time.sleep(5)
    pyautogui.click(x=804, y=456)  # go to text
    time.sleep(10)

    pyautogui.click(x=1482, y=464)  # go to select and press
    time.sleep(0.5)

    pyautogui.moveTo(1538, 567)  # move to categories checkboxes
    time.sleep(0.5)

    pyautogui.scroll(clicks=scroll_clicks)
    pyautogui.scroll(clicks=scroll_clicks)
    time.sleep(1)

    pyautogui.click(x=pos_X, y=pos_Y)  # click on the box
    time.sleep(0.5)

    pyautogui.click(x=612, y=336)  # title press
    time.sleep(1)
    copy_paste(title)
    time.sleep(1)

    pyautogui.click(x=607, y=403)  # go to textbox
    time.sleep(1)
    copy_paste(content)
    time.sleep(1)

    pyautogui.click(1834, 975)  # next
    time.sleep(2)
    pyautogui.click(1834, 975)  # submit
    time.sleep(10)

    pyautogui.click(x=136, y=814)  # click to close submit button
    time.sleep(1)


def loop_for_webnovel_submission(title: str, content: str):
    pyautogui.click(1706, 187)  # create
    time.sleep(5)

    pyautogui.click(642, 400)  # title
    copy_paste(title)
    time.sleep(1)

    pyautogui.click(656, 489)  # textbox
    copy_paste(content)
    time.sleep(1)

    pyautogui.click(1769, 188)  # publish
    time.sleep(5)

    pyautogui.click(1216, 950)  # confirm
    time.sleep(5)
    
	# returns to story page


def load_inkstone():
    pyautogui.click(425, 111)
    copy_paste("https://inkstone.webnovel.com/novels/list?story=1")
    pyautogui.press('enter')
    time.sleep(10)


def open_inkstone_and_choose_story(procedure: dict):
    scroll_clicks = procedure["Scroll"]
    pos_X = procedure["PositionX"]
    pos_Y = procedure["PositionY"]

    pyautogui.click(425, 111)
    copy_paste("https://inkstone.webnovel.com/novels/list?story=1")
    pyautogui.press('enter')
    time.sleep(5)

    pyautogui.click(888, 502)
    time.sleep(0.5)

    pyautogui.scroll(scroll_clicks)
    pyautogui.scroll(clicks=scroll_clicks)
    time.sleep(1)

    pyautogui.click(pos_X, pos_Y) # access story page
    time.sleep(5)


def open_patreon():
    pyautogui.click(425, 111)
    copy_paste("https://www.patreon.com/FFAddict")
    pyautogui.press('enter')
    time.sleep(5)