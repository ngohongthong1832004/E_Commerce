import os
from hdfs import InsecureClient

# Cấu hình HDFS
HDFS_URL = 'http://localhost:9870'  
client = InsecureClient(HDFS_URL, user='hadoop')  

def push_parquet_files(local_dir, hdfs_dir):
    """
    Tải tất cả các tệp Parquet từ thư mục cục bộ lên thư mục HDFS.

    Args:
    - local_dir (str): Đường dẫn tới thư mục cục bộ chứa các tệp Parquet.
    - hdfs_dir (str): Đường dẫn thư mục trên HDFS để lưu các tệp.
    """
    client.makedirs(hdfs_dir)
    
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            if file.endswith('.parquet'):
                local_file_path = os.path.join(root, file)
                hdfs_file_path = os.path.join(hdfs_dir, file)
                try:
                    client.upload(hdfs_file_path, local_file_path, overwrite=True)
                    print(f"Tải lên HDFS thành công: {hdfs_file_path}")
                except Exception as e:
                    print(f"Lỗi khi tải {local_file_path} lên HDFS: {e}")

local_parquet_dir = "./src/data"
hdfs_destination_dir = "/user/hadoop/tiki_dataset"  
push_parquet_files(local_parquet_dir, hdfs_destination_dir)
