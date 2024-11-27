#!/bin/bash

# Thêm Hadoop vào PATH
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH

# Kiểm tra lệnh hdfs
echo "PATH hiện tại: $PATH"
which hdfs || echo "Lệnh hdfs không được tìm thấy trong PATH."

# Kiểm tra vai trò của container
if [[ "$HOSTNAME" == "namenode" ]]; then
    echo "Starting NameNode setup..."
    mkdir -p /opt/hdfs/namenode /opt/hdfs/datanode
    mkdir -p /opt/hdfs/namenode /opt/hadoop/tiki_data
    chown -R root:root /opt/hdfs

    export CLASSPATH=$(hadoop classpath)
    echo 'export CLASSPATH=$(hadoop classpath)' >> ~/.bashrc
    source ~/.bashrc

    # python3 /opt/hadoop/dags/push_to_hdfs.py


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


