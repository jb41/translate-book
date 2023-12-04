# Translate books with GPT

This project harnesses the power of GPT-4 LLM to translate eBooks from any language into your preferred language, maintaining the integrity and structure of the original content. Imagine having access to a vast world of literature, regardless of the original language, right at your fingertips.

This tool not only translates the text but also carefully compiles each element of the eBook – chapters, footnotes, and all – into a perfectly formatted EPUB file. We use the `gpt-4-1106-preview` (GPT-4 Turbo) model by default to ensure high-quality translations. However, we understand the need for flexibility, so we've made it easy to switch models in `main.py` according to your specific needs.


## 🛠️ Installation

To install the necessary components for our project, follow these simple steps:

```bash
pip install -r requirements.txt
cp config.yaml.example config.yaml
```

Remember to add your OpenAI key to `config.yaml`.


## 🎮 Usage

Our script comes with a variety of parameters to suit your needs. Here's how you can make the most out of it:

### Show Chapters

Before diving into translation, it's recommended to use the `show-chapters` mode to review the structure of your book:

```bash
python main.py show-chapters --input yourbook.epub
```

This command will display all the chapters, helping you to plan your translation process effectively.

### Translate Mode

#### Basic Usage

To translate a book from English to Polish, use the following command:

```bash
python main.py translate --input yourbook.epub --output translatedbook.epub --config config.yaml --from-lang EN --to-lang PL
```

#### Advanced Usage

For more specific needs, such as translating from chapter 13 to chapter 37 from English to Polish, use:

```bash
python main.py translate --input yourbook.epub --output translatedbook.epub --config config.yaml --from-chapter 13 --to-chapter 37 --from-lang EN --to-lang PL
```


## Converting from AZW3 to EPUB

For books in AZW3 format (Amazon Kindle), use Calibre (https://calibre-ebook.com) to convert them to EPUB before using this tool.


## DRM (Digital Rights Management)

Amazon eBooks (AZW3 format) are encrypted with your device's serial number. To decrypt these books, use the DeDRM tool (https://dedrm.com). You can find your Kindle's serial number at https://www.amazon.com/hz/mycd/digital-console/alldevices.


## 🤝 Contributing

We warmly welcome contributions to this project! Your insights and improvements are invaluable. Currently, we're particularly interested in contributions in the following areas:

- Support for other eBook formats: AZW3, MOBI, PDF.
- Integration of a built-in DeDRM tool

Join us in breaking down language barriers in literature and enhancing the accessibility of eBooks worldwide!
