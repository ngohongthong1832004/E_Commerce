from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from pyspark.sql.types import IntegerType, DoubleType, StringType, LongType
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# PostgreSQL connection configuration
jdbc_url = "jdbc:postgresql://localhost:5432/product_db"  # Update with your database name
table_name = "new_product"
user = "airflow"  # Update with your PostgreSQL username
password = "airflow"  # Update with your PostgreSQL password
write_mode = "overwrite"  # Or "append" depending on your needs

# Define the fields to migrate
selected_columns = [
    'id', 'sku', 'name', 'price', 'list_price', 'discount',
    'discount_rate', 'rating_average', 'review_count',
    'order_count', 'favourite_count', 'thumbnail_url',
    'quantity_sold', 'original_price', 'seller_id', 'seller',
    'seller_product_id', 'brand_name', 'category_l1_name',
    'category_l2_name', 'category_l3_name'
]

# Define the data types for each column
column_types = {
    'id': LongType(),
    'sku': StringType(),
    'name': StringType(),
    'price': DoubleType(),
    'list_price': DoubleType(),
    'discount': DoubleType(),
    'discount_rate': DoubleType(),
    'rating_average': DoubleType(),
    'review_count': IntegerType(),
    'order_count': IntegerType(),
    'favourite_count': IntegerType(),
    'thumbnail_url': StringType(),
    'quantity_sold': IntegerType(),
    'original_price': DoubleType(),
    'seller_id': LongType(),
    'seller': StringType(),
    'seller_product_id': LongType(),
    'brand_name': StringType(),
    'category_l1_name': StringType(),
    'category_l2_name': StringType(),
    'category_l3_name': StringType()
}

def handle_parquet_and_save(parquet_path):
    try:
        # Initialize SparkSession
        spark = SparkSession.builder \
            .appName("Handle Parquet and Save to PostgreSQL") \
            .config("spark.jars", "/path/to/postgresql-42.7.4.jar") \
            .getOrCreate()

        # Read data from Parquet files
        logger.info(f"Reading Parquet data from {parquet_path}...")
        df = spark.read.parquet(parquet_path)

        # Cast columns to appropriate data types and select required columns
        logger.info("Selecting necessary columns and casting data types...")
        for column in selected_columns:
            if column in df.columns:
                df = df.withColumn(column, col(column).cast(column_types[column]))
            else:
                logger.warning(f"Column {column} not found in DataFrame. Filling with null values.")
                df = df.withColumn(column, lit(None).cast(column_types[column]))

        # Select the columns in the specified order
        filtered_df = df.select(selected_columns)

        # Write the data to PostgreSQL
        logger.info(f"Writing data to PostgreSQL table {table_name}...")
        filtered_df.write.jdbc(
            url=jdbc_url,
            table=table_name,
            mode=write_mode,
            properties={
                "user": user,
                "password": password,
                "driver": "org.postgresql.Driver"
            }
        )
        logger.info("Data written successfully to PostgreSQL!")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
    finally:
        # Stop SparkSession
        spark.stop()

if __name__ == "__main__":
    # Update the path to your Parquet files
    parquet_path = "/opt/hadoop/tiki_data"
    handle_parquet_and_save(parquet_path)
