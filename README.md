----HDFS----
docker build -t hadoop_base:1 .

docker compose up



# namenode
hadoop classpath

export CLASSPATH=$(hadoop classpath)

echo 'export CLASSPATH=$(hadoop classpath)' >> ~/.bashrc

source ~/.bashrc

hdfs dfs -ls /opt/hadoop/tiki_data/

python3 /opt/hadoop/dags/push_to_hdfs.py

python3 /opt/hadoop/dags/migrate_hdfs_to_postgres.py



pip3 install psycopg2-binary

hdfs dfs -mkdir -p /spark-logs

hdfs dfs -chmod 777 /spark-logs

spark-submit     --master local[*]     /opt/hadoop/dags/migrate_hdfs_to_postgres.py 





# docker 
docker rm -f $(docker ps -a -q)


