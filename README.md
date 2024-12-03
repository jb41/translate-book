# Translate books with GPT

This project harnesses the power of GPT-4 LLM to translate eBooks from any language into your preferred language, maintaining the integrity and structure of the original content. Imagine having access to a vast world of literature, regardless of the original language, right at your fingertips.

This tool not only translates the text but also carefully compiles each element of the eBook – chapters, footnotes, and all – into a perfectly formatted EPUB file. We use the `gpt-4o-2024-11-20` model by default to ensure high-quality translations.


## 🛠️ Installation

To install the necessary components for our project, follow these simple steps:

```bash
pip install -r requirements.txt
cp config.yaml.example config.yaml
```

Remember to add your OpenAI key to `config.yaml`.


## 🎮 Usage

The application can be used in two modes: interactive CLI mode and command-line arguments mode.

### Interactive CLI Mode

Simply run the application without any arguments to enter interactive mode:

```bash
python main.py
```

The interactive mode will guide you through the process:
1. Choose between translating a book or viewing chapters
2. Enter the path to your EPUB file
3. Provide the configuration file path
4. Select source and target languages
5. Choose which chapters to translate

### Command-Line Arguments Mode

For automation or advanced usage, you can use command-line arguments:

#### Show Chapters

To review the structure of your book:

```bash
python main.py show-chapters --input yourbook.epub
```

#### Translate Mode

Basic usage:

```bash
python main.py translate --input yourbook.epub --output translatedbook.epub --config config.yaml --from-lang EN --to-lang PL
```

Advanced usage (translating specific chapters):

```bash
python main.py translate --input yourbook.epub --output translatedbook.epub --config config.yaml --from-chapter 13 --to-chapter 37 --from-lang EN --to-lang PL
```


## Converting from AZW3 to EPUB

For books in AZW3 format (Amazon Kindle), use Calibre (https://calibre-ebook.com) to convert them to EPUB before using this tool.


## DRM (Digital Rights Management)

Amazon eBooks (AZW3 format) are encrypted with your device's serial number. To decrypt these books, use the DeDRM tool (https://dedrm.com). You can find your Kindle's serial number at https://www.amazon.com/hz/mycd/digital-console/alldevices.


## 🤝 Contributing

We warmly welcome contributions to this project! Your insights and improvements are invaluable. Currently, we're particularly interested in contributions in the following areas:

- Support for other eBook formats: AZW3, MOBI, PDF
- Integration of a built-in DeDRM tool
- Additional language support
- UI/UX improvements for the interactive mode

Join us in breaking down language barriers in literature and enhancing the accessibility of eBooks worldwide!
