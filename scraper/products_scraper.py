"""
Products scraper for web-scraping.dev using Selenium
Scrapes product data from /products pages (6 pages total)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import os

BASE_URL = "https://web-scraping.dev"
PRODUCTS_URL = f"{BASE_URL}/products"


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


def scrape_products():
    """Scrape all products from web-scraping.dev/products using Selenium"""
    all_products = []
    driver = get_driver()
    
    try:
        # There are 6 pages of products
        for page in range(1, 7):
            print(f"Scraping products page {page}...")
            
            url = f"{PRODUCTS_URL}?page={page}"
            driver.get(url)
            
            # Wait for page to load (with timeout handling)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".product"))
                )
            except:
                print(f"No products found on page {page}, skipping...")
                continue
            
            # Find all product elements
            product_elements = driver.find_elements(By.CSS_SELECTOR, ".product")
            
            for product_elem in product_elements:
                try:
                    # Extract product name from h3 > a
                    name_elem = product_elem.find_element(By.CSS_SELECTOR, "h3 a")
                    name = name_elem.text.strip()
                    product_url = name_elem.get_attribute("href")
                    
                    # Extract price from .price div
                    price_elem = product_elem.find_element(By.CSS_SELECTOR, ".price")
                    price_text = price_elem.text.strip()
                    price = f"${price_text}" if not price_text.startswith('$') else price_text
                    
                    # Extract description from .short-description
                    desc_elem = product_elem.find_element(By.CSS_SELECTOR, ".short-description")
                    description = desc_elem.text.strip()
                    
                    # Extract image
                    img_elem = product_elem.find_element(By.CSS_SELECTOR, "img")
                    image = img_elem.get_attribute("src")
                    
                    product = {
                        "name": name,
                        "url": product_url,
                        "price": price,
                        "description": description,
                        "image": image
                    }
                    
                    all_products.append(product)
                    
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue
            
            # Small delay between pages
            time.sleep(0.5)
            
    finally:
        driver.quit()
    
    return all_products


def save_products(products, filepath):
    """Save products to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(products)} products to {filepath}")


if __name__ == "__main__":
    # Get the script's directory to save data in the right place
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'data')
    
    products = scrape_products()
    save_products(products, os.path.join(data_dir, 'products.json'))
    
    print(f"\n{'='*50}")
    print(f"TOTAL PRODUCTS EXTRACTED: {len(products)}")
    print(f"{'='*50}")
