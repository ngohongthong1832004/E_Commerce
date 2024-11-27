import pyarrow.fs as fs
import os
import logging

# Define directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
DATA_DIR = os.path.join(BASE_DIR, 'data')
HDFS_DIR = '/opt/hadoop/tiki_data'
LOCAL_DIR = DATA_DIR  # Use local directory under BASE_DIR for data files


# Initialize logging
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

logger = init_log('hdfs_tiki', LOG_DIR, 'hdfs_tiki.log')

# Function to push Parquet files to HDFS
def push_parquet_files(local_dir, hdfs_dir):
    """
    Upload .parquet files from a local directory to HDFS.
    """
    try:
        logger.info("Attempting to connect to HDFS namenode on port 9000...")
        hdfs = fs.HadoopFileSystem('namenode', port=9000)
        logger.info("Successfully connected to HDFS.")

        logger.info(f"Scanning local directory for .parquet files: {local_dir}")
        for root, _, files in os.walk(local_dir):
            logger.info(f"Scanning directory: {root}")
            for file in files:
                if file.endswith('.parquet'):
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, local_dir)
                    hdfs_file_path = os.path.join(hdfs_dir, relative_path).replace("\\", "/")

                    logger.info(f"Found .parquet file: {local_file_path}. Preparing to upload to HDFS path: {hdfs_file_path}")
                    
                    # Ensure HDFS directories exist
                    hdfs_dirname = os.path.dirname(hdfs_file_path)
                    try:
                        hdfs.create_dir(hdfs_dirname)
                        logger.info(f"HDFS directory ensured: {hdfs_dirname}")
                    except Exception as e:
                        logger.warning(f"Failed to create HDFS directory {hdfs_dirname}: {e}")

                    # Upload the file to HDFS
                    try:
                        with open(local_file_path, 'rb') as f:
                            with hdfs.open_output_stream(hdfs_file_path) as out:
                                out.write(f.read())
                        logger.info(f"Successfully uploaded file to HDFS: {hdfs_file_path}")
                    except Exception as e:
                        logger.error(f"Error uploading file {file} to HDFS: {e}")
    except Exception as e:
        logger.error(f"Failed to connect to HDFS: {e}")
    finally:
        logger.info("HDFS upload process completed.")

# Main entry point
if __name__ == "__main__":
    logger.info("Starting HDFS push process...")
    try:
        if os.path.exists(LOCAL_DIR):
            logger.info(f"Local directory exists: {LOCAL_DIR}")
            parquet_files = [f for f in os.listdir(LOCAL_DIR) if f.endswith('.parquet')]
            if parquet_files:
                logger.info(f"Found {len(parquet_files)} .parquet files: {parquet_files}")
                push_parquet_files(LOCAL_DIR, HDFS_DIR)
            else:
                logger.info(f"No .parquet files found in directory: {LOCAL_DIR}")
        else:
            logger.warning(f"Local directory does not exist: {LOCAL_DIR}")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
    logger.info("HDFS push process finished.")
