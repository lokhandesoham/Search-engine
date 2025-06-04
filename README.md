# 🔍 Advanced Web Search Engine

A powerful, feature-rich search engine implementation that combines efficient indexing, intelligent search algorithms, and a modern web interface. Built with Python and Flask, this search engine delivers fast, relevant results with the added benefit of AI-powered summaries.

## 🎥 Demo

![Search Engine Demo](demo.gif)

## ✨ Features

- **Efficient Indexing**: Advanced document processing with NLTK for tokenization and stemming
- **Smart Search**: Boolean AND operations with TF-IDF scoring for relevant results
- **Modern Web Interface**: Clean, responsive Flask-based GUI
- **AI-Powered Summaries**: Integration with OpenAI's GPT-3.5 for intelligent result summaries
- **Duplicate Detection**: Built-in mechanism to eliminate redundant pages
- **Performance Metrics**: Real-time search execution time tracking

## 🚀 Quick Start

### Prerequisites

Make sure you have Python 3.2+ installed and the following Python packages:

```bash
pip3 install nltk bs4 re os json tqdm openai flask
```

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/Search-engine.git
cd Search-engine
```

2. Download the required NLTK data:
```python
python3 -c "import nltk; nltk.download('punkt')"
```

3. Set up your OpenAI API key:
   - Get your API key from [OpenAI](https://platform.openai.com)
   - Update the API key in `gui.py` and `Searcher.py`

### Building the Index

1. Ensure you have the `DEV` folder containing your documents in the same directory as `indexer.py`
2. Run the indexer:
```bash
python3 indexer.py
```
   - This process takes approximately 15-16 minutes
   - Progress bar shows real-time indexing status
   - Generates necessary index files:
     - `finalreverseindexer.txt`
     - `index2.txt`
     - `index3.txt`
     - `DocIDS.json`

### Running the Search Engine

1. Start the web interface:
```bash
python3 gui.py
```

2. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## 💡 Usage

1. Enter your search query in the search box
2. View the top 5 most relevant results
3. Click the "Summary" button next to any result to get an AI-generated summary
4. Track search execution time for performance monitoring

## 🛠️ Technical Details

### Indexing Process
- Document parsing using BeautifulSoup
- Word tokenization and stemming with NLTK
- TF-IDF scoring for term importance
- Efficient partial indexing with disk offloading
- Multi-level index structure for fast lookups

### Search Algorithm
- Query processing with stopword removal
- Boolean AND operations for precise results
- TF-IDF based scoring and ranking
- Importance weighting for headers and bold text

### Web Interface
- Flask-based responsive design
- Real-time search execution
- Asynchronous summary generation
- Clean and intuitive user experience



