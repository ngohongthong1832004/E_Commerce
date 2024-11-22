FROM ubuntu:20.04

ENV JAVA_HOME=/opt/jdk
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    tar \
    python3 \
    python3-pip \
    openjdk-11-jdk-headless && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt

# Copy JDK và Hadoop từ thư mục assets
COPY ./assets/jdk.tar.gz /opt/jdk.tar.gz
COPY ./assets/hadoop-3.3.6.tar.gz /opt/hadoop.tar.gz

# Copy file requirements.txt vào container
COPY ./requirements.txt /opt/requirements.txt
# Cài đặt các package từ requirements.txt
RUN pip install -r /opt/requirements.txt


# Giải nén JDK
RUN tar -xzf /opt/jdk.tar.gz -C /opt && \
    mv /opt/jdk8u382-b05 /opt/jdk && \
    rm -f /opt/jdk.tar.gz

# Giải nén Hadoop
RUN tar -xzf /opt/hadoop.tar.gz -C /opt && \
    mv /opt/hadoop-3.3.6 /opt/hadoop && \
    rm -f /opt/hadoop.tar.gz

# Copy file cấu hình Hadoop
COPY ./config-files/hadoop-env.sh $HADOOP_HOME/etc/hadoop/
COPY ./config-files/core-site.xml $HADOOP_HOME/etc/hadoop/
COPY ./config-files/hdfs-site.xml $HADOOP_HOME/etc/hadoop/

# Tạo thư mục cho NameNode và DataNode
RUN mkdir -p /opt/hdfs/namenode /opt/hdfs/datanode && \
    chown -R root:root /opt/hdfs

# Copy dữ liệu từ dags/data
COPY ./dags/push_to_hdfs.py /opt/hadoop/push_to_hdfs.py

# Copy và cấu hình entrypoint script
COPY ./entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

# Expose cổng Hadoop
EXPOSE 9870 9864 8088 9000

CMD ["/opt/entrypoint.sh"]
