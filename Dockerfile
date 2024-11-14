# Sử dụng image Ubuntu cơ bản
FROM ubuntu:20.04

# Đặt các biến môi trường cần thiết
ENV HADOOP_VERSION=3.3.4
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Cài đặt các gói cần thiết
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk wget curl ssh rsync python3-pip \
    && apt-get clean

# Cài đặt thư viện hdfs cho Python
RUN pip3 install hdfs

# Tạo thư mục cho Hadoop và tải về Hadoop
RUN mkdir -p $HADOOP_HOME && \
    wget -qO- https://downloads.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz | tar -xz -C /opt/ && \
    mv /opt/hadoop-$HADOOP_VERSION/* $HADOOP_HOME && \
    rm -rf /opt/hadoop-$HADOOP_VERSION

# Thiết lập cấu hình SSH không mật khẩu
RUN ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys

# Thiết lập quyền
RUN mkdir -p /opt/hadoop_tmp/hdfs/namenode && \
    mkdir -p /opt/hadoop_tmp/hdfs/datanode && \
    chown -R root:root /opt/hadoop_tmp

# Cấu hình HDFS và YARN (copy core-site.xml, hdfs-site.xml, và yarn-site.xml)
COPY core-site.xml $HADOOP_CONF_DIR/core-site.xml
COPY hdfs-site.xml $HADOOP_CONF_DIR/hdfs-site.xml
COPY yarn-site.xml $HADOOP_CONF_DIR/yarn-site.xml

# Mở cổng cho HDFS và YARN
EXPOSE 9870 9864 8088 8042

# Khởi tạo HDFS
RUN $HADOOP_HOME/bin/hdfs namenode -format

# Thiết lập lệnh khởi chạy
CMD ["/bin/bash"]
