import pyarrow.fs as fs
import os
import logging

HDFS_DIR = 'user/opt/hadoop/tiki_data'
LOCAL_DIR = '/opt/hadoop/data'

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

# Hàm đẩy file lên HDFS
def push_parquet_files(local_dir, hdfs_dir):
    """
    Đẩy tất cả các file .parquet từ thư mục cục bộ lên HDFS.

    Args:
        local_dir (str): Đường dẫn thư mục cục bộ.
        hdfs_dir (str): Đường dẫn thư mục trên HDFS.
    """
    try:
        hdfs = fs.HadoopFileSystem('namenode', port=9000)  # Kết nối đến HDFS
        for root, _, files in os.walk(local_dir):
            for file in files:
                if file.endswith('.parquet'):
                    local_file_path = os.path.join(root, file)
                    hdfs_file_path = f"{hdfs_dir}/{file}"
                    try:
                        logger.info(f"Uploading {local_file_path} to {hdfs_file_path}...")
                        with open(local_file_path, 'rb') as f:
                            with hdfs.open_output_stream(hdfs_file_path) as out:
                                out.write(f.read())
                        logger.info(f"Successfully uploaded {file} to HDFS.")
                    except Exception as e:
                        logger.error(f"Error uploading {file} to HDFS: {e}")
    except Exception as e:
        logger.error(f"Error connecting to HDFS: {e}")

if __name__ == "__main__":
    if os.path.exists(LOCAL_DIR) and any(f.endswith('.parquet') for f in os.listdir(LOCAL_DIR)):
        push_parquet_files(LOCAL_DIR, HDFS_DIR)
    else:
        logger.info(f"No .parquet files found in directory: {LOCAL_DIR}")
