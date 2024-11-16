FROM hadoop_base:1

# Tạo thư mục lưu trữ cho NameNode
RUN mkdir -p /opt/hdfs/namenode

# Thêm tệp cấu hình
ADD ./config-file/core-site.xml $HADOOP_HOME/etc/hadoop/
ADD ./config-file/hdfs-site.xml $HADOOP_HOME/etc/hadoop/
ADD ./config-file/hadoop-env.sh $HADOOP_HOME/etc/hadoop/

# Format NameNode trước khi chạy
RUN hdfs namenode -format

# Chạy NameNode
CMD ["hdfs", "namenode"]
