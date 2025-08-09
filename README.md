

# Hadoop on Two Ubuntu Containers 🐘

This document provides a comprehensive guide to setting up and running a two-node Hadoop cluster using Podman on Ubuntu containers. The setup includes a master node and a worker node, configured to process data using a MapReduce job.

---

## ⚙️ 1. Hadoop Installation

This section details the steps to create a network, define the container environment, and build the necessary Docker image.

### 1.1. Create a Network

[cite_start]Execute the following command on the host machine to create a network for the Hadoop containers[cite: 4]:
```bash
podman network create hadoop-net
````

### 1.2. Define the Environment with a Dockerfile

[cite\_start]Create a `Dockerfile` to define the Ubuntu environment[cite: 5]. [cite\_start]This file will install dependencies, set up a user, configure passwordless SSH, and download Hadoop[cite: 6].

```dockerfile
# Dockerfile
FROM ubuntu:22.04

# [cite_start]Avoid interactive prompts during installation [cite: 9]
ARG DEBIAN_FRONTEND=noninteractive

# [cite_start]Install dependencies, including nano and vim [cite: 11]
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    ssh \
    wget \
    pdsh \
    nano \
    vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# [cite_start]Download and unpack Hadoop (v3.3.6 is a stable version) [cite: 21]
RUN wget [https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz](https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz) -P /tmp/ && \
    tar -xvf /tmp/hadoop-3.3.6.tar.gz -C /opt/ && \
    rm /tmp/hadoop-3.3.6.tar.gz && \
    ln -s /opt/hadoop-3.3.6 /opt/hadoop

# [cite_start]Add hadoop user and group [cite: 26]
RUN groupadd --gid 1000 hadoop && \
    useradd --uid 1000 --gid 1000 -m hadoop

# [cite_start]Set up passwordless SSH for the hadoop user [cite: 29]
RUN su hadoop -c "ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa" && \
    su hadoop -c "cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys" && \
    chmod 600 /home/hadoop/.ssh/authorized_keys

# [cite_start]Set environment variables [cite: 35]
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# [cite_start]Set default shell for hadoop user to bash [cite: 40]
RUN chsh -s /bin/bash hadoop

# [cite_start]Change ownership of Hadoop Installation to the hadoop user [cite: 42]
RUN chown -R hadoop:hadoop /opt/hadoop-3.3.6

# [cite_start]Create the parent directory for Hadoop data and set ownership [cite: 44]
RUN mkdir -p /opt/hadoop_data
RUN chown -R hadoop:hadoop /opt/hadoop_data

# [cite_start]Copy config folder to Hadoop's config directory [cite: 47]
COPY config/ $HADOOP_CONF_DIR/

# [cite_start]Resolve Missing privilege separation directory error [cite: 50]
RUN mkdir /run/sshd

# [cite_start]Run SSH service [cite: 51]
CMD ["/usr/sbin/sshd", "-D"]
```

### 1.3. Create Configuration Files

[cite\_start]Create a `config` directory [cite: 53] and populate it with the following configuration files:

  * [cite\_start]**`config/hadoop-env.sh`**[cite: 55]:

    ```bash
    # [cite_start]Set JAVA_HOME [cite: 56]
    export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
    # [cite_start]Force pdsh to use ssh [cite: 58]
    export PDSH_RCMD_TYPE=ssh
    ```

  * [cite\_start]**`config/core-site.xml`**[cite: 60]:

    ```xml
    <configuration>
        <property>
            <name>fs.defaultFS</name>
            <value>hdfs://hadoop-master:9000</value>
        </property>
    </configuration>
    ```

  * [cite\_start]**`config/hdfs-site.xml`**[cite: 67]:

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

  * [cite\_start]**`config/yarn-site.xml`**[cite: 82]:

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

  * [cite\_start]**`config/mapred-site.xml`**[cite: 93]:

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

  * [cite\_start]**`config/workers`**[cite: 113]:

    ```
    hadoop-worker
    ```

### 1.4. Build and Launch the Containers

1.  [cite\_start]**Build the docker image** by running the following command in the same directory as your Dockerfile[cite: 115]:

    ```bash
    podman build -t hadoop-ubuntu .
    ```

2.  [cite\_start]**Launch the master and worker containers**[cite: 116]:

    ```bash
    # [cite_start]Launch the master container [cite: 118]
    podman run -d --name hadoop-master --hostname hadoop-master --network hadoop-net --cap-add=SYS_NICE -p 9870:9870 -p 8088:8088 hadoop-ubuntu

    # [cite_start]Launch the worker container [cite: 120]
    podman run -d --name hadoop-worker --hostname hadoop-worker --network hadoop-net --cap-add=SYS_NICE hadoop-ubuntu
    ```

### 1.5. Format and Start the Cluster

[cite\_start]These commands are run from your host machine but executed on the master container[cite: 123].

1.  [cite\_start]**Format the NameNode** (run this only once\!)[cite: 124, 125]:

    ```bash
    podman exec -u hadoop hadoop-master hdfs namenode -format
    ```

2.  [cite\_start]**Start HDFS and YARN daemons**[cite: 128]:

    ```bash
    podman exec -u hadoop hadoop-master start-dfs.sh
    podman exec -u hadoop hadoop-master start-yarn.sh
    ```

### 1.6. Verify the Hadoop Cluster

1.  [cite\_start]**Check Running Java Processes** using the `jps` command on both containers[cite: 135]:

      * [cite\_start]On the **master**, you should see `NameNode`, `ResourceManager`, and `SecondaryNameNode`[cite: 136].
        ```bash
        podman exec -u hadoop hadoop-master jps
        ```
      * [cite\_start]On the **worker**, you should see `DataNode` and `NodeManager`[cite: 139].
        ```bash
        podman exec -u hadoop hadoop-worker jps
        ```

2.  [cite\_start]**Access Web UIs**[cite: 141]:

      * [cite\_start]**HDFS NameNode UI**: `http://localhost:9870` [cite: 143]
      * [cite\_start]**YARN ResourceManager UI**: `http://localhost:8088` [cite: 146]

[cite\_start]You can log in to the `hadoop-master`'s shell by executing[cite: 149]:

```bash
podman exec -it -u hadoop hadoop-master bash
```

-----

## 🚀 2. Running a MapReduce Job

This section outlines how to load your data and processing scripts into the Hadoop cluster.

1.  [cite\_start]**Create a `process` directory** in your installation folder and copy your data file, `mapper.py`, and `reducer.py` into it[cite: 152, 154].

2.  [cite\_start]**Copy the scripts and data to the master container**[cite: 155]:

    ```bash
    podman cp process/mapper.py hadoop-master:/tmp/mapper.py
    podman cp process/reducer.py hadoop-master:/tmp/reducer.py
    podman cp process/generated_data.csv hadoop-master:/tmp/generated_data.csv
    ```

3.  [cite\_start]**Access the hadoop master shell**[cite: 158]:

    ```bash
    podman exec -it -u hadoop hadoop-master bash
    ```

4.  [cite\_start]**Create an input directory in HDFS**[cite: 160]:

    ```bash
    hdfs dfs -mkdir -p /user/hadoop/input
    ```

5.  [cite\_start]**Upload the data file to HDFS**[cite: 162]:

    ```bash
    hdfs dfs -put /tmp/generated_data.csv /user/hadoop/input
    ```

6.  [cite\_start]**Run the Hadoop streaming job**[cite: 164]:

    ```bash
    hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
      -files /tmp/mapper.py,/tmp/reducer.py \
      -mapper 'python3 mapper.py' \
      -reducer 'python3 reducer.py' \
      -input /user/hadoop/input/generated_data.csv \
      -output /user/hadoop/output
    ```

7.  [cite\_start]**Check the output** after the job is complete[cite: 175]:

    ```bash
    # [cite_start]List the files in your output directory [cite: 176]
    hdfs dfs -ls /user/hadoop/output

    # [cite_start]View the contents of the result file [cite: 179]
    hdfs dfs -cat /user/hadoop/output/part-00000
    ```

-----

## 🐍 3. Sample Python Code

[cite\_start]The following scripts demonstrate a MapReduce job to aggregate products purchased per unique phone number[cite: 184].

### `mapper.py`

```python
#!/usr/bin/env python3
import sys

# [cite_start]The input provided to the mapper is through stdin. [cite: 195]
for line in sys.stdin:
    [cite_start]line = line.strip() # This will remove any leading or trailing whitespaces. [cite: 190]
    [cite_start]if not line: # Incase the line is invalid, skip onto the next line. [cite: 191, 196]
        continue
    [cite_start]if line.startswith("PhoneNumber"): # Skip header if present. [cite: 193]
        continue
    
    # [cite_start]As the file is a csv, the phone and product can be separated by splitting them by the (comma) symbol. [cite: 198, 199]
    phone, product = line.split(",", 1)
    
    # [cite_start]Print the phone number and the product. [cite: 201]
    print(f"{phone}\t{product}")
```

### `reducer.py`

```python
#!/usr/bin/env python3
import sys

current_phone = None
products = []

# [cite_start]The input provided to the reducer is through stdin. [cite: 209]
for line in sys.stdin:
    [cite_start]line = line.strip() # Strip the line again in case any whitespaces got introduced. [cite: 210, 213]
    [cite_start]if not line: # Continue if not a valid line. [cite: 214, 220]
        continue
    
    # [cite_start]Split the variables using '\t' as the delimiter set by the mapper function. [cite: 221]
    phone, product = line.split("\t", 1)

    # Check phone number by phone number
    if current_phone == phone:
        # [cite_start]if the retrieved phone number == currently observed phone number, append the product to the product list. [cite: 222, 223]
        products.append(product)
    else:
        if current_phone:
            # [cite_start]Final output. [cite: 231]
            print(f"{current_phone}\t{','.join(products)}")
        current_phone = phone
        products = [product]

# [cite_start]In case the phone number was set to none, set the retrieved phone number to currently observed phone number. [cite: 235]
if current_phone:
    # [cite_start]Print the output. [cite: 236]
    print(f"{current_phone}\t{','.join(products)}")
```

```
```
