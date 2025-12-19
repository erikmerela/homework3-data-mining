"""
Testimonials scraper for web-scraping.dev using Selenium
Scrapes testimonials from /testimonials page with infinite scroll
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

BASE_URL = "https://web-scraping.dev"
TESTIMONIALS_URL = f"{BASE_URL}/testimonials"


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


def scrape_testimonials_selenium():
    """Scrape testimonials from web-scraping.dev/testimonials using Selenium"""
    all_testimonials = []
    driver = get_driver()
    
    try:
        print("Navigating to testimonials page...")
        driver.get(TESTIMONIALS_URL)
        
        # Wait for testimonials to load
        time.sleep(2)
        
        # Handle infinite scroll - scroll down multiple times to load more
        last_height = driver.execute_script("return document.body.scrollHeight")
        max_scrolls = 5  # Limit scrolls
        scroll_count = 0
        
        while scroll_count < max_scrolls:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)  # Wait for content to load
            
            # Check if we've reached the bottom
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached bottom of page")
                break
            
            last_height = new_height
            scroll_count += 1
            print(f"Scrolled {scroll_count} times")
        
        # Extract testimonials
        print("Extracting testimonials...")
        
        # Try different selectors for testimonials
        testimonial_elements = driver.find_elements(By.CSS_SELECTOR, ".testimonial")
        
        if not testimonial_elements:
            # Try alternative selectors
            testimonial_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='testimonial']")
        
        print(f"Found {len(testimonial_elements)} testimonial elements")
        
        for testimonial_elem in testimonial_elements:
            try:
                # Try to find the text element
                try:
                    text_elem = testimonial_elem.find_element(By.CSS_SELECTOR, ".text, p.text")
                    text = text_elem.text.strip()
                except NoSuchElementException:
                    # Fallback to full text
                    text = testimonial_elem.text.strip()
                
                if not text:
                    continue
                
                author = "Anonymous"
                
                # Try to find author element
                try:
                    author_elem = testimonial_elem.find_element(By.CSS_SELECTOR, ".author, .testimonial-author")
                    author = author_elem.text.strip()
                except NoSuchElementException:
                    pass
                
                # Count stars - look for SVG elements in the .rating span
                star_svgs = testimonial_elem.find_elements(By.CSS_SELECTOR, ".rating svg")
                rating = len(star_svgs) if star_svgs else 5
                
                if text and len(text) > 5:
                    testimonial = {
                        "text": text,
                        "author": author,
                        "rating": rating
                    }
                    all_testimonials.append(testimonial)
                    
            except Exception as e:
                print(f"Error parsing testimonial: {e}")
                continue
                
    finally:
        driver.quit()
    
    return all_testimonials


def scrape_testimonials():
    """Main function to scrape testimonials using Selenium"""
    testimonials = []
    
    try:
        testimonials = scrape_testimonials_selenium()
        print(f"Scraped {len(testimonials)} testimonials using Selenium")
    except Exception as e:
        print(f"Selenium scraping failed: {e}")
    
    return testimonials


def save_testimonials(testimonials, filepath):
    """Save testimonials to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(testimonials, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(testimonials)} testimonials to {filepath}")


if __name__ == "__main__":
    # Get the script's directory to save data in the right place
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'data')
    
    testimonials = scrape_testimonials()
    save_testimonials(testimonials, os.path.join(data_dir, 'testimonials.json'))
    
    print(f"\nTOTAL TESTIMONIALS EXTRACTED: {len(testimonials)}")
    
    print(f"\n{'='*50}")
    print(f"TOTAL TESTIMONIALS EXTRACTED: {len(testimonials)}")
    print(f"{'='*50}")
