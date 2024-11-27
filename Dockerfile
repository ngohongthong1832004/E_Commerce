FROM ubuntu:20.04

# Environment setup
ENV JAVA_HOME=/opt/jdk
ENV HADOOP_HOME=/opt/hadoop
ENV SPARK_HOME=/opt/spark
ENV PATH=$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin:$PATH
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV LD_LIBRARY_PATH=$JAVA_HOME/lib/server:$LD_LIBRARY_PATH

# Install essential packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    tar \
    python3 \
    python3-pip \
    openjdk-8-jdk-headless \
    rsync \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt

# Copy JDK, Hadoop, and Spark archives
COPY ./assets/jdk.tar.gz /opt/jdk.tar.gz
COPY ./assets/hadoop-3.3.6.tar.gz /opt/hadoop.tar.gz
COPY ./assets/spark-3.5.3-bin-hadoop3.tgz /opt/spark.tar.gz

# Copy PostgreSQL driver
RUN mkdir -p /opt/spark/jars
COPY ./assets/postgresql-42.7.4.jar /opt/spark/jars/postgresql-42.7.4.jar

# Install Python dependencies
COPY ./requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt

# Extract and configure JDK
RUN tar -xzf /opt/jdk.tar.gz -C /opt && \
    mv /opt/jdk8u382-b05 /opt/jdk && \
    rm -f /opt/jdk.tar.gz

# Extract and configure Hadoop
RUN tar -xzf /opt/hadoop.tar.gz -C /opt && \
    mv /opt/hadoop-3.3.6 /opt/hadoop && \
    rm -f /opt/hadoop.tar.gz

# Extract and configure Spark
RUN tar -xzf /opt/spark.tar.gz -C /opt && \
    rsync -av /opt/spark-3.5.3-bin-hadoop3/ /opt/spark/ && \
    rm -rf /opt/spark-3.5.3-bin-hadoop3 && \
    rm -f /opt/spark.tar.gz

# Configure Spark environment
RUN cp $SPARK_HOME/conf/spark-env.sh.template $SPARK_HOME/conf/spark-env.sh && \
    echo "export JAVA_HOME=$JAVA_HOME" >> $SPARK_HOME/conf/spark-env.sh && \
    echo "export HADOOP_HOME=$HADOOP_HOME" >> $SPARK_HOME/conf/spark-env.sh && \
    echo "export SPARK_HOME=$SPARK_HOME" >> $SPARK_HOME/conf/spark-env.sh && \
    echo "export HADOOP_CONF_DIR=$HADOOP_CONF_DIR" >> $SPARK_HOME/conf/spark-env.sh

RUN cp $SPARK_HOME/conf/spark-defaults.conf.template $SPARK_HOME/conf/spark-defaults.conf && \
    echo "spark.master local[*]" >> $SPARK_HOME/conf/spark-defaults.conf && \
    echo "spark.eventLog.enabled true" >> $SPARK_HOME/conf/spark-defaults.conf && \
    echo "spark.eventLog.dir hdfs://namenode:9000/spark-logs" >> $SPARK_HOME/conf/spark-defaults.conf && \
    echo "spark.history.fs.logDirectory hdfs://namenode:9000/spark-logs" >> $SPARK_HOME/conf/spark-defaults.conf

# Copy Hadoop configuration files
RUN mkdir -p $HADOOP_HOME/etc/hadoop
COPY ./config-files/hadoop-env.sh $HADOOP_HOME/etc/hadoop/
COPY ./config-files/core-site.xml $HADOOP_HOME/etc/hadoop/
COPY ./config-files/hdfs-site.xml $HADOOP_HOME/etc/hadoop/

# Create HDFS directories
RUN mkdir -p /opt/hdfs/namenode /opt/hdfs/datanode && \
    chown -R root:root /opt/hdfs

# Copy DAGs
RUN mkdir -p /opt/hadoop/dags
COPY ./dags/push_to_hdfs.py /opt/hadoop/dags/push_to_hdfs.py
COPY ./dags/migrate_hdfs_to_postgres.py /opt/hadoop/dags/migrate_hdfs_to_postgres.py
COPY ./dags/result.py /opt/hadoop/dags/result.py

# Copy and configure entrypoint script
COPY ./entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

# Expose necessary ports
EXPOSE 9870 9864 8088 9000 4040

# Start the entrypoint
CMD ["/opt/entrypoint.sh"]
