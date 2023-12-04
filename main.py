import argparse, \
       re, \
       yaml

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from openai import OpenAI



def read_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    return config


def split_html_by_sentence(html_str, max_chunk_size=2000):
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
    p  = "You are an %s-to-%s translator. " % (from_lang, to_lang)
    p += "Keep all special characters and HTML tags as in the source text. Return only %s translation." % to_lang
    return p


def translate_chunk(client, text, from_lang='EN', to_lang='PL'):
    response = client.chat.completions.create(
        model='gpt-4-1106-preview',
        temperature=0.2,
        messages=[
            { 'role': 'system', 'content': system_prompt(from_lang, to_lang) },
            { 'role': 'user', 'content': text },
        ]
    )

    translated_text = response.choices[0].message.content
    return translated_text


def translate_text(client, text, from_lang='EN', to_lang='PL'):
    translated_chunks = []
    chunks = split_html_by_sentence(text)

    for i, chunk in enumerate(chunks):
        print("\tTranslating chunk %d/%d..." % (i+1, len(chunks)))
        translated_chunks.append(translate_chunk(client, chunk, from_lang, to_lang))

    return ' '.join(translated_chunks)


def translate(client, input_epub_path, output_epub_path, from_chapter=0, to_chapter=9999, from_lang='EN', to_lang='PL'):
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



if __name__ == "__main__":
    # Create the top-level parser
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
        openai_client = OpenAI(api_key=config['openai']['api_key'])

        translate(openai_client, args.input, args.output, from_chapter, to_chapter, from_lang, to_lang)

    elif args.mode == 'show-chapters':
        show_chapters(args.input)

    else:
        parser.print_help()
