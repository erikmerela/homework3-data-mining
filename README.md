# E-commerce Sentiment Analyzer

A Streamlit web application that scrapes e-commerce data and displays sentiment analysis results. Sentiment is pre-computed using HuggingFace Transformers (DistilBERT) for lightweight deployment on Render.

## Features

- **Web Scraping** - Selenium-based scrapers for products, reviews, and testimonials from web-scraping.dev
- **Sentiment Analysis** - Pre-computed using DistilBERT model (positive/negative classification)
- **Interactive Dashboard** - Filter reviews by month, view sentiment distribution charts
- **Word Cloud** - Visual representation of common words in reviews
- **Modern UI** - Gradient styling, responsive cards, interactive Plotly charts

## Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\Activate.ps1

# Install dependencies (full - for scraping & analysis)
pip install -r requirements.txt
```

## Usage

### 1. Scrape Data

```bash
python scraper/products_scraper.py
python scraper/reviews_scraper.py
python scraper/testimonials_scraper.py
```

### 2. Run Sentiment Analysis

```bash
python analysis/run_analysis.py
```

This creates `data/reviews_analyzed.json` with pre-computed sentiment scores.

### 3. Run App

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Deployment (Render)

For deployment, use the minimal requirements file (no ML dependencies):

```bash
pip install -r requirements-deploy.txt
```

The app loads pre-analyzed data from JSON files, so no ML inference is needed at runtime.

## Project Structure

```
homework3/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Full dependencies (scraping + ML)
├── requirements-deploy.txt   # Minimal dependencies (deployment)
├── analysis/
│   ├── sentiment.py          # HuggingFace sentiment analysis module
│   └── run_analysis.py       # Pre-compute sentiment script
├── scraper/
│   ├── products_scraper.py   # Scrape products (Selenium)
│   ├── reviews_scraper.py    # Scrape reviews (Selenium)
│   └── testimonials_scraper.py
└── data/
    ├── products.json
    ├── reviews.json
    ├── reviews_analyzed.json  # Reviews with sentiment scores
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
