import requests
import pandas as pd
import logging
import os
from concurrent.futures import ThreadPoolExecutor


def init_log(logger_name, log_dir, log_file):
    """
    Khởi tạo logger với cấu hình log cụ thể.
    """
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


logger = init_log('tiki', './logs', 'tiki.log')


def get_categories():
    """
    Lấy tất cả danh mục từ Tiki.vn.
    Trả về danh sách các liên kết danh mục.
    """
    url = 'https://api.tiki.vn/raiden/v2/menu-config?platform=desktop'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data_dict = response.json()
        return [item['link'] for item in data_dict.get("menu_block", {}).get("items", []) if 'link' in item]
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi khi lấy danh mục: {e}")
        return []


def get_data(url):
    """
    Lấy dữ liệu từ một URL cụ thể.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        logger.warning(f"Lỗi khi tải dữ liệu từ {url}: {e}")
        return []


def save_to_parquet(data, filename):
    """
    Lưu dữ liệu dưới dạng tệp Parquet.
    """
    output_dir = "./data"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    try:
        df = pd.DataFrame(data)
        df.to_parquet(filepath, index=False)
        logger.info(f"Dữ liệu được lưu vào: {filepath}")
    except Exception as e:
        logger.error(f"Lỗi khi lưu dữ liệu vào {filepath}: {e}")


def process_category(category_link):
    """
    Xử lý dữ liệu cho một danh mục cụ thể.
    """
    try:
        param = category_link.split("/c")[-1]
        total_data = []
        page = 1

        while True:
            url = f'https://tiki.vn/api/personalish/v1/blocks/listings?limit=300&category={param}&page={page}'
            data = get_data(url)
            if not data:
                logger.info(f"Hết dữ liệu cho danh mục {param} tại trang {page}")
                break
            total_data.extend(data)
            logger.info(f"Lấy thành công {len(data)} sản phẩm từ danh mục {param}, trang {page}")
            page += 1

        if total_data:
            save_to_parquet(total_data, f"category_{param}.parquet")
    except Exception as e:
        logger.error(f"Lỗi khi xử lý danh mục {category_link}: {e}")


def main():
    """
    Điểm bắt đầu của chương trình.
    """
    categories = get_categories()
    if not categories:
        logger.error("Không tìm thấy danh mục nào để xử lý.")
        return

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_category, categories)


if __name__ == "__main__":
    main()
