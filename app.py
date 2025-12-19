"""
E-commerce Sentiment Analyzer - Basic Version
"""

import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Sentiment Analyzer", layout="wide")

# Data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def load_json(filename):
    """Load JSON file"""
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def get_months(reviews):
    """Get unique months from reviews"""
    months = sorted(set(r['date'][:7] for r in reviews if r.get('date')))
    return months


def filter_by_month(reviews, month):
    """Filter reviews by month"""
    return [r for r in reviews if r.get('date', '').startswith(month)]


# Load data
products = load_json('products.json')
reviews = load_json('reviews.json')
testimonials = load_json('testimonials.json')

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Section", ["Products", "Reviews", "Testimonials"])

# Month filter for reviews
if page == "Reviews" and reviews:
    months = get_months(reviews)
    if months:
        selected_month = st.sidebar.selectbox("Month", months)

st.sidebar.caption(f"{len(products)} products | {len(reviews)} reviews | {len(testimonials)} testimonials")

# Main content
st.title("E-commerce Sentiment Analyzer")

if page == "Products":
    st.header("Products")
    if products:
        for p in products:
            st.markdown(f"**{p.get('name', 'Unknown')}** - {p.get('price', 'N/A')}")
            st.caption(p.get('description', '')[:200])
            st.divider()
    else:
        st.warning("No products found")

elif page == "Testimonials":
    st.header("Testimonials")
    if testimonials:
        for t in testimonials:
            stars = "⭐" * t.get('rating', 5)
            st.markdown(f"{stars} - {t.get('author', 'Anonymous')}")
            st.write(t.get('text', ''))
            st.divider()
    else:
        st.warning("No testimonials found")

elif page == "Reviews":
    st.header("Reviews & Sentiment Analysis")
    
    if not reviews:
        st.warning("No reviews found")
    else:
        # Filter by month
        months = get_months(reviews)
        if months:
            filtered = filter_by_month(reviews, selected_month)
        else:
            filtered = reviews
        
        st.subheader(f"Analyzing {len(filtered)} reviews...")
        
        if filtered:
            # Run sentiment analysis
            from analysis.sentiment import analyze_reviews, get_sentiment_summary
            
            texts = [r.get('text', '') for r in filtered]
            sentiments = analyze_reviews(texts)
            
            # Add results to reviews
            for i, r in enumerate(filtered):
                r['sentiment'] = sentiments[i]['label']
                r['confidence'] = sentiments[i]['score']
            
            # Summary
            summary = get_sentiment_summary(sentiments)
            
            col1, col2 = st.columns(2)
            col1.metric("Positive", summary['positive_count'])
            col2.metric("Negative", summary['negative_count'])
            
            # Chart
            fig = go.Figure(data=[go.Bar(
                x=['Positive', 'Negative'],
                y=[summary['positive_count'], summary['negative_count']],
                marker_color=['green', 'red']
            )])
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Word cloud
            st.subheader("Word Cloud")
            all_text = ' '.join(texts)
            if all_text.strip():
                from wordcloud import WordCloud
                wc = WordCloud(width=800, height=300, background_color='white').generate(all_text)
                st.image(wc.to_array())
            
            # Table
            st.subheader("Review Details")
            df = pd.DataFrame(filtered)[['date', 'text', 'rating', 'sentiment', 'confidence']]
            df['confidence'] = df['confidence'].apply(lambda x: f"{x:.1%}")
            st.dataframe(df, use_container_width=True)
