import requests
import pandas as pd
import logging
import os
from concurrent.futures import ThreadPoolExecutor

# Define base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
DATA_DIR = os.path.join(BASE_DIR, 'data')

def init_log(logger_name, log_dir, log_file):
    """
    Initialize logger with specific configuration.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers
    if not logger.handlers:
        log_path = os.path.join(log_dir, log_file)
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
    return logger

logger = init_log('tiki', LOG_DIR, 'tiki.log')

def get_categories():
    """
    Fetch all categories from Tiki.vn.
    Returns a list of category links.
    """
    logger.info("Fetching categories from Tiki.vn")
    url = 'https://api.tiki.vn/raiden/v2/menu-config?platform=desktop'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data_dict = response.json()
        categories = []

        # Extract category links recursively
        def extract_links(items):
            for item in items:
                if 'link' in item:
                    categories.append(item['link'])
                if 'items' in item:
                    extract_links(item['items'])

        extract_links(data_dict.get("menu_block", {}).get("items", []))
        logger.info(f"Found {len(categories)} categories.")
        return categories
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching categories: {e}")
        return []

def get_data(url):
    """
    Fetch data from a specific URL.
    """
    logger.info(f"Fetching data from URL: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching data from {url}: {e}")
        return []

def extract_product_fields(product):
    """
    Extract important fields from product data.
    """
    important_fields = {}
    important_fields['id'] = product.get('id')
    important_fields['sku'] = product.get('sku')
    important_fields['name'] = product.get('name')
    important_fields['price'] = product.get('price')
    important_fields['list_price'] = product.get('list_price')
    important_fields['discount'] = product.get('discount')
    important_fields['discount_rate'] = product.get('discount_rate')
    important_fields['rating_average'] = product.get('rating_average')
    important_fields['review_count'] = product.get('review_count')
    important_fields['order_count'] = product.get('order_count')
    important_fields['favourite_count'] = product.get('favourite_count')
    important_fields['thumbnail_url'] = product.get('thumbnail_url')
    # Extract 'quantity_sold' value
    quantity_sold = product.get('quantity_sold')
    if isinstance(quantity_sold, dict):
        important_fields['quantity_sold'] = quantity_sold.get('value')
    else:
        important_fields['quantity_sold'] = None
    important_fields['original_price'] = product.get('original_price')
    important_fields['seller_id'] = product.get('seller_id')
    # Extract 'seller' name
    seller = product.get('seller')
    if isinstance(seller, dict):
        important_fields['seller'] = seller.get('name')
    else:
        important_fields['seller'] = None
    important_fields['seller_product_id'] = product.get('seller_product_id')
    important_fields['brand_name'] = product.get('brand_name')
    # Extract category names from 'breadcrumbs' if available
    breadcrumbs = product.get('breadcrumbs', [])
    important_fields['category_l1_name'] = breadcrumbs[0]['name'] if len(breadcrumbs) > 0 else None
    important_fields['category_l2_name'] = breadcrumbs[1]['name'] if len(breadcrumbs) > 1 else None
    important_fields['category_l3_name'] = breadcrumbs[2]['name'] if len(breadcrumbs) > 2 else None

    return important_fields

def save_to_parquet(data, filename):
    """
    Save data as a Parquet file with only important columns.
    """
    important_columns = [
        'id', 'sku', 'name', 'price', 'list_price', 'discount',
        'discount_rate', 'rating_average', 'review_count',
        'order_count', 'favourite_count', 'thumbnail_url',
        'quantity_sold', 'original_price', 'seller_id', 'seller',
        'seller_product_id', 'brand_name', 'category_l1_name',
        'category_l2_name', 'category_l3_name'
    ]

    output_dir = DATA_DIR
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    try:
        df = pd.DataFrame(data)
        # Select only important columns
        df = df[important_columns]
        df.to_parquet(filepath, index=False)
        logger.info(f"Data saved to: {filepath}")
    except Exception as e:
        logger.error(f"Error saving data to {filepath}: {e}")

def process_category(category_link):
    """
    Process data for a specific category.
    """
    logger.info(f"Processing category: {category_link}")
    try:
        if "/c" in category_link:
            param = category_link.split("/c")[-1]
        else:
            logger.warning(f"Invalid category link format: {category_link}")
            return
        total_data = []
        page = 1

        while True:
            url = f'https://tiki.vn/api/personalish/v1/blocks/listings?limit=48&category={param}&page={page}'
            data = get_data(url)
            if not data:
                logger.info(f"No more data for category {param} at page {page}")
                break
            # Extract important fields
            processed_data = [extract_product_fields(item) for item in data]
            total_data.extend(processed_data)
            logger.info(f"Fetched {len(data)} products from category {param}, page {page}")
            page += 1

        if total_data:
            save_to_parquet(total_data, f"category_{param}.parquet")
    except Exception as e:
        logger.error(f"Error processing category {category_link}: {e}")

def main():
    """
    Entry point of the program.
    """
    logger.info("Starting the main function.")
    logger.info(f"Logs directory: {LOG_DIR}")
    logger.info(f"Data directory: {DATA_DIR}")
    categories = get_categories()
    if not categories:
        logger.error("No categories found to process.")
        return

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_category, categories)
    logger.info("Finished processing all categories.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
