# E-commerce Sentiment Analyzer

A Streamlit web application that scrapes e-commerce data and performs sentiment analysis using HuggingFace Transformers.

## Features

- **Web Scraping** - Selenium-based scrapers for products, reviews, and testimonials from web-scraping.dev
- **Sentiment Analysis** - DistilBERT model for classifying reviews as positive/negative
- **Interactive Dashboard** - Filter reviews by month, view sentiment distribution charts
- **Word Cloud** - Visual representation of common words in reviews
- **Modern UI** - Gradient styling, responsive cards, interactive charts

## Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Usage

### 1. Scrape Data

```bash
python scraper/products_scraper.py
python scraper/reviews_scraper.py
python scraper/testimonials_scraper.py
```

### 2. Run App

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Project Structure

```
homework3/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── analysis/
│   └── sentiment.py       # HuggingFace sentiment analysis
├── scraper/
│   ├── products_scraper.py
│   ├── reviews_scraper.py
│   └── testimonials_scraper.py
└── data/
    ├── products.json
    ├── reviews.json
    └── testimonials.json
```

## Tech Stack

- **Streamlit** - Web framework
- **Selenium** - Web scraping
- **HuggingFace Transformers** - Sentiment analysis (DistilBERT-SST2)
- **Plotly** - Interactive charts
- **WordCloud** - Text visualization

## Data Source

All data scraped from [web-scraping.dev](https://web-scraping.dev)
