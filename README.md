----HDFS----
docker build -t hadoop_base .

docker compose -f hdfs-docker-compose.yml up -d