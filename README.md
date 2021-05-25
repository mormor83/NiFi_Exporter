# NiFi Exporter

Prometheus exporter for Nifi metrics written in python  
Data is scraped by [prometheus](https://prometheus.io).

## Installation

### Docker
Run the following to build the image using docker

      docker build -t nifi_monitor .

Run the following to run the exporter
      
      docker run --rm --name nifi_monitor -p 9092:5000 -e BASE_URL=[HOST:PORT] nifi_monitor
      
As alternative, run the following to build the image using Docker-compose

      docker-compose up -d --build

 
## Configuration

nifi_exporter uses environment variables for configuration.
Settings:

Environment variable|default|description
--------------------|-------|------------
BASE_URL|None| Use the following format https:// <Nifi Domain> : <Cluster port>
USERNAME|None|Please make sure you have the relevant policies 
PASSWORD|None|
CONNECTIONS_QUEUE|True| set `True` if you want to get queue metrics or `False` if not
  
  
## Metrics

All metrics are prefixed with "nifi_".


### Nodes
metric | description
-------| ------------
nifi_nodes_status| General status per node
nifi_node_activeThreadCount| Active Thread Count
nifi_node_queuedItems|Each node queued items

### Cluster
metric | description
-------| ------------
nifi_cluster_activeThreadCount |
nifi_cluster_terminatedThreadCount |
nifi_cluster_flowFilesQueued |
nifi_cluster_bytesQueued |
nifi_cluster_runningCount|
nifi_cluster_stoppedCount|
nifi_cluster_invalidCount|

### Processor
metric | description
-------| ------------
nifi_amount_items_queued | Count the number of queued files per PG

### Queue
metric | description
-------| ------------
nifi_connection_queue | Queue size by connection. Queue name is `SourceProcessor`\_to_`DestinationProcessor`


Grafana Dashboard
-------
Grafana Dashboard ID: 11387, name: NiFi Monitoring.  
For details of the dashboard please see [NiFi Monitoring](https://grafana.com/grafana/dashboards/11387).









