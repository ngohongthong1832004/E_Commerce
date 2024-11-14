import requests
import pandas as pd
import json
import logging, os
from concurrent.futures import ThreadPoolExecutor

def init_log(logger_name, log_dir, log_file):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    
    log_path = os.path.join(log_dir, log_file)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    return logger

logger = init_log('tiki', './src/logs', 'tiki.log')

def get_categories():
    '''
        get_categories: Get all categories from Tiki.vn
        Returns:
            list: List of category links
            
        Example:
            get_categories()
            
            Output:
            [category_link_1, category_link_2, ...]
            
    '''
    url = 'https://api.tiki.vn/raiden/v2/menu-config?platform=desktop'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 403:
        logger.error("Access Denied (403)")
        return []
    
    data_dict = response.json()
    return [item['link'] for item in data_dict["menu_block"]["items"] if 'link' in item]

def get_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        logger.info(f"Request error: {e}")
        return []

def save_to_parquet(data, filename):
    '''
        save_to_parquet: Save data to a parquet file
    '''
    output_dir = "./src/data"
    os.makedirs(output_dir, exist_ok=True)  
    filepath = os.path.join(output_dir, filename)
    df = pd.DataFrame(data)
    df.to_parquet(filepath, index=False)
    logger.info(f"Data saved to {filepath}")

def process_category(category_link):
    '''
        process_category: Process data for a given category link
        
        Args:
            category_link (str): Category link
            
        Example:
            process_category('https://tiki.vn/laptop-may-vi-tinh/c1846')
            
    '''
    try:
        param = category_link.split("/c")[-1]
        total_data = []
        page = 1
        while True:
            url = f'https://tiki.vn/api/personalish/v1/blocks/listings?limit=300&category={param}&page={page}'
            data = get_data(url)
            if not data:
                logger.info(f"No more data for category {param} on page {page}")
                break
            total_data += data
            page += 1

        if total_data:
            save_to_parquet(total_data, f"category_{param}.parquet")
    except Exception as e:
        logger.error(f"Error processing category {category_link}: {e}")

def main():
    categories = get_categories()
    
    if not categories:
        logger.error("No categories found.")
        return

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_category, categories)

if __name__ == "__main__":
    main()
