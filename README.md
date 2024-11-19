----HDFS----
docker build -t hadoop_base:1 .

docker compose -f hdfs-docker-compose.yml up -d