FROM hadoop_base:1

# Tạo thư mục lưu trữ cho DataNode
RUN mkdir -p /opt/hdfs/datanode

# Thêm tệp cấu hình
ADD ./config-file/core-site.xml $HADOOP_HOME/etc/hadoop/
ADD ./config-file/hdfs-site.xml $HADOOP_HOME/etc/hadoop/
ADD ./config-file/hadoop-env.sh $HADOOP_HOME/etc/hadoop/

# Chạy DataNode
CMD ["hdfs", "datanode"]
