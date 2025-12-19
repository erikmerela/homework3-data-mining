"""
Reviews scraper for web-scraping.dev using Selenium
Scrapes review data from /reviews page with "Load More" pagination
Reviews have dates in 2023 format (YYYY-MM-DD)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import os
import re
from datetime import datetime
from collections import Counter

BASE_URL = "https://web-scraping.dev"
REVIEWS_URL = f"{BASE_URL}/reviews"


def get_driver():
    """Create and return a Chrome WebDriver instance"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def parse_date(date_str):
    """Parse date string to standardized format"""
    try:
        # Format: YYYY-MM-DD
        dt = datetime.strptime(date_str.strip(), '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return date_str


def scrape_reviews_selenium():
    """Scrape reviews from web-scraping.dev/reviews using Selenium with Load More"""
    all_reviews = []
    driver = get_driver()
    
    try:
        print("Navigating to reviews page...")
        driver.get(REVIEWS_URL)
        
        # Wait for reviews to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".review"))
        )
        
        # Click "Load More" button multiple times to get all reviews
        max_clicks = 10  # Safety limit
        click_count = 0
        
        while click_count < max_clicks:
            try:
                # Find and click the "Load More" button (id="page-load-more")
                load_more_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.ID, "page-load-more"))
                )
                
                # Scroll to button and click
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", load_more_btn)  # JS click for reliability
                click_count += 1
                print(f"Clicked 'Load More' ({click_count} times)")
                
                # Wait for new content to load
                time.sleep(1.5)
                
            except TimeoutException:
                print("No more 'Load More' button found - all reviews loaded")
                break
            except Exception as e:
                print(f"Error clicking Load More: {e}")
                break
        
        # Now extract all reviews from the page
        print("Extracting reviews from page...")
        review_elements = driver.find_elements(By.CSS_SELECTOR, ".review")
        print(f"Found {len(review_elements)} review elements")
        
        for review_elem in review_elements:
            try:
                # Get the full text of the review element
                review_text = review_elem.text.strip()
                
                # Extract date using the specific selector or regex fallback
                try:
                    date_elem = review_elem.find_element(By.CSS_SELECTOR, "[data-testid='review-date']")
                    date = date_elem.text.strip()
                except NoSuchElementException:
                    # Fallback to regex
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', review_text)
                    date = date_match.group(1) if date_match else None
                
                if not date:
                    continue  # Skip reviews without dates
                
                # Extract review content using specific selector
                try:
                    text_elem = review_elem.find_element(By.CSS_SELECTOR, "[data-testid='review-text'], .review-text, p")
                    text = text_elem.text.strip()
                except NoSuchElementException:
                    # Fallback: get text and remove the date part
                    text = re.sub(r'\d{4}-\d{2}-\d{2}', '', review_text).strip()
                
                # Count stars - look for SVG elements in the review-stars span
                star_svgs = review_elem.find_elements(By.CSS_SELECTOR, "[data-testid='review-stars'] svg, .review-stars svg")
                if not star_svgs:
                    # Fallback to any SVG in the review
                    star_svgs = review_elem.find_elements(By.CSS_SELECTOR, "svg")
                rating = len(star_svgs) if star_svgs else 5
                
                if text and len(text) > 10:  # Only add if there's meaningful text
                    review = {
                        "text": text,
                        "date": parse_date(date),
                        "rating": rating
                    }
                    all_reviews.append(review)
                    
            except Exception as e:
                print(f"Error parsing review: {e}")
                continue
                
    finally:
        driver.quit()
    
    return all_reviews


def scrape_reviews():
    """Main function to scrape reviews using Selenium - only 2023 reviews"""
    reviews = []
    
    try:
        all_reviews = scrape_reviews_selenium()
        # Filter to only keep 2023 reviews
        reviews = [r for r in all_reviews if r.get('date', '').startswith('2023')]
        print(f"Scraped {len(all_reviews)} reviews, kept {len(reviews)} from 2023")
    except Exception as e:
        print(f"Selenium scraping failed: {e}")
    
    return reviews


def save_reviews(reviews, filepath):
    """Save reviews to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(reviews)} reviews to {filepath}")


if __name__ == "__main__":
    # Get the script's directory to save data in the right place
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'data')
    
    reviews = scrape_reviews()
    save_reviews(reviews, os.path.join(data_dir, 'reviews.json'))
    
    print(f"\nTOTAL REVIEWS EXTRACTED: {len(reviews)}")
    
    # Show distribution by month
    months = [r['date'][:7] for r in reviews if 'date' in r]
    month_counts = Counter(months)
    print("\nReviews by month:")
    for month in sorted(month_counts.keys()):
        print(f"  {month}: {month_counts[month]} reviews")
    
    print(f"\n{'='*50}")
    print(f"TOTAL REVIEWS EXTRACTED: {len(reviews)}")
    print(f"{'='*50}")
