from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
from webdriver_manager.firefox import GeckoDriverManager


def formatting(url, next_link):
    if "http" in next_link:
        return next_link
    else:
        bracket_position = url.find("/", url.find("//") + 2)
        return url[:bracket_position] + next_link

def append_to_file(file_path, content, counter):
    with open(f"{file_path}/{counter}.txt", "w", encoding="utf-8") as file:
        file.write(content)
    return counter + 1

def find_divs_with_text(soup, search_text):
    search_text = search_text.strip()
    divs = soup.find_all(lambda tag: tag.name == "div" and search_text in tag.text)
    for div in divs:
        tag_class = " ".join(div.get("class", []))
        tag_id = div.get("id", "")
        return tag_class, tag_id
    return "", ""

def get_link(soup, link_text):
    text = link_text.lower().split(" ")
    for search_text in text:
        if search_text:
            for counter in range(5):
                matched_tags = soup.find_all(lambda tag: len(tag.find_all()) == counter and search_text in tag.text.lower())
                for tag in matched_tags:
                    if tag.name == "a":
                        return tag.get("href")
    links = soup.find_all("a" ,href=True)
    for link in links:
        return link['href']
    raise ValueError("Failed to fetch the link with the given class names or link text. Possibly due to the end")

def create_selenium_driver():
    options = Options()
    options.add_argument("--headless")
    service = Service(executable_path=GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)

def scrape_webpage(driver, url, link_text, content_class, content_id, full_dir, counter):
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        result = "\n".join([content.get_text(separator="\n") for content in soup.find_all("div", class_=content_class, id=content_id)])
        counter = append_to_file(full_dir, result, counter)
        next_link = get_link(soup, link_text)
        if next_link:
            print(f"Navigating to the next link: {next_link}")
            scrape_webpage(driver, formatting(url, next_link), link_text, content_class, content_id, full_dir, counter)
        else:
            print("No next link found, or there was an error fetching it.")
    except Exception as e:
        print(f"An error occurred: {e}")