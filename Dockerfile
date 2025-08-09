# Dockerfile
FROM ubuntu:22.04

# Avoid interactive prompts during installation
ARG DEBIAN_FRONTEND=noninteractive

# Install dependencies including nano and vim
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    ssh \
    wget \
    pdsh \
    nano \
    vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download and unpack Hadoop (v3.3.6 is a stable version)
RUN wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz -P /tmp/ && \
    tar -xvf /tmp/hadoop-3.3.6.tar.gz -C /opt/ && \
    rm /tmp/hadoop-3.3.6.tar.gz && \
    ln -s /opt/hadoop-3.3.6 /opt/hadoop

# Add hadoop user and group
RUN groupadd --gid 1000 hadoop && \
    useradd --uid 1000 --gid 1000 -m hadoop

# Set up passwordless SSH for the 'hadoop' user
RUN su - hadoop -c "ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa" && \
    su - hadoop -c "cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys" && \
    chmod 600 /home/hadoop/.ssh/authorized_keys

# Set environment variables
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Set default shell for hadoop user to bash
RUN chsh -s /bin/bash hadoop

# Change ownership of hadoop installation to the hadoop user
RUN chown -R hadoop:hadoop /opt/hadoop-3.3.6

# Create the parent directory for Hadoop data and set ownership
RUN mkdir -p /opt/hadoop_data
RUN chown -R hadoop:hadoop /opt/hadoop_data

# Copy config folder to Hadoop's config directory
COPY config/* $HADOOP_CONF_DIR/

# Resolve Missing privilege separation directory error
RUN mkdir /run/sshd

# Run SSH service
CMD ["/usr/sbin/sshd", "-D"]
