----HDFS----
docker build -t hadoop_base:1 .

docker compose -f hdfs-docker-compose.yml up



# namenode
export CLASSPATH=$(hadoop classpath)

echo 'export CLASSPATH=$(hadoop classpath)' >> ~/.bashrc

source ~/.bashrc