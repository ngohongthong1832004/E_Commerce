import pyarrow.fs as fs
import os
import logging

HDFS_DIR = '/opt/hadoop/tiki_data'
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
    try:
        logger.info(f"Connecting to HDFS namenode on port 9000...")
        hdfs = fs.HadoopFileSystem('namenode', port=9000)
        logger.info("Connected to HDFS.")
        for root, _, files in os.walk(local_dir):
            for file in files:
                if file.endswith('.parquet'):
                    local_file_path = os.path.join(root, file)
                    hdfs_file_path = f"{hdfs_dir}/{file}"
                    logger.info(f"Processing file {local_file_path}...")
                    try:
                        with open(local_file_path, 'rb') as f:
                            with hdfs.open_output_stream(hdfs_file_path) as out:
                                out.write(f.read())
                        logger.info(f"Successfully uploaded {file} to HDFS.")
                    except Exception as e:
                        logger.error(f"Error uploading {file}: {e}")
    except Exception as e:
        logger.error(f"Error connecting to HDFS: {e}")
if __name__ == "__main__":
    if os.path.exists(LOCAL_DIR) and any(f.endswith('.parquet') for f in os.listdir(LOCAL_DIR)):
        push_parquet_files(LOCAL_DIR, HDFS_DIR)
    else:
        logger.info(f"No .parquet files found in directory: {LOCAL_DIR}")
