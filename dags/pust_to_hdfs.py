import os
from hdfs import InsecureClient
import logging

# Cấu hình HDFS và thư mục
HDFS_URL = 'http://localhost:9870'
HDFS_DIR = '/user/hadoop/tiki_data'
LOCAL_DIR = './data'

client = InsecureClient(HDFS_URL, user='hadoop')

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

logger = init_log('hdfs_tiki', './logs', 'hdfs_tiki.log')

def push_parquet_files(local_dir, hdfs_dir):
    if not os.path.exists(local_dir):
        logger.error(f"Thư mục cục bộ {local_dir} không tồn tại.")
        return

    # Kiểm tra file Parquet trong thư mục
    parquet_files = [f for f in os.listdir(local_dir) if f.endswith('.parquet')]
    if not parquet_files:
        logger.warning(f"Không tìm thấy tệp .parquet nào trong thư mục {local_dir}.")
        return

    # Tạo thư mục trên HDFS nếu chưa tồn tại
    try:
        client.makedirs(hdfs_dir)
        logger.info(f"Thư mục HDFS {hdfs_dir} đã được tạo hoặc đã tồn tại.")
    except Exception as e:
        logger.error(f"Lỗi khi tạo thư mục HDFS {hdfs_dir}: {e}")
        return

    # Tải file lên HDFS
    for root, _, files in os.walk(local_dir):
        for file in files:
            if file.endswith('.parquet'):
                local_file_path = os.path.join(root, file)
                hdfs_file_path = os.path.join(hdfs_dir, file)
                try:
                    logger.info(f"Đang tải {local_file_path} lên {hdfs_file_path}...")
                    client.upload(hdfs_file_path, local_file_path, overwrite=True)
                    logger.info(f"Tải lên HDFS thành công: {hdfs_file_path}")
                except Exception as e:
                    logger.error(f"Lỗi khi tải {local_file_path} lên HDFS: {e}")

if __name__ == "__main__":
    try:
        push_parquet_files(LOCAL_DIR, HDFS_DIR)
    except Exception as e:
        logger.error(f"Lỗi trong quá trình thực thi: {e}")
