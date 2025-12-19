"""
Streamlit Web Application for E-commerce Sentiment Analysis
Displays products, testimonials, and reviews with sentiment analysis
Modern UI with async scraping and dynamic month detection
"""

import streamlit as st
import pandas as pd
import json
import os
from collections import Counter
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="E-commerce Sentiment Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS Styling
st.markdown("""
<style>
    /* Hide stale/loading elements completely instead of graying out */
    [data-stale="true"], .stale-element, .element-container[data-stale="true"] {
        display: none !important;
    }
    
    /* Or alternatively, just hide the opacity effect */
    .main .block-container {
        opacity: 1 !important;
    }
    
    /* Disable Streamlit animations */
    * {
        transition: none !important;
        animation: none !important;
    }
    
    /* Main background and fonts */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        font-size: 2.5rem !important;
    }
    
    h2, h3 {
        color: #4a5568 !important;
        font-weight: 600 !important;
    }
    
    /* Card styling */
    .product-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 4px solid #667eea;
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
    }
    
    .testimonial-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #764ba2;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #3d5a73 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stSlider label, 
    [data-testid="stSidebar"] .stSlider span {
        color: white !important;
    }
    
    [data-testid="stSidebar"] button {
        background: rgba(255,255,255,0.2) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background: rgba(255,255,255,0.3) !important;
    }
    
    /* DataFrame styling */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: 600;
        transition: transform 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Scraping status */
    .scraping-status {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Constants
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


@st.cache_data(ttl=3600)
def load_products():
    """Load products data from JSON file"""
    filepath = os.path.join(DATA_DIR, 'products.json')
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


@st.cache_data(ttl=3600)
def load_reviews():
    """Load pre-analyzed reviews from JSON file"""
    # Try analyzed file first, fallback to raw reviews
    analyzed_path = os.path.join(DATA_DIR, 'reviews_analyzed.json')
    raw_path = os.path.join(DATA_DIR, 'reviews.json')
    
    try:
        with open(analyzed_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        try:
            with open(raw_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []


@st.cache_data(ttl=3600)
def load_testimonials():
    """Load testimonials data from JSON file"""
    filepath = os.path.join(DATA_DIR, 'testimonials.json')
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def get_available_months(reviews):
    """Extract all unique months from reviews and return sorted list"""
    months = set()
    for review in reviews:
        date_str = review.get('date', '')
        if date_str and len(date_str) >= 7:
            month_key = date_str[:7]  # YYYY-MM format
            months.add(month_key)
    
    # Sort months chronologically
    sorted_months = sorted(list(months))
    
    # Create human-readable labels
    month_names = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
        '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
        '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }
    
    month_options = []
    month_map = {}
    
    for month_key in sorted_months:
        year = month_key[:4]
        month_num = month_key[5:7]
        label = f"{month_names.get(month_num, month_num)} {year}"
        month_options.append(label)
        month_map[label] = month_key
    
    return month_options, month_map


def filter_reviews_by_month(reviews: list, month_key: str) -> list:
    """Filter reviews by the selected month"""
    filtered = []
    for review in reviews:
        date_str = review.get('date', '')
        if date_str.startswith(month_key):
            filtered.append(review)
    return filtered


def display_products():
    """Display products section with modern cards"""
    st.markdown("## 🛍️ Products")
    st.markdown("*Browse products scraped from web-scraping.dev*")
    
    products = load_products()
    
    if not products:
        st.warning("No products available. Run the scrapers first.")
        return
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Total Products", len(products))
    with col2:
        prices = [float(p.get('price', '$0').replace('$', '')) for p in products if p.get('price')]
        avg_price = sum(prices) / len(prices) if prices else 0
        st.metric("💰 Average Price", f"${avg_price:.2f}")
    with col3:
        st.metric("📄 Pages Scraped", "5")
    
    st.markdown("---")
    
    # Product grid with modern cards
    st.markdown("### 📋 Product Catalog")
    
    cols = st.columns(3)
    for idx, product in enumerate(products):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="product-card">
                <h4 style="color: #667eea; margin-bottom: 10px;">{product.get('name', 'Unknown')}</h4>
                <p style="font-size: 1.5rem; font-weight: bold; color: #28a745;">{product.get('price', 'N/A')}</p>
                <p style="color: #6c757d; font-size: 0.9rem;">
                    {product.get('description', '')[:120]}{'...' if len(product.get('description', '')) > 120 else ''}
                </p>
            </div>
            """, unsafe_allow_html=True)


def display_testimonials():
    """Display testimonials section with modern cards"""
    st.markdown("## 💬 Testimonials")
    st.markdown("*Customer testimonials from web-scraping.dev*")
    
    testimonials = load_testimonials()
    
    if not testimonials:
        st.warning("No testimonials available. Click 'Refresh Data' to scrape testimonials.")
        return
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💬 Total Testimonials", len(testimonials))
    with col2:
        avg_rating = sum(t.get('rating', 5) for t in testimonials) / len(testimonials)
        st.metric("⭐ Average Rating", f"{avg_rating:.1f}")
    with col3:
        five_star = len([t for t in testimonials if t.get('rating', 0) == 5])
        st.metric("🌟 5-Star Reviews", five_star)
    
    st.markdown("---")
    
    # Rating distribution chart
    st.markdown("### 📊 Rating Distribution")
    rating_counts = Counter([t.get('rating', 5) for t in testimonials])
    
    fig = go.Figure(data=[
        go.Bar(
            x=[f"{'⭐' * i}" for i in range(1, 6)],
            y=[rating_counts.get(i, 0) for i in range(1, 6)],
            marker_color=['#dc3545', '#fd7e14', '#ffc107', '#20c997', '#28a745'],
            text=[rating_counts.get(i, 0) for i in range(1, 6)],
            textposition='auto'
        )
    ])
    fig.update_layout(
        xaxis_title="Rating",
        yaxis_title="Count",
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, width='stretch')
    
    # Testimonials cards
    st.markdown("### 💭 All Testimonials")
    
    cols = st.columns(2)
    for idx, testimonial in enumerate(testimonials):
        with cols[idx % 2]:
            stars = '⭐' * testimonial.get('rating', 5)
            st.markdown(f"""
            <div class="testimonial-card">
                <div style="font-size: 1.2rem; margin-bottom: 10px;">{stars}</div>
                <p style="font-style: italic; color: #495057;">"{testimonial.get('text', '')}"</p>
                <p style="color: #6c757d; font-size: 0.8rem; text-align: right;">— {testimonial.get('author', 'Anonymous')}</p>
            </div>
            """, unsafe_allow_html=True)


def display_reviews():
    """Display reviews section with sentiment analysis"""
    st.markdown("## 📝 Reviews & Sentiment Analysis")
    st.markdown("*Analyze customer reviews using Deep Learning (HuggingFace Transformers)*")
    
    reviews = load_reviews()
    
    if not reviews:
        st.warning("No reviews available. Click 'Refresh Data' to scrape reviews.")
        return
    
    # Get available months dynamically
    month_options, month_map = get_available_months(reviews)
    
    if not month_options:
        st.warning("No dated reviews found in the data.")
        return
    
    # Get selected month from session state (set in main())
    selected_month = st.session_state.get('selected_month', month_options[len(month_options) // 2])
    month_map = st.session_state.get('month_map', month_map)
    
    # Filter reviews by selected month
    month_key = month_map.get(selected_month, '')
    filtered_reviews = filter_reviews_by_month(reviews, month_key)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Reviews", len(reviews))
    with col2:
        st.metric(f"📅 {selected_month}", len(filtered_reviews))
    with col3:
        if filtered_reviews:
            avg_rating = sum(r.get('rating', 5) for r in filtered_reviews) / len(filtered_reviews)
            st.metric("⭐ Avg Rating", f"{avg_rating:.1f}")
        else:
            st.metric("⭐ Avg Rating", "N/A")
    with col4:
        st.metric("🗓️ Months Available", len(month_options))
    
    if not filtered_reviews:
        st.warning(f"No reviews found for {selected_month}. Try selecting a different month.")
        return
    
    st.markdown("---")
    
    # Display sentiment analysis (pre-computed)
    st.markdown(f"### 🤖 Sentiment Analysis for {selected_month}")
    
    # Get review texts for word cloud
    review_texts = [r.get('text', '') for r in filtered_reviews]
    
    # Calculate summary from pre-analyzed data
    positive = [r for r in filtered_reviews if r.get('sentiment') == 'POSITIVE']
    negative = [r for r in filtered_reviews if r.get('sentiment') == 'NEGATIVE']
    
    summary = {
        'positive_count': len(positive),
        'negative_count': len(negative),
        'positive_avg_confidence': sum(r.get('confidence', 0) for r in positive) / len(positive) if positive else 0,
        'negative_avg_confidence': sum(r.get('confidence', 0) for r in negative) / len(negative) if negative else 0
    }
    
    # Sentiment summary cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Positive", summary['positive_count'])
    with col2:
        st.metric("❌ Negative", summary['negative_count'])
    with col3:
        st.metric("📈 Pos. Confidence", f"{summary['positive_avg_confidence']:.1%}")
    with col4:
        st.metric("📉 Neg. Confidence", f"{summary['negative_avg_confidence']:.1%}")
    
    # Single bar chart with distribution and confidence on hover
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=['Positive', 'Negative'],
        y=[summary['positive_count'], summary['negative_count']],
        marker_color=['#28a745', '#dc3545'],
        text=[summary['positive_count'], summary['negative_count']],
        textposition='auto',
        customdata=[[summary['positive_avg_confidence']], [summary['negative_avg_confidence']]],
        hovertemplate='<b>%{x}</b><br>Count: %{y}<br>Avg Confidence: %{customdata[0]:.1%}<extra></extra>'
    ))
    fig_bar.update_layout(
        title='Sentiment Distribution (hover for confidence)',
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        yaxis_title="Number of Reviews"
    )
    st.plotly_chart(fig_bar, width='stretch')
    
    # Word Cloud
    st.markdown("---")
    st.markdown("### ☁️ Word Cloud")
    st.markdown("*Visual representation of the most common words in reviews*")
    
    all_text = ' '.join(review_texts)
    
    if all_text.strip():
        wordcloud = WordCloud(
            width=1200,
            height=400,
            background_color='white',
            colormap='plasma',
            max_words=100,
            min_font_size=12,
            max_font_size=80,
            random_state=42
        ).generate(all_text)
        
        fig_wc, ax = plt.subplots(figsize=(12, 4))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig_wc)
        plt.close(fig_wc)
    
    # Reviews table
    st.markdown("---")
    st.markdown(f"### 📋 Reviews for {selected_month}")
    
    df = pd.DataFrame(filtered_reviews)
    display_columns = ['date', 'text', 'rating', 'sentiment', 'confidence']
    df = df[[c for c in display_columns if c in df.columns]]
    
    if 'confidence' in df.columns:
        df['confidence'] = df['confidence'].apply(lambda x: f"{x:.1%}")
    
    if 'sentiment' in df.columns:
        df['sentiment'] = df['sentiment'].apply(
            lambda x: f"✅ {x}" if x == "POSITIVE" else f"❌ {x}"
        )
    
    if 'rating' in df.columns:
        df['rating'] = df['rating'].apply(lambda x: '⭐' * int(x) if pd.notna(x) else '')
    
    st.dataframe(df, width='stretch', hide_index=True)


def main():
    """Main application entry point"""
    # Header
    st.markdown("# E-commerce Sentiment Analyzer")
    
    # Navigation
    page = st.sidebar.radio("Section", ["Reviews", "Products", "Testimonials"], index=0)
    
    # Month filter for Reviews
    reviews = load_reviews()
    if page == "Reviews" and reviews:
        month_options, month_map = get_available_months(reviews)
        if month_options:
            default_idx = len(month_options) // 2
            selected_month = st.sidebar.select_slider(
                "Month", options=month_options,
                value=month_options[default_idx], key="month_slider_main"
            )
            st.session_state['selected_month'] = selected_month
            st.session_state['month_map'] = month_map
    
    # Compact stats
    products = load_products()
    testimonials = load_testimonials()
    st.sidebar.caption(f"Data: {len(products)} products, {len(reviews)} reviews, {len(testimonials)} testimonials")
    
    # Display selected section - use container with key to prevent fade effect
    selected_month = st.session_state.get('selected_month', '')
    content_key = f"{page}_{selected_month}"
    
    with st.container(key=content_key):
        if page == "Products":
            display_products()
        elif page == "Testimonials":
            display_testimonials()
        else:
            display_reviews()


if __name__ == "__main__":
    main()
