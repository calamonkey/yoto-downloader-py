import requests
import os
import json
import sys

output_dir = '/path/to/save/location'

scriptContentStart = '<script id="__NEXT_DATA__" type="application/json">'
scriptContentEnd = '</script>'

cardTitleStart = 'class="card-title">'
cardTitleEnd = '</h1>'

cardAuthorStart = 'class="card-author"><b>'
cardAuthorEnd = '</b></div>'

file_format = {
    'opus': 'ogg',
    'aac': 'ogg'
}

def fetch_and_parse_chapters_v1(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    base_script = response.text[response.text.find(scriptContentStart) + len(scriptContentStart):]
    base_script = json.loads(base_script[:base_script.find(scriptContentEnd)])
    card_title = response.text[response.text.find(cardTitleStart) + len(cardTitleStart):]
    card_title = card_title[:card_title.find(cardTitleEnd)].strip()
    sanitized_title = "".join(c for c in card_title if c.isalnum() or c in (' ', '_', '-')).rstrip()
    card_author = response.text[response.text.find(cardAuthorStart) + len(cardAuthorStart):]
    card_author = card_author[:card_author.find(cardAuthorEnd)].strip()
    chapters = base_script['props']['pageProps']['card']['content']['chapters']
    return {
        'chapters' : chapters,
        'title': sanitized_title,
        'author': card_author
    }

def download_chapter_audio(chapter, card_title, author, output_dir):
    tracks = chapter['tracks']
    for track in tracks:
        if track['type'] == 'audio':
            audio_url = track['trackUrl']
            audio_response = requests.get(audio_url, stream=True)
            audio_response.raise_for_status()
            chapter_title = track['title']
            chapter_number = track['key']
            sanitized_title = "".join(c for c in chapter_title if c.isalnum() or c in (' ', '_', '-')).rstrip()
            file_path = os.path.join(output_dir, author, card_title, f"{chapter_number}-{sanitized_title}.{file_format[track['format']]}")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as audio_file:
                for chunk in audio_response.iter_content(chunk_size=8192):
                    audio_file.write(chunk)
            print(f"Downloaded: {file_path}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else ''
    author = sys.argv[2] if len(sys.argv) > 2 else ''
    if not url:
        print("Please provide a URL as a command-line argument.")
        sys.exit(1)
    book_data = fetch_and_parse_chapters_v1(url)
    if len(book_data['author']) < 50 and not author:
        author = book_data['author']
    if not author:
        print("Please provide an author name as a command-line argument or ensure it's available in the data.")
        sys.exit(1)
    for chapter in book_data['chapters']:
        download_chapter_audio(chapter, book_data['title'], author, output_dir)

