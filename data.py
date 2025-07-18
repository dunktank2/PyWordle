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
