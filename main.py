import argparse
import os
import re
import sys
import warnings

import ebooklib
import yaml
from bs4 import BeautifulSoup
from ebooklib import epub
from openai import OpenAI

warnings.filterwarnings('ignore', category=UserWarning, module='ebooklib.epub')
warnings.filterwarnings('ignore', category=FutureWarning, module='ebooklib.epub')


def read_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    return config


def split_html_by_sentence(html_str, max_chunk_size=10000):
    sentences = html_str.split('. ')

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_chunk_size:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            current_chunk += '. '
            current_chunk += sentence

    if current_chunk:
        chunks.append(current_chunk)

    # Remove dot from the beginning of first chunk
    chunks[0] = chunks[0][2:]

    # Add dot to the end of each chunk
    for i in range(len(chunks)):
        chunks[i] += '.'

    return chunks


def system_prompt(from_lang, to_lang):
    p = "You are an %s-to-%s translator. " % (from_lang, to_lang)
    p += "Keep all special characters and HTML tags as in the source text. Return only %s translation." % to_lang
    return p


def translate_chunk(client, text, from_lang, to_lang):
    response = client.chat.completions.create(
        model='gpt-4o-2024-11-20',
        temperature=0.2,
        messages=[
            {'role': 'system', 'content': system_prompt(from_lang, to_lang)},
            {'role': 'user', 'content': text},
        ]
    )

    translated_text = response.choices[0].message.content
    return translated_text


def translate_text(client, text, from_lang, to_lang):
    translated_chunks = []
    chunks = split_html_by_sentence(text)

    for i, chunk in enumerate(chunks):
        print("\tTranslating chunk %d/%d..." % (i + 1, len(chunks)))
        translated_chunks.append(translate_chunk(client, chunk, from_lang, to_lang))

    return ' '.join(translated_chunks)


def translate(client, input_epub_path, output_epub_path, from_lang, to_lang, from_chapter=0, to_chapter=9999):
    book = epub.read_epub(input_epub_path)

    current_chapter = 1
    chapters_count = len([i for i in book.get_items() if i.get_type() == ebooklib.ITEM_DOCUMENT])

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            if current_chapter >= from_chapter and current_chapter <= to_chapter:
                print("Processing chapter %d/%d..." % (current_chapter, chapters_count))
                soup = BeautifulSoup(item.content, 'html.parser')
                translated_text = translate_text(client, str(soup), from_lang, to_lang)
                item.content = translated_text.encode('utf-8')

            current_chapter += 1

    epub.write_epub(output_epub_path, book, {})


def show_chapters(input_epub_path):
    book = epub.read_epub(input_epub_path)

    current_chapter = 1
    chapters_count = len([i for i in book.get_items() if i.get_type() == ebooklib.ITEM_DOCUMENT])

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            print("▶️  Chapter %d/%d (%d characters)" % (current_chapter, chapters_count, len(item.content)))
            soup = BeautifulSoup(item.content, 'html.parser')
            chapter_beginning = soup.text[0:250]
            chapter_beginning = re.sub(r'\n{2,}', '\n', chapter_beginning)
            print(chapter_beginning + "\n\n")

            current_chapter += 1


def interactive_mode():
    print("\n📚 Welcome to Book Translator!")
    print("\nWhat would you like to do?")
    print("1. Translate a book")
    print("2. Show chapters")
    print("3. Exit")

    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice in ['1', '2', '3']:
            break
        print("Invalid choice. Please enter 1, 2, or 3.")

    if choice == '3':
        print("\nGoodbye! 👋")
        return

    while True:
        input_path = input("\nEnter the path to your book (epub format): ").strip()
        if os.path.exists(input_path) and input_path.lower().endswith('.epub'):
            break
        print("❌ File not found or not an epub file. Please try again.")

    if choice == '2':
        show_chapters(input_path)
        return

    # For translation mode
    while True:
        config_path = input("\nEnter the path to config.yaml: ").strip()
        if os.path.exists(config_path):
            break
        print("❌ Config file not found. Please try again.")

    output_path = input("\nEnter the output path for translated book: ").strip()

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    print("\nAvailable languages:")
    print("EN - English")
    print("RU - Russian")
    print("FR - French")
    print("ES - Spanish")
    print("DE - German")
    # Add other language

    while True:
        from_lang = input("\nEnter source language code (e.g., EN): ").strip().upper()
        if len(from_lang) == 2:
            break
        print("❌ Invalid language code. Please enter a 2-letter code.")

    while True:
        to_lang = input("\nEnter target language code (e.g., RU): ").strip().upper()
        if len(to_lang) == 2:
            break
        print("❌ Invalid language code. Please enter a 2-letter code.")

    # Show chapters and ask for range
    print("\nShowing chapters of your book:")
    show_chapters(input_path)

    chapters_count = len(
        [i for i in epub.read_epub(input_path).get_items()
         if i.get_type() == ebooklib.ITEM_DOCUMENT])

    while True:
        try:
            from_chapter = input(f"\nEnter starting chapter (1-{chapters_count}, or press Enter for all): ").strip()
            if from_chapter == "":
                from_chapter = 1
            else:
                from_chapter = int(from_chapter)
                if not (1 <= from_chapter <= chapters_count):
                    raise ValueError()
            break
        except ValueError:
            print("❌ Invalid chapter number. Please try again.")

    while True:
        try:
            to_chapter = input(
                f"Enter ending chapter ({from_chapter}-{chapters_count}, or press Enter for all): ").strip()
            if to_chapter == "":
                to_chapter = chapters_count
            else:
                to_chapter = int(to_chapter)
                if not (from_chapter <= to_chapter <= chapters_count):
                    raise ValueError()
            break
        except ValueError:
            print("❌ Invalid chapter number. Please try again.")

    # Start translation
    config = read_config(config_path)
    try:
        # New version library
        openai_client = OpenAI(
            api_key=config['openai']['api_key']
        )
    except TypeError:
        # The old version of the library
        openai_client = OpenAI(
            api_key=config['openai']['api_key'],
            base_url="https://api.openai.com/v1"
        )

    print("\n🚀 Starting translation...")
    translate(openai_client, input_path, output_path, from_lang, to_lang, from_chapter, to_chapter)
    print("\n✅ Translation completed!")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        parser = argparse.ArgumentParser(description='App to translate or show chapters of a book.')
        subparsers = parser.add_subparsers(dest='mode', help='Mode of operation.')

        # Create the parser for the "translate" mode
        parser_translate = subparsers.add_parser('translate', help='Translate a book.')
        parser_translate.add_argument('--input', required=True, help='Input file path.')
        parser_translate.add_argument('--output', required=True, help='Output file path.')
        parser_translate.add_argument('--config', required=True, help='Configuration file path.')
        parser_translate.add_argument('--from-chapter', type=int, help='Starting chapter for translation.')
        parser_translate.add_argument('--to-chapter', type=int, help='Ending chapter for translation.')
        parser_translate.add_argument('--from-lang', help='Source language.', default='EN')
        parser_translate.add_argument('--to-lang', help='Target language.', default='PL')

        # Create the parser for the "show-chapters" mode
        parser_show = subparsers.add_parser('show-chapters', help='Show the list of chapters.')
        parser_show.add_argument('--input', required=True, help='Input file path.')

        # Parse the arguments
        args = parser.parse_args()

        # Call the appropriate function based on the mode
        if args.mode == 'translate':
            config = read_config(args.config)
            from_chapter = int(args.from_chapter)
            to_chapter = int(args.to_chapter)
            from_lang = args.from_lang
            to_lang = args.to_lang
            try:
                # New version library
                openai_client = OpenAI(
                    api_key=config['openai']['api_key']
                )
            except TypeError:
                # The old version of the library
                openai_client = OpenAI(
                    api_key=config['openai']['api_key'],
                    base_url="https://api.openai.com/v1"
                )

            translate(openai_client, args.input, args.output, from_lang, to_lang, from_chapter, to_chapter)

        elif args.mode == 'show-chapters':
            show_chapters(args.input)

        else:
            parser.print_help()
