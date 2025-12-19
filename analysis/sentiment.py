"""
Sentiment Analysis module using HuggingFace Transformers
Uses distilbert-base-uncased-finetuned-sst-2-english for classification
"""

import os
import streamlit as st

# Set cache directories before importing transformers
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
os.environ['HF_HOME'] = '/tmp/huggingface'

from transformers import pipeline


@st.cache_resource(show_spinner="Loading sentiment model...")
def load_sentiment_model():
    """
    Load the sentiment analysis model with caching.
    Uses @st.cache_resource to load the model only once.
    """
    try:
        print("Loading sentiment analysis model...")
        classifier = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1,  # Force CPU
            model_kwargs={"low_cpu_mem_usage": True}
        )
        print("Model loaded successfully!")
        return classifier
    except Exception as e:
        print(f"Error loading model: {e}")
        return None


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of a single text.
    
    Args:
        text: The text to analyze
        
    Returns:
        dict with 'label' (POSITIVE/NEGATIVE) and 'score' (confidence)
    """
    classifier = load_sentiment_model()
    
    if classifier is None:
        # Fallback if model failed to load
        return {"label": "UNKNOWN", "score": 0.0}
    
    # Truncate text if too long (model has max token limit)
    if len(text) > 512:
        text = text[:512]
    
    result = classifier(text)[0]
    return {
        "label": result["label"],
        "score": round(result["score"], 4)
    }


@st.cache_data(ttl=3600)
def analyze_reviews(texts: tuple) -> list:
    """
    Analyze sentiment of multiple texts.
    Uses caching to avoid re-analyzing the same reviews.
    
    Args:
        texts: Tuple of text strings to analyze (tuple for hashability)
        
    Returns:
        List of dicts with 'label' and 'score' for each text
    """
    classifier = load_sentiment_model()
    
    if classifier is None:
        # Fallback if model failed to load
        return [{"label": "UNKNOWN", "score": 0.0} for _ in texts]
    
    # Convert tuple back to list and truncate texts if too long
    truncated_texts = [t[:512] if len(t) > 512 else t for t in texts]
    
    # Process in smaller batches to reduce memory usage
    results = []
    batch_size = 8
    for i in range(0, len(truncated_texts), batch_size):
        batch = truncated_texts[i:i+batch_size]
        batch_results = classifier(batch)
        results.extend(batch_results)
    
    return [
        {
            "label": r["label"],
            "score": round(r["score"], 4)
        }
        for r in results
    ]


def get_sentiment_summary(sentiments: list) -> dict:
    """
    Get summary statistics for sentiment analysis results.
    
    Args:
        sentiments: List of sentiment dicts from analyze_reviews
        
    Returns:
        dict with counts, percentages, and average confidence scores
    """
    if not sentiments:
        return {
            "positive_count": 0,
            "negative_count": 0,
            "positive_avg_confidence": 0.0,
            "negative_avg_confidence": 0.0,
            "total": 0
        }
    
    positive = [s for s in sentiments if s["label"] == "POSITIVE"]
    negative = [s for s in sentiments if s["label"] == "NEGATIVE"]
    
    positive_count = len(positive)
    negative_count = len(negative)
    
    positive_avg_conf = sum(s["score"] for s in positive) / positive_count if positive_count > 0 else 0.0
    negative_avg_conf = sum(s["score"] for s in negative) / negative_count if negative_count > 0 else 0.0
    
    return {
        "positive_count": positive_count,
        "negative_count": negative_count,
        "positive_avg_confidence": round(positive_avg_conf, 4),
        "negative_avg_confidence": round(negative_avg_conf, 4),
        "total": len(sentiments)
    }
