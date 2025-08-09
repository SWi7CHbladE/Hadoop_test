

# Hadoop on Two Ubuntu Containers 🐘

This document provides a comprehensive guide to setting up and running a two-node Hadoop cluster using Podman on Ubuntu containers. The setup includes a master node and a worker node, configured to process data using a MapReduce job.

---

## ⚙️ 1. Hadoop Installation

This section details the steps to create a network, define the container environment, and build the necessary Docker image.

### 1.1. Create a Network

[cite: *
Execute the following command on the host machine to create a network for the Hadoop containers:
```bash
podman network create hadoop-net
````

### 1.2. Define the Environment with a Dockerfile

Create a `Dockerfile` to define the Ubuntu environment. This file will install dependencies, set up a user, configure passwordless SSH, and download Hadoop.

```dockerfile
# Dockerfile
FROM ubuntu:22.04

# Avoid interactive prompts during installation 
ARG DEBIAN_FRONTEND=noninteractive

# Install dependencies, including nano and vim 
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
RUN wget [https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz](https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz) -P /tmp/ && \
    tar -xvf /tmp/hadoop-3.3.6.tar.gz -C /opt/ && \
    rm /tmp/hadoop-3.3.6.tar.gz && \
    ln -s /opt/hadoop-3.3.6 /opt/hadoop

# Add hadoop user and group 
RUN groupadd --gid 1000 hadoop && \
    useradd --uid 1000 --gid 1000 -m hadoop

# Set up passwordless SSH for the hadoop user 
RUN su hadoop -c "ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa" && \
    su hadoop -c "cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys" && \
    chmod 600 /home/hadoop/.ssh/authorized_keys

# Set environment variables 
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Set default shell for hadoop user to bash 
RUN chsh -s /bin/bash hadoop

# Change ownership of Hadoop Installation to the hadoop user 
RUN chown -R hadoop:hadoop /opt/hadoop-3.3.6

# Create the parent directory for Hadoop data and set ownership 
RUN mkdir -p /opt/hadoop_data
RUN chown -R hadoop:hadoop /opt/hadoop_data

# Copy config folder to Hadoop's config directory 
COPY config/ $HADOOP_CONF_DIR/

# Resolve Missing privilege separation directory error 
RUN mkdir /run/sshd

# Run SSH service 
CMD ["/usr/sbin/sshd", "-D"]
```

### 1.3. Create Configuration Files

Create a `config` directory  and populate it with the following configuration files:

  * **`config/hadoop-env.sh`**:

    ```bash
    # Set JAVA_HOME 
    export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
    # Force pdsh to use ssh 
    export PDSH_RCMD_TYPE=ssh
    ```

  * **`config/core-site.xml`**:

    ```xml
    <configuration>
        <property>
            <name>fs.defaultFS</name>
            <value>hdfs://hadoop-master:9000</value>
        </property>
    </configuration>
    ```

  * **`config/hdfs-site.xml`**:

    ```xml
    <configuration>
        <property>
            <name>dfs.replication</name>
            <value>1</value>
        </property>
        <property>
            <name>dfs.namenode.name.dir</name>
            <value>file:///opt/hadoop_data/hdfs/namenode</value>
        </property>
        <property>
            <name>dfs.datanode.data.dir</name>
            <value>file:///opt/hadoop_data/hdfs/datanode</value>
        </property>
    </configuration>
    ```

  * **`config/yarn-site.xml`**:

    ```xml
    <configuration>
        <property>
            <name>yarn.resourcemanager.hostname</name>
            <value>hadoop-master</value>
        </property>
        <property>
            <name>yarn.nodemanager.aux-services</name>
            <value>mapreduce_shuffle</value>
        </property>
    </configuration>
    ```

  * **`config/mapred-site.xml`**:

    ```xml
    <configuration>
        <property>
            <name>mapreduce.framework.name</name>
            <value>yarn</value>
        </property>
        <property>
            <name>yarn.app.mapreduce.am.env</name>
            <value>HADOOP_MAPRED_HOME=${HADOOP_HOME}</value>
        </property>
        <property>
            <name>mapreduce.map.env</name>
            <value>HADOOP_MAPRED_HOME=${HADOOP_HOME}</value>
        </property>
        <property>
            <name>mapreduce.reduce.env</name>
            <value>HADOOP_MAPRED_HOME=${HADOOP_HOME}</value>
        </property>
    </configuration>
    ```

  * **`config/workers`**:

    ```
    hadoop-worker
    ```

### 1.4. Build and Launch the Containers

1.  **Build the docker image** by running the following command in the same directory as your Dockerfile:

    ```bash
    podman build -t hadoop-ubuntu .
    ```

2.  **Launch the master and worker containers**:

    ```bash
    # Launch the master container 
    podman run -d --name hadoop-master --hostname hadoop-master --network hadoop-net --cap-add=SYS_NICE -p 9870:9870 -p 8088:8088 hadoop-ubuntu

    # Launch the worker container 
    podman run -d --name hadoop-worker --hostname hadoop-worker --network hadoop-net --cap-add=SYS_NICE hadoop-ubuntu
    ```

### 1.5. Format and Start the Cluster

These commands are run from your host machine but executed on the master container.

1.  **Format the NameNode** (run this only once\!):

    ```bash
    podman exec -u hadoop hadoop-master hdfs namenode -format
    ```

2.  **Start HDFS and YARN daemons**:

    ```bash
    podman exec -u hadoop hadoop-master start-dfs.sh
    podman exec -u hadoop hadoop-master start-yarn.sh
    ```

### 1.6. Verify the Hadoop Cluster

1.  **Check Running Java Processes** using the `jps` command on both containers:

      * On the **master**, you should see `NameNode`, `ResourceManager`, and `SecondaryNameNode`.
        ```bash
        podman exec -u hadoop hadoop-master jps
        ```
      * On the **worker**, you should see `DataNode` and `NodeManager`.
        ```bash
        podman exec -u hadoop hadoop-worker jps
        ```

2.  **Access Web UIs**:

      * **HDFS NameNode UI**: `http://localhost:9870` 
      * **YARN ResourceManager UI**: `http://localhost:8088` 

You can log in to the `hadoop-master`'s shell by executing:

```bash
podman exec -it -u hadoop hadoop-master bash
```

-----

## 🚀 2. Running a MapReduce Job

This section outlines how to load your data and processing scripts into the Hadoop cluster.

1.  **Create a `process` directory** in your installation folder and copy your data file, `mapper.py`, and `reducer.py` into it.

2.  **Copy the scripts and data to the master container**:

    ```bash
    podman cp process/mapper.py hadoop-master:/tmp/mapper.py
    podman cp process/reducer.py hadoop-master:/tmp/reducer.py
    podman cp process/generated_data.csv hadoop-master:/tmp/generated_data.csv
    ```

3.  **Access the hadoop master shell**:

    ```bash
    podman exec -it -u hadoop hadoop-master bash
    ```

4.  **Create an input directory in HDFS**:

    ```bash
    hdfs dfs -mkdir -p /user/hadoop/input
    ```

5.  **Upload the data file to HDFS**:

    ```bash
    hdfs dfs -put /tmp/generated_data.csv /user/hadoop/input
    ```

6.  **Run the Hadoop streaming job**:

    ```bash
    hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
      -files /tmp/mapper.py,/tmp/reducer.py \
      -mapper 'python3 mapper.py' \
      -reducer 'python3 reducer.py' \
      -input /user/hadoop/input/generated_data.csv \
      -output /user/hadoop/output
    ```

7.  **Check the output** after the job is complete:

    ```bash
    # List the files in your output directory 
    hdfs dfs -ls /user/hadoop/output

    # View the contents of the result file 
    hdfs dfs -cat /user/hadoop/output/part-00000
    ```

-----

## 🐍 3. Sample Python Code

The following scripts demonstrate a MapReduce job to aggregate products purchased per unique phone number.

### `mapper.py`

```python
#!/usr/bin/env python3
import sys

# The input provided to the mapper is through stdin. 
for line in sys.stdin:
    line = line.strip() # This will remove any leading or trailing whitespaces. 
    if not line: # Incase the line is invalid, skip onto the next line. 
        continue
    if line.startswith("PhoneNumber"): # Skip header if present. 
        continue
    
    # As the file is a csv, the phone and product can be separated by splitting them by the (comma) symbol. 
    phone, product = line.split(",", 1)
    
    # Print the phone number and the product. 
    print(f"{phone}\t{product}")
```

### `reducer.py`

```python
#!/usr/bin/env python3
import sys

current_phone = None
products = []

# The input provided to the reducer is through stdin. 
for line in sys.stdin:
    line = line.strip() # Strip the line again in case any whitespaces got introduced. 
    if not line: # Continue if not a valid line. 
        continue
    
    # Split the variables using '\t' as the delimiter set by the mapper function. 
    phone, product = line.split("\t", 1)

    # Check phone number by phone number
    if current_phone == phone:
        # if the retrieved phone number == currently observed phone number, append the product to the product list. 
        products.append(product)
    else:
        if current_phone:
            # Final output. 
            print(f"{current_phone}\t{','.join(products)}")
        current_phone = phone
        products = [product]

# In case the phone number was set to none, set the retrieved phone number to currently observed phone number. 
if current_phone:
    # Print the output. 
    print(f"{current_phone}\t{','.join(products)}")
```
