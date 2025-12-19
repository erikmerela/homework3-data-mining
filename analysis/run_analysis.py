"""
Standalone script to run sentiment analysis on reviews and save results.
Run this BEFORE deploying to pre-compute all sentiment data.

Usage:
    python analysis/run_analysis.py
"""

import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.sentiment import analyze_reviews, get_sentiment_summary

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def run_analysis():
    """Run sentiment analysis on all reviews and save results"""
    reviews_path = os.path.join(DATA_DIR, 'reviews.json')
    
    # Load reviews
    print("Loading reviews...")
    with open(reviews_path, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    
    print(f"Loaded {len(reviews)} reviews")
    
    if not reviews:
        print("No reviews found!")
        return
    
    # Run sentiment analysis
    print("Running sentiment analysis with HuggingFace Transformers...")
    print("(This may take a moment on first run to download the model)")
    
    texts = tuple(r.get('text', '') for r in reviews)
    sentiments = analyze_reviews(texts)
    
    # Add sentiment to each review
    for i, review in enumerate(reviews):
        review['sentiment'] = sentiments[i]['label']
        review['confidence'] = sentiments[i]['score']
    
    # Save analyzed reviews
    output_path = os.path.join(DATA_DIR, 'reviews_analyzed.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved analyzed reviews to {output_path}")
    
    # Print summary
    positive = sum(1 for r in reviews if r['sentiment'] == 'POSITIVE')
    negative = len(reviews) - positive
    
    print("\n" + "=" * 50)
    print("SENTIMENT ANALYSIS COMPLETE")
    print("=" * 50)
    print(f"Total reviews: {len(reviews)}")
    print(f"Positive: {positive} ({positive/len(reviews)*100:.1f}%)")
    print(f"Negative: {negative} ({negative/len(reviews)*100:.1f}%)")


if __name__ == "__main__":
    run_analysis()
