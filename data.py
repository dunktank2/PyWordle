import http.client
import json
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import os
from datetime import datetime


def fetch_past_wordle_answers():
    # URL of the webpage containing the list of past Wordle answers
    html_content = get_html_content('https://www.rockpapershotgun.com/wordle-past-answers')
    soup = BeautifulSoup(html_content, 'html.parser')

    # Adjust the selector here based on the actual webpage structure
    words = []
    for item in soup.select('.inline > li'):
        words.append(item.get_text().strip().lower())

    return words

def fetch_word_list():
    """
    Fetch only the list of possible Wordle answers from NYT's website.
    Returns a list of answer words.
    """
    url = 'https://www.nytimes.com/games/wordle/index.html'
    answer1 = 'cigar'  # Known answer to look for

    try:
        # Get the main page content
        html_content = get_html_content(url).decode('utf-8')
        js_files = re.findall(r'<script[^>]+src="([^"]+\.js)"', html_content)
        pattern = rf'\[((?:"[a-z]{{5}}",)*?"{answer1}"(?:,"[a-z]{{5}}")+)\]'

        for js_path in js_files:
            if not js_path.startswith('http'):
                js_path = f'https://www.nytimes.com{js_path}'

            try:
                js_content = get_html_content(js_path).decode('utf-8')
                matches = re.findall(pattern, js_content)

                if matches:
                    words_str = matches[0]
                    # Split into list and remove quotes
                    word_list = [w.strip('"') for w in words_str.split(',')]

                    # Find the index of the known answer
                    try:
                        cigar_index = word_list.index('cigar')
                        # Only keep words from 'cigar' onwards - these are the answers
                        answers = word_list[cigar_index:]
                        # Filter out any invalid words
                        valid_answers = [word for word in answers if len(word) == 5 and word.isalpha()]
                        return sorted(valid_answers)
                    except ValueError:
                        print("Could not find 'cigar' in word list")
                        continue

            except Exception as e:
                print(f"Failed to process JS file {js_path}: {str(e)}")
                continue

        raise Exception("Could not find word list in any JavaScript file")

    except Exception as e:
        print(f"Warning: Failed to fetch word list from NYT: {str(e)}")
        raise

def get_html_content(url):
    # Parse the URL
    parsed_url = urlparse(url)
    conn = http.client.HTTPSConnection(parsed_url.netloc)

    # Perform the GET request
    conn.request("GET", parsed_url.path)
    response = conn.getresponse()

    if response.status != 200:
        raise Exception(f"Failed to fetch data. HTTP status code: {response.status}")

    # Read, parse, and return the HTML content
    return response.read()


def save_words_to_file(words, file_path):
    with open(file_path, 'w') as file:
        for word in words:
            file.write(f"{word}\n")


def load_word_list(file_path):
    """
    Load a word list from a file.
    """
    with open(file_path, 'r') as file:
        words = file.read().splitlines()
    return words

def update_used_words_if_needed(file_path):
    if os.path.exists(file_path):
        last_modified_date = datetime.fromtimestamp(os.path.getmtime(file_path)).date()
        today = datetime.today().date()
        if last_modified_date == today:
            return  # File is already updated today
    past_words = fetch_past_wordle_answers()
    save_words_to_file(past_words, file_path)

def update_word_list_if_needed(file_path):
    if os.path.exists(file_path):
        last_modified_date = datetime.fromtimestamp(os.path.getmtime(file_path)).date()
        if last_modified_date == datetime.today().date():
            return # File is already updated today
    word_list = fetch_word_list()
    save_words_to_file(word_list, file_path)