import argparse
import re
import yaml
import json
import time
from pathlib import Path
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from openai import OpenAI


def read_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def split_html_by_sentence(html_str, max_chunk_size=20000):
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
    p = f"You are an expert {from_lang}-to-{to_lang} translator. "
    p += f"You are currently translating a chunk from the book 'Difficult Conversations' by Douglas Stone. "
    p += "Maintain the original tone and style of the book while ensuring accuracy in translation. "
    p += "Preserve all special characters and HTML tags as they appear in the source text. "
    p += f"Provide only the {to_lang} translation, without any additional comments or explanations."
    return p


def translate_chunk(client, text, from_lang='EN', to_lang='BG', max_retries=3, retry_delay=180, model=None):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0.2,
                messages=[
                    {'role': 'system', 'content': system_prompt(from_lang, to_lang)},
                    {'role': 'user', 'content': text},
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            if "rate limit" in str(e).lower():
                if attempt < max_retries - 1:
                    print(f"Rate limit hit. Waiting {retry_delay} seconds before retry {attempt + 1}/{max_retries}")
                    time.sleep(retry_delay)
                    continue
            raise


def save_progress(progress_file, chapter, chunk_index, total_chunks):
    with open(progress_file, 'w') as f:
        json.dump({
            'chapter': chapter,
            'chunk_index': chunk_index,
            'total_chunks': total_chunks,
            'timestamp': time.time()
        }, f)


def load_progress(progress_file):
    if Path(progress_file).exists():
        with open(progress_file, 'r') as f:
            return json.load(f)
    return None


def translate_text(client, text, from_lang='English', to_lang='Bulgarian', progress_file=None, chapter=None, model=None):
    translated_chunks = []
    chunks = split_html_by_sentence(text)
    
    # Load progress if available
    start_chunk = 0
    if progress_file and chapter is not None:
        progress = load_progress(progress_file)
        if progress and progress['chapter'] == chapter:
            start_chunk = progress['chunk_index']
            translated_chunks = [''] * start_chunk  # Placeholder for already translated chunks

    for i, chunk in enumerate(chunks[start_chunk:], start=start_chunk):
        print(f"\tTranslating chunk {i + 1}/{len(chunks)}...")
        try:
            translated_chunk = translate_chunk(client, chunk, from_lang, to_lang, model=model)
            translated_chunks.append(translated_chunk)
            
            if progress_file and chapter is not None:
                save_progress(progress_file, chapter, i + 1, len(chunks))
                
        except Exception as e:
            print(f"Error translating chunk {i + 1}: {str(e)}")
            raise

    return ' '.join(translated_chunks)


def translate(client, input_epub_path, output_epub_path, from_chapter=0, to_chapter=9999, from_lang='EN', to_lang='PL', progress_file=None, model=None):
    book = epub.read_epub(input_epub_path)
    
    if progress_file is None:
        progress_file = f"{output_epub_path}.progress"
    
    current_chapter = 1
    chapters_count = len([i for i in book.get_items() if i.get_type() == ebooklib.ITEM_DOCUMENT])

    try:
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                if from_chapter <= current_chapter <= to_chapter:
                    print("Processing chapter %d/%d..." % (current_chapter, chapters_count))
                    soup = BeautifulSoup(item.content, 'html.parser')
                    translated_text = translate_text(client, str(soup), from_lang, to_lang, progress_file, current_chapter, model=model)
                    item.content = translated_text.encode('utf-8')
                    
                    # Save intermediate progress after each chapter
                    epub.write_epub(f"{output_epub_path}.partial", book, {})

                current_chapter += 1

        # Clean up progress file and write final epub
        if Path(progress_file).exists():
            Path(progress_file).unlink()
        if Path(f"{output_epub_path}.partial").exists():
            Path(f"{output_epub_path}.partial").unlink()
            
        epub.write_epub(output_epub_path, book, {})
        
    except Exception as e:
        print(f"Translation interrupted: {str(e)}")
        print(f"Progress saved. You can resume from chapter {current_chapter} using --from-chapter {current_chapter}")
        # Keep the progress file and partial epub in case of error
        raise


def show_chapters(input_epub_path):
    book = epub.read_epub(input_epub_path)

    current_chapter = 1
    chapters_count = len([i for i in book.get_items() if i.get_type() == ebooklib.ITEM_DOCUMENT])
    total_characters = 0

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapter_length = len(item.content)
            total_characters += chapter_length
            print(f"▶️  Chapter {current_chapter}/{chapters_count} ({chapter_length} characters)")
            soup = BeautifulSoup(item.content, 'html.parser')
            chapter_beginning = soup.text[:250]
            chapter_beginning = re.sub(r'\n{2,}', '\n', chapter_beginning)
            print(f"{chapter_beginning}\n\n")

            current_chapter += 1

    print(f"Total characters in the book: {total_characters}")


def initialize_llm_client(api_key, base_url):
    """
    Initialize the OpenAI client with GEMINI base URL.
    """
    print ('api key', api_key)
    print ('base_url', base_url)
    return OpenAI(api_key=api_key) if base_url is None else OpenAI(api_key=api_key, base_url=base_url)


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
    parser_translate.add_argument('--progress-file', help='File to save translation progress.')
    parser_translate.add_argument('--llm-provider', choices=['openai', 'gemini'], required=True, help='LLM provider to use for translation.')

    # Create the parser for the "show-chapters" mode
    parser_show = subparsers.add_parser('show-chapters', help='Show the list of chapters.')
    parser_show.add_argument('--input', required=True, help='Input file path.')

    # Parse the arguments
    args = parser.parse_args()

    if args.mode == 'translate':
        config = read_config(args.config)
        from_chapter = int(args.from_chapter or 0)
        to_chapter = int(args.to_chapter or 9999)
        from_lang = args.from_lang
        to_lang = args.to_lang

        if args.llm_provider == 'openai':
            api_key = config['openai']['api_key']
            base_url = None
            model = 'gpt-4o'
        else:  # gemini
            api_key = config['gemini']['api_key']
            base_url = config['gemini'].get('base_url', 'https://generativelanguage.googleapis.com/v1beta/')
            model = 'gemini-2.0-flash-exp'
        
        llm_client = initialize_llm_client(api_key=api_key, base_url=base_url)

        # Perform translation
        translate(llm_client, args.input, args.output, from_chapter, to_chapter, from_lang, to_lang, args.progress_file, model=model)

    elif args.mode == 'show-chapters':
        show_chapters(args.input)

    else:
        parser.print_help()
