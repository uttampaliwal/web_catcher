# 🌐 Web Catcher: The Ultimate Data Extraction & Segmentation Guide

Welcome to **Web Catcher**! This tool is designed to help you "capture" data from the internet (Webpages, Wikipedia, PDFs) and turn it into structured, machine-readable JSON. Whether you're a seasoned ML engineer or just getting started, this guide will walk you through every command you need.

---

## 🛠 1. Quick Start (The "starter" Guide)

If you just want to get it running as fast as possible, follow these steps:

### Setup the Environment
First, ensure you have the dependencies installed in a virtual environment so you don't mess up your system:

```bash
# 1. Enter the project directory
cd /home/uttam/dev/web_catcher

# 2. Create a virtual environment (one-time setup)
python3 -m venv venv

# 3. Activate the environment
source venv/bin/activate

# 4. Install requirements
pip install -r requirements.txt
```

### Your Very First Extraction
Try extracting a Wikipedia page to see it in action:
```bash
python3 src/main.py "Python (programming language)" --type wiki --output my_first_extraction.json
```
Check the `my_first_extraction.json` file in your folder!

---

## 🧭 2. Detailed Navigation (The "Nerd" Guide)

The core script is `src/main.py`. Here is how to master its parameters.

### CLI Arguments Breakdown
| Argument | Description | Required? |
| :--- | :--- | :--- |
| `source` | The URL, Wikipedia title, or local Path to a PDF. | **Yes** |
| `--type` | Force a type: `web`, `wiki`, `pdf`. Default is `auto`. | No |
| `--output` | Save results to a file. If omitted, prints to terminal. | No |
| `--config` | Path to a custom `config.yaml` file. | No |

---

## 🚀 3. Extensive Usage Examples

### 📝 Wikipedia Extraction
Wikipedia is segmented by its actual section headers (`heading_l1`, `heading_l2`, etc.), making it perfect for training RAG (Retrieval-Augmented Generation) systems.

```bash
# Extract by Title
python3 src/main.py "Machine Learning" --type wiki --output ml_wiki.json

# Extract by URL (Internal auto-detection handles this)
python3 src/main.py "https://en.wikipedia.org/wiki/Artificial_intelligence" --output ai_wiki.json
```

### 📄 PDF Extraction
Extracts text block-by-block while keeping track of page numbers and identifying images.

```bash
# Extract a local PDF
python3 src/main.py "data/research_paper.pdf" --type pdf --output paper_segments.json
```

### 🕸 Webpage Extraction
Uses `trafilatura` to strip away ads, nav-bars, and footers, leaving only the "meat" of the article.

```bash
# Extract an online article
python3 src/main.py "https://trafilatura.readthedocs.io/en/latest/index.html" --type web --output doc_clean.json
```

---

## 🏗 4. Understanding the Output Structure

Every output follows this exact Pydantic-validated JSON schema:

```json
{
  "metadata": {
    "title": "Title of the document",
    "author": "Author name (if found)",
    "date": "Publication date (if found)",
    "url": "Source URL",
    "source_type": "web | wiki | pdf",
    "additional": { "extra_fields": "like page count" }
  },
  "segments": [
    {
      "type": "heading_l1 | text | image | table",
      "content": "The actual text or data",
      "metadata": { "page": "1", "block_no": "5" }
    }
  ]
}
```

---

## 💡 5. Pro Tips

- **Auto-Detection**: You usually don't need `--type`. The app checks if it's a `.pdf` file or a `wikipedia.org` link automatically.
- **Pipe to JQ**: If you want to explore the JSON in your terminal nicely:
  ```bash
  python3 src/main.py "Machine Learning" --type wiki | jq .metadata
  ```
- **Custom Config**: Create a `config.yaml` to override default behaviors like Wikipedia language or PDF image extraction.
  ```bash
  python3 src/main.py "data/report.pdf" --config my_config.yaml
  ```
- **Batch Processing**: Use a simple bash loop to process multiple URLs:
  ```bash
  for url in $(cat urls.txt); do python3 src/main.py "$url" --output "data/$(basename $url).json"; done
  ```

---

## 🧪 6. Testing & Development

We maintain a high-quality codebase with comprehensive unit and integration tests.

### Running Tests
To run the entire test suite:
```bash
pytest
```

To run with coverage (if installed):
```bash
pytest --cov=src
```

### Adding New Extractors
1. Create a new class in `src/extractors/` inheriting from `BaseExtractor`.
2. Register it in `src/main.py`.
3. Add corresponding tests in `tests/test_your_extractor.py`.
