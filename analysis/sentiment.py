"""
Lightweight Sentiment Analysis module using HuggingFace Transformers
"""

_classifier = None

def load_sentiment_model():
    """Load the sentiment model once"""
    global _classifier
    if _classifier is None:
        print("Loading sentiment analysis model...")
        from transformers import pipeline
        _classifier = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        print("Model loaded!")
    return _classifier


def analyze_reviews(texts):
    """Analyze sentiment of multiple texts"""
    classifier = load_sentiment_model()
    
    # Truncate long texts
    truncated = [t[:512] if len(t) > 512 else t for t in texts]
    
    results = classifier(truncated)
    
    return [{"label": r["label"], "score": round(r["score"], 4)} for r in results]


def get_sentiment_summary(sentiments):
    """Get summary statistics"""
    positive = [s for s in sentiments if s["label"] == "POSITIVE"]
    negative = [s for s in sentiments if s["label"] == "NEGATIVE"]
    
    pos_count = len(positive)
    neg_count = len(negative)
    
    pos_conf = sum(s["score"] for s in positive) / pos_count if pos_count > 0 else 0
    neg_conf = sum(s["score"] for s in negative) / neg_count if neg_count > 0 else 0
    
    return {
        "positive_count": pos_count,
        "negative_count": neg_count,
        "positive_avg_confidence": pos_conf,
        "negative_avg_confidence": neg_conf,
        "total": len(sentiments)
    }
