#!/bin/bash

# Thiết lập biến môi trường cơ bản
export JAVA_HOME=${JAVA_HOME:-/opt/jdk}
export HADOOP_HOME=${HADOOP_HOME:-/opt/hadoop}
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
export LD_LIBRARY_PATH=$JAVA_HOME/jre/lib/amd64/server:$LD_LIBRARY_PATH

# Kiểm tra biến môi trường
echo "JAVA_HOME hiện tại: $JAVA_HOME"
echo "HADOOP_HOME hiện tại: $HADOOP_HOME"
echo "PATH hiện tại: $PATH"
echo "LD_LIBRARY_PATH hiện tại: $LD_LIBRARY_PATH"

# Kiểm tra lệnh hdfs
which hdfs || { echo "Lệnh hdfs không được tìm thấy trong PATH. Kiểm tra HADOOP_HOME."; exit 1; }

# Kiểm tra vai trò của container
if [[ "$HOSTNAME" == "namenode" ]]; then
    echo "Starting NameNode setup..."
    mkdir -p /opt/hdfs/namenode /opt/hdfs/datanode
    mkdir -p /opt/hdfs/namenode /opt/hadoop/tiki_data
    chown -R root:root /opt/hdfs

    # Kiểm tra xem NameNode đã được format chưa
    if [ ! -d "/opt/hdfs/namenode/current" ]; then
        echo "Formatting NameNode..."
        hdfs namenode -format -force -nonInteractive
    else
        echo "NameNode đã được format trước đó."
    fi

    echo "Starting NameNode..."
    exec hdfs namenode
else
    echo "Starting DataNode setup..."
    mkdir -p /opt/hdfs/datanode
    chown -R root:root /opt/hdfs

    echo "Starting DataNode..."
    exec hdfs datanode
fi
